import hmac
import json
import os
import secrets
import re
from pathlib import Path
from typing import Literal
from uuid import UUID

from fastapi import FastAPI, File, Form, Header, HTTPException, UploadFile
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field
from starlette.concurrency import run_in_threadpool

from . import modulos, imagens
from .catalogo import preparar
from .registros import Repositorio, EnvioConflitante

RAIZ = Path(__file__).resolve().parents[1]
Contexto = Literal["nao_informado", "area_publica", "frente_imovel", "obstaculo", "iluminacao_existente", "nova_iluminacao", "asfalto_comum", "corredor_onibus"]


class Entrada(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")


class Localizacao(Entrada):
    latitude: float = Field(ge=-90, le=90, allow_inf_nan=False)
    longitude: float = Field(ge=-180, le=180, allow_inf_nan=False)
    precisao_m: float | None = Field(default=None, ge=0, le=100000, allow_inf_nan=False)
    origem: Literal['gps', 'manual']
    confirmado: Literal[True]


class Pedido(Entrada):
    descricao: str = Field(min_length=10, max_length=1500)
    bairro: str = Field(min_length=2, max_length=100)
    local: str = Field(default="", max_length=250)
    contexto: Contexto = "nao_informado"
    confirmado: Literal[True]
    origem_id: str | None = Field(default=None, max_length=64)
    localizacao: Localizacao | None = None
    envio_id: UUID | None = None


class Revisao(Entrada):
    prioridade: Literal["Baixa", "Média", "Alta"]
    justificativa: str = Field(min_length=10, max_length=500)
    revisor: str = Field(min_length=2, max_length=80)


class Contestacao(Entrada):
    motivo: str = Field(min_length=10, max_length=500)


class Protocolo(Entrada):
    protocolo: str = Field(min_length=1, max_length=80)


class Pergunta(Entrada):
    pergunta: str = Field(min_length=1, max_length=500)
    anterior: str | None = Field(default=None, max_length=40)
    atendimento_id: str | None = Field(default=None, max_length=40)


class Trecho(Entrada):
    linha_corpus: int = Field(ge=1, le=10000)


def criar_app(pasta_dados: Path | None = None) -> FastAPI:
    pasta = pasta_dados or Path(os.getenv("GOV_DATA_DIR", str(RAIZ / "data")))
    pasta.mkdir(parents=True, exist_ok=True)
    repo = Repositorio(pasta / "central.sqlite")
    chave = os.getenv("GOV_MANAGER_KEY", "").strip()
    if not chave:
        arquivo_chave = pasta / "chave-gestao.txt"
        if not arquivo_chave.exists():
            arquivo_chave.write_text(secrets.token_urlsafe(32), encoding="utf-8")
        chave = arquivo_chave.read_text(encoding="utf-8").strip()

    app = FastAPI(title="Central CitizenTech", version="0.2.0", docs_url="/contrato")
    app.state.repo = repo

    def gestor(valor):
        if not valor or not hmac.compare_digest(valor, chave):
            raise HTTPException(401, "Chave de revisão não autorizada.")

    def obter(identificador):
        caso = repo.obter(identificador)
        if caso is None:
            raise HTTPException(404, "Atendimento não encontrado.")
        return caso

    @app.exception_handler(ValueError)
    async def valor_invalido(request, erro):
        return JSONResponse(status_code=422, content={"erro": str(erro)})

    @app.exception_handler(EnvioConflitante)
    async def envio_conflitante(request, erro):
        return JSONResponse(status_code=409, content={'erro': str(erro)})

    @app.exception_handler(RuntimeError)
    async def modulo_indisponivel(request, erro):
        return JSONResponse(status_code=503, content={"erro": str(erro)})

    @app.exception_handler(RequestValidationError)
    async def contrato_invalido(request, erro):
        campos = sorted({str(e["loc"][-1]) for e in erro.errors()})
        return JSONResponse(status_code=422, content={"erro": "Confira os campos e os limites de preenchimento.", "campos": campos})

    @app.middleware("http")
    async def proteger(request, call_next):
        tamanho = request.headers.get("content-length")
        if tamanho and (not tamanho.isdigit() or int(tamanho) > 9 * 1024 * 1024):
            return JSONResponse(status_code=413, content={"erro": "O envio excede o limite de tamanho."})
        resposta = await call_next(request)
        resposta.headers["X-Content-Type-Options"] = "nosniff"
        resposta.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        resposta.headers["Cache-Control"] = "no-store"
        resposta.headers["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data: blob: https://tile.openstreetmap.org; "
            "media-src 'self' blob:; object-src 'none'; base-uri 'none'; frame-ancestors 'none'; form-action 'self'"
        )
        return resposta

    @app.get("/api/status")
    def status():
        return {"servico": "Central CitizenTech", "status": "ok", "modo": "Demonstração local",
                "validacao_em_campo": False, "abertura_automatica_sp156": False}

    @app.post("/api/atendimentos", status_code=201)
    def criar(entrada: Pedido):
        dados = entrada.model_dump(mode='json', exclude={"confirmado"})
        dados["triagem_original"] = modulos.triagem(entrada.descricao)
        dados["preparacao"] = preparar(entrada.descricao, entrada.contexto, entrada.local)
        return repo.criar(dados)

    def ler_pedido(dados):
        try:
            return Pedido.model_validate_json(dados)
        except ValueError as erro:
            raise ValueError('Confira descrição, bairro, contexto e coordenadas confirmadas. Use somente os campos do formulário.') from erro

    @app.post('/api/atendimentos/com-anexo', status_code=201)
    async def criar_com_anexo(dados: str = Form(max_length=10000), arquivo: UploadFile | None = File(default=None)):
        entrada = ler_pedido(dados)
        foto = None
        if arquivo:
            foto = await run_in_threadpool(imagens.guardar, await arquivo.read(8 * 1024 * 1024 + 1), pasta / 'fotos')
        payload = entrada.model_dump(mode='json', exclude={'confirmado'})
        payload.update(foto=foto, triagem_original=modulos.triagem(entrada.descricao),
                       preparacao=preparar(entrada.descricao, entrada.contexto, entrada.local))
        return repo.criar(payload)

    @app.get('/api/atendimentos/{identificador}/foto')
    def foto_do_pedido(identificador: str):
        foto = obter(identificador).get('foto')
        sha = foto.get('sha256', '') if foto else ''
        if not re.fullmatch('[a-f0-9]{64}', sha):
            raise HTTPException(404, 'Este pedido não possui foto.')
        caminho = pasta / 'fotos' / (sha + '.jpg')
        if not caminho.is_file():
            raise HTTPException(404, 'Foto não disponível nesta instalação.')
        return FileResponse(caminho, media_type='image/jpeg')

    @app.get("/api/atendimentos")
    def listar():
        return repo.listar()

    @app.get("/api/atendimentos/{identificador}")
    def detalhe(identificador: str):
        return obter(identificador)

    @app.put("/api/atendimentos/{identificador}")
    def atualizar(identificador: str, entrada: Pedido):
        obter(identificador)
        if entrada.origem_id is not None:
            raise ValueError("A origem do atendimento não pode ser alterada.")
        dados = entrada.model_dump(mode='json', exclude={"confirmado", "origem_id", "envio_id"}, exclude_unset=True)
        dados.update(local=entrada.local, contexto=entrada.contexto)
        dados.update(triagem_original=modulos.triagem(entrada.descricao),
                     preparacao=preparar(entrada.descricao, entrada.contexto, entrada.local))
        return repo.atualizar(identificador, dados)

    @app.put('/api/atendimentos/{identificador}/com-anexo')
    async def atualizar_com_anexo(identificador: str, dados: str = Form(max_length=10000),
                                 arquivo: UploadFile | None = File(default=None), remover_foto: bool = Form(default=False)):
        obter(identificador)
        entrada = ler_pedido(dados)
        if arquivo and remover_foto:
            raise ValueError('Escolha substituir ou remover a foto.')
        foto = None
        if arquivo:
            foto = await run_in_threadpool(imagens.guardar, await arquivo.read(8 * 1024 * 1024 + 1), pasta / 'fotos')
        payload = entrada.model_dump(mode='json', exclude={'confirmado', 'origem_id', 'envio_id'}, exclude_unset=True)
        payload.update(local=entrada.local, contexto=entrada.contexto,
                       triagem_original=modulos.triagem(entrada.descricao),
                       preparacao=preparar(entrada.descricao, entrada.contexto, entrada.local))
        if entrada.origem_id is not None:
            raise ValueError('A origem do atendimento não pode ser alterada.')
        if arquivo or remover_foto:
            payload['foto'] = foto
        return repo.atualizar(identificador, payload)

    @app.post("/api/atendimentos/{identificador}/revisao")
    def revisar(identificador: str, entrada: Revisao, x_manager_key: str | None = Header(default=None)):
        gestor(x_manager_key)
        obter(identificador)
        return repo.revisar(identificador, entrada.prioridade, entrada.justificativa, entrada.revisor)

    @app.post("/api/atendimentos/{identificador}/contestacao")
    def contestar(identificador: str, entrada: Contestacao):
        obter(identificador)
        return repo.contestar(identificador, entrada.motivo)

    @app.post("/api/atendimentos/{identificador}/protocolo")
    def protocolo(identificador: str, entrada: Protocolo):
        obter(identificador)
        return repo.informar_protocolo(identificador, entrada.protocolo)

    @app.post("/api/atendimentos/{identificador}/zelabairro")
    def encaminhar(identificador: str, x_manager_key: str | None = Header(default=None)):
        gestor(x_manager_key)
        caso = obter(identificador)
        if not caso.get("revisao") or caso["preparacao"]["faltantes"]:
            raise HTTPException(409, "Revise a decisão e complete as informações antes de confirmar no ZelaBairro.")
        categoria = caso["triagem_original"]["category"]
        mapa = {"Acessibilidade": "Calçada", "Buraco ou pavimento": "Buraco", "Iluminação pública": "Iluminação"}
        dados = {"cidadao_id": caso["id"] + ":" + caso["revisao"]["data"], "descricao": caso["descricao"],
                 "bairro": caso["bairro"], "categoria": mapa.get(categoria, "Outro"),
                 "prioridade": caso["revisao"]["prioridade"], "resumo": caso["descricao"][:300]}
        registro = modulos.registrar_no_frontend(dados, pasta / "zelabairro.sqlite")
        return repo.vincular_frontend(identificador, registro, caso["revisao"])

    @app.get("/api/indicadores")
    def indicadores():
        return repo.indicadores()

    @app.get("/api/ativos")
    def ativos():
        return modulos.ativos()

    @app.get("/api/materiais/{identificador}")
    def material(identificador: str):
        item = modulos.materiais().get(identificador)
        if not item:
            raise HTTPException(404, "Material não encontrado.")
        caminho = (modulos.MATERIAIS / item["arquivo"]).resolve()
        if not caminho.is_relative_to(modulos.MATERIAIS.resolve()) or not caminho.is_file():
            raise HTTPException(404, "Material não disponível.")
        return FileResponse(caminho, filename=caminho.name)

    @app.get("/api/fontes")
    def fontes(q: str = ""):
        if len(q) > 500:
            raise ValueError("Use uma consulta de até 500 caracteres.")
        return modulos.buscar_fontes(q)

    @app.post("/api/atendimentos/{identificador}/evidencia-pln")
    def vincular_trecho(identificador: str, entrada: Trecho):
        obter(identificador)
        linhas = modulos.CORPUS.read_text(encoding="utf-8").splitlines()
        if entrada.linha_corpus > len(linhas):
            raise ValueError("O trecho não existe no corpus entregue.")
        trecho = json.loads(linhas[entrada.linha_corpus - 1])
        return repo.adicionar_evidencia(identificador, "pln", {**trecho, "linha_corpus": entrada.linha_corpus})

    @app.post("/api/lotes")
    async def lote(arquivo: UploadFile = File(...), x_manager_key: str | None = Header(default=None)):
        gestor(x_manager_key)
        conteudo = await arquivo.read(1024 * 1024 + 1)
        resultado = await run_in_threadpool(modulos.importar_lote, conteudo)
        entradas = []
        for registro in resultado["registros"]:
            try:
                entradas.append(Pedido(descricao=registro["description"], bairro=registro["neighborhood"],
                                       origem_id="rpa:" + registro["case_id"], confirmado=True))
            except ValueError as erro:
                raise ValueError("O lote contém um registro fora dos limites: descrição de 10 a 1500 caracteres, bairro de 2 a 100 e ID de até 60.") from erro
        ids = []
        for entrada in entradas:
            dados = entrada.model_dump(exclude={"confirmado"})
            dados.update(triagem_original=modulos.triagem(entrada.descricao),
                         preparacao=preparar(entrada.descricao, entrada.contexto, entrada.local))
            ids.append(repo.criar(dados)["id"])
        return {**resultado, "atendimentos": ids}

    @app.post("/api/assistente")
    def assistente(entrada: Pergunta):
        if entrada.atendimento_id:
            obter(entrada.atendimento_id)
        resultado = modulos.perguntar(entrada.pergunta, entrada.anterior)
        if resultado["status"] == "indisponivel":
            raise RuntimeError("O modelo local está indisponível. Confira o serviço de Generative AI.")
        if entrada.atendimento_id:
            repo.adicionar_evidencia(entrada.atendimento_id, "genai", resultado)
        return resultado

    @app.post("/api/visao")
    async def visao(arquivo: UploadFile = File(...), atendimento_id: str = Form(default="")):
        if atendimento_id:
            obter(atendimento_id)
        conteudo = await arquivo.read(8 * 1024 * 1024 + 1)
        resultado = await run_in_threadpool(modulos.analisar_imagem, conteudo)
        if atendimento_id:
            repo.adicionar_evidencia(atendimento_id, "visao", resultado)
        return resultado

    @app.get("/")
    def inicio():
        return FileResponse(RAIZ / "web/index.html")

    @app.get('/sw.js')
    def service_worker():
        return FileResponse(RAIZ / 'web/sw.js', media_type='application/javascript')

    web = RAIZ / "web"
    if web.is_dir():
        app.mount("/web", StaticFiles(directory=web), name="web")
    return app


app = criar_app()
