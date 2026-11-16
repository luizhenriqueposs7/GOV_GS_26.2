import json
import hashlib
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch
from uuid import uuid4

from fastapi.testclient import TestClient

from central.passagem import avaliar, validar_vinculo


def pedido(identificador, trecho, condicao='bloqueado'):
    return {'id': identificador, 'descricao': 'Barreira de demonstração',
            'passagem': {'percurso_id': 'ponto-ubs-demo', 'trecho_id': trecho, 'condicao': condicao},
            'revisao': None}


class PlanejamentoTest(unittest.TestCase):
    def setUp(self):
        self.casos = [pedido('a', 'calcada'), pedido('b', 'rampa')]

    def test_duas_intervencoes_precisam_acontecer_juntas(self):
        original = deepcopy(self.casos)
        for reparos, estado, barreiras in [([], 'interrompido', 2), (['calcada'], 'interrompido', 1),
                                           (['rampa'], 'interrompido', 1),
                                           (['calcada', 'rampa'], 'sem_barreiras_informadas', 0)]:
            with self.subTest(reparos=reparos):
                saida = avaliar(self.casos, reparos)
                self.assertEqual(saida['atual']['barreiras'], 2)
                self.assertEqual(saida['simulado']['estado'], estado)
                self.assertEqual(saida['simulado']['barreiras'], barreiras)
        self.assertEqual(self.casos, original)

    def test_desconhecido_nao_vira_livre_por_reparo(self):
        for casos in ([], [pedido('a', 'calcada', 'nao_verificado')],
                      self.casos + [pedido('c', 'rampa', 'nao_verificado')]):
            with self.subTest(casos=casos):
                saida = avaliar(casos, ['calcada', 'rampa'])
                self.assertEqual(saida['simulado']['estado'], 'incerto')
                self.assertGreater(saida['simulado']['desconhecidos'], 0)

    def test_multiplos_relatos_contam_um_trecho_e_nao_sumem(self):
        saida = avaliar(self.casos + [pedido('c', 'calcada', 'dificultado')], ['calcada'])
        self.assertEqual(saida['atual']['barreiras'], 2)
        self.assertEqual(len(saida['trechos'][1]['pedidos']), 2)
        self.assertEqual(saida['simulado']['barreiras'], 1)

    def test_relato_desconhecido_continua_visivel_ao_lado_de_barreira(self):
        saida = avaliar(self.casos + [pedido('c', 'calcada', 'nao_verificado')], ['calcada', 'rampa'])
        self.assertEqual(saida['atual']['desconhecidos'], 1)
        self.assertEqual(saida['simulado']['desconhecidos'], 1)
        self.assertTrue(saida['trechos'][1]['tem_condicao_desconhecida'])

    def test_base_independe_da_ordem_e_muda_com_evidencia_ou_revisao(self):
        base = avaliar(self.casos, [])['base']
        self.assertEqual(base, avaliar(self.casos[::-1], ['rampa'])['base'])
        self.casos[0]['evidencias'] = [{'modulo': 'pln', 'resultado': 'Trecho vinculado'}]
        self.assertNotEqual(base, avaliar(self.casos, [])['base'])

    def test_correcao_nao_remove_condicao_desconhecida(self):
        desconhecido = pedido('x', 'acesso', 'nao_verificado')
        desconhecido['atendimento'] = {'etapa': 'correcao_verificada', 'demonstracao': True}
        resultado = avaliar([desconhecido], [])
        self.assertEqual(resultado['trechos'][0]['atual'], 'nao_verificado')
        self.assertEqual(resultado['atual']['desconhecidos'], 3)

    def test_vinculo_opcional_e_valores_invalidos(self):
        self.assertIsNone(validar_vinculo(None))
        valido = self.casos[0]['passagem']
        self.assertEqual(validar_vinculo(valido), valido)
        for alteracao in ({'percurso_id': 'inventado'}, {'trecho_id': 'rua-inexistente'},
                          {'condicao': 'livre'}, {'extra': 'campo'}):
            with self.subTest(alteracao=alteracao), self.assertRaises(ValueError):
                validar_vinculo({**valido, **alteracao})
        with self.assertRaises(ValueError):
            avaliar(self.casos, ['trecho-inexistente'])
        with self.assertRaises(ValueError):
            avaliar(self.casos, ['rampa', 'rampa'])


class PassagemAPITest(unittest.TestCase):
    def setUp(self):
        from central.app import criar_app
        self.pasta = tempfile.TemporaryDirectory()
        self.addCleanup(self.pasta.cleanup)
        ambiente = patch.dict('os.environ', {'GOV_MANAGER_KEY': 'chave-passagem-teste'})
        ambiente.start()
        self.addCleanup(ambiente.stop)
        self.app = criar_app(Path(self.pasta.name))
        self.client = TestClient(self.app)
        self.addCleanup(self.client.close)
        self.chave = {'X-Manager-Key': 'chave-passagem-teste'}

    def preparar(self):
        resposta = self.client.post('/api/passagem/demonstracao', headers=self.chave)
        self.assertEqual(resposta.status_code, 200, resposta.text)
        return self.client.get('/api/atendimentos').json()

    def revisar(self, casos):
        for caso in casos:
            resposta = self.client.post('/api/atendimentos/' + caso['id'] + '/revisao', headers=self.chave,
                json={'prioridade': 'Alta', 'revisor': 'Revisor do cenário',
                      'justificativa': 'A barreira interrompe o percurso didático até a unidade de saúde.'})
            self.assertEqual(resposta.status_code, 200, resposta.text)

    def plano(self):
        resultado = self.client.post('/api/passagem/simular', json={'reparos': ['calcada', 'rampa']}).json()
        return {'base': resultado['base'], 'reparos': ['calcada', 'rampa'], 'revisor': 'Revisor do cenário',
                'justificativa': 'Os dois trechos precisam ser tratados para completar a ligação no cenário.'}

    def test_seed_protegido_idempotente_e_sem_restaurar_contestacao(self):
        self.assertEqual(self.client.post('/api/passagem/demonstracao').status_code, 401)
        casos = self.preparar()
        self.assertEqual(len(casos), 2)
        self.assertTrue(all(c['triagem_original']['category'] for c in casos))
        self.assertTrue(all(c['exige_revisao'] for c in casos))
        self.client.post('/api/atendimentos/' + casos[0]['id'] + '/contestacao',
                         json={'motivo': 'O contexto precisa ser conferido novamente.'})
        de_novo = self.preparar()
        self.assertEqual({c['id'] for c in casos}, {c['id'] for c in de_novo})
        caso = self.client.get('/api/atendimentos/' + casos[0]['id']).json()
        self.assertEqual(len(caso['historico']), 2)
        self.assertEqual(caso['situacao'], 'Nova revisão solicitada')

    def test_plano_exige_chave_revisao_e_base_atual(self):
        casos = self.preparar()
        entrada = self.plano()
        self.assertEqual(self.client.post('/api/passagem/planos', json=entrada).status_code, 401)
        self.assertEqual(self.client.post('/api/passagem/planos', json=entrada, headers=self.chave).status_code, 409)
        self.revisar(casos)
        self.assertEqual(self.client.post('/api/passagem/planos', json=entrada, headers=self.chave).status_code, 409)
        entrada = self.plano()
        resposta = self.client.post('/api/passagem/planos', json=entrada, headers=self.chave)
        self.assertEqual(resposta.status_code, 201, resposta.text)
        plano = resposta.json()
        self.assertEqual(plano['resultado']['simulado']['estado'], 'sem_barreiras_informadas')
        self.assertFalse(self.client.get('/api/passagem').json()['planos'][0]['desatualizado'])
        self.client.post('/api/atendimentos/' + casos[0]['id'] + '/contestacao',
                         json={'motivo': 'A rampa continua obstruída e deve ser reavaliada.'})
        atual = self.client.get('/api/passagem').json()
        self.assertTrue(atual['planos'][0]['desatualizado'])
        self.assertEqual(atual['atual']['barreiras'], 2)
        self.assertEqual(atual['planos'][0]['id'], plano['id'])
        self.assertEqual(self.client.post('/api/passagem/planos', json=self.plano(), headers=self.chave).status_code, 409)

    def test_formulario_anexo_edicao_desvinculo_e_validacao(self):
        entrada = {'descricao': 'Calçada de demonstração com passagem dificultada', 'bairro': 'Bairro de teste',
                   'local': 'Praça de demonstração', 'contexto': 'area_publica', 'confirmado': True,
                   'passagem': pedido('x', 'calcada')['passagem']}
        resposta = self.client.post('/api/atendimentos/com-anexo', data={'dados': json.dumps(entrada)})
        self.assertEqual(resposta.status_code, 201, resposta.text)
        caso = resposta.json()
        self.assertEqual(caso['passagem'], entrada['passagem'])
        self.revisar([caso])
        alterado = self.client.put('/api/atendimentos/' + caso['id'], json={**entrada, 'passagem': None}).json()
        self.assertIsNone(alterado['passagem'])
        self.assertIsNone(alterado['revisao'])
        self.assertEqual(self.client.get('/api/passagem').json()['atual']['desconhecidos'], 2)
        for alteracao in ({'trecho_id': 'inválido'}, {'condicao': 'livre'}):
            self.assertEqual(self.client.post('/api/atendimentos', json={**entrada,
                'passagem': {**entrada['passagem'], **alteracao}}).status_code, 422)
        self.assertEqual(len(self.client.get('/api/atendimentos').json()), 1)
        self.assertEqual(self.client.post('/api/passagem/simular', json={'reparos': ['inválido']}).status_code, 422)
        self.assertEqual(self.client.post('/api/passagem/simular', json={'reparos': [], 'resultado': {}}).status_code, 422)

    def test_reenvio_anterior_a_passagem_reutiliza_pedido_sem_novo_evento(self):
        entrada = {'descricao': 'Calçada danificada em praça de demonstração', 'bairro': 'Bairro de teste',
                   'local': 'Praça de teste', 'contexto': 'area_publica', 'confirmado': True, 'envio_id': str(uuid4())}
        caso = self.client.post('/api/atendimentos', json=entrada).json()
        campos_antigos = ('descricao', 'bairro', 'local', 'contexto', 'triagem_original', 'preparacao',
                          'origem_id', 'foto', 'localizacao')
        assinatura_antiga = hashlib.sha256(json.dumps({k: caso.get(k) for k in campos_antigos},
                                         sort_keys=True, ensure_ascii=False).encode()).hexdigest()
        with self.app.state.repo.conexao() as con:
            con.execute('UPDATE envios SET assinatura = ? WHERE id = ?', (assinatura_antiga, entrada['envio_id']))
        resposta = self.client.post('/api/atendimentos', json={**entrada, 'passagem': None})
        self.assertEqual(resposta.status_code, 201, resposta.text)
        self.assertEqual(resposta.json()['id'], caso['id'])
        self.assertEqual(len(resposta.json()['historico']), 1)


if __name__ == '__main__':
    unittest.main()
