import csv
import io
import json
import math
import os
import re
import sqlite3
import subprocess
import sys
import tempfile
from contextlib import closing
from pathlib import Path
from threading import Lock
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import ProxyHandler, Request, build_opener

from PIL import Image, ImageOps, UnidentifiedImageError

from materiais.rpa.pipeline import classificar_solicitacao, executar_pipeline, normalizar

RAIZ = Path(__file__).resolve().parents[1]
MATERIAIS = RAIZ / "materiais"
CORPUS = MATERIAIS / "pln/corpus/corpus_texto.jsonl"
FRONTEND_LOCK = Lock()


def triagem(descricao: str) -> dict:
    return classificar_solicitacao(descricao)


def importar_lote(conteudo: bytes) -> dict:
    if not conteudo or len(conteudo) > 1024 * 1024:
        raise ValueError("Envie um CSV de até 1 MB com case_id, description e neighborhood.")
    with tempfile.TemporaryDirectory() as pasta:
        base = Path(pasta)
        entrada = base / "entrada.csv"
        entrada.write_bytes(conteudo)
        resumo = executar_pipeline(entrada, base / "saida", base / "rpa.sqlite")
        if resumo["status"] != "ok":
            raise ValueError(resumo["message"])
        with (base / "saida/solicitacoes_processadas.csv").open(encoding="utf-8", newline="") as f:
            registros = list(csv.DictReader(f))
        with (base / "saida/registros_rejeitados.csv").open(encoding="utf-8", newline="") as f:
            rejeitados = list(csv.DictReader(f))
    return {"resumo": resumo, "registros": registros, "rejeitados": rejeitados,
            "modo": "Execução do pipeline original de RPA"}


def buscar_fontes(pergunta: str) -> list[dict]:
    comuns = {"como", "para", "uma", "que", "com", "dos", "das", "por", "sobre", "qual", "quais"}
    termos = sorted(set(re.findall(r"\w{3,}", normalizar(pergunta))) - comuns)[:12]
    if not termos:
        return []
    registros = []
    try:
        for linha in CORPUS.read_text(encoding="utf-8").splitlines():
            dado = json.loads(linha)
            if not isinstance(dado, dict):
                raise ValueError("O corpus possui um registro fora do formato esperado.")
            url = urlsplit(dado.get("url", ""))
            paginas = dado.get("paginas")
            localizador_valido = (
                isinstance(paginas, list) and bool(paginas)
                and all(isinstance(p, int) and p > 0 for p in paginas)
            ) or (
                paginas is None and str(dado.get("fonte", "")).lower().endswith((".html", ".htm"))
                and bool(dado.get("secao"))
            )
            if (not isinstance(dado.get("text"), str) or not dado["text"].strip()
                    or not localizador_valido
                    or url.scheme != "https" or not url.hostname
                    or not (url.hostname == "gov.br" or url.hostname.endswith(".gov.br"))):
                raise ValueError("O corpus possui trecho sem conteúdo ou origem válida.")
            registros.append(dado)
    except (OSError, json.JSONDecodeError) as erro:
        raise ValueError("O corpus não pôde ser lido. Confira os materiais de PLN.") from erro
    with closing(sqlite3.connect(":memory:")) as con:
        con.execute("CREATE VIRTUAL TABLE trechos USING fts5(texto, tokenize='unicode61 remove_diacritics 2')")
        con.executemany("INSERT INTO trechos(rowid, texto) VALUES (?, ?)",
                        ((i + 1, r["text"]) for i, r in enumerate(registros)))
        consulta = " OR ".join('"' + t + '"' for t in termos)
        linhas = con.execute("SELECT rowid FROM trechos WHERE trechos MATCH ? ORDER BY bm25(trechos) LIMIT 5",
                             (consulta,)).fetchall()
    return [{**registros[i - 1], "linha_corpus": i, "modo": "Consulta textual ao corpus de PLN"} for (i,) in linhas]


def perguntar(texto: str, anterior: str | None = None) -> dict:
    base = os.getenv("CITIZENTECH_GENAI_URL", "http://127.0.0.1:8765").rstrip("/")
    url = urlsplit(base)
    if (url.scheme != "http" or url.hostname not in {"127.0.0.1", "localhost", "::1"}
            or url.username or url.password or url.path not in {"", "/"} or url.query or url.fragment):
        raise ValueError("O serviço de IA deve usar um endereço local permitido.")
    requisicao = Request(base + "/perguntar", data=json.dumps(
        {"pergunta": texto, "anterior": anterior}, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json"}, method="POST")
    try:
        with build_opener(ProxyHandler({})).open(requisicao, timeout=60) as resposta:
            conteudo = resposta.read(1024 * 1024 + 1)
        if len(conteudo) > 1024 * 1024:
            raise ValueError("Resposta muito extensa.")
        saida = json.loads(conteudo)
        estados = {"respondido", "esclarecer", "fora_escopo", "sem_evidencia", "bloqueado", "privacidade", "indisponivel"}
        if (not isinstance(saida, dict) or not isinstance(saida.get("resposta"), str)
                or not saida["resposta"].strip() or saida.get("status") not in estados):
            raise ValueError("Resposta fora do contrato.")
        fonte = saida.get("fonte")
        if saida["status"] == "respondido":
            destino = urlsplit(fonte.get("url", "")) if isinstance(fonte, dict) else urlsplit("")
            if (destino.scheme != "https" or not destino.hostname
                    or not (destino.hostname == "prefeitura.sp.gov.br" or destino.hostname.endswith(".prefeitura.sp.gov.br"))
                    or fonte.get("texto") != saida["resposta"]):
                raise ValueError("A orientação não corresponde à fonte permitida.")
        return {**saida, "modo": "Serviço atual de Generative AI", "historico": False}
    except (URLError, HTTPError, OSError, ValueError, KeyError, TypeError) as erro:
        raise RuntimeError("O assistente local não respondeu corretamente. Inicie o serviço de Generative AI e tente novamente.") from erro


def executar_worker(operacao: str, dados: dict, interpretador: str | None = None) -> dict:
    try:
        retorno = subprocess.run(
            [interpretador or sys.executable, "-X", "utf8", str(RAIZ / "central/worker.py"), operacao],
            input=json.dumps(dados, ensure_ascii=False), text=True, encoding="utf-8",
            capture_output=True, timeout=90, cwd=RAIZ,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        )
        if retorno.returncode:
            raise RuntimeError("O módulo não conseguiu executar. Confira o ambiente e os materiais necessários.")
        resultado = json.loads(retorno.stdout)
        if not isinstance(resultado, dict):
            raise ValueError("Resultado fora do contrato.")
        return resultado
    except (OSError, ValueError, subprocess.TimeoutExpired) as erro:
        raise RuntimeError("O módulo não está disponível neste ambiente. Confira a instalação e tente novamente.") from erro


def analisar_imagem(conteudo: bytes) -> dict:
    if not conteudo or len(conteudo) > 8 * 1024 * 1024:
        raise ValueError("Envie uma imagem JPEG ou PNG de até 8 MB.")
    try:
        with Image.open(io.BytesIO(conteudo)) as imagem:
            if imagem.format not in {"JPEG", "PNG"} or imagem.width * imagem.height > 4096 * 4096:
                raise ValueError("Use JPEG ou PNG de até 16,8 megapixels.")
            normalizada = ImageOps.exif_transpose(imagem).convert("RGB")
    except (OSError, UnidentifiedImageError, Image.DecompressionBombError) as erro:
        raise ValueError("A imagem está ilegível ou excede o limite de tamanho.") from erro
    ambiente = os.getenv("CITIZENTECH_VISION_PYTHON", str(RAIZ / ".venv/Scripts/python.exe") if os.name == "nt" else sys.executable)
    with tempfile.TemporaryDirectory() as pasta:
        caminho = Path(pasta) / "imagem.png"
        normalizada.save(caminho)
        resultado = executar_worker("visao", {"imagem": str(caminho)}, ambiente)
    numeros = [resultado.get(k) for k in ("confianca", "escore", "limiar")]
    if (not all(type(n) in (float, int) and math.isfinite(n) and 0 <= n <= 1 for n in numeros)
            or type(resultado.get("alerta")) is not bool
            or resultado.get("classe") != ("Possível fissura" if resultado.get("alerta") else "Sem fissura sinalizada")
            or resultado.get("modelo") != "ResNet18" or resultado.get("resolucao") != 160
            or resultado["alerta"] != (resultado["escore"] >= resultado["limiar"])):
        raise RuntimeError("O modelo de Visão retornou uma saída fora do contrato. Nenhuma inferência foi registrada.")
    return {**resultado, "modo": "Inferência atual com checkpoint entregue",
            "limite": "Sinalização de possível fissura. Não atesta gravidade, acessibilidade ou segurança estrutural."}


def registrar_no_frontend(dados: dict, caminho_banco: Path) -> dict:
    with FRONTEND_LOCK:
        return executar_worker("frontend", {"dados": dados, "banco": str(caminho_banco.resolve())})


def materiais() -> dict:
    return json.loads((MATERIAIS / "manifesto.json").read_text(encoding="utf-8"))["itens"]


def ativos() -> list[dict]:
    resultado_gen = json.loads((MATERIAIS / "genai/resultados.json").read_text(encoding="utf-8"))
    visual = json.loads((MATERIAIS / "visao/artifacts/metricas.json").read_text(encoding="utf-8"))
    return [
        {"id": "rpa", "nome": "RPA", "modo": "Código reutilizado", "resumo": "Triagem e processamento de lotes do notebook original.",
         "limite": "Regras limitadas ao vocabulário. A confiança é heurística.", "materiais": ["rpa_notebook", "rpa_codigo"]},
        {"id": "cluster", "nome": "Cluster Computing", "modo": "Simulação histórica", "resumo": "Dois modelos iSPD, com 2 e 4 workers.",
         "limite": "O resultado simulado não mede o aplicativo completo.", "materiais": ["cluster_relatorio", "cluster_2", "cluster_4"],
         "metricas": [{"nome": "Tempo simulado com 2 workers", "valor": "1,20230 s"}, {"nome": "Tempo simulado com 4 workers", "valor": "0,604501 s"}]},
        {"id": "quantica", "nome": "Computação Quântica", "modo": "Estudo conceitual", "resumo": "Planejamento da revisão humana, alternativas clássicas e condições para pesquisa quântica.",
         "limite": "Nenhum algoritmo ou ganho quântico foi demonstrado.", "materiais": ["quantica_relatorio"]},
        {"id": "frontend", "nome": "Frontend", "modo": "Persistência reutilizada", "resumo": "A rotina do ZelaBairro registra os relatos confirmados em banco próprio da central.",
         "limite": "Protocolo local de uma POC. Não abre chamado municipal.", "materiais": ["frontend_readme", "frontend_testes", "frontend_video"]},
        {"id": "genai", "nome": "Generative AI", "modo": "Serviço local", "resumo": "Busca híbrida e seleção de evidências com Qwen3. O botão de consulta verifica a execução atual.",
         "limite": "As métricas abaixo são avaliações históricas, incluindo casos reaplicados.", "materiais": ["genai_relatorio", "genai_resultados", "genai_corpus"],
         "metricas": [{"nome": p["rotulo"], "valor": p["valor"]} for p in resultado_gen["placar"]]},
        {"id": "iot", "nome": "IoT e OuviAí", "modo": "Execução externa no celular", "resumo": "Reconhecimento de sons e resposta visual no navegador do smartphone.",
         "limite": "A central reúne evidências e não recebe previsões automaticamente.", "materiais": ["iot_relatorio", "iot_videos", "iot_enunciado"],
         "videos": [{"nome": "Abertura do modelo", "url": "https://www.youtube.com/watch?v=sc7K3uruowY"}, {"nome": "Porta", "url": "https://www.youtube.com/watch?v=DbAzry9Ixf0"}, {"nome": "Ambiente", "url": "https://www.youtube.com/watch?v=UEolGS6UU3s"}, {"nome": "Campainha", "url": "https://www.youtube.com/watch?v=LqlBq3hvnYA"}],
         "metricas": [{"nome": "Teste por janela", "valor": "78/100"}, {"nome": "Teste ao vivo documentado", "valor": "14/15"}, {"nome": "Reconhecimento imediato", "valor": "12/15"}]},
        {"id": "pln", "nome": "Processamento de Linguagem Natural", "modo": "Consulta ao corpus", "resumo": "Trechos sobre desastres com fonte, página, data e seção.",
         "limite": "A revisão humana do corpus continua pendente. Não fornece alertas locais em tempo real.", "materiais": ["pln_relatorio", "pln_corpus_texto", "pln_corpus_qa", "pln_corpus_chat", "pln_corpus_teste", "pln_qualidade", "pln_revisao"]},
        {"id": "visao", "nome": "Visão Computacional", "modo": "Inferência local", "resumo": "ResNet18 com checkpoint de 160 × 160, aplicado à imagem enviada.",
         "limite": "Métricas históricas no mesmo acervo; não constituem laudo estrutural.", "materiais": ["visao_relatorio", "visao_codigo", "visao_metricas", "visao_treino", "visao_manifesto", "visao_video"],
         "metricas": [{"nome": "F1 histórico no teste", "valor": round(visual["teste"]["f1"], 4)}, {"nome": "Recortes de teste", "valor": 352}]},
        {"id": "governanca", "nome": "Governança e Business Analytics", "modo": "Registros desta central", "resumo": "Revisão, contestação, origem das evidências e indicadores do processo.",
         "limite": "Sem testes com pessoas ou validação em campo, por decisão do grupo.", "materiais": []},
    ]
