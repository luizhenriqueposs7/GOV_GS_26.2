"""Exporta e confere a apresentação técnica com a narração original integral."""
import argparse
import hashlib
import io
import json
import math
import subprocess
from pathlib import Path

import cv2
import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw, ImageFont

PASTA = Path(__file__).resolve().parent
RAIZ = PASTA.parents[1]
CAPTURA = PASTA / "captura_tecnica.webm"
AUDIO = PASTA.parent / "narracao_original.ogg"
DESTINO = RAIZ / "Apresentacao_Tecnica_CitizenTech.mp4"
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()


def audio(caminho):
    p = subprocess.run(
        [FFMPEG, "-v", "error", "-i", str(caminho), "-vn", "-ac", "1",
         "-ar", "16000", "-f", "f32le", "pipe:1"],
        check=True, stdout=subprocess.PIPE,
    )
    return np.frombuffer(p.stdout, dtype="<f4")


def exportar():
    if DESTINO.exists():
        raise FileExistsError(DESTINO)
    plano = json.loads((PASTA / "gravacao.json").read_text(encoding="utf-8"))
    assert plano["erros"] == []
    assert {c["acao"] for c in plano["comandos"]} == {"dados", "teste", "ambiente", "sutis"}
    assert all(c["codigo"] == 0 for c in plano["comandos"])
    fim = math.ceil(plano["duracao_audio"] * plano["fps"])
    edicao = {
        "captura": CAPTURA.name, "audio": "../narracao_original.ogg",
        "destino": DESTINO.name, "quadro_inicial": 0,
        "quadro_final_exclusivo": fim, "fps": plano["fps"],
        "velocidade_audio": 1.0, "velocidade_captura": 1.0, "ganho_db": -2.5,
        "resolucao": plano["canvas"],
        "cor": "SDR; conversão da captura full-range para faixa limitada",
        "corte_final": "Apenas o excedente técnico após o fim da narração.",
    }
    (PASTA / "edicao.json").write_text(json.dumps(edicao, ensure_ascii=False, indent=2), encoding="utf-8")
    subprocess.run([
        FFMPEG, "-nostdin", "-n", "-v", "error", "-progress", str(PASTA / "progresso_exportacao.txt"),
        "-i", str(CAPTURA), "-i", str(AUDIO),
        "-map", "0:v:0", "-map", "1:a:0",
        "-vf", f"trim=end_frame={fim},setpts=PTS-STARTPTS,scale=in_range=full:out_range=tv",
        "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-pix_fmt", "yuv420p",
        "-color_range", "tv", "-af", "volume=-2.5dB", "-c:a", "aac",
        "-b:a", "128k", "-ar", "48000", "-movflags", "+faststart", str(DESTINO),
    ], check=True)
    print(DESTINO, flush=True)


def quadro(captura, segundo):
    captura.set(cv2.CAP_PROP_POS_MSEC, segundo * 1000)
    ok, frame = captura.read()
    assert ok, segundo
    return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)


def quadro_fonte(segundo):
    # O OpenCV trata esta captura full-range como limitada; aplicar a conversão também na referência.
    p = subprocess.run([
        FFMPEG, "-v", "error", "-ss", str(segundo), "-i", str(CAPTURA),
        "-frames:v", "1", "-vf", "scale=in_range=full:out_range=tv",
        "-f", "image2pipe", "-vcodec", "png", "pipe:1",
    ], check=True, stdout=subprocess.PIPE)
    return np.asarray(Image.open(io.BytesIO(p.stdout)).convert("RGB"))


def verificar():
    plano = json.loads((PASTA / "gravacao.json").read_text(encoding="utf-8"))
    assert plano["erros"] == []
    assert all(c["codigo"] == 0 for c in plano["comandos"])
    atualizacoes = next(e["quantidade"] for e in plano["eventos"] if e["nome"] == "atualizacoes_ao_vivo")
    assert atualizacoes >= 100
    original, final = audio(AUDIO), audio(DESTINO)
    assert abs(len(final) - len(original)) / 16000 < 0.2
    correlacoes = []
    for inicio in (0, 60, 120, 180, 240, 300, 360, 420, 449):
        a, b = inicio * 16000, min((inicio + 8) * 16000, len(original), len(final))
        r = float(np.corrcoef(original[a:b], final[a:b])[0, 1])
        assert r > 0.97, (inicio, r)
        correlacoes.append({"inicio_s": inicio, "correlacao": r})
    pico = float(np.abs(final).max())
    assert pico < 1.0
    cap = cv2.VideoCapture(str(DESTINO))
    fonte = cv2.VideoCapture(str(CAPTURA))
    assert cap.isOpened() and fonte.isOpened()
    tamanho = [int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))]
    assert tamanho == [1440, 900], tamanho
    fps = cap.get(cv2.CAP_PROP_FPS)
    duracao = cap.get(cv2.CAP_PROP_FRAME_COUNT) / fps
    assert abs(duracao - len(original) / 16000) < 0.15
    amostras = [5, 24, 39, 55, 69, 80, 88, 95, 102, 108, 116, 127, 141,
                156, 165, 179, 190, 198, 206, 212, 220, 228, 245, 257, 268,
                281, 297, 308, 319, 330, 340, 349, 353, 364, 372, 382, 393,
                401, 407, 418, 432, 443, 453]
    erros, miniaturas = [], []
    for segundo in amostras:
        atual = quadro(cap, segundo)
        esperado = quadro_fonte(segundo)
        erro = float(np.abs(atual.astype(float) - esperado.astype(float)).mean())
        assert erro < 12, (segundo, erro)
        erros.append({"segundo": segundo, "erro_medio_rgb": erro})
        im = Image.fromarray(atual)
        im.thumbnail((480, 300))
        miniaturas.append((segundo, im))
    colunas, altura = 3, 327
    contato = Image.new("RGB", (colunas * 480, math.ceil(len(miniaturas) / colunas) * altura), "white")
    desenho = ImageDraw.Draw(contato)
    fonte_texto = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 16)
    for i, (segundo, im) in enumerate(miniaturas):
        x, y = i % colunas * 480, i // colunas * altura
        contato.paste(im, (x, y))
        desenho.text((x + 10, y + 303), f"{segundo // 60:02}:{segundo % 60:02}", fill="black", font=fonte_texto)
    contato.save(PASTA / "conferencia_visual.jpg", quality=93)
    for segundo in (108, 179, 349, 364, 393):
        Image.fromarray(quadro(cap, segundo)).save(PASTA / f"conferencia_{segundo}.png")
    cap.release()
    fonte.release()
    referencia = np.asarray(Image.open(PASTA / "metricas_recalculadas.png").convert("RGB"))
    cap = cv2.VideoCapture(str(DESTINO))
    erro_cor = float(np.abs(quadro(cap, 179).astype(float) - referencia.astype(float)).mean())
    cap.release()
    assert erro_cor < 8, erro_cor
    subprocess.run([FFMPEG, "-v", "error", "-i", str(DESTINO), "-f", "null", "-"], check=True)
    resultado = {
        "video": DESTINO.name, "duracao_video_s": duracao,
        "duracao_audio_s": len(final) / 16000, "resolucao": tamanho,
        "fps": fps, "atualizacoes_ao_vivo": atualizacoes,
        "comandos": [{"acao": c["acao"], "codigo": c["codigo"]} for c in plano["comandos"]],
        "sha256_narracao_original": hashlib.sha256(AUDIO.read_bytes()).hexdigest(),
        "comparacao_audio": correlacoes, "pico_audio_dbfs": float(20 * np.log10(pico)),
        "comparacao_captura": erros, "decodificacao_integral": "OK",
        "erro_medio_rgb_vs_captura_png": erro_cor,
        "limite_revisao": "Conferência visual, transcrição e medições; sem escuta perceptiva.",
    }
    (PASTA / "verificacao.json").write_text(json.dumps(resultado, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Conferido: {duracao:.2f} s; {tamanho}; {fps:.4f} FPS.", flush=True)
    print(f"{atualizacoes} atualizações ao vivo; 4 comandos reais concluídos; áudio original preservado.", flush=True)


if __name__ == "__main__":
    cli = argparse.ArgumentParser()
    cli.add_argument("--verificar", action="store_true")
    args = cli.parse_args()
    verificar() if args.verificar else exportar()
