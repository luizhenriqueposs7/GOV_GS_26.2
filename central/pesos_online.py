"""Cache descartável dos pesos publicados, com tamanho e SHA-256 fixados."""
import hashlib
from http.client import HTTPException
import os
import re
import tempfile
from pathlib import Path
from threading import RLock
from time import monotonic, sleep
from urllib.parse import urlsplit
from urllib.request import urlopen


CACHE = Path(tempfile.gettempdir()) / "zelabairro-modelos"
_LOCK = RLock()
REVISAO_ENCODER = "faf4aa4225822f3bc6376869cb1164e8e3feedd0"
REPOSITORIO_ENCODER = "Qdrant/paraphrase-multilingual-MiniLM-L12-v2-onnx-Q"
PASTA_ENCODER = "models--Qdrant--paraphrase-multilingual-MiniLM-L12-v2-onnx-Q"
PESOS_ENCODER = {
    "config.json": ("c8ec081fdad2df991bf5abbf18418fec7a5cdaa421f60ffb060a30040b8c376f", 673),
    "model_optimized.onnx": ("634d0f66c29dc934c8fa72b8a4fe91dd4d420a22f1d82a241058d4316e659a99", 235052644),
    "special_tokens_map.json": ("8c785abebea9ae3257b61681b4e6fd8365ceafde980c21970d001e834cf10835", 964),
    "tokenizer_config.json": ("0666eebf692422757e1dddf3c9fb1ded73ba3dc726c5828671fc89e45bf3609f", 1416),
    "tokenizer.json": ("fa685fc160bbdbab64058d4fc91b60e62d207e8dc60b9af5c002c5ab946ded00", 17083009),
}


def _restante(deadline: float) -> float:
    restante = deadline - monotonic()
    if restante <= 0:
        raise TimeoutError("Prazo total de preparação excedido.")
    return restante


def _travar_arquivo(trava, deadline: float):
    if os.name != "nt":
        import fcntl
        while True:
            _restante(deadline)
            try:
                fcntl.flock(trava.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                return
            except BlockingIOError:
                sleep(min(0.05, _restante(deadline)))


def _hash_arquivo(caminho: Path, deadline: float) -> str:
    digest = hashlib.sha256()
    with caminho.open("rb") as arquivo:
        while bloco := arquivo.read(1024 * 1024):
            _restante(deadline)
            digest.update(bloco)
    _restante(deadline)
    return digest.hexdigest()


def garantir_peso(nome: str, url: str, sha256: str, tamanho: int, *, deadline: float | None = None) -> Path:
    """Usa um prazo monotônico compartilhável, incluindo locks e validação do cache."""
    deadline = monotonic() + 50 if deadline is None else deadline
    destino = CACHE / nome
    endereco = urlsplit(url)
    if (not nome or Path(nome).is_absolute() or ".." in Path(nome).parts
            or endereco.scheme != "https" or not endereco.hostname or endereco.username or endereco.password
            or not re.fullmatch(r"[0-9a-f]{64}", sha256) or type(tamanho) is not int or tamanho <= 0):
        raise ValueError("Identificação inválida do peso publicado.")
    adquirida = False
    try:
        adquirida = _LOCK.acquire(timeout=_restante(deadline))
        if not adquirida:
            raise TimeoutError("Prazo de espera pelo cache excedido.")
        _restante(deadline)
        if not destino.resolve().is_relative_to(CACHE.resolve()):
            raise ValueError("O peso deve permanecer dentro do cache temporário.")
        destino.parent.mkdir(parents=True, exist_ok=True)
        with destino.with_suffix(destino.suffix + ".lock").open("a+b") as trava:
            _travar_arquivo(trava, deadline)
            if destino.is_file() and destino.stat().st_size == tamanho and _hash_arquivo(destino, deadline) == sha256:
                return destino
            destino.unlink(missing_ok=True)
            temporario = destino.with_suffix(destino.suffix + ".partial")
            try:
                digest, recebidos = hashlib.sha256(), 0
                with urlopen(url, timeout=min(10, _restante(deadline))) as resposta, temporario.open("wb") as arquivo:
                    # read1 evita esperar preencher 1 MiB enquanto chegam pequenos fragmentos.
                    ler = getattr(resposta, "read1", resposta.read)
                    while True:
                        timeout = min(10, _restante(deadline))
                        socket = getattr(getattr(getattr(resposta, "fp", None), "raw", None), "_sock", None)
                        if socket is not None:
                            socket.settimeout(timeout)
                        bloco = ler(1024 * 1024)
                        _restante(deadline)
                        if not bloco:
                            break
                        recebidos += len(bloco)
                        if recebidos > tamanho:
                            raise ValueError("O peso excede o tamanho publicado.")
                        digest.update(bloco)
                        arquivo.write(bloco)
                if recebidos != tamanho or digest.hexdigest() != sha256:
                    raise ValueError("O peso diverge do tamanho ou SHA-256 publicado.")
                _restante(deadline)
                temporario.replace(destino)
            finally:
                temporario.unlink(missing_ok=True)
            return destino
    except TimeoutError as erro:
        raise RuntimeError("O prazo de preparação do modelo online foi excedido. Tente novamente; nenhuma inferência foi registrada.") from erro
    except (OSError, ValueError, HTTPException) as erro:
        raise RuntimeError("Não foi possível preparar o peso de inferência online. Tente novamente; nenhuma inferência foi registrada.") from erro
    finally:
        if adquirida:
            _LOCK.release()
