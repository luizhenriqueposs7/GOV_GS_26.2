import hmac
import hashlib
import json
import os
import secrets
import re
from pathlib import Path
from typing import Literal
from uuid import UUID
from time import perf_counter
from urllib.parse import quote

from fastapi import FastAPI, File, Form, Header, HTTPException, UploadFile, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse, Response, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field
from starlette.concurrency import run_in_threadpool

from . import modulos, imagens, passagem, relato_foto
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


class VinculoPassagem(Entrada):
    percurso_id: Literal['ponto-ubs-demo']
    trecho_id: Literal['acesso', 'calcada', 'rampa', 'entrada']
    condicao: Literal['bloqueado', 'dificultado', 'nao_verificado']


class Pedido(Entrada):
    descricao: str = Field(min_length=10, max_length=1500)
    bairro: str = Field(min_length=2, max_length=100)
    local: str = Field(default="", max_length=250)
    contexto: Contexto = "nao_informado"
    confirmado: Literal[True]
    origem_id: str | None = Field(default=None, max_length=64)
    localizacao: Localizacao | None = None
    envio_id: UUID | None = None
    passagem: VinculoPassagem | None = None


class Revisao(Entrada):
    prioridade: Literal["Baixa", "Média", "Alta"]
    justificativa: str = Field(min_length=10, max_length=500)
    revisor: str = Field(min_length=2, max_length=80)


class Contestacao(Entrada):
    motivo: str = Field(min_length=10, max_length=500)


class Protocolo(Entrada):
    protocolo: str = Field(min_length=1, max_length=80)
    demonstracao: bool = False


class Conferencia(Entrada):
    base: str = Field(min_length=1, max_length=40)
    revisor: str = Field(min_length=2, max_length=80)
    justificativa: str = Field(min_length=10, max_length=500)
    confirmado: Literal[True]


class Pergunta(Entrada):
    pergunta: str = Field(min_length=1, max_length=500)
    anterior: str | None = Field(default=None, max_length=40)
    atendimento_id: str | None = Field(default=None, max_length=40)


class Trecho(Entrada):
    linha_corpus: int = Field(ge=1, le=10000)


class SimulacaoPassagem(Entrada):
    reparos: list[str] = Field(max_length=4)


class PlanoPassagem(SimulacaoPassagem):
    base: str = Field(pattern='^[a-f0-9]{64}$')
    revisor: str = Field(min_length=2, max_length=80)
    justificativa: str = Field(min_length=10, max_length=500)


class Worker(BaseModel):
    model_config = ConfigDict(extra='forbid')
    csv: str = Field(min_length=1, max_length=1048576)
    worker: int = Field(ge=1, le=4, strict=True)
    lote_id: UUID


class AnaliseWorker(Entrada):
    category: Literal['Iluminação pública', 'Buraco ou pavimento', 'Resíduos e limpeza', 'Acessibilidade', 'Outros']
    priority: Literal['Baixa', 'Média', 'Alta']
    confidence: float = Field(ge=0, le=1, allow_inf_nan=False)
    review_required: bool = Field(strict=True)


class ItemPlanejado(Entrada):
    id: str = Field(min_length=1, max_length=40)
    minutos: int = Field(ge=1, le=240, strict=True)
    prioridade: Literal['Baixa', 'Média', 'Alta']
    obrigatorio: bool = Field(default=False, strict=True)


class SimulacaoRevisoes(Entrada):
    itens: list[ItemPlanejado] = Field(min_length=1, max_length=8)
    capacidade: int = Field(ge=1, le=480, strict=True)


class PlanoRevisoes(SimulacaoRevisoes):
    base: str = Field(pattern='^[a-f0-9]{64}$')
    metodo: Literal['fila', 'classico', 'qaoa']
    revisor: str = Field(min_length=2, max_length=80)
    justificativa: str = Field(min_length=10, max_length=500)
    confirmado: Literal[True]


def criar_app(pasta_dados: Path | None = None) -> FastAPI:
    pasta = pasta_dados or Path(os.getenv("GOV_DATA_DIR", str(RAIZ / "data")))
    nuvem = os.getenv('GOV_RUNTIME') == 'vercel' or os.getenv('VERCEL') == '1'
    fotos = None
    if nuvem:
        obrigatorias = ('GOV_DATABASE_URL', 'GOV_MANAGER_KEY', 'SUPABASE_URL', 'SUPABASE_SECRET_KEY')
        faltantes = [nome for nome in obrigatorias if not os.getenv(nome, '').strip()]
        if faltantes:
            raise RuntimeError('Configure as variáveis do servidor: ' + ', '.join(faltantes))
        if len(os.environ['GOV_MANAGER_KEY'].strip()) < 24:
            raise RuntimeError('Use uma chave de gestão de pelo menos 24 caracteres.')
        from .postgres import RepositorioPostgres
        from .storage import StorageFotos
        repo = RepositorioPostgres(os.environ['GOV_DATABASE_URL'])
        fotos = StorageFotos(os.environ['SUPABASE_URL'], os.environ['SUPABASE_SECRET_KEY'])
    else:
        pasta.mkdir(parents=True, exist_ok=True)
        repo = Repositorio(pasta / "central.sqlite")
    chave = os.getenv("GOV_MANAGER_KEY", "").strip()
    if not chave:
        arquivo_chave = pasta / "chave-gestao.txt"
        if not arquivo_chave.exists():
            arquivo_chave.write_text(secrets.token_urlsafe(32), encoding="utf-8")
        chave = arquivo_chave.read_text(encoding="utf-8").strip()

    app = FastAPI(title="ZelaBairro", version="0.6.4", docs_url="/contrato")
    app.state.repo = repo

    def guardar_foto(conteudo, previa=''):
        if previa:
            relato_foto.validar(previa, imagens.preparar_foto(conteudo)[1], chave)
        return fotos.guardar(conteudo) if fotos else imagens.guardar(conteudo, pasta / 'fotos')

    def gestor(valor):
        if not valor or not hmac.compare_digest(valor.encode(), chave.encode()):
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
        origem = request.headers.get('origin')
        if nuvem and request.method not in {'GET', 'HEAD', 'OPTIONS'} and (
                (origem and origem.rstrip('/') != str(request.base_url).rstrip('/'))
                or request.headers.get('sec-fetch-site') == 'cross-site'):
            resposta = JSONResponse(status_code=403, content={'erro': 'Envie o pedido pelo endereço desta central.'})
        elif tamanho and (not tamanho.isdigit() or int(tamanho) > (4 if nuvem else 9) * 1024 * 1024):
            resposta = JSONResponse(status_code=413, content={"erro": "O envio excede o limite de tamanho. Reduza a foto e tente novamente."})
        else:
            resposta = await call_next(request)
        resposta.headers["X-Content-Type-Options"] = "nosniff"
        resposta.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        resposta.headers["Cache-Control"] = 'public, max-age=86400' if request.url.path.startswith('/ouviai/') and resposta.status_code == 200 else 'no-store'
        resposta.headers["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'self' 'wasm-unsafe-eval'; worker-src 'self'; style-src 'self'; img-src 'self' data: blob: https://tile.openstreetmap.org; "
            "connect-src 'self' https://api.bigdatacloud.net; media-src 'self' blob:; object-src 'none'; base-uri 'none'; frame-ancestors 'none'; form-action 'self'"
        )
        return resposta

    @app.get("/api/status")
    def status():
        return {"servico": "ZelaBairro", "status": "ok", "modo": "Demonstração online" if nuvem else "Demonstração local",
                'modelo_genai': 'Qwen3.8-27B via Groq' if nuvem else 'Qwen3-4B-Instruct-2507 local',
                'genai_configurada': bool(os.getenv('GROQ_API_KEY')) if nuvem else True,
                "validacao_em_campo": False, "abertura_automatica_sp156": False}

    @app.get('/api/passagem')
    def percurso():
        resultado = passagem.avaliar(repo.listar(), [])
        resultado['planos'] = [{**p, 'desatualizado': p['base'] != resultado['base']}
                               for p in repo.planos_passagem()]
        return resultado

    @app.post('/api/passagem/simular')
    def simular_passagem(entrada: SimulacaoPassagem):
        return passagem.avaliar(repo.listar(), entrada.reparos)

    @app.get('/api/planejamento')
    def fila_planejamento():
        casos = repo.listar()
        planos = {}
        for caso in casos:
            for e in caso.get('evidencias', []):
                if e['modulo'] == 'planejamento_revisao':
                    plano = e['resultado']; planos[plano['id']] = plano
        campos = ('id', 'descricao', 'bairro', 'criado_em', 'triagem_original', 'exige_revisao')
        return {'pendentes': [{k: c.get(k) for k in campos} for c in casos if not c.get('revisao')],
                'planos': sorted(planos.values(), key=lambda p: p['data'], reverse=True)[:5]}

    @app.post('/api/planejamento/simular')
    async def simular_revisoes(entrada: SimulacaoRevisoes, x_manager_key: str | None = Header(default=None)):
        gestor(x_manager_key)
        from .quantica import simular
        casos = await run_in_threadpool(repo.listar)
        return await run_in_threadpool(simular, casos, [i.model_dump() for i in entrada.itens], entrada.capacidade)

    @app.post('/api/planejamento/planos', status_code=201)
    async def plano_revisoes(entrada: PlanoRevisoes, x_manager_key: str | None = Header(default=None)):
        gestor(x_manager_key)
        return await run_in_threadpool(repo.registrar_planejamento, [i.model_dump() for i in entrada.itens],
            entrada.capacidade, entrada.base, entrada.metodo, entrada.revisor, entrada.justificativa)

    @app.post('/api/cluster/worker')
    def worker_lote(entrada: Worker, x_manager_key: str | None = Header(default=None)):
        gestor(x_manager_key)
        from .cluster import processar_worker
        return processar_worker(entrada.csv.encode('utf-8'), entrada.worker, str(entrada.lote_id))

    @app.post('/api/cluster/lotes')
    async def cluster_lote(arquivo: UploadFile = File(...), workers: int = Form(ge=2, le=4),
                          x_manager_key: str | None = Header(default=None)):
        gestor(x_manager_key)
        inicio = perf_counter()
        from .cluster import executar, chamar_http
        conteudo = await arquivo.read(1024 * 1024 + 1)
        callback = (lambda dados, worker, lote: chamar_http(dados, worker, lote, chave)) if nuvem else None
        resultado = await run_in_threadpool(executar, conteudo, workers, callback)
        # shortcut: gravação domina o tempo; ampliar só após medir ou reduzir as consultas por lote.
        if resultado['resumo']['valid'] > 50:
            raise ValueError('A central grava até 50 registros aceitos por minilote. Divida arquivos maiores.')
        persistido = await run_in_threadpool(persistir_lote, resultado, True)
        return {**persistido, 'tempo_total_ms': (perf_counter() - inicio) * 1000}

    @app.post('/api/passagem/planos', status_code=201)
    def plano_passagem(entrada: PlanoPassagem, x_manager_key: str | None = Header(default=None)):
        gestor(x_manager_key)
        return repo.planejar_passagem(entrada.base, entrada.reparos, entrada.revisor, entrada.justificativa)

    @app.post('/api/passagem/demonstracao')
    def preparar_percurso(x_manager_key: str | None = Header(default=None)):
        gestor(x_manager_key)
        exemplos = [
            ('calcada', 'Cenário fictício: calçada quebrada impede a passagem com cadeira de rodas na praça.',
             'area_publica', 'Praça ilustrativa · trecho 02', -23.54415, -46.64360),
            ('rampa', 'Cenário fictício: objeto obstrui a rampa da travessia e interrompe a passagem pela calçada.',
             'obstaculo', 'Travessia ilustrativa · trecho 03', -23.54430, -46.64340),
        ]
        ids = []
        for trecho, descricao, contexto, local, lat, lon in exemplos:
            dados = {'descricao': descricao, 'bairro': 'Bairro de demonstração', 'local': local,
                     'contexto': contexto, 'origem_id': 'passagem:demo:' + trecho,
                     'triagem_original': modulos.triagem(descricao), 'preparacao': preparar(descricao, contexto, local),
                     'localizacao': {'latitude': lat, 'longitude': lon, 'origem': 'manual',
                                     'precisao_m': None, 'confirmado': True},
                     'passagem': {'percurso_id': passagem.PERCURSO['id'], 'trecho_id': trecho, 'condicao': 'bloqueado'}}
            ids.append(repo.criar(dados, somente_se_novo=True)['id'])
        return {'atendimentos': ids, 'modo': 'Pedidos fictícios; sem vistoria ou reparo executado.'}

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

    @app.post('/api/relato-foto')
    async def gerar_relato_foto(arquivo: UploadFile = File(...)):
        return await run_in_threadpool(relato_foto.gerar, await arquivo.read(8 * 1024 * 1024 + 1), chave)

    @app.post('/api/atendimentos/com-anexo', status_code=201)
    async def criar_com_anexo(dados: str = Form(max_length=10000), arquivo: UploadFile | None = File(default=None),
                             previa: str = Form(default='', max_length=16000)):
        entrada = ler_pedido(dados)
        foto = None
        if arquivo:
            foto = await run_in_threadpool(guardar_foto, await arquivo.read(8 * 1024 * 1024 + 1), previa)
        payload = entrada.model_dump(mode='json', exclude={'confirmado'})
        payload.update(foto=foto, triagem_original=modulos.triagem(entrada.descricao),
                       preparacao=preparar(entrada.descricao, entrada.contexto, entrada.local))
        if previa:
            payload['sugestao_foto'] = relato_foto.validar(previa, foto, chave)
        return await run_in_threadpool(repo.criar, payload)

    @app.get('/api/atendimentos/{identificador}/foto')
    @app.get('/api/atendimentos/{identificador}/foto-correcao')
    def foto_do_pedido(identificador: str, request: Request):
        caso = obter(identificador)
        foto = (caso.get('atendimento', {}).get('retorno', {}).get('foto')
                if request.url.path.endswith('/foto-correcao') else caso.get('foto'))
        sha = foto.get('sha256', '') if foto else ''
        if not re.fullmatch('[a-f0-9]{64}', sha):
            raise HTTPException(404, 'Este pedido não possui foto.')
        if fotos:
            return Response(fotos.ler(sha), media_type='image/jpeg')
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
                                 arquivo: UploadFile | None = File(default=None), remover_foto: bool = Form(default=False),
                                 previa: str = Form(default='', max_length=16000)):
        anterior = await run_in_threadpool(obter, identificador)
        entrada = ler_pedido(dados)
        if arquivo and remover_foto:
            raise ValueError('Escolha substituir ou remover a foto.')
        foto = None
        if arquivo:
            foto = await run_in_threadpool(guardar_foto, await arquivo.read(8 * 1024 * 1024 + 1), previa)
        payload = entrada.model_dump(mode='json', exclude={'confirmado', 'origem_id', 'envio_id'}, exclude_unset=True)
        payload.update(local=entrada.local, contexto=entrada.contexto,
                       triagem_original=modulos.triagem(entrada.descricao),
                       preparacao=preparar(entrada.descricao, entrada.contexto, entrada.local))
        if entrada.origem_id is not None:
            raise ValueError('A origem do atendimento não pode ser alterada.')
        if arquivo or remover_foto:
            payload['foto'] = foto
            payload['sugestao_foto'] = None
        if previa:
            payload['sugestao_foto'] = relato_foto.validar(previa, foto if arquivo or remover_foto else anterior.get('foto'), chave)
        return await run_in_threadpool(repo.atualizar, identificador, payload)

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
        return repo.informar_protocolo(identificador, entrada.protocolo, entrada.demonstracao)

    @app.get('/api/atendimentos/{identificador}/ficha')
    def ficha(identificador: str):
        from .catalogo import ficha_encaminhamento
        return Response(ficha_encaminhamento(obter(identificador)), media_type='text/plain',
                        headers={'Content-Disposition': f'attachment; filename="zelabairro-{identificador}.txt"'})

    @app.post('/api/atendimentos/{identificador}/retorno')
    async def retorno(identificador: str, etapa: Literal['em_atendimento', 'sem_solucao', 'correcao_informada'] = Form(),
                      relato: str = Form(min_length=10, max_length=1000), arquivo: UploadFile | None = File(default=None)):
        caso = await run_in_threadpool(obter, identificador)
        if not caso.get('atendimento') or caso['atendimento']['etapa'] == 'correcao_verificada':
            raise ValueError('Anote o protocolo ou solicite nova análise de um acompanhamento encerrado.')
        foto = None
        if arquivo:
            conteudo = await arquivo.read(8 * 1024 * 1024 + 1)
            metadados = await run_in_threadpool(lambda: imagens.preparar_foto(conteudo)[1])
            inicial = (caso.get('foto') or {}).get('sha256')
            if etapa != 'correcao_informada' or inicial in {metadados['sha256'], hashlib.sha256(conteudo).hexdigest()}:
                raise ValueError('Use uma nova foto para informar a correção, diferente da foto inicial.')
            foto = await run_in_threadpool(guardar_foto, conteudo)
        return await run_in_threadpool(repo.registrar_retorno, identificador, etapa, relato, foto)

    @app.post('/api/atendimentos/{identificador}/verificar-correcao')
    def verificar_correcao(identificador: str, entrada: Conferencia, x_manager_key: str | None = Header(default=None)):
        gestor(x_manager_key)
        obter(identificador)
        return repo.verificar_correcao(identificador, entrada.revisor, entrada.justificativa, entrada.base)

    @app.post("/api/atendimentos/{identificador}/zelabairro")
    def encaminhar(identificador: str, x_manager_key: str | None = Header(default=None)):
        gestor(x_manager_key)
        if nuvem:
            try:
                return repo.confirmar_frontend(identificador)
            except KeyError:
                raise HTTPException(404, 'Atendimento não encontrado.') from None
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
        if nuvem:
            return RedirectResponse('https://github.com/luizhenriqueposs7/GOV_GS_26.2/blob/aacab6427679a87d9ac3971d8343ea95f3c6adea/materiais/'
                                    + quote(item['arquivo'], safe='/'), status_code=307)
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

    def persistir_lote(resultado, distribuido=False):
        entradas = []
        for registro in resultado["registros"]:
            try:
                entradas.append(Pedido(descricao=registro["description"], bairro=registro["neighborhood"],
                                       origem_id="rpa:" + registro["case_id"], confirmado=True))
            except ValueError as erro:
                raise ValueError("O lote contém um registro fora dos limites: descrição de 10 a 1500 caracteres, bairro de 2 a 100 e ID de até 60.") from erro
        dados_lote = []
        for entrada, registro in zip(entradas, resultado['registros']):
            dados = entrada.model_dump(exclude={"confirmado"})
            analise = (AnaliseWorker.model_validate(registro['triagem_original']).model_dump()
                       if distribuido else modulos.triagem(entrada.descricao))
            dados.update(triagem_original=analise,
                         preparacao=preparar(entrada.descricao, entrada.contexto, entrada.local))
            dados_lote.append(dados)
        evidencia = ({k: resultado[k] for k in ('lote_id', 'workers_solicitados', 'workers_executados', 'execucoes', 'tempo_ms', 'modo')}
                     if distribuido else None)
        inicio_persistencia = perf_counter()
        ids = repo.criar_em_lote(dados_lote, evidencia)
        return {**resultado, "atendimentos": ids, 'tempo_persistencia_ms': (perf_counter() - inicio_persistencia) * 1000}

    @app.post("/api/lotes")
    async def lote(arquivo: UploadFile = File(...), x_manager_key: str | None = Header(default=None)):
        gestor(x_manager_key)
        conteudo = await arquivo.read(1024 * 1024 + 1)
        resultado = await run_in_threadpool(modulos.importar_lote, conteudo)
        return await run_in_threadpool(persistir_lote, resultado)

    @app.post("/api/assistente")
    def assistente(entrada: Pergunta):
        if entrada.atendimento_id:
            obter(entrada.atendimento_id)
        resultado = modulos.perguntar(entrada.pergunta, entrada.anterior)
        if resultado["status"] == "indisponivel":
            raise RuntimeError("O assistente está indisponível. Confira a configuração do serviço de Generative AI.")
        if entrada.atendimento_id:
            repo.adicionar_evidencia(entrada.atendimento_id, "genai", resultado)
        return resultado

    @app.post("/api/visao")
    async def visao(arquivo: UploadFile = File(...), atendimento_id: str = Form(default="")):
        if atendimento_id:
            await run_in_threadpool(obter, atendimento_id)
        conteudo = await arquivo.read(8 * 1024 * 1024 + 1)
        resultado = await run_in_threadpool(modulos.analisar_imagem, conteudo)
        if atendimento_id:
            await run_in_threadpool(repo.adicionar_evidencia, atendimento_id, "visao", resultado)
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
    if not nuvem and (RAIZ / 'public/ouviai').is_dir():
        app.mount('/ouviai', StaticFiles(directory=RAIZ / 'public/ouviai'), name='audio-local')
    return app


app = criar_app()
