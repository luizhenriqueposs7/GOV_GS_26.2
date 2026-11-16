import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


class BuildVercelTest(unittest.TestCase):
    def test_limpeza_preserva_codigo_e_nao_toca_instalacao_fora_do_build(self):
        from scripts import build_vercel
        with tempfile.TemporaryDirectory() as pasta:
            raiz = Path(pasta)
            pacotes = raiz / '.vercel/python/.venv/lib/python3.13/site-packages'
            (pacotes / 'pacote/tests').mkdir(parents=True)
            (pacotes / 'pacote/__pycache__').mkdir()
            (pacotes / 'pacote/modulo.py').write_text('codigo preservado')
            (pacotes / 'pacote/tests/teste.py').write_text('fixture')
            (pacotes / 'pacote/__pycache__/modulo.pyc').write_bytes(b'bytecode')
            fora = raiz / 'global/site-packages'
            fora.mkdir(parents=True)
            (fora / 'preservar.py').write_text('global')
            with patch.object(build_vercel, 'RAIZ', raiz):
                build_vercel.limpar_dependencias(pacotes)
                with self.assertRaises(RuntimeError):
                    build_vercel.limpar_dependencias(fora)
            self.assertEqual((pacotes / 'pacote/modulo.py').read_text(), 'codigo preservado')
            self.assertFalse((pacotes / 'pacote/tests').exists())
            self.assertFalse((pacotes / 'pacote/__pycache__').exists())
            self.assertEqual((fora / 'preservar.py').read_text(), 'global')
