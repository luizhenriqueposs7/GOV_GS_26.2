import importlib
import itertools
import json
import math
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

import numpy as np


def caso(identificador, criado_em='2026-11-17T10:00:00+00:00'):
    return {'id': identificador, 'descricao': f'Pedido de teste {identificador}',
            'bairro': 'Bairro de teste', 'origem_id': f'rpa:{identificador}',
            'criado_em': criado_em, 'atualizado_em': criado_em, 'revisao': None,
            'triagem_original': {'priority': 'Baixa', 'confidence': 0.2},
            'exige_revisao': True}


def item(identificador, minutos=3, prioridade='Média', obrigatorio=False):
    return {'id': identificador, 'minutos': minutos, 'prioridade': prioridade,
            'obrigatorio': obrigatorio}


class QuanticaTest(unittest.TestCase):
    def setUp(self):
        try:
            self.quantica = importlib.import_module('central.quantica')
        except ModuleNotFoundError:
            self.fail('O simulador operacional ainda não foi implementado.')
        self.casos = [caso('a'), caso('b'), caso('c'), caso('d')]

    def test_evolucao_aplica_fase_e_mixer_com_a_ordem_e_angulo_corretos(self):
        estado = self.quantica.evoluir(np.array([0., 1.]), math.pi / 2, math.pi / 4)
        np.testing.assert_allclose(abs(estado) ** 2, [0., 1.], atol=1e-12)

    def test_evolucao_preserva_norma_e_identidade_para_ate_oito_qubits(self):
        for n in (1, 3, 8):
            energias = np.arange(2 ** n, dtype=float) ** 2
            uniforme = np.full(2 ** n, 1 / math.sqrt(2 ** n), dtype=complex)
            with self.subTest(n=n):
                np.testing.assert_allclose(self.quantica.evoluir(energias, 0, 0), uniforme)
                estado = self.quantica.evoluir(energias, 0.137, 0.328)
                self.assertAlmostEqual(float(np.vdot(estado, estado).real), 1.)

    def test_evolucao_rejeita_energias_e_parametros_invalidos(self):
        for energias, gamma, beta in (([], 0, 0), ([0, 1, 2], 0, 0),
                                     ([[0, 1]], 0, 0), ([0, float('nan')], 0, 0),
                                     ([0, 1j], 0, 0), ([0, 1e308], 1e308, 0),
                                     ([0, 1], float('inf'), 0), ([0, 1], 0, float('nan'))):
            with self.subTest(energias=energias, gamma=gamma, beta=beta), self.assertRaises(ValueError):
                self.quantica.evoluir(np.array(energias), gamma, beta)

    def test_compara_fila_gulosa_exato_e_qaoa_sem_sumir_pedidos(self):
        itens = [item('a', 4, 'Alta'), item('b', 3, 'Média'), item('c', 3, 'Média')]
        original = deepcopy((self.casos, itens))
        resultado = self.quantica.simular(self.casos, itens, 6)
        self.assertEqual(resultado['capacidade'], 6)
        self.assertEqual(resultado['pendentes_total'], 4)
        self.assertEqual(resultado['fora_do_recorte_ids'], ['d'])
        self.assertEqual(resultado['metodos']['fila']['selecionados'], ['a'])
        self.assertEqual(resultado['metodos']['classico']['selecionados'], ['b', 'c'])
        self.assertEqual(resultado['metodos']['classico']['beneficio'], 4)
        self.assertEqual((self.casos, itens), original)
        for metodo in resultado['metodos'].values():
            self.assertLessEqual(metodo['minutos'], 6)
            self.assertEqual(set(metodo['selecionados']) | set(metodo['adiados']), {'a', 'b', 'c'})
            self.assertFalse(set(metodo['selecionados']) & set(metodo['adiados']))
            self.assertLessEqual(metodo['beneficio'], 4)
            self.assertEqual(len(metodo['bitstring']), 3)
        self.assertEqual(resultado['itens'][0]['prioridade'], 'Alta')
        self.assertEqual(resultado['itens'][0]['origem_id'], 'rpa:a')
        self.assertEqual(resultado['itens'][0]['descricao'], self.casos[0]['descricao'])
        self.assertEqual(resultado['itens'][0]['bairro'], 'Bairro de teste')
        json.dumps(resultado, allow_nan=False)

    def test_fila_respeita_prioridade_conferida_antiguidade_e_obrigatorios(self):
        self.casos[1]['criado_em'] = '2026-11-16T10:00:00+00:00'
        itens = [item('a'), item('b'), item('c', 2, 'Baixa', True)]
        fila = self.quantica.simular(self.casos, itens, 5)['metodos']['fila']
        self.assertEqual(set(fila['selecionados']), {'b', 'c'})
        self.assertEqual(fila['adiados'], ['a'])

    def test_exato_concorda_com_enumeracao_independente_em_recortes_pequenos(self):
        pesos = {'Baixa': 1, 'Média': 2, 'Alta': 3}
        itens = [item('a', 4, 'Alta'), item('b', 2, 'Baixa', True), item('c', 3, 'Média'), item('d', 1, 'Alta')]
        for capacidade in (2, 3, 5, 8, 10):
            candidatos = [(bits, sum(i['minutos'] for i, b in zip(itens, bits) if b),
                           sum(pesos[i['prioridade']] for i, b in zip(itens, bits) if b))
                          for bits in itertools.product((0, 1), repeat=len(itens))
                          if all(b or not i['obrigatorio'] for i, b in zip(itens, bits))]
            melhor = max(beneficio for _, minutos, beneficio in candidatos if minutos <= capacidade)
            with self.subTest(capacidade=capacidade):
                metodos = self.quantica.simular(self.casos, itens, capacidade)['metodos']
                self.assertEqual(metodos['classico']['beneficio'], melhor)
                for metodo in metodos.values():
                    self.assertIn('b', metodo['selecionados'])
                    self.assertLessEqual(metodo['minutos'], capacidade)
                    self.assertLessEqual(metodo['beneficio'], melhor)

    def test_qaoa_informa_probabilidades_do_estado_e_escolhe_o_factivel_mais_provavel(self):
        itens = [item('a', 4, 'Alta'), item('b', 3, 'Média'), item('c', 3, 'Baixa', True)]
        saida = self.quantica.simular(self.casos, itens, 6)
        qaoa = saida['metodos']['qaoa']
        # Diagonal calculada aqui a partir do problema, sem reutilizar o Hamiltoniano da implementação.
        estados = list(itertools.product((0, 1), repeat=3))
        energias = np.array([-3*a - 2*b - c + 7*max(0, 4*a + 3*b + 3*c - 6)**2 + 7*(1-c)
                             for a, b, c in estados])
        estado = self.quantica.evoluir(energias, qaoa['parametros']['gamma'], qaoa['parametros']['beta'])
        probabilidades = abs(estado) ** 2
        viaveis = [j for j, (a, b, c) in enumerate(estados) if c and 4*a+3*b+3*c <= 6]
        escolhido = int(qaoa['bitstring'], 2)
        self.assertIn(escolhido, viaveis)
        self.assertAlmostEqual(qaoa['probabilidade'], float(probabilidades[escolhido]))
        self.assertAlmostEqual(qaoa['probabilidade'], max(float(probabilidades[j]) for j in viaveis))
        self.assertAlmostEqual(qaoa['probabilidade_viavel'], float(sum(probabilidades[j] for j in viaveis)))
        self.assertAlmostEqual(qaoa['energia_esperada'], float(probabilidades @ energias))
        self.assertEqual(qaoa['p'], 1)
        self.assertEqual(qaoa['estados'], 8)
        self.assertGreaterEqual(qaoa['runtime_ms'], 0)
        self.assertEqual(len(qaoa['top5_probabilidades']), 5)
        for registro in qaoa['top5_probabilidades']:
            self.assertAlmostEqual(registro['probabilidade'], float(probabilidades[int(registro['bitstring'], 2)]))

    def test_prioridade_nao_e_inferida_do_bairro_deficiencia_ou_triagem(self):
        itens = [item('a', prioridade='Baixa'), item('b', prioridade='Alta')]
        self.casos[0].update(descricao='Urgência de pessoa idosa com deficiência', bairro='Centro',
                            triagem_original={'priority': 'Alta', 'confidence': 1.0})
        resultado = self.quantica.simular(self.casos, itens, 3)
        self.assertEqual(resultado['metodos']['fila']['selecionados'], ['b'])
        self.assertEqual([i['beneficio'] for i in resultado['itens']], [1, 3])

    def test_revisados_ficam_fora_dos_pendentes_e_nao_podem_entrar_no_recorte(self):
        self.casos[0]['revisao'] = {'prioridade': 'Alta'}
        resultado = self.quantica.simular(self.casos, [item('b')], 3)
        self.assertEqual(resultado['pendentes_total'], 3)
        self.assertEqual(resultado['fora_do_recorte_ids'], ['c', 'd'])
        with self.assertRaisesRegex(ValueError, '[Rr]evis|pendente'):
            self.quantica.simular(self.casos, [item('a')], 3)

    def test_rejeita_zeros_limites_tipos_nao_inteiros_e_campos_ausentes(self):
        for alteracao in ({'minutos': 0}, {'minutos': 241}, {'minutos': -1}, {'minutos': 1.5},
                          {'minutos': float('inf')}, {'minutos': float('nan')}, {'minutos': True},
                          {'prioridade': 'Urgente'}, {'prioridade': None}, {'obrigatorio': 1}, {'id': ''}):
            with self.subTest(alteracao=alteracao), self.assertRaises(ValueError):
                self.quantica.simular(self.casos, [{**item('a'), **alteracao}], 3)
        for capacidade in (0, 481, -1, 3.5, True, float('inf'), float('nan'), '3'):
            with self.subTest(capacidade=capacidade), self.assertRaises(ValueError):
                self.quantica.simular(self.casos, [item('a')], capacidade)
        for chave in ('id', 'minutos', 'prioridade', 'obrigatorio'):
            incompleto = item('a')
            del incompleto[chave]
            with self.subTest(chave=chave), self.assertRaises(ValueError):
                self.quantica.simular(self.casos, [incompleto], 3)

    def test_rejeita_recorte_vazio_mais_de_oito_ids_invalidos_e_repetidos(self):
        for itens in ([], [item('inexistente')], [item('a'), item('a')], [None], None):
            with self.subTest(itens=itens), self.assertRaises(ValueError):
                self.quantica.simular(self.casos, itens, 3)
        nove = [caso(str(i)) for i in range(9)]
        with self.assertRaises(ValueError):
            self.quantica.simular(nove, [item(str(i)) for i in range(9)], 30)

    def test_capacidade_insuficiente_nao_adia_obrigatorio_nem_aceita_recorte_impossivel(self):
        with self.assertRaisesRegex(ValueError, '[Oo]brigat'):
            self.quantica.simular(self.casos, [item('a', 4, obrigatorio=True), item('b', 3, obrigatorio=True)], 6)
        with self.assertRaisesRegex(ValueError, 'cab|capacidade'):
            self.quantica.simular(self.casos, [item('a', 4), item('b', 5)], 3)
        for metodo in self.quantica.simular(self.casos, [item('a', 3, obrigatorio=True)], 3)['metodos'].values():
            self.assertEqual(metodo['selecionados'], ['a'])
            self.assertEqual(metodo['minutos'], 3)

    def test_aceita_oito_pedidos_e_limites_superiores_sem_nan(self):
        casos = [caso(str(i)) for i in range(8)]
        resultado = self.quantica.simular(casos, [item(str(i), 240) for i in range(8)], 480)
        self.assertEqual(resultado['metodos']['qaoa']['estados'], 256)
        self.assertEqual(resultado['metodos']['classico']['minutos'], 480)
        json.dumps(resultado, allow_nan=False)

    def test_base_usa_casos_e_entradas_e_nao_evidencias_ou_ordem_da_consulta(self):
        itens = [item('a')]
        base = self.quantica.simular(self.casos, itens, 3)['base']
        self.assertEqual(len(base), 64)
        self.assertEqual(base, self.quantica.simular(self.casos[::-1], itens, 3)['base'])
        self.casos[0]['evidencias'] = [{'modulo': 'quantica'}]
        self.casos[0]['historico'] = [{'acao': 'Plano registrado'}]
        self.assertEqual(base, self.quantica.simular(self.casos, itens, 3)['base'])
        for campo, valor in (('descricao', 'Relato alterado'), ('atualizado_em', '2026-11-17T11:00:00+00:00'),
                             ('triagem_original', {'priority': 'Alta'})):
            alterados = deepcopy(self.casos)
            alterados[0][campo] = valor
            with self.subTest(campo=campo):
                self.assertNotEqual(base, self.quantica.simular(alterados, itens, 3)['base'])
        for novos_itens, capacidade in (([item('a', prioridade='Alta')], 3), (itens, 4),
                                        ([item('a', 2)], 3), ([item('a', obrigatorio=True)], 3)):
            self.assertNotEqual(base, self.quantica.simular(self.casos, novos_itens, capacidade)['base'])

    def test_base_muda_apos_atualizacao_real_do_repositorio(self):
        from central.registros import Repositorio
        with tempfile.TemporaryDirectory() as pasta:
            repo = Repositorio(Path(pasta) / 'casos.sqlite')
            dados = {'descricao': 'Buraco no passeio da praça de teste', 'bairro': 'Bairro de teste',
                     'triagem_original': {'priority': 'Baixa'}, 'preparacao': {'faltantes': []}}
            criado = repo.criar(dados)
            itens = [item(criado['id'])]
            base = self.quantica.simular(repo.listar(), itens, 3)['base']
            repo.atualizar(criado['id'], {'descricao': 'Buraco maior no passeio da praça de teste'})
            self.assertNotEqual(base, self.quantica.simular(repo.listar(), itens, 3)['base'])


if __name__ == '__main__':
    unittest.main()
