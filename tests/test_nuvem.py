import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from central.app import criar_app


class NuvemTest(unittest.TestCase):
    def setUp(self):
        self.env = {'GOV_RUNTIME': 'vercel', 'GOV_DATABASE_URL': 'postgresql://servidor/banco?sslmode=require',
                    'GOV_MANAGER_KEY': 'gestao-' + 'x' * 32, 'GOV_ACCESS_USER': 'demonstracao',
                    'GOV_ACCESS_PASSWORD': 'senha-' + 'y' * 24,
                    'SUPABASE_URL': 'https://projeto.supabase.co', 'SUPABASE_SECRET_KEY': 'sb_secret_' + 'z' * 32}

    def test_nuvem_sem_configuracao_nao_cria_sqlite_nem_chave_local(self):
        with tempfile.TemporaryDirectory() as pasta, patch.dict(os.environ, {'GOV_RUNTIME': 'vercel'}, clear=True):
            with self.assertRaisesRegex(RuntimeError, 'GOV_DATABASE_URL'):
                criar_app(Path(pasta) / 'nao-criar')
            self.assertEqual(list(Path(pasta).iterdir()), [])

    def test_autenticacao_protege_tambem_foto_estaticos_e_contrato(self):
        with patch.dict(os.environ, self.env), patch('central.postgres.RepositorioPostgres') as repositorio:
            with TestClient(criar_app()) as client:
                for url in ['/', '/web/app.js', '/api/status', '/api/atendimentos/qualquer/foto', '/contrato']:
                    r = client.get(url)
                    self.assertEqual(r.status_code, 401, url)
                    self.assertEqual(r.headers['cache-control'], 'no-store')
                    self.assertIn('Basic', r.headers['www-authenticate'])
                self.assertEqual(client.get('/api/status', headers={'Authorization': 'Basic /w=='}).status_code, 401)
                client.auth = ('demonstracao', self.env['GOV_ACCESS_PASSWORD'])
                self.assertEqual(client.get('/api/status').status_code, 200)
                self.assertEqual(client.get('/web/app.js').status_code, 200)
                self.assertIn('online', client.get('/api/status').json()['modo'])
                self.assertEqual(client.post('/api/atendimentos', json={}, headers={'Origin': 'https://outro.example'}).status_code, 403)
                repositorio.return_value.confirmar_frontend.return_value = {'id': 'teste'}
                r = client.post('/api/atendimentos/teste/zelabairro', headers={'X-Manager-Key': self.env['GOV_MANAGER_KEY']})
                self.assertEqual(r.status_code, 200, r.text)
                repositorio.return_value.confirmar_frontend.assert_called_once_with('teste')

    def test_falha_do_upload_nao_cria_pedido(self):
        import io
        import json
        from PIL import Image
        imagem = io.BytesIO()
        Image.new('RGB', (20, 20)).save(imagem, format='JPEG')
        entrada = dict(descricao='Buraco na rua de demonstração', bairro='Bairro fictício', confirmado=True)
        with patch.dict(os.environ, self.env), patch('central.postgres.RepositorioPostgres') as repositorio:
            with patch('central.storage.StorageFotos.guardar', side_effect=RuntimeError('Armazenamento indisponível.')):
                with TestClient(criar_app()) as client:
                    client.auth = ('demonstracao', self.env['GOV_ACCESS_PASSWORD'])
                    r = client.post('/api/atendimentos/com-anexo', data={'dados': json.dumps(entrada)},
                                    files={'arquivo': ('foto.jpg', imagem.getvalue(), 'image/jpeg')})
        self.assertEqual(r.status_code, 503)
        repositorio.return_value.criar.assert_not_called()

    def test_nuvem_recusa_pedido_maior_que_o_limite_da_funcao(self):
        with patch.dict(os.environ, self.env), patch('central.postgres.RepositorioPostgres'):
            with TestClient(criar_app()) as client:
                client.auth = ('demonstracao', self.env['GOV_ACCESS_PASSWORD'])
                r = client.post('/api/atendimentos', content=b'x', headers={'Content-Length': str(5 * 1024 * 1024)})
                self.assertEqual(r.status_code, 413)

    def test_banco_lento_no_envio_nao_bloqueia_outras_requisicoes(self):
        import json
        from concurrent.futures import ThreadPoolExecutor
        from threading import Event
        esperando, liberar = Event(), Event()
        entrada = dict(descricao='Buraco na rua de demonstração', bairro='Bairro fictício', confirmado=True)

        def gravar(dados):
            esperando.set()
            if not liberar.wait(10):
                raise RuntimeError('Teste não liberou a gravação.')
            return {'id': 'teste'}

        with patch.dict(os.environ, self.env), patch('central.postgres.RepositorioPostgres') as repositorio:
            repositorio.return_value.criar.side_effect = gravar
            with TestClient(criar_app()) as client, ThreadPoolExecutor(max_workers=2) as pool:
                client.auth = ('demonstracao', self.env['GOV_ACCESS_PASSWORD'])
                envio = pool.submit(client.post, '/api/atendimentos/com-anexo', data={'dados': json.dumps(entrada)})
                try:
                    self.assertTrue(esperando.wait(3))
                    status = pool.submit(client.get, '/api/status').result(timeout=2)
                    self.assertEqual(status.status_code, 200)
                finally:
                    liberar.set()
                    envio.result(timeout=5)
