"""Prepara modelos e remove somente fixtures e bytecode da instalação do build."""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))


def limpar_dependencias(pasta: Path):
    pasta = pasta.resolve()
    permitido = (RAIZ / '.vercel/python/.venv').resolve()
    if pasta.name != 'site-packages' or not pasta.is_relative_to(permitido):
        raise RuntimeError('A limpeza só pode atingir dependências da instalação isolada do build Vercel.')
    antes = sum(p.stat().st_size for p in pasta.rglob('*') if p.is_file())
    for nome in ('tests', '__pycache__'):
        for caminho in sorted(pasta.rglob(nome), key=lambda p: len(p.parts)):
            if caminho.is_dir():
                if not caminho.resolve().is_relative_to(pasta):
                    raise RuntimeError('A instalação contém um link para fora da pasta permitida.')
                shutil.rmtree(caminho)
    depois = sum(p.stat().st_size for p in pasta.rglob('*') if p.is_file())
    return {'bytes_antes': antes, 'bytes_depois': depois, 'bytes_removidos': antes - depois}


def main():
    from scripts.preparar_modelos_online import preparar
    print(json.dumps(preparar(), ensure_ascii=False), flush=True)
    if os.getenv('VERCEL') == '1':
        import numpy
        print(json.dumps({'dependencias': limpar_dependencias(Path(numpy.__file__).resolve().parents[1])}), flush=True)
        subprocess.run([sys.executable, '-c',
            "import fastapi,pandas,numpy,onnxruntime,fastembed,psycopg,PIL; "
            "from central.modulos import triagem,buscar_fontes; "
            "assert triagem('Calçada sem rampa acessível')['category']=='Acessibilidade'; "
            "assert buscar_fontes('enchente'); print('Dependências e RPA/PLN conferidos após a limpeza.')"], check=True)


if __name__ == '__main__':
    main()
