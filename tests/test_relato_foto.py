import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient
from PIL import Image


class RelatoFotoTest(unittest.TestCase):
    def setUp(self):
        self.pasta = tempfile.TemporaryDirectory()
        self.addCleanup(self.pasta.cleanup)
        self.env = patch.dict('os.environ', {'GOV_MANAGER_KEY': 'chave-teste', 'GROQ_API_KEY': 'teste'})
        self.env.start()
        self.addCleanup(self.env.stop)
        from central.app import criar_app
        self.client = TestClient(criar_app(Path(self.pasta.name)))
        self.addCleanup(self.client.close)
        saida = io.BytesIO()
        exif = Image.Exif()
        exif[270] = 'metadado privado'
        Image.new('RGB', (50, 40), 'gray').save(saida, format='JPEG', exif=exif)
        self.foto = saida.getvalue()
        self.sugestao = {'status': 'identificado', 'descricao': 'Possível fissura visível na superfície fotografada.',
                         'tipo': 'fissura', 'limites': 'A imagem não permite avaliar a gravidade.'}

    def remoto(self, dados=None, modelo='qwen/qwen3.8-27b', finish='stop'):
        return io.BytesIO(json.dumps({'model': modelo, 'choices': [
            {'finish_reason': finish, 'message': {'content': json.dumps(dados or self.sugestao)}}]}).encode())

    def previa(self):
        return self.client.post('/api/relato-foto', files={'arquivo': ('foto.jpg', self.foto, 'image/jpeg')})

    def test_previa_usa_imagem_sem_exif_e_nao_grava_pedido(self):
        import base64
        from central import relato_foto

        def chamar(req, timeout):
            self.assertEqual(timeout, 45)
            corpo = json.loads(req.data)
            imagem = corpo['messages'][1]['content'][1]['image_url']['url']
            with Image.open(io.BytesIO(base64.b64decode(imagem.split(',')[1]))) as foto:
                self.assertFalse(foto.getexif())
            self.assertTrue(corpo['response_format']['json_schema']['strict'])
            return self.remoto()

        with patch.object(relato_foto, 'urlopen', chamar):
            r = self.previa()
        self.assertEqual(r.status_code, 200, r.text)
        self.assertEqual(r.json()['descricao'], self.sugestao['descricao'])
        self.assertTrue(r.json()['previa'])
        self.assertEqual(self.client.get('/api/atendimentos').json(), [])
        self.assertFalse((Path(self.pasta.name) / 'fotos').exists())

    def test_arquivo_invalido_falha_antes_do_provedor(self):
        r = self.client.post('/api/relato-foto', files={'arquivo': ('foto.jpg', b'invalido', 'image/jpeg')})
        self.assertEqual(r.status_code, 422)

    def test_inconclusiva_nao_recebe_descricao_fabricada(self):
        from central import relato_foto
        dados = {**self.sugestao, 'status': 'inconclusivo', 'descricao': 'Uma ocorrência suposta', 'tipo': 'outro'}
        with patch.object(relato_foto, 'urlopen', return_value=self.remoto(dados)):
            r = self.previa()
        self.assertEqual(r.status_code, 200, r.text)
        self.assertEqual(r.json()['descricao'], '')

    def test_resposta_adulterada_truncada_e_erro_remoto_nao_viram_sucesso(self):
        from central import relato_foto
        from urllib.error import HTTPError
        for remoto in [self.remoto(modelo='outro'), self.remoto(finish='length'),
                       self.remoto({**self.sugestao, 'tipo': 'inventado'}), io.BytesIO(b'x' * 16385)]:
            with patch.object(relato_foto, 'urlopen', return_value=remoto):
                self.assertEqual(self.previa().status_code, 503)
        with patch.object(relato_foto, 'urlopen', side_effect=HTTPError('https://api.groq.com', 429, 'limite', {}, None)):
            self.assertEqual(self.previa().status_code, 503)
        self.assertEqual(self.client.get('/api/atendimentos').json(), [])

    def test_diagnostico_remoto_nao_expoe_chave_ou_imagem(self):
        from central import relato_foto
        from urllib.error import HTTPError
        erro = HTTPError('https://api.groq.com', 400, 'contrato', {}, io.BytesIO(json.dumps({
            'error': {'message': 'Schema recusado. Credencial chave-diagnostico, imagem data:image/jpeg;base64,QUJDRA=='}}).encode()))
        with patch.dict('os.environ', {'GROQ_API_KEY': 'chave-diagnostico'}), \
                patch.object(relato_foto, 'urlopen', side_effect=erro), self.assertLogs('central.relato_foto', 'WARNING') as logs:
            r = self.previa()
        self.assertEqual(r.status_code, 503)
        self.assertIn('400', logs.output[0])
        self.assertNotIn('chave-diagnostico', logs.output[0])
        self.assertNotIn('QUJDRA==', logs.output[0])
        self.assertNotIn('Schema recusado', r.text)

    def test_origem_assinada_preserva_texto_original_e_contestacao(self):
        from central import relato_foto
        with patch.object(relato_foto, 'urlopen', return_value=self.remoto()):
            r = self.previa()
        self.assertEqual(r.status_code, 200, r.text)
        entrada = {'descricao': 'Teste: calçada quebrada na praça, descrição conferida pela pessoa.',
                   'bairro': 'Região fictícia', 'local': 'Praça ilustrativa', 'contexto': 'area_publica', 'confirmado': True}
        dados = {'dados': json.dumps(entrada), 'previa': r.json()['previa']}
        foto = {'arquivo': ('foto.jpg', self.foto, 'image/jpeg')}
        caso = self.client.post('/api/atendimentos/com-anexo', data=dados, files=foto)
        self.assertEqual(caso.status_code, 201, caso.text)
        caso = caso.json()
        self.assertEqual(caso['sugestao_foto']['descricao'], self.sugestao['descricao'])
        self.assertNotEqual(caso['descricao'], caso['sugestao_foto']['descricao'])
        self.assertEqual(caso['sugestao_foto']['foto_sha256'], caso['foto']['sha256'])
        self.assertEqual(caso['historico'][0]['dados']['sugestao_foto'], caso['sugestao_foto'])
        url = '/api/atendimentos/' + caso['id']
        chave = {'X-Manager-Key': 'chave-teste'}
        self.assertEqual(self.client.post(url+'/revisao', headers=chave, json={
            'prioridade': 'Alta', 'revisor': 'Teste', 'justificativa': 'Barreira conferida no cenário de teste.'}).status_code, 200)
        self.assertEqual(self.client.post(url+'/zelabairro', headers=chave).status_code, 200)
        contestado = self.client.post(url+'/contestacao', json={'motivo': 'Teste: reconsiderar a prioridade atribuída.'}).json()
        self.assertIsNone(contestado['revisao'])
        self.assertEqual(contestado['sugestao_foto'], caso['sugestao_foto'])
        self.assertEqual(self.client.post(url+'/zelabairro', headers=chave).status_code, 409)
        dados['previa'] += 'alterado'
        self.assertEqual(self.client.post('/api/atendimentos/com-anexo', data=dados, files=foto).status_code, 422)
        dados['previa'] = r.json()['previa']
        outro = io.BytesIO()
        Image.new('RGB', (50,40), 'white').save(outro, format='JPEG')
        fotos_antes = set((Path(self.pasta.name) / 'fotos').iterdir())
        self.assertEqual(self.client.post('/api/atendimentos/com-anexo', data=dados,
            files={'arquivo': ('outra.jpg', outro.getvalue(), 'image/jpeg')}).status_code, 422)
        self.assertEqual(set((Path(self.pasta.name) / 'fotos').iterdir()), fotos_antes)
        self.assertEqual(len(self.client.get('/api/atendimentos').json()), 1)
