"""Visualizador local dos arquivos reais e da saída de verificações permitidas."""
import csv
import json
import subprocess
import sys
from pathlib import Path
from flask import Flask, Response, abort, jsonify, request, send_file, stream_with_context
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import JsonLexer, PythonLexer, TextLexer

PASTA = Path(__file__).resolve().parent
RAIZ = PASTA.parents[1]
ARQUIVOS = (
    "README.md", "dados.py", "visao.py", "train.py", "inspecao.py",
    "static/inspecao.js", "experimentos.py", "data/manifesto.csv",
    "artifacts/metricas.json", "artifacts/resolucao_224/metricas.json",
    "artifacts/analise_erros.csv", "artifacts/experimentos.json",
    "data/sutis/manifesto.csv", "video/tecnico/conferir.py",
)
app = Flask(__name__)
app.json.ensure_ascii = False


@app.get("/")
def inicio():
    return send_file(PASTA / "index.html")


@app.get("/lista")
def lista():
    return jsonify(list(ARQUIVOS))


@app.get("/estilo")
def estilo():
    return Response(HtmlFormatter(style="monokai").get_style_defs(".codigo"), mimetype="text/css")


@app.get("/arquivo")
def arquivo():
    nome = request.args.get("nome", "")
    if nome not in ARQUIVOS:
        abort(404)
    caminho = RAIZ / nome
    texto = caminho.read_text(encoding="utf-8")
    lexer = PythonLexer() if caminho.suffix == ".py" else JsonLexer() if caminho.suffix == ".json" else TextLexer()
    linhas = highlight(texto, lexer, HtmlFormatter(nowrap=True)).splitlines()
    conteudo = "".join(
        f'<div class="linha" data-linha="{i}"><span class="numero">{i}</span>'
        f'<span class="texto">{linha or " "}</span></div>'
        for i, linha in enumerate(linhas, 1)
    )
    return jsonify(nome=nome, html=conteudo, linhas=len(linhas))


@app.get("/imagem")
def imagem():
    caminho = (RAIZ / request.args.get("nome", "")).resolve()
    permitidas = (RAIZ / "data/recortes", RAIZ / "data/sutis/recortes")
    if not (any(caminho.is_relative_to(p) for p in permitidas)
            or caminho == RAIZ / "video/contexto_mascara.png"):
        abort(404)
    if caminho.suffix.lower() not in (".jpg", ".png") or not caminho.is_file():
        abort(404)
    return send_file(caminho)


@app.get("/tabela")
def tabela():
    nome = request.args.get("nome", "")
    if nome not in ARQUIVOS or not nome.endswith(".csv"):
        abort(404)
    with (RAIZ / nome).open(encoding="utf-8", newline="") as stream:
        return jsonify(list(csv.DictReader(stream)))


@app.get("/json")
def conteudo_json():
    nome = request.args.get("nome", "")
    if nome not in ARQUIVOS or not nome.endswith(".json"):
        abort(404)
    return jsonify(json.loads((RAIZ / nome).read_text(encoding="utf-8")))


@app.get("/executar/<acao>")
def executar(acao):
    if acao not in ("dados", "teste", "sutis", "ambiente"):
        abort(404)

    @stream_with_context
    def saida():
        processo = subprocess.Popen(
            [sys.executable, "-X", "utf8", "-u", str(PASTA / "conferir.py"), acao],
            cwd=RAIZ, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, encoding="utf-8",
        )
        try:
            for linha in processo.stdout:
                yield "data: " + json.dumps({"linha": linha}, ensure_ascii=False) + "\n\n"
            codigo = processo.wait()
            yield "event: fim\ndata: " + json.dumps({"codigo": codigo}) + "\n\n"
        finally:
            if processo.poll() is None:
                processo.terminate()
            processo.stdout.close()
    return Response(saida(), mimetype="text/event-stream")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8767, threaded=True)
