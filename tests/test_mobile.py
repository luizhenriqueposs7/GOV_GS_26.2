import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from uuid import uuid4

from fastapi.testclient import TestClient
from PIL import Image


class MobileTest(unittest.TestCase):
    def setUp(self):
        self.pasta = tempfile.TemporaryDirectory()
        self.addCleanup(self.pasta.cleanup)
        self.env = patch.dict('os.environ', {'GOV_MANAGER_KEY': 'chave-teste'})
        self.env.start()
        self.addCleanup(self.env.stop)
        from central.app import criar_app
        self.client = TestClient(criar_app(Path(self.pasta.name)))
        self.addCleanup(self.client.close)
        self.entrada = dict(descricao='Buraco no asfalto da rua de demonstração', bairro='Bairro fictício',
                            local='Rua Exemplo, número fictício 10', contexto='asfalto_comum', confirmado=True,
                            envio_id=str(uuid4()), localizacao=dict(latitude=-23.55, longitude=-46.63,
                            precisao_m=25, origem='manual', confirmado=True))
        imagem = Image.new('RGB', (40, 30), 'gray')
        exif = Image.Exif()
        exif[270] = 'metadado que nao deve permanecer'
        buf = io.BytesIO()
        imagem.save(buf, format='JPEG', exif=exif)
        self.foto = buf.getvalue()

    def enviar(self, entrada=None, foto=None, url='/api/atendimentos/com-anexo', method='POST', **extras):
        return self.client.request(method, url, data={'dados': json.dumps(entrada or self.entrada), **extras},
                                   files={'arquivo': ('../../nome.jpg', self.foto if foto is None else foto, 'image/jpeg')})

    def test_foto_fica_no_pedido_sem_exif_e_pode_ser_consultada(self):
        r = self.enviar()
        self.assertEqual(r.status_code, 201, r.text)
        caso = r.json()
        self.assertEqual(caso['preparacao']['servico']['id'], '952')
        self.assertEqual(caso['localizacao']['latitude'], -23.55)
        imagem = self.client.get(f'/api/atendimentos/{caso["id"]}/foto')
        self.assertEqual(imagem.status_code, 200)
        with Image.open(io.BytesIO(imagem.content)) as foto:
            self.assertFalse(foto.getexif())
            self.assertEqual(foto.size, (40, 30))
        self.assertEqual(caso['foto']['largura'], 40)
        self.assertNotIn('nome.jpg', json.dumps(caso))

    def test_reenvio_igual_nao_duplica_e_conteudo_diferente_conflita(self):
        primeiro = self.enviar()
        segundo = self.enviar()
        self.assertEqual(primeiro.status_code, 201)
        self.assertEqual(segundo.status_code, 201)
        self.assertEqual(primeiro.json()['id'], segundo.json()['id'])
        self.assertEqual(len(segundo.json()['historico']), 1)
        diferente = {**self.entrada, 'descricao': 'Outra ocorrência no asfalto da rua fictícia'}
        self.assertEqual(self.enviar(diferente).status_code, 409)
        self.assertEqual(len(self.client.get('/api/atendimentos').json()), 1)

    def test_coordenadas_invalidas_ou_nao_confirmadas_nao_registram(self):
        for campos in ({'latitude': 91}, {'longitude': -181}, {'latitude': 'NaN'}, {'confirmado': False},
                       {'origem': 'inferida'}, {'precisao_m': -1}):
            with self.subTest(campos=campos):
                entrada = {**self.entrada, 'localizacao': {**self.entrada['localizacao'], **campos}}
                self.assertEqual(self.enviar(entrada).status_code, 422)
        self.assertEqual(self.client.get('/api/atendimentos').json(), [])

    def test_arquivo_falso_nao_cria_pedido(self):
        self.assertEqual(self.enviar(foto=b'nao e imagem').status_code, 422)
        self.assertEqual(self.client.get('/api/atendimentos').json(), [])

    def test_cliente_nao_define_caminho_da_foto(self):
        entrada = {**self.entrada, 'foto': {'arquivo': '../chave-gestao.txt'}}
        self.assertEqual(self.enviar(entrada).status_code, 422)

    def test_edicao_antiga_preserva_foto_posicao_e_nova_remove_com_historico(self):
        r = self.enviar()
        self.assertEqual(r.status_code, 201, r.text)
        caso = r.json()
        url = '/api/atendimentos/' + caso['id']
        self.client.post(url + '/revisao', headers={'X-Manager-Key': 'chave-teste'},
                         json=dict(prioridade='Alta', justificativa='Conferência técnica do caso fictício.', revisor='Teste'))
        antiga = {k: self.entrada[k] for k in ('descricao', 'bairro', 'local', 'contexto', 'confirmado')}
        antiga['descricao'] += ' corrigido'
        editado = self.client.put(url, json=antiga).json()
        self.assertEqual(editado['foto'], caso['foto'])
        self.assertEqual(editado['localizacao'], caso['localizacao'])
        self.assertIsNone(editado['revisao'])
        removido = self.client.put(url + '/com-anexo', data={'dados': json.dumps({**antiga, 'localizacao': None}),
                                                          'remover_foto': 'true'}).json()
        self.assertIsNone(removido['foto'])
        self.assertIsNone(removido['localizacao'])
        self.assertEqual(removido['historico'][-1]['dados']['entrada_anterior']['foto'], caso['foto'])
        self.assertEqual(self.client.get(url + '/foto').status_code, 404)

    def test_pedido_sem_foto_e_sem_gps_continua_possivel(self):
        entrada = {**self.entrada, 'localizacao': None}
        r = self.client.post('/api/atendimentos/com-anexo', data={'dados': json.dumps(entrada)})
        self.assertEqual(r.status_code, 201, r.text)
        self.assertIsNone(r.json()['localizacao'])
        self.assertIsNone(r.json()['foto'])

    def test_nomes_de_arquivo_ou_ids_arbitrarios_nao_leem_dados(self):
        self.assertEqual(self.client.get('/api/atendimentos/chave-gestao.txt/foto').status_code, 404)

    def test_reimportacao_rpa_preserva_foto_e_posicao_enriquecidas(self):
        r = self.enviar({**self.entrada, 'origem_id': 'rpa:MOBILE-001'})
        self.assertEqual(r.status_code, 201)
        caso = r.json()
        dados = {k: caso[k] for k in ('descricao', 'bairro', 'triagem_original', 'preparacao', 'origem_id')}
        dados.update(descricao=caso['descricao'] + ' atualizado pelo lote', local='', contexto='nao_informado')
        novo = self.client.app.state.repo.criar(dados)
        self.assertEqual(novo['id'], caso['id'])
        self.assertEqual(novo['foto'], caso['foto'])
        self.assertEqual(novo['localizacao'], caso['localizacao'])
        self.assertEqual(novo['local'], caso['local'])

    def test_pwa_entrega_apenas_formulario_estatico(self):
        manifest = self.client.get('/web/manifest.webmanifest').json()
        self.assertEqual(manifest['start_url'], '/#pedido')
        for icone in manifest['icons']:
            self.assertEqual(self.client.get(icone['src']).status_code, 200)
        sw = self.client.get('/sw.js')
        self.assertEqual(sw.status_code, 200)
        self.assertIn('application/javascript', sw.headers['content-type'])

    def test_modelo_audio_publico_tem_cache_e_mime_wasm_sem_cachear_pedidos(self):
        wasm = self.client.head('/ouviai/wasm/audio_wasm_internal.wasm')
        self.assertEqual(wasm.status_code, 200)
        self.assertIn('application/wasm', wasm.headers['content-type'])
        self.assertIn('max-age=', wasm.headers['cache-control'])
        self.assertEqual(self.client.get('/api/atendimentos').headers['cache-control'], 'no-store')

    def test_mapa_e_fontes_sao_locais_e_politica_so_libera_tiles_em_imagem(self):
        for caminho in ('mapa.mjs', 'brand.svg', 'vendor/leaflet.js', 'vendor/leaflet.css', 'vendor/archivo-bold.ttf'):
            self.assertEqual(self.client.get('/web/' + caminho).status_code, 200)
        resposta = self.client.get('/')
        csp = resposta.headers['content-security-policy']
        self.assertIn("script-src 'self'", csp)
        self.assertIn("img-src 'self' data: blob: https://tile.openstreetmap.org", csp)
        self.assertNotIn('unsafe-inline', csp)
        self.assertEqual(resposta.headers['referrer-policy'], 'strict-origin-when-cross-origin')

    def test_fluxo_foto_ponto_revisao_confirmacao_contestacao_e_nova_revisao(self):
        caso = self.enviar().json()
        url = '/api/atendimentos/' + caso['id']
        chave = {'X-Manager-Key': 'chave-teste'}
        self.assertEqual(self.client.post(url+'/zelabairro', headers=chave).status_code, 409)
        revisao = dict(prioridade='Alta', justificativa='Barreira de passagem no cenário fictício.', revisor='Teste técnico')
        self.assertEqual(self.client.post(url+'/revisao', headers=chave, json=revisao).status_code, 200)
        confirmado = self.client.post(url+'/zelabairro', headers=chave)
        self.assertEqual(confirmado.status_code, 200, confirmado.text)
        self.assertTrue(confirmado.json()['frontend']['id'])
        contestado = self.client.post(url+'/contestacao', json={'motivo':'O registro fictício precisa de nova avaliação.'}).json()
        self.assertIsNone(contestado['revisao'])
        self.assertIsNone(contestado.get('frontend'))
        self.assertEqual(self.client.post(url+'/zelabairro', headers=chave).status_code, 409)
        self.assertEqual(self.client.post(url+'/revisao', headers=chave, json=revisao).status_code, 200)
        atual = self.client.get(url).json()
        self.assertEqual(atual['foto'], caso['foto'])
        self.assertEqual(atual['localizacao'], caso['localizacao'])
        self.assertEqual(len(atual['historico']), 5)

    def test_reenvio_apos_revisao_devolve_estado_atual_sem_novo_evento(self):
        caso = self.enviar().json()
        self.client.post('/api/atendimentos/' + caso['id'] + '/revisao', headers={'X-Manager-Key':'chave-teste'},
                         json=dict(prioridade='Alta', justificativa='Revisão do cenário de demonstração.', revisor='Teste'))
        repetido = self.enviar().json()
        self.assertEqual(repetido['id'], caso['id'])
        self.assertEqual(repetido['revisao']['prioridade'], 'Alta')
        self.assertEqual(len(repetido['historico']), 2)


if __name__ == '__main__':
    unittest.main()
