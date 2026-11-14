import argparse
import csv
import json
import math
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


PASTA = Path(__file__).resolve().parent
PROJETO = PASTA.parent
ASSETS = PASTA / "assets"
W, H = 1280, 800
FUNDO, ESCURO, TEXTO = "#eef0f1", "#161a1d", "#1b2125"
LARANJA, CINZA = "#f67024", "#505b62"
FONTES = Path("C:/Windows/Fonts")


def fonte(tamanho=24, tipo="normal"):
    nomes = {"normal": "segoeui.ttf", "bold": "segoeuib.ttf", "mono": "consola.ttf"}
    return ImageFont.truetype(str(FONTES / nomes[tipo]), tamanho)


def escrever(im, x, y, texto, tamanho=24, cor=TEXTO, tipo="normal", largura=None):
    d = ImageDraw.Draw(im)
    f = fonte(tamanho, tipo)
    linhas = []
    for paragrafo in str(texto).split("\n"):
        atual = ""
        for palavra in paragrafo.split():
            candidato = (atual + " " + palavra).strip()
            if largura and atual and d.textlength(candidato, font=f) > largura:
                linhas.append(atual)
                atual = palavra
            else:
                atual = candidato
        linhas.append(atual)
    for linha in linhas:
        d.text((x, y), linha, font=f, fill=cor)
        y += round(tamanho * 1.4)
    return y


def tela(titulo, subtitulo=""):
    im = Image.new("RGB", (W, H), FUNDO)
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, W, 65), fill=ESCURO)
    escrever(im, 44, 12, "CitizenTech", 29, "#fafafa", "bold")
    escrever(im, 825, 23, "FIAP · GLOBAL SOLUTION 2026.2", 17, "#c8ccce", "mono")
    d.rectangle((0, 65, W, 69), fill=LARANJA)
    escrever(im, 44, 94, titulo, 42, tipo="bold")
    if subtitulo:
        escrever(im, 46, 155, subtitulo, 22, CINZA, largura=1180)
    return im


def painel(im, caixa):
    ImageDraw.Draw(im).rounded_rectangle(caixa, radius=16, fill="#fafafa", outline="#dce0e2", width=2)


def foto(im, caminho, caixa):
    with Image.open(caminho) as original:
        imagem = ImageOps.contain(original.convert("RGB"), (caixa[2] - caixa[0], caixa[3] - caixa[1]))
    x = caixa[0] + (caixa[2] - caixa[0] - imagem.width) // 2
    y = caixa[1] + (caixa[3] - caixa[1] - imagem.height) // 2
    im.paste(imagem, (x, y))


def grade(im, linhas, x=46, y=225, largura=1186, altura=65, proporcoes=None, tamanho=24):
    d = ImageDraw.Draw(im)
    proporcoes = proporcoes or [1] * len(linhas[0])
    larguras = [largura * a / sum(proporcoes) for a in proporcoes]
    for i, linha in enumerate(linhas):
        d.rectangle((x, y, x + largura, y + altura), fill=ESCURO if i == 0 else ("#fafafa" if i % 2 else "#e3e7e9"))
        xx = x
        for texto, ww in zip(linha, larguras, strict=True):
            escrever(im, xx + 14, y + 15, texto, tamanho, "#fafafa" if i == 0 else TEXTO,
                     "bold" if i == 0 else "normal")
            xx += ww
        y += altura
    return y


def salvar(im, nome):
    im.save(ASSETS / (nome + ".png"))


def ler_csv(caminho):
    with caminho.open(encoding="utf-8", newline="") as arquivo:
        return list(csv.DictReader(arquivo))


def trecho(nome, inicio, fim, titulo, subtitulo):
    im = tela(titulo, subtitulo)
    linhas = (PROJETO / nome).read_text(encoding="utf-8").splitlines()
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((44, 213, 1236, 739), radius=14, fill="#1b2227")
    escrever(im, 68, 230, nome, 21, "#ff9254", "mono")
    y = 280
    for n in range(inicio, min(fim, len(linhas))):
        escrever(im, 65, y, str(n + 1).rjust(3), 20, "#86949d", "mono")
        d.text((130, y), linhas[n].expandtabs(4), font=fonte(21, "mono"), fill="#ecf0f2")
        y += 31
    assert y < 750, (nome, inicio, fim)
    return im


def gerar():
    ASSETS.mkdir(exist_ok=True)
    met = json.loads((PROJETO / "artifacts/metricas.json").read_text(encoding="utf-8"))
    manifest = ler_csv(PROJETO / "data/manifesto.csv")
    teste = [r for r in manifest if r["conjunto"] == "teste"]

    im = tela("Visão Computacional para Manutenção Urbana")
    escrever(im, 48, 230, "Triagem de fissuras em concreto", 44, tipo="bold")
    escrever(im, 48, 312, "Dados públicos · transferência de aprendizado · execução no CitizenTech", 26, CINZA, largura=1120)
    for i, pessoa in enumerate(("Luiz Henrique Poss · RM562177", "Luis Filipe Chaves Amorim · RM564706", "Felipe Stefani Honorato · RM563380")):
        escrever(im, 49, 574 + 44 * i, pessoa, 25)
    salvar(im, "abertura")

    im = tela("Triagem para manutenção urbana", "A imagem indica um local que merece inspeção.")
    for i, (arquivo, rotulo) in enumerate((("117_227_1362.jpg", "Com fissura"), ("223_2951_454.jpg", "Sem fissura"))):
        x = 80 + 610 * i
        foto(im, PROJETO / "data/recortes" / arquivo, (x, 225, x + 390, 615))
        escrever(im, x, 645, rotulo, 30, tipo="bold")
    salvar(im, "problema")

    im = tela("Como a análise aparece no protótipo")
    foto(im, PROJETO / "data/recortes/117_227_1362.jpg", (90, 238, 540, 688))
    painel(im, (820, 242, 1228, 630))
    escrever(im, 850, 282, "Imagem enviada", 27, tipo="bold")
    escrever(im, 850, 370, "Classe prevista", 27, tipo="bold")
    escrever(im, 850, 458, "Confiança do modelo", 27, tipo="bold")
    escrever(im, 850, 546, "Revisão humana", 27, "#9e410f", "bold")
    salvar(im, "fluxo")

    im = tela("Fotos e máscaras de origem", "Acervo de Çağlar Fırat Özgenel · Mendeley Data · CC BY 4.0")
    foto(im, PROJETO / "data/recortes/117_227_1362.jpg", (70, 230, 500, 660))
    escrever(im, 560, 260, "458 fotos originais", 43, tipo="bold")
    escrever(im, 560, 340, "Imagens RGB e máscaras de fissura", 27, largura=620)
    escrever(im, 560, 435, "Origem da base Concrete Crack Images for Classification", 30, largura=620)
    escrever(im, 560, 600, "doi.org/10.17632/jwsn7tfbrp.1", 20, CINZA, "mono")
    salvar(im, "origem")

    im = tela("Amostra utilizada", "Recortes de 227 × 227 pixels, com rótulos derivados das máscaras.")
    for i, (valor, texto) in enumerate((("144", "fotos originais"), ("2.304", "recortes"), ("50% / 50%", "com e sem fissura"))):
        x = 46 + i * 410
        painel(im, (x, 220, x + 377, 400))
        escrever(im, x + 20, 248, valor, 46, tipo="bold")
        escrever(im, x + 20, 326, texto, 24, CINZA)
    galeria = [r for r in teste if r["classe"] == "crack"][:3]
    galeria += [r for r in teste if r["classe"] == "no_crack"][:3]
    for i, linha in enumerate(galeria):
        x = 52 + i * 204
        foto(im, PROJETO / "data" / linha["arquivo"], (x, 450, x + 180, 630))
        escrever(im, x, 650, linha["origem"], 22, CINZA, "mono")
    salvar(im, "amostra")

    im = tela("Divisão por foto original", "A separação acontece antes de extrair os recortes.")
    grade(im, [["Conjunto", "Fotos", "Recortes", "Com / sem fissura"],
        ["Treino", "100", "1.600", "800 / 800"],
        ["Validação", "22", "352", "176 / 176"],
        ["Teste", "22", "352", "176 / 176"]], proporcoes=[2, 1, 1.4, 2.1])
    escrever(im, 52, 555, "Cada foto pertence a um único conjunto.", 32, tipo="bold")
    escrever(im, 52, 620, "Orientação EXIF corrigida para alinhar a foto à máscara.", 25, CINZA)
    salvar(im, "divisao")

    im = tela("Manifesto e verificação de duplicatas", "Cada recorte mantém o vínculo com sua foto de origem.")
    amostra = [[Path(r["arquivo"]).name, r["origem"], r["conjunto"], r["sha256_rgb"][:12] + "…"] for r in manifest[:5]]
    grade(im, [["Recorte", "Foto", "Conjunto", "Hash RGB abreviado"], *amostra],
          altura=55, proporcoes=[3.4, 1, 1.5, 2.2], tamanho=22)
    escrever(im, 50, 609, "Zero fotos compartilhadas entre os conjuntos", 30, tipo="bold")
    escrever(im, 50, 665, "Zero recortes com pixels idênticos entre os conjuntos", 28, "#9e410f", "bold")
    salvar(im, "manifesto")

    salvar(trecho("train.py", 155, 169, "Transferência de aprendizado", "ResNet18 com pesos ImageNet e saída para duas classes."), "modelo")
    salvar(trecho("train.py", 158, 173, "Treinamento", "4 épocas · lotes de 32 imagens · AdamW · ajuste do último bloco e da cabeça"), "treino")
    salvar(trecho("visao.py", 19, 32, "Pré-processamento", "Entrada de 160 × 160 · normalização ImageNet · inversão horizontal apenas no treino"), "preprocessamento")

    im = tela("Seleção na validação", "Época e limiar definidos antes da avaliação de teste.")
    hist = met["historico_validacao"]
    grade(im, [["Época", "F1 na validação", "Limiar"],
        *[[str(r["epoca"]), f'{r["f1"] * 100:.2f}%'.replace(".", ","), f'{r["limiar"]:.2f}'.replace(".", ",")] for r in hist]],
        proporcoes=[1, 2, 1], altura=58)
    escrever(im, 50, 575, "Modelo selecionado", 28, CINZA)
    escrever(im, 50, 625, "4ª época · limiar 0,49", 42, tipo="bold")
    salvar(im, "validacao")

    im = tela("Resultados no conjunto de teste", "352 recortes de 22 fotos reservadas.")
    for i, (numero, nome) in enumerate((("97,11%", "Precisão"), ("95,45%", "Recall"), ("96,28%", "F1"), ("96,31%", "Acurácia"))):
        x = 48 + (i % 2) * 610
        y = 235 + (i // 2) * 230
        painel(im, (x, y, x + 565, y + 190))
        escrever(im, x + 28, y + 26, nome, 28, CINZA)
        escrever(im, x + 28, y + 80, numero, 58, tipo="bold")
    salvar(im, "metricas")

    im = tela("Matriz de confusão", "Valores registrados nas previsões individuais do teste.")
    grade(im, [["Classe real", "Previsto sem fissura", "Previsto com fissura"],
        ["Sem fissura", "171", "5"], ["Com fissura", "8", "168"]],
        proporcoes=[1.8, 2, 2], altura=90, tamanho=28)
    escrever(im, 50, 570, "5 falsos positivos + 8 falsos negativos = 13 erros", 36, tipo="bold")
    salvar(im, "matriz")

    im = tela("Revisão dos 13 erros", "Observações feitas nos recortes e nas máscaras de origem.")
    grupos = [
        ("475_1135_0.jpg", "Fragmento na borda"),
        ("464_1816_1135.jpg", "Baixo contraste"),
        ("117_3405_227.jpg", "Marca clara"),
    ]
    for i, (arquivo, texto) in enumerate(grupos):
        x = 62 + i * 410
        foto(im, PROJETO / "data/recortes" / arquivo, (x, 224, x + 320, 544))
        escrever(im, x, 565, texto, 26, tipo="bold", largura=330)
    escrever(im, 52, 659, "Falsos negativos · 4 fragmentos nas bordas, 3 com baixo contraste e 1 causa incerta", 25, CINZA, largura=1150)
    salvar(im, "erros")

    im = tela("Possível omissão na máscara", "O rótulo publicado foi preservado no cálculo das métricas.")
    foto(im, PASTA / "contexto_mascara.png", (45, 240, 1235, 570))
    escrever(im, 55, 625, "Foto 291 · recorte 291_2043_1135", 27, tipo="bold")
    escrever(im, 55, 675, "A máscara sinaliza a fissura maior e deixa o traço menor sem marcação.", 24, CINZA)
    salvar(im, "mascara")

    im = tela("Comparação de resoluções", "Mesmos recortes e protocolo de treinamento.")
    for i, tamanho in enumerate((160, 224)):
        x = 130 + i * 610
        foto(im, PROJETO / "data/recortes/117_227_1362.jpg", (x, 230, x + 350, 580))
        escrever(im, x, 620, f"{tamanho} × {tamanho} pixels", 37, tipo="bold")
    salvar(im, "resolucoes")

    im = tela("Qualidade nas duas configurações")
    grade(im, [["Entrada", "Precisão", "Recall", "F1", "FP / FN"],
        ["160 × 160", "97,11%", "95,45%", "96,28%", "5 / 8"],
        ["224 × 224", "95,98%", "94,89%", "95,43%", "7 / 9"]],
        proporcoes=[1.5, 1.3, 1.3, 1.3, 1.2], altura=90, tamanho=28)
    escrever(im, 52, 575, "O teste utiliza 352 recortes em ambas as configurações.", 29, CINZA)
    salvar(im, "comparacao")

    im = tela("Como o desempenho foi medido")
    grade(im, [["Clipe", "Resolução original", "Quadros"],
        ["Sequência", "480 × 480 pixels", "48"],
        ["Movimento", "640 × 480 pixels", "72"]], proporcoes=[1.5, 2, 1], altura=70)
    escrever(im, 50, 490, "5 execuções por configuração, após aquecimento", 30, tipo="bold")
    escrever(im, 50, 570, "Intel Core i5-12450H · CPU · 4 threads", 31, tipo="bold")
    escrever(im, 50, 640, "Windows · Python 3.13 · PyTorch 2.8", 24, CINZA)
    salvar(im, "equipamento")

    im = tela("Taxa de processamento contínuo", "Médias de cinco execuções por clipe, após aquecimento.")
    grade(im, [["Entrada", "Sequência", "Movimento"],
        ["160 × 160", "26,29 FPS", "27,00 FPS"],
        ["224 × 224", "16,92 FPS", "18,24 FPS"]], proporcoes=[1.4, 1.7, 1.7], altura=95, tamanho=31)
    escrever(im, 55, 590, "Latência em 160 × 160", 28, CINZA)
    escrever(im, 55, 640, "38,31 ms / quadro · 37,06 ms / quadro", 34, tipo="bold")
    salvar(im, "velocidade")

    im = tela("O que entra no tempo de processamento")
    etapas = ["Leitura", "Decodificação", "Pré-processamento", "Inferência", "Prévia"]
    for i, nome in enumerate(etapas):
        x = 46 + i * 246
        painel(im, (x, 250, x + 214, 390))
        escrever(im, x + 14, 285, nome, 23, tipo="bold", largura=188)
    escrever(im, 50, 492, "Configuração adotada no CitizenTech", 29, CINZA)
    escrever(im, 50, 550, "ResNet18 · 160 × 160 pixels · limiar 0,49", 40, tipo="bold")
    escrever(im, 50, 650, "A interface exibe a latência da foto e o FPS de sequências e vídeos.", 25, CINZA)
    salvar(im, "pipeline")

    sutis = ler_csv(PROJETO / "data/sutis/manifesto.csv")
    im = tela("Avaliação complementar de sinais sutis", "Recortes com 1 a 31 pixels marcados na máscara.")
    escrever(im, 52, 220, "26 recortes de 13 fotos reservadas para teste", 35, tipo="bold")
    for i, linha in enumerate(sutis[:4]):
        x = 56 + i * 306
        foto(im, PROJETO / "data/sutis" / linha["arquivo"], (x, 335, x + 250, 585))
        escrever(im, x, 613, linha["pixels_mascara"] + " pixels BW", 25, CINZA)
    salvar(im, "sutis")

    im = tela("Resultado nos 26 recortes sutis")
    grade(im, [["Entrada", "Recortes sinalizados"],
        ["160 × 160", "2 de 26"], ["224 × 224", "2 de 26"]],
        proporcoes=[1.4, 2], altura=95, tamanho=36)
    escrever(im, 54, 590, "Marcação mínima, fragmentos e baixo contraste dificultam a sinalização.", 29, tipo="bold", largura=1130)
    escrever(im, 54, 685, "A confiança precisa ser interpretada junto da imagem e da captura.", 24, CINZA)
    salvar(im, "sutis_resultado")

    im = tela("Integração ao CitizenTech")
    escrever(im, 50, 230, "Foto ou vídeo", 42, tipo="bold")
    escrever(im, 50, 330, "Classe e confiança por quadro", 42, tipo="bold")
    escrever(im, 50, 430, "Sinalização para revisão humana", 42, "#9e410f", "bold")
    escrever(im, 50, 600, "Durante a execução, a interface recebe os resultados de cada quadro.", 27, CINZA, largura=1130)
    salvar(im, "integracao")

    im = tela("Aplicação e limites")
    escrever(im, 50, 230, "Avaliação em fotos do mesmo acervo", 36, tipo="bold")
    escrever(im, 50, 330, "Outros locais, câmeras e condições de iluminação", 34, tipo="bold", largura=1130)
    escrever(im, 50, 445, "Gravidade e segurança estrutural exigem avaliação profissional.", 36, "#9e410f", "bold", largura=1120)
    escrever(im, 50, 650, "O módulo apoia a seleção de locais para inspeção.", 29, CINZA)
    salvar(im, "limites")

    im = tela("CitizenTech")
    escrever(im, 52, 230, "Visão Computacional", 62, tipo="bold")
    escrever(im, 52, 325, "para Manutenção Urbana", 44, tipo="bold")
    escrever(im, 52, 465, "Classificação de fissuras e triagem para inspeção humana", 29, CINZA, largura=1120)
    escrever(im, 52, 650, "FIAP · Global Solution 2026.2", 25, CINZA)
    salvar(im, "encerramento")

    eventos = [
        (0.0, "abertura"), (8.0, "problema"), (29.4, "fluxo"),
        (35.4, "origem"), (51.1, "amostra"), (67.6, "divisao"), (85.9, "manifesto"),
        (99.0, "modelo"), (120.6, "treino"), (135.7, "preprocessamento"),
        (151.5, "validacao"), (170.8, "metricas"), (187.9, "matriz"),
        (194.0, "erros"), (216.1, "mascara"), (225.4, "resolucoes"),
        (241.7, "comparacao"), (253.8, "equipamento"), (274.0, "velocidade"),
        (292.9, "pipeline"), (303.5, "ao_vivo"), (375.0, "sutis"),
        (390.3, "sutis_resultado"), (412.6, "integracao"), (427.1, "limites"),
        (448.6, "encerramento"),
    ]
    timeline = {
        "audio": "narracao_original.ogg", "duracao_audio": 457.0935,
        "canvas": [W, H], "fps": 25,
        "eventos": [{"inicio": a, "tela": n} for a, n in eventos],
    }
    assert all(a < b for (a, _), (b, _) in zip(eventos, eventos[1:]))
    (PASTA / "roteiro_visual.json").write_text(json.dumps(timeline, ensure_ascii=False, indent=2), encoding="utf-8")
    (PASTA / "tempos_narracao.json").write_text(json.dumps(
        {"duracao": 457.0935, "referencia": "roteiro_visual.json", "unidade": "segundos"},
        ensure_ascii=False, indent=2
    ), encoding="utf-8")
    print(f"{len(eventos) - 1} telas e trecho de execução ao vivo preparados.", flush=True)


def exportar(ffmpeg):
    destino = PROJETO / "Apresentacao_Completa_CitizenTech.mp4"
    plano = json.loads((PASTA / "roteiro_visual.json").read_text(encoding="utf-8"))
    ultimo_quadro = math.ceil(plano["duracao_audio"] * plano["fps"])
    (PASTA / "edicao.json").write_text(json.dumps({
        "captura": "captura_completa.webm", "quadro_inicial": 0,
        "quadro_final_exclusivo": ultimo_quadro, "fps": plano["fps"],
        "audio": "narracao_original.ogg", "velocidade": 1.0,
        "ganho_db": -2.5, "fim_da_apresentacao_s": ultimo_quadro / plano["fps"],
        "faixa_video": "captura full-range convertida para faixa de vídeo limitada",
        "motivo_do_corte_final": "encerrar após a fala e o encerramento previstos no roteiro",
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    subprocess.run([
        ffmpeg, "-y", "-loglevel", "error", "-i", str(PASTA / "captura_completa.webm"),
        "-i", str(PASTA / "narracao_original.ogg"), "-map", "0:v:0", "-map", "1:a:0",
        "-vf", f"trim=end_frame={ultimo_quadro},setpts=PTS-STARTPTS,scale=in_range=full:out_range=tv",
        "-c:v", "libx264", "-preset", "fast", "-crf", "21", "-pix_fmt", "yuv420p",
        "-color_range", "tv",
        "-af", "volume=-2.5dB", "-c:a", "aac", "-b:a", "128k", "-ar", "48000",
        "-movflags", "+faststart", str(destino),
    ], check=True)
    print(destino, flush=True)


if __name__ == "__main__":
    cli = argparse.ArgumentParser(description="Prepara as telas e exporta a apresentação com a narração original.")
    cli.add_argument("--exportar", metavar="FFMPEG")
    args = cli.parse_args()
    if args.exportar:
        exportar(args.exportar)
    else:
        gerar()
