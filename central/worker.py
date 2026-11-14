"""Executa funções entregues em processo separado, sem misturar dependências."""
import json
import os
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]


def main():
    operacao = sys.argv[1]
    dados = json.load(sys.stdin)
    if operacao == "visao":
        sys.path.insert(0, str(RAIZ / "materiais/visao"))
        from PIL import Image
        from visao import carregar_modelo, classificar
        modelo, parametros, preprocessar = carregar_modelo()
        with Image.open(dados["imagem"]) as imagem:
            resultado = classificar(imagem, modelo, parametros, preprocessar)
        resultado.update(limiar=parametros["threshold"], resolucao=parametros["image_size"], modelo="ResNet18")
    elif operacao == "frontend":
        sys.path.insert(0, str(RAIZ / "materiais/frontend"))
        os.environ["DATABASE_PATH"] = dados["banco"]
        from backend.providers import repository
        from backend.schemas.relato import CriarRelatoRequest
        entrada = CriarRelatoRequest.model_validate(dados["dados"])
        repository.inicializar_banco()
        existentes = repository.listar_por_cidadao(entrada.cidadao_id)
        resultado = existentes[0] if existentes else repository.criar_relato(entrada.model_dump())
    else:
        raise ValueError("Operação de módulo não permitida.")
    print(json.dumps(resultado, ensure_ascii=False))


if __name__ == "__main__":
    main()
