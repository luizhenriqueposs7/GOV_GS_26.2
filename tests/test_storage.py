import hashlib
import io
import unittest
from unittest.mock import patch

import httpx
from PIL import Image

from central.storage import StorageFotos


class StorageTest(unittest.TestCase):
    def setUp(self):
        saida = io.BytesIO()
        exif = Image.Exif()
        exif[270] = 'remover metadado'
        Image.new('RGB', (40, 30), 'gray').save(saida, format='JPEG', exif=exif)
        self.original = saida.getvalue()
        self.storage = StorageFotos('https://projeto.supabase.co', 'sb_secret_' + 'x' * 32)

    def test_upload_privado_normaliza_e_leitura_confere_integridade(self):
        objetos = {}

        def atender(request):
            self.assertEqual(request.headers['apikey'], 'sb_secret_' + 'x' * 32)
            self.assertNotIn('authorization', request.headers)
            self.assertNotIn('/public/', request.url.path)
            if request.method == 'POST':
                objetos[request.url.path] = request.content
                return httpx.Response(200, json={'Key': request.url.path})
            return httpx.Response(200, content=objetos[request.url.path])

        cliente = httpx.Client(transport=httpx.MockTransport(atender))
        with cliente, patch('central.storage.httpx.request', side_effect=cliente.request):
            foto = self.storage.guardar(self.original)
            conteudo = self.storage.ler(foto['sha256'])
        self.assertEqual(hashlib.sha256(conteudo).hexdigest(), foto['sha256'])
        self.assertEqual(foto['bytes'], len(conteudo))
        with Image.open(io.BytesIO(conteudo)) as imagem:
            self.assertFalse(imagem.getexif())

    def test_reenvio_duplicado_exige_os_mesmos_bytes(self):
        with patch('central.storage.httpx.request') as requisicao:
            requisicao.return_value = httpx.Response(400, json={'error': 'Duplicate'})
            with patch.object(self.storage, 'ler', return_value=b'corrompido'):
                with self.assertRaisesRegex(RuntimeError, 'foto'):
                    self.storage.guardar(self.original)

    def test_falha_externa_nao_vaza_chave_nem_confirma_upload(self):
        with patch('central.storage.httpx.request', side_effect=httpx.ConnectError('segredo interno')):
            with self.assertRaises(RuntimeError) as erro:
                self.storage.guardar(self.original)
        self.assertNotIn('sb_secret', str(erro.exception))
        self.assertNotIn('segredo interno', str(erro.exception))

    def test_chave_publica_e_caminho_de_objeto_arbitrario_sao_recusados(self):
        with self.assertRaises(ValueError):
            StorageFotos('https://projeto.supabase.co', 'sb_publishable_teste')
        with self.assertRaises(ValueError):
            self.storage.ler('../segredo')

    def test_download_corrompido_nao_e_entregue(self):
        with patch('central.storage.httpx.request', return_value=httpx.Response(200, content=b'outros bytes')):
            with self.assertRaises(RuntimeError):
                self.storage.ler('a' * 64)
