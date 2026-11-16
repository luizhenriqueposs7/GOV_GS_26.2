"""Inferência CPU do checkpoint ResNet18 entregue, exportado sem treino adicional."""
import hashlib
import json
import os
from functools import lru_cache
from pathlib import Path
from time import monotonic

import numpy as np
from PIL import Image

from .imagens import normalizar
from .pesos_online import garantir_peso


ARTEFATOS = Path(__file__).resolve().parents[1] / "modelos_online/visao"
CHECKPOINT_SHA256 = "67d0b015527c8f487aaa4f84354328cd4cf6f305cb0f038187f0261c18c316e8"
ONNX_SHA256 = "1e5b4acda6e11ff3d83f029c69dc2a60bf5bd6e870ea6010647520de327a2007"
ONNX_BYTES = 44700649
ONNX_URL = ("https://raw.githubusercontent.com/luizhenriqueposs7/GOV_GS_26.2/"
            "07064804a9eafe8d1618bd39a1f22c8c7b17864d/modelos_online/visao/crack_resnet18.onnx")


def caminho_pesos() -> Path:
    caminho = ARTEFATOS / "crack_resnet18.onnx"
    if caminho.is_file() or os.getenv("VERCEL") != "1":
        return caminho
    return garantir_peso(f"visao/{ONNX_SHA256}/crack_resnet18.onnx", ONNX_URL, ONNX_SHA256, ONNX_BYTES, deadline=monotonic() + 50)


@lru_cache(maxsize=1)
def modelo():
    try:
        import onnxruntime as ort
        dados = json.loads((ARTEFATOS / "manifesto.json").read_text(encoding="utf-8"))
        caminho = caminho_pesos()
        with caminho.open("rb") as arquivo:
            sha = hashlib.file_digest(arquivo, "sha256").hexdigest()
        if (dados.get("checkpoint_sha256") != CHECKPOINT_SHA256 or dados.get("onnx_sha256") != ONNX_SHA256 or sha != ONNX_SHA256
                or dados.get("modelo") != "ResNet18" or dados.get("image_size") != 160
                or type(dados.get("positive_idx")) is not int or dados["positive_idx"] not in {0, 1}
                or type(dados.get("threshold")) not in {float, int} or not 0 <= dados["threshold"] <= 1):
            raise ValueError("Artefato ou parâmetros divergentes.")
        opcoes = ort.SessionOptions()
        opcoes.intra_op_num_threads = 1
        opcoes.inter_op_num_threads = 1
        return ort.InferenceSession(str(caminho), sess_options=opcoes, providers=["CPUExecutionProvider"]), dados
    except Exception as erro:
        raise RuntimeError("O modelo de Visão online não está disponível. Confira os artefatos preparados no build.") from erro


def preprocessar(imagem: Image.Image) -> np.ndarray:
    imagem = imagem.convert("RGB").resize((160, 160), resample=Image.Resampling.BILINEAR)
    tensor = np.asarray(imagem, dtype=np.float32).transpose(2, 0, 1) / np.float32(255.0)
    media = np.array([0.485, 0.456, 0.406], dtype=np.float32)[:, None, None]
    desvio = np.array([0.229, 0.224, 0.225], dtype=np.float32)[:, None, None]
    return np.ascontiguousarray(((tensor - media) / desvio)[None, :])


def analisar_imagem(conteudo: bytes) -> dict:
    imagem = normalizar(conteudo)
    sessao, parametros = modelo()
    try:
        logits = np.asarray(sessao.run(None, {"imagem": preprocessar(imagem)})[0])
        if logits.shape != (1, 2) or not np.isfinite(logits).all():
            raise ValueError("Saída inválida.")
        exponenciais = np.exp(logits[0] - logits[0].max())
        escore = float((exponenciais / exponenciais.sum())[parametros["positive_idx"]])
        if not 0 <= escore <= 1:
            raise ValueError("Escore inválido.")
    except Exception as erro:
        raise RuntimeError("O modelo de Visão retornou uma saída inválida. Nenhuma inferência foi registrada.") from erro
    alerta = escore >= parametros["threshold"]
    return {
        "classe": "Possível fissura" if alerta else "Sem fissura sinalizada",
        "confianca": escore if alerta else 1.0 - escore,
        "escore": escore, "alerta": alerta, "limiar": parametros["threshold"],
        "resolucao": parametros["image_size"], "modelo": "ResNet18",
        "modo": "Inferência atual com checkpoint entregue · ONNX CPU", "historico": False,
        "limite": "Sinalização de possível fissura. Não atesta gravidade, acessibilidade ou segurança estrutural.",
    }
