import json
import tomllib
import unittest
from pathlib import Path


class ConfiguracaoVercelTest(unittest.TestCase):
    def test_manifesto_prioritario_tem_as_mesmas_dependencias_e_entrada_correta(self):
        raiz = Path(__file__).resolve().parents[1]
        projeto = tomllib.loads((raiz / 'pyproject.toml').read_text())
        requisitos = (raiz / 'requirements.txt').read_text().splitlines()
        self.assertEqual(projeto['project']['dependencies'], [r.strip() for r in requisitos if r.strip()])
        self.assertEqual(projeto['tool']['vercel']['entrypoint'], 'central.app:app')
        self.assertFalse(projeto['tool']['vercel']['fastapi']['static']['cdn'])
        config = json.loads((raiz / 'vercel.json').read_text())
        self.assertLessEqual(len(config['functions']['central/app.py']['excludeFiles']), 256)
