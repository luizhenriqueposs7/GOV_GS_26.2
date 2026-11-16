import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient
from PIL import Image


class AtendimentoTest(unittest.TestCase):
    def setUp(self):
        from central.app import criar_app
        self.pasta = tempfile.TemporaryDirectory()
        self.addCleanup(self.pasta.cleanup)
        ambiente = patch.dict('os.environ', {'GOV_MANAGER_KEY': 'gestor-teste'})
        ambiente.start()
        self.addCleanup(ambiente.stop)
        self.app = criar_app(Path(self.pasta.name))
        self.client = TestClient(self.app)
        self.addCleanup(self.client.close)
        self.chave = {'X-Manager-Key': 'gestor-teste'}
        self.dados = dict(descricao='Buraco prejudica a passagem na calçada da praça.', bairro='Cenário de teste',
                          local='Praça fictícia, 10', contexto='area_publica', confirmado=True,
                          passagem=dict(percurso_id='ponto-ubs-demo', trecho_id='calcada', condicao='bloqueado'))
        self.caso = self.client.post('/api/atendimentos', json=self.dados).json()
        self.url = '/api/atendimentos/' + self.caso['id']

    def revisar(self):
        r = self.client.post(self.url + '/revisao', headers=self.chave,
                             json=dict(prioridade='Alta', justificativa='Conferido o pedido do cenário.', revisor='Grupo'))
        self.assertEqual(r.status_code, 200, r.text)
        r = self.client.post(self.url + '/zelabairro', headers=self.chave, json={})
        self.assertEqual(r.status_code, 200, r.text)

    def protocolo(self):
        r = self.client.post(self.url + '/protocolo', json=dict(protocolo='SIM-001', demonstracao=True))
        self.assertEqual(r.status_code, 200, r.text)
        return r.json()

    def retorno(self, cor='green', relato='Superfície regularizada neste cenário de demonstração.'):
        foto = io.BytesIO()
        Image.new('RGB', (60, 40), cor).save(foto, 'JPEG')
        return self.client.post(self.url + '/retorno', data=dict(etapa='correcao_informada', relato=relato),
                                files={'arquivo': ('depois.jpg', foto.getvalue(), 'image/jpeg')})

    def verificar(self, chave=True):
        return self.client.post(self.url + '/verificar-correcao', headers=self.chave if chave else {},
            json=dict(base=self.client.get(self.url).json()['atualizado_em'], revisor='Grupo', justificativa='Foto posterior e contexto conferidos no cenário.', confirmado=True))

    def test_ciclo_demonstra_encaminhamento_sem_fingir_recebimento_oficial(self):
        self.revisar()
        caso = self.protocolo()
        self.assertIsNone(caso['protocolo_oficial'])
        self.assertTrue(caso['atendimento']['demonstracao'])
        ficha = self.client.get(self.url + '/ficha')
        self.assertEqual(ficha.status_code, 200)
        self.assertIn('DEMONSTRAÇÃO', ficha.text)
        self.assertIn('Secretaria Municipal das Subprefeituras', ficha.text)
        self.assertIn('não comprova recebimento', ficha.text)
        self.assertEqual(self.verificar().status_code, 422)
        self.assertEqual(self.retorno().status_code, 200)
        self.assertEqual(self.verificar(chave=False).status_code, 401)
        base = self.client.get('/api/passagem').json()['base']
        caso = self.verificar().json()
        self.assertEqual(caso['atendimento']['etapa'], 'correcao_verificada')
        self.assertFalse(caso['atendimento']['protocolo']['verificado_no_orgao'])
        percurso = self.client.get('/api/passagem').json()
        self.assertNotEqual(base, percurso['base'])
        self.assertEqual(percurso['atual']['barreiras'], 0)
        self.assertEqual(percurso['atual']['estado'], 'incerto')
        repetido = self.protocolo()
        self.assertEqual(repetido['atendimento']['etapa'], 'correcao_verificada')
        self.assertEqual(self.retorno().status_code, 422)
        reaberto = self.client.post(self.url + '/contestacao', json=dict(motivo='A passagem permanece bloqueada no cenário.')).json()
        self.assertEqual(reaberto['atendimento']['etapa'], 'reaberto')
        self.assertNotIn('conferencia', reaberto['atendimento'])
        self.assertEqual(self.client.get('/api/passagem').json()['atual']['barreiras'], 1)
        self.assertTrue(any(e['dados'].get('atendimento_anterior', {}).get('conferencia') for e in reaberto['historico']))

    def test_retorno_exige_protocolo_e_foto_nova_sem_poder_forjar_conferencia(self):
        self.assertEqual(self.retorno().status_code, 422)
        self.protocolo()
        self.assertEqual(self.client.post(self.url + '/retorno', data=dict(etapa='correcao_informada', relato='Retorno sem foto posterior.')).status_code, 422)
        self.assertEqual(self.client.post(self.url + '/retorno', data=dict(etapa='correcao_verificada', relato='Tentativa de encerrar pela API pública.')).status_code, 422)
        self.assertEqual(self.retorno().status_code, 200)
        self.assertEqual(self.verificar().status_code, 422)

    def test_alteracao_do_pedido_invalida_correcao_e_preserva_historico(self):
        self.revisar(); self.protocolo(); self.retorno(); self.verificar()
        r = self.client.put(self.url, json={**self.dados, 'local': 'Outro ponto fictício, 20'})
        self.assertEqual(r.status_code, 200, r.text)
        self.assertEqual(r.json()['atendimento']['etapa'], 'reaberto')
        self.assertEqual(self.client.get('/api/passagem').json()['atual']['barreiras'], 1)

    def test_protocolo_real_continua_declarado_e_contadores_separam_demonstracao(self):
        self.protocolo()
        metricas = self.client.get('/api/indicadores').json()
        self.assertEqual(metricas['protocolos_informados'], 0)
        self.assertEqual(metricas['protocolos_demonstracao'], 1)
        r = self.client.post(self.url + '/protocolo', json=dict(protocolo='2026-EXEMPLO'))
        self.assertEqual(r.status_code, 422)

    def test_foto_inicial_nao_e_aceita_como_prova_de_correcao(self):
        foto = io.BytesIO()
        Image.new('RGB', (60, 40), 'green').save(foto, 'JPEG')
        r = self.client.put(self.url + '/com-anexo', data={'dados': json.dumps(self.dados)},
                            files={'arquivo': ('antes.jpg', foto.getvalue(), 'image/jpeg')})
        self.assertEqual(r.status_code, 200, r.text)
        self.protocolo()
        self.assertEqual(self.retorno().status_code, 422)
        self.assertNotIn('retorno', self.client.get(self.url).json()['atendimento'])

    def test_nova_revisao_reabre_correcao_e_outro_pedido_mantem_barreira(self):
        self.revisar(); self.protocolo(); self.retorno(); self.verificar()
        self.client.post('/api/atendimentos', json={**self.dados, 'descricao': 'Outro obstáculo no mesmo trecho fictício.'})
        self.assertEqual(self.client.get('/api/passagem').json()['atual']['barreiras'], 1)
        self.revisar()
        self.assertEqual(self.client.get(self.url).json()['atendimento']['etapa'], 'reaberto')

    def test_protocolo_legado_inicia_acompanhamento_com_o_mesmo_numero(self):
        repo = self.app.state.repo
        with repo.conexao() as con:
            caso = repo._obter(con, self.caso['id'])
            caso['protocolo_oficial'] = {'numero': 'ANTERIOR-001', 'verificado_no_orgao': False}
            repo._salvar(con, caso, 'Fixture da versão anterior', {})
        r = self.client.post(self.url + '/protocolo', json={'protocolo': 'ANTERIOR-001'})
        self.assertEqual(r.status_code, 200, r.text)
        self.assertEqual(r.json()['atendimento']['etapa'], 'protocolo_informado')

    def test_foto_substituida_exige_nova_conferencia(self):
        self.revisar(); self.protocolo(); self.retorno()
        base = self.client.get(self.url).json()['atualizado_em']
        self.retorno('blue', 'Outra evidência posterior, recebida durante a conferência.')
        r = self.client.post(self.url + '/verificar-correcao', headers=self.chave, json=dict(
            base=base, revisor='Grupo', justificativa='Conferência da foto anterior, agora desatualizada.', confirmado=True))
        self.assertEqual(r.status_code, 409, r.text)
        self.assertEqual(self.client.get(self.url).json()['atendimento']['etapa'], 'correcao_informada')
