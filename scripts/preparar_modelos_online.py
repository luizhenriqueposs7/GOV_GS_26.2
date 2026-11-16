"""Prepara pesos fixos no build; --exportar-visao requer apenas ferramentas locais de exportação."""
import argparse
import csv
import hashlib
import importlib.metadata
import json
import shutil
import sys
from pathlib import Path
from urllib.request import urlopen


RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
from central import visao_online
from central.pesos_online import PESOS_ENCODER, REPOSITORIO_ENCODER, REVISAO_ENCODER, PASTA_ENCODER

ARQUIVOS_ENCODER = {nome: dado[0] for nome, dado in PESOS_ENCODER.items()}
CACHE_ENCODER = RAIZ / "modelos_online/genai/.runtime/embeddings"
PASTA_MODELO = PASTA_ENCODER


def sha256(caminho):
    with caminho.open("rb") as arquivo:
        return hashlib.file_digest(arquivo, "sha256").hexdigest()


def preparar_embeddings(cache_origem=None):
    repositorio = CACHE_ENCODER / PASTA_MODELO
    snapshot = repositorio / "snapshots" / REVISAO_ENCODER
    snapshot.mkdir(parents=True, exist_ok=True)
    metadata = {}
    for nome, esperado in ARQUIVOS_ENCODER.items():
        destino = snapshot / nome
        if not destino.is_file() or sha256(destino) != esperado:
            temporario = destino.with_suffix(destino.suffix + ".partial")
            origem = Path(cache_origem) / PASTA_MODELO / "snapshots" / REVISAO_ENCODER / nome if cache_origem else None
            if origem and not origem.is_file():
                origem = Path(cache_origem) / PASTA_MODELO.replace("Qdrant", "qdrant") / "snapshots" / REVISAO_ENCODER / nome
            try:
                if origem and origem.is_file() and sha256(origem) == esperado:
                    shutil.copyfile(origem, temporario)
                else:
                    url = f"https://huggingface.co/{REPOSITORIO_ENCODER}/resolve/{REVISAO_ENCODER}/{nome}"
                    with urlopen(url, timeout=120) as resposta, temporario.open("wb") as arquivo:
                        shutil.copyfileobj(resposta, arquivo, length=1024 * 1024)
                if sha256(temporario) != esperado:
                    raise ValueError(f"O encoder diverge do snapshot entregue: {nome}")
                temporario.replace(destino)
            finally:
                temporario.unlink(missing_ok=True)
        metadata[str(Path("snapshots") / REVISAO_ENCODER / nome)] = {"size": destino.stat().st_size}
    (repositorio / "refs").mkdir(exist_ok=True)
    (repositorio / "refs/main").write_text(REVISAO_ENCODER, encoding="utf-8")
    (repositorio / "files_metadata.json").write_text(json.dumps(metadata), encoding="utf-8")
    resumo = {"repositorio": REPOSITORIO_ENCODER, "revisao": REVISAO_ENCODER, "sha256": ARQUIVOS_ENCODER}
    (CACHE_ENCODER / "refs-ready.json").write_text(json.dumps(resumo, indent=2), encoding="utf-8")
    return resumo


def exportar_visao():
    import numpy as np
    import onnxruntime as ort
    import torch
    from PIL import Image
    from materiais.visao.visao import carregar_modelo, classificar

    checkpoint = RAIZ / "materiais/visao/artifacts/crack_resnet18.pth"
    if sha256(checkpoint) != visao_online.CHECKPOINT_SHA256:
        raise ValueError("O checkpoint não corresponde ao arquivo entregue.")
    modelo, parametros, preprocessar = carregar_modelo()
    if parametros["image_size"] != 160:
        raise ValueError("A exportação exige o checkpoint de 160 × 160.")
    destino = visao_online.ARTEFATOS
    destino.mkdir(parents=True, exist_ok=True)
    temporario = destino / "crack_resnet18.partial.onnx"
    try:
        torch.onnx.export(modelo, torch.zeros(1, 3, 160, 160), str(temporario),
                          input_names=["imagem"], output_names=["logits"],
                          opset_version=17, dynamo=False)
        opcoes = ort.SessionOptions()
        opcoes.intra_op_num_threads = opcoes.inter_op_num_threads = 1
        sessao = ort.InferenceSession(str(temporario), sess_options=opcoes, providers=["CPUExecutionProvider"])
        pasta_dados = RAIZ / "materiais/visao/data"
        with (RAIZ / "materiais/visao/artifacts/previsoes_teste.csv").open(encoding="utf-8", newline="") as arquivo:
            caminhos = [pasta_dados / linha["arquivo"] for linha in csv.DictReader(arquivo)]
        caminhos.extend(sorted((pasta_dados / "sutis/recortes").glob("*.jpg")))
        casos = [(str(p.relative_to(RAIZ)).replace("\\", "/"), p) for p in caminhos]
        casos.extend((f"controle:{cor}", Image.new("RGB", (227, 227), cor)) for cor in ("black", "white", "gray"))
        resultados = []
        for nome, entrada in casos:
            imagem = Image.open(entrada) if isinstance(entrada, Path) else entrada
            try:
                esperado = classificar(imagem, modelo, parametros, preprocessar)
                tensor = visao_online.preprocessar(imagem)
                np.testing.assert_array_equal(tensor, preprocessar(imagem.convert("RGB")).unsqueeze(0).numpy())
                logits = sessao.run(None, {"imagem": tensor})[0][0]
                exponenciais = np.exp(logits - logits.max())
                escore = float((exponenciais / exponenciais.sum())[parametros["positive_idx"]])
                resultados.append({"arquivo": nome, "pytorch_escore": esperado["escore"], "onnx_escore": escore,
                                   "erro_absoluto": abs(escore - esperado["escore"]),
                                   "alerta_pytorch": esperado["alerta"], "alerta_onnx": escore >= parametros["threshold"]})
            finally:
                imagem.close()
        erro = max(r["erro_absoluto"] for r in resultados)
        divergencias = sum(r["alerta_pytorch"] != r["alerta_onnx"] for r in resultados)
        if erro > 1e-5 or divergencias:
            raise ValueError(f"A conversão não preservou a inferência: erro={erro}, decisões divergentes={divergencias}.")
        manifesto = {
            "modelo": "ResNet18", "checkpoint_sha256": visao_online.CHECKPOINT_SHA256,
            "onnx_sha256": sha256(temporario), "image_size": parametros["image_size"],
            "positive_idx": parametros["positive_idx"], "threshold": parametros["threshold"],
            "opset": 17, "versoes_exportacao": {n: importlib.metadata.version(n) for n in ("torch", "torchvision", "onnx", "onnxruntime", "numpy", "Pillow")},
        }
        proximas = sorted((r for r in resultados if not r["arquivo"].startswith("controle:")),
                          key=lambda r: abs(r["pytorch_escore"] - parametros["threshold"]))[:12]
        paridade = {"onnx_sha256": manifesto["onnx_sha256"], "tolerancia_absoluta": 1e-5,
                    "imagens_reais": len(caminhos), "controles": 3, "divergencias_decisao": divergencias,
                    "erro_absoluto_maximo": erro, "limiar": parametros["threshold"],
                    "proximas_limiar": proximas, "resultados": resultados}
        temporario.replace(destino / "crack_resnet18.onnx")
        for nome, dados in (("manifesto.json", manifesto), ("paridade.json", paridade)):
            (destino / nome).write_text(json.dumps(dados, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return paridade
    finally:
        temporario.unlink(missing_ok=True)


def verificar_encoder(assistente):
    import numpy as np
    import platform
    from central.ia_online import original
    encoder = original().codificador().model
    caminho_efetivo = encoder._model_dir / encoder.model_description.model_file
    sha_efetivo = sha256(caminho_efetivo)
    print(json.dumps({"encoder_efetivo": str(caminho_efetivo), "sha256": sha_efetivo,
                      "providers": encoder.model.get_providers(), "threads": encoder.threads,
                      "arquitetura": platform.machine(), "implementacao": type(encoder).__name__}, ensure_ascii=False), flush=True)
    if sha_efetivo != ARQUIVOS_ENCODER["model_optimized.onnx"]:
        raise ValueError("O modelo efetivamente carregado não corresponde ao encoder entregue.")
    referencia = json.loads((RAIZ / "modelos_online/genai/referencia_encoder.json").read_text(encoding="utf-8"))
    consultas = referencia["consultas"]
    corpus = np.asarray(assistente.indice.vetores, dtype=np.float64)
    if [t.id for t in assistente.trechos] != referencia["ids_corpus"]:
        raise ValueError("O corpus não corresponde à referência de paridade do encoder.")
    vetores = np.asarray([next(original().codificador().query_embed(q)) for q in consultas], dtype=np.float64)
    pares = ((corpus, np.asarray(referencia["vetores_corpus"], dtype=np.float64)),
             (vetores, np.asarray(referencia["vetores_consultas"], dtype=np.float64)))
    validos = all(atual.shape == esperado.shape and np.isfinite(atual).all() and np.isfinite(esperado).all()
                  for atual, esperado in pares)
    print(json.dumps({"encoder_formas": [list(v.shape) for par in pares for v in par], "encoder_finitos_e_formas_validas": bool(validos)}), flush=True)
    if not validos:
        raise ValueError("O encoder retornou vetores com forma divergente ou valores não finitos.")
    erros, cossenos = [], []
    for atual, esperado in pares:
        denominador = np.linalg.norm(atual, axis=1) * np.linalg.norm(esperado, axis=1)
        if (denominador <= 0).any():
            raise ValueError("O encoder retornou um vetor sem direção definida.")
        erros.append(float(np.max(np.abs(atual - esperado))))
        cossenos.append(float(np.min(np.clip(np.sum(atual * esperado, axis=1) / denominador, -1, 1))))
    rankings = [[t.id for t, _ in assistente.indice.buscar(q)] for q in consultas]
    resultado = {"referencia_fastembed": referencia["versoes"]["fastembed"],
                 "fastembed_runtime": importlib.metadata.version("fastembed"), "revisao": REVISAO_ENCODER,
                 "encoder_sha256": sha_efetivo, "sistema": platform.system(), "arquitetura": platform.machine(),
                 "trechos": len(assistente.trechos), "consultas": len(consultas),
                 "erro_absoluto_maximo_vetores": max(erros), "erros_absolutos_corpus_consultas": erros,
                 "cosseno_minimo_corpus": cossenos[0], "cosseno_minimo_consultas": cossenos[1],
                 "rankings_identicos": rankings == referencia["rankings"],
                 "criterio_portatil_fp16": {"erro_absoluto_maximo": 1e-3, "cosseno_minimo": 0.99999, "rankings_identicos": True}}
    print(json.dumps({"paridade_encoder": resultado}, ensure_ascii=False), flush=True)
    # FP16 usa kernels distintos por CPU/SO; direção e ranking também precisam permanecer equivalentes.
    if max(erros) > 1e-3 or min(cossenos) < 0.99999 or not resultado["rankings_identicos"]:
        raise ValueError((f"O encoder ou o ranking híbrido diverge da implementação original. "
                          f"erro_corpus={erros[0]:.9g}; erro_consultas={erros[1]:.9g}; rankings_divergentes="
                          + json.dumps([{"consulta": i + 1, "esperado": esperado, "atual": atual}
                                        for i, (esperado, atual) in enumerate(zip(referencia["rankings"], rankings))
                                        if esperado != atual], ensure_ascii=False))[:1000])
    (RAIZ / "modelos_online/genai/paridade_encoder.json").write_text(json.dumps(resultado, indent=2) + "\n", encoding="utf-8")
    return resultado


def preparar(cache_origem=None):
    preparar_embeddings(cache_origem)
    sessao, manifesto = visao_online.modelo()
    paridade = json.loads((visao_online.ARTEFATOS / "paridade.json").read_text(encoding="utf-8"))
    if (paridade.get("onnx_sha256") != manifesto["onnx_sha256"] or paridade.get("divergencias_decisao") != 0
            or paridade.get("erro_absoluto_maximo", 1) > 1e-5):
        raise ValueError("O relatório de paridade não corresponde ao modelo convertido.")
    from central.ia_online import bot
    assistente = bot()
    if assistente.indice.vetores is None:
        raise ValueError("A busca híbrida original não foi preparada.")
    verificar_encoder(assistente)
    return {"encoder_revisao": REVISAO_ENCODER, "visao_sha256": manifesto["onnx_sha256"],
            "trechos": len(assistente.trechos), "busca_hibrida": True,
            "bytes_artefatos": sum(p.stat().st_size for p in (RAIZ / "modelos_online").rglob("*") if p.is_file()),
            "versoes_runtime": {n: importlib.metadata.version(n) for n in ("fastembed", "onnxruntime", "numpy", "Pillow")}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exportar-visao", action="store_true", help="Exporta e compara contra o PyTorch local; não é necessário no build.")
    parser.add_argument("--cache-embeddings", type=Path, help="Reutiliza o cache original se seus hashes forem idênticos.")
    argumentos = parser.parse_args()
    if argumentos.exportar_visao:
        resultado = exportar_visao()
        print(json.dumps({k: v for k, v in resultado.items() if k not in {"resultados", "proximas_limiar"}}, ensure_ascii=False))
    print(json.dumps(preparar(argumentos.cache_embeddings), ensure_ascii=False))


if __name__ == "__main__":
    main()
