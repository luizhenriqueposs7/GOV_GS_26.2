import argparse
import json
import subprocess
from pathlib import Path

import cv2
import numpy as np
from PIL import Image


PASTA = Path(__file__).resolve().parent
PROJETO = PASTA.parent


def audio(caminho, ffmpeg):
    processo = subprocess.run([
        ffmpeg, "-v", "error", "-i", str(caminho), "-vn",
        "-ac", "1", "-ar", "16000", "-f", "f32le", "pipe:1",
    ], check=True, stdout=subprocess.PIPE)
    return np.frombuffer(processo.stdout, dtype="<f4")


def verificar(ffmpeg):
    destino = PROJETO / "Apresentacao_Completa_CitizenTech.mp4"
    plano = json.loads((PASTA / "roteiro_visual.json").read_text(encoding="utf-8"))
    registro = json.loads((PASTA / "verificacao_gravacao.json").read_text(encoding="utf-8"))
    assert registro["erros"] == []
    atualizacoes = [r for r in registro["eventos"] if r["nome"] == "atualizacoes_ao_vivo"]
    assert len(atualizacoes) == 1 and atualizacoes[0]["quantidade"] >= 100

    cap = cv2.VideoCapture(str(destino))
    assert cap.isOpened()
    fps = cap.get(cv2.CAP_PROP_FPS)
    duracao = cap.get(cv2.CAP_PROP_FRAME_COUNT) / fps
    assert (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))) == (1280, 800)
    assert abs(duracao - plano["duracao_audio"]) < 2.0, duracao
    imagens = []
    for evento in plano["eventos"]:
        if evento["tela"] == "ao_vivo":
            continue
        segundo = evento["inicio"] + 1.5
        cap.set(cv2.CAP_PROP_POS_MSEC, segundo * 1000)
        ok, frame = cap.read()
        assert ok, segundo
        with Image.open(PASTA / "assets" / (evento["tela"] + ".png")) as im:
            referencia = np.asarray(im.convert("RGB"), dtype=np.float32)
        atual = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB).astype(np.float32)
        erro = float(np.mean(np.abs(atual - referencia)))
        assert erro < 8.0, (segundo, evento["tela"], erro)
        imagens.append({"tela": evento["tela"], "segundo": segundo, "erro_medio": erro})
    cap.release()

    original = audio(PASTA / "narracao_original.ogg", ffmpeg)
    final = audio(destino, ffmpeg)
    assert abs(len(final) - len(original)) / 16000 < 0.2
    n = min(len(original), len(final))
    correlacoes = []
    for inicio in (0, 120, 240, 360, 430):
        a, b = inicio * 16000, min((inicio + 20) * 16000, n)
        correlacao = float(np.corrcoef(original[a:b], final[a:b])[0, 1])
        assert correlacao > 0.97, (inicio, correlacao)
        correlacoes.append({"inicio": inicio, "correlacao": correlacao})
    pico = float(np.max(np.abs(final)))
    assert pico < 1.0
    subprocess.run([ffmpeg, "-v", "error", "-i", str(destino), "-f", "null", "-"], check=True)
    resultado = {
        "duracao_video_s": duracao, "duracao_audio_s": len(final) / 16000,
        "fps": fps, "atualizacoes_ao_vivo": atualizacoes[0]["quantidade"],
        "telas_conferidas": imagens, "comparacao_audio": correlacoes, "pico_audio": pico,
    }
    (PASTA / "verificacao_exportacao.json").write_text(
        json.dumps(resultado, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"Vídeo conferido: {duracao:.2f} s, {fps:g} FPS, {len(imagens)} telas.", flush=True)
    print(f"Áudio integral conferido em cinco trechos. Pico de {20 * np.log10(pico):.2f} dBFS.", flush=True)


if __name__ == "__main__":
    cli = argparse.ArgumentParser(description="Confere o áudio, as telas e a captura contínua exportada.")
    cli.add_argument("ffmpeg")
    verificar(cli.parse_args().ffmpeg)
