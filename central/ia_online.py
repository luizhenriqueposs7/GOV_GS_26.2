"""Seleção online no Groq Free com o pipeline original de recuperação e proteção."""
import builtins
import importlib.util
import json
import os
import sys
from contextlib import contextmanager
from functools import lru_cache
from pathlib import Path
from threading import RLock
from time import monotonic
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .pesos_online import garantir_peso, PASTA_ENCODER, PESOS_ENCODER, REPOSITORIO_ENCODER, REVISAO_ENCODER


RAIZ = Path(__file__).resolve().parents[1]
MODELO = "qwen/qwen3.8-27b"
ARTEFATOS = RAIZ / "modelos_online/genai"
_CARGA = RLock()
_BOT = None


def caminho_encoder() -> Path:
    snapshot = ARTEFATOS / ".runtime/embeddings" / PASTA_ENCODER / "snapshots" / REVISAO_ENCODER
    if all((snapshot / nome).is_file() for nome in PESOS_ENCODER):
        return snapshot
    if os.getenv("VERCEL") != "1":
        raise RuntimeError("O encoder original não foi preparado neste servidor.")
    deadline = monotonic() + 50
    for nome, (sha, tamanho) in PESOS_ENCODER.items():
        peso = garantir_peso(f"encoder/{REVISAO_ENCODER}/{nome}",
                              f"https://huggingface.co/{REPOSITORIO_ENCODER}/resolve/{REVISAO_ENCODER}/{nome}", sha, tamanho, deadline=deadline)
    return peso.parent


@contextmanager
def _carga():
    if not _CARGA.acquire(timeout=45):
        raise RuntimeError("O assistente ainda está carregando após 45 segundos. Tente novamente; nenhuma inferência foi registrada.")
    try:
        yield
    finally:
        _CARGA.release()


@lru_cache(maxsize=1)
def original():
    with _carga():
        nome = "_zelabairro_genai_original"
        if nome in sys.modules:
            return sys.modules[nome]
        pasta = RAIZ / "materiais/genai"
        spec_triagem = importlib.util.spec_from_file_location("_zelabairro_triagem", pasta / "triagem.py")
        triagem = importlib.util.module_from_spec(spec_triagem)
        spec_triagem.loader.exec_module(triagem)
        spec = importlib.util.spec_from_file_location(nome, pasta / "assistente.py")
        modulo = importlib.util.module_from_spec(spec)

        def importar(nome_importado, globals=None, locals=None, fromlist=(), level=0):
            if nome_importado == "triagem" and not level:
                return triagem
            return builtins.__import__(nome_importado, globals, locals, fromlist, level)

        # O import absoluto entregue fica isolado; nenhum módulo global triagem é substituído.
        modulo.__builtins__ = {**vars(builtins), "__import__": importar}
        sys.modules[nome] = modulo
        try:
            spec.loader.exec_module(modulo)
        except Exception:
            sys.modules.pop(nome, None)
            raise
        # Nesta cópia isolada, PASTA só muda o cache do encoder; defaults do corpus já foram definidos.
        modulo.PASTA = ARTEFATOS
        classe_embedding = modulo.TextEmbedding

        def embedding_local(*args, **parametros):
            snapshot = caminho_encoder()
            parametros.update(cache_dir=str(snapshot), local_files_only=True, specific_model_path=str(snapshot), providers=["CPUExecutionProvider"])
            try:
                return classe_embedding(*args, **parametros)
            except (OSError, ValueError) as erro:
                raise RuntimeError("O encoder original preparado não pôde ser carregado offline.") from erro

        modulo.TextEmbedding = embedding_local
        return modulo


def bot():
    global _BOT
    with _carga():
        if _BOT is not None:
            return _BOT
        try:
            modulo = original()
            _BOT = modulo.Assistente(modulo.carregar_corpus(), selecionar=selecionar)
            return _BOT
        except (OSError, ValueError, ImportError) as erro:
            raise RuntimeError("O encoder original não está disponível neste servidor.") from erro


def selecionar(pergunta, trechos):
    chave = os.getenv("GROQ_API_KEY", "").strip()
    if not chave:
        raise RuntimeError("Configure GROQ_API_KEY no servidor para consultar o assistente online.")
    opcoes = [t.id for t in trechos] + ["SEM_EVIDENCIA", "FORA_ESCOPO", "ESCLARECER"]
    contexto = "\n\n".join(f"[{t.id}] {t.secao}\n{t.texto}" for t in trechos)
    corpo = {
        "model": MODELO,
        "messages": [
            {"role": "system", "content": original().PROMPT},
            {"role": "user", "content": f"TRECHOS DE REFERÊNCIA\n{contexto}\n\nPERGUNTA DO CIDADÃO\n{pergunta}"},
        ],
        "temperature": 0, "seed": 42, "max_tokens": 48, "reasoning_effort": "none",
        "response_format": {"type": "json_schema", "json_schema": {
            "name": "evidencia", "strict": True, "schema": {
                "type": "object", "properties": {"id": {"type": "string", "enum": opcoes}},
                "required": ["id"], "additionalProperties": False,
            },
        }},
    }
    requisicao = Request("https://api.groq.com/openai/v1/chat/completions",
                         data=json.dumps(corpo, ensure_ascii=False).encode("utf-8"),
                         headers={"Content-Type": "application/json", "Accept": "application/json",
                                  "User-Agent": "ZelaBairro/0.3", "Authorization": f"Bearer {chave}"}, method="POST")
    try:
        with urlopen(requisicao, timeout=45) as resposta:
            conteudo = resposta.read(65537)
        if len(conteudo) > 65536:
            raise ValueError("Resposta excessiva.")
        dados = json.loads(conteudo)
        escolha = dados["choices"][0]
        selecao = json.loads(escolha["message"]["content"])
        if (dados.get("model") != MODELO or escolha.get("finish_reason") != "stop"
                or not isinstance(selecao, dict) or set(selecao) != {"id"}
                or not isinstance(selecao["id"], str) or selecao["id"] not in opcoes):
            raise ValueError("Saída fora do contrato.")
        return selecao["id"]
    except HTTPError as erro:
        if erro.code == 429:
            raise RuntimeError("A cota gratuita do assistente foi atingida. Aguarde e tente novamente.") from erro
        if erro.code in {401, 403}:
            raise RuntimeError(f"O Groq recusou a credencial ou o acesso ao modelo (HTTP {erro.code}). Confira GROQ_API_KEY e as permissões do modelo no provedor.") from erro
        raise RuntimeError("O serviço de IA online está indisponível. Nenhuma inferência foi registrada.") from erro
    except (URLError, OSError, ValueError, KeyError, IndexError, TypeError) as erro:
        raise RuntimeError("O serviço de IA online não retornou uma seleção válida. Nenhuma inferência foi registrada.") from erro


def perguntar(texto: str, anterior: str | None = None) -> dict:
    if not isinstance(texto, str) or not 1 <= len(texto.strip()) <= 500:
        raise ValueError("Escreva uma pergunta de 1 a 500 caracteres.")
    if not os.getenv("GROQ_API_KEY", "").strip():
        raise RuntimeError("Configure GROQ_API_KEY no servidor para consultar o assistente online.")
    assistente = bot()
    if anterior is not None and (not isinstance(anterior, str) or
                                (anterior not in assistente.docs and anterior not in assistente.por_id)):
        raise ValueError("Assunto anterior inválido. Inicie uma nova conversa.")
    resultado = assistente.responder(texto.strip(), anterior)
    if resultado["status"] == "indisponivel":
        raise RuntimeError("O assistente online está indisponível. Nenhuma inferência foi registrada.")
    return {**resultado, "modelo": MODELO, "modo": "Generative AI online · Groq Free", "historico": False}
