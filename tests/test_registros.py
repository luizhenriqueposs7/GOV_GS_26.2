import tempfile
import unittest
from pathlib import Path


class RegistrosTest(unittest.TestCase):
    def setUp(self):
        self.pasta = tempfile.TemporaryDirectory()
        self.addCleanup(self.pasta.cleanup)
        try:
            from central.registros import Repositorio
        except ModuleNotFoundError:
            self.fail("O registro de decisões ainda não foi implementado.")
        self.repo = Repositorio(Path(self.pasta.name) / "casos.sqlite")

    def dados(self, origem=None):
        return {
            "descricao": "Calçada sem rampa acessível", "bairro": "Bairro fictício",
            "local": "Praça de demonstração", "contexto": "nao_informado",
            "triagem_original": {"category": "Acessibilidade", "priority": "Baixa", "confidence": 1.0, "review_required": False},
            "preparacao": {"faltantes": ["contexto"], "fonte": None}, "origem_id": origem,
        }

    def test_controle_novo_preserva_a_saida_original(self):
        caso = self.repo.criar(self.dados())
        self.assertTrue(caso["exige_revisao"])
        self.assertFalse(caso["triagem_original"]["review_required"])
        self.assertEqual(caso["triagem_original"]["priority"], "Baixa")

    def test_revisao_nao_apaga_a_sugestao_e_tem_historico(self):
        caso = self.repo.criar(self.dados())
        revisado = self.repo.revisar(caso["id"], "Média", "Barreira exige avaliação do responsável.", "Revisor da demonstração")
        self.assertEqual(revisado["revisao"]["prioridade"], "Média")
        self.assertEqual(revisado["triagem_original"]["priority"], "Baixa")
        self.assertEqual(len(revisado["historico"]), 2)

    def test_justificativa_vazia_nao_registra_decisao(self):
        caso = self.repo.criar(self.dados())
        with self.assertRaises(ValueError):
            self.repo.revisar(caso["id"], "Alta", " ", "Revisor")
        self.assertIsNone(self.repo.obter(caso["id"])["revisao"])

    def test_contestacao_reabre_a_revisao(self):
        caso = self.repo.criar(self.dados())
        self.repo.revisar(caso["id"], "Média", "Revisão do cenário sintético.", "Revisor")
        contestado = self.repo.contestar(caso["id"], "Ainda falta analisar a alternativa de passagem.")
        self.assertIsNone(contestado["revisao"])
        self.assertTrue(contestado["exige_revisao"])
        self.assertEqual(self.repo.indicadores()["revisoes_pendentes"], 1)

    def test_protocolo_informado_nao_e_confirmacao_do_orgao(self):
        caso = self.repo.criar(self.dados())
        atualizado = self.repo.informar_protocolo(caso["id"], "EXEMPLO-123")
        self.assertEqual(atualizado["protocolo_oficial"]["origem"], "Informado pelo usuário")
        self.assertFalse(atualizado["protocolo_oficial"]["verificado_no_orgao"])
        self.assertEqual(atualizado["id"], caso["id"])

    def test_lote_repetido_nao_duplica_e_mudanca_invalida_revisao(self):
        dados = self.dados("rpa:S001")
        caso = self.repo.criar(dados)
        self.repo.revisar(caso["id"], "Média", "Revisão do cenário original.", "Revisor")
        repetido = self.repo.criar(dados)
        self.assertEqual(repetido["id"], caso["id"])
        self.assertIsNotNone(repetido["revisao"])
        dados["descricao"] = "Calçada sem rampa e sem alternativa de passagem"
        alterado = self.repo.criar(dados)
        self.assertIsNone(alterado["revisao"])
        self.assertEqual(len(self.repo.listar()), 1)
        self.assertEqual(len(alterado["historico"]), 3)

    def test_indicadores_usam_os_registros_e_o_denominador_real(self):
        caso = self.repo.criar(self.dados())
        self.repo.criar(self.dados())
        self.repo.revisar(caso["id"], "Média", "Revisão técnica desta demonstração.", "Revisor")
        indicadores = self.repo.indicadores()
        self.assertEqual(indicadores["total"], 2)
        self.assertEqual(indicadores["revisados"], 1)
        self.assertEqual(indicadores["sugestoes_corrigidas"], 1)
        self.assertEqual(indicadores["revisoes_pendentes"], 1)

    def test_correcao_do_pedido_invalida_revisao_sem_apagar_entrada(self):
        caso = self.repo.criar(self.dados())
        self.repo.revisar(caso["id"], "Média", "Decisão do pedido anterior.", "Revisor")
        dados = self.dados()
        dados["local"] = "Outro ponto de referência fictício"
        novo = self.repo.atualizar(caso["id"], dados)
        self.assertEqual(novo["id"], caso["id"])
        self.assertIsNone(novo["revisao"])
        self.assertEqual(novo["historico"][-1]["dados"]["entrada_anterior"]["local"], caso["local"])

    def test_confirmacao_com_revisao_obsoleta_e_rejeitada(self):
        caso = self.repo.criar(self.dados())
        revisado = self.repo.revisar(caso["id"], "Média", "Decisão do pedido anterior.", "Revisor")
        self.repo.contestar(caso["id"], "Informação mudou após a revisão.")
        with self.assertRaises(ValueError):
            self.repo.vincular_frontend(caso["id"], {"id": "local-ficticio"}, revisado["revisao"])
        self.assertNotIn("frontend", self.repo.obter(caso["id"]))

    def test_nova_revisao_ou_contestacao_retira_vinculo_da_decisao_anterior(self):
        for operacao in ("revisar", "contestar"):
            with self.subTest(operacao=operacao):
                caso = self.repo.criar(self.dados())
                revisado = self.repo.revisar(caso["id"], "Média", "Decisão anterior do caso.", "Revisor")
                self.repo.vincular_frontend(caso["id"], {"id": "frontend-anterior", "prioridade": "Média"}, revisado["revisao"])
                if operacao == "revisar":
                    novo = self.repo.revisar(caso["id"], "Alta", "Novas informações para a decisão.", "Revisor")
                else:
                    novo = self.repo.contestar(caso["id"], "A prioridade precisa de nova análise.")
                self.assertNotIn("frontend", novo)
                self.assertEqual(novo["historico"][-1]["dados"]["frontend_anterior"]["id"], "frontend-anterior")

    def test_reimportacao_identica_preserva_complementos_e_revisao(self):
        origem = self.dados("rpa:001")
        caso = self.repo.criar(origem)
        complemento = {**origem, "local": "Praça de demonstração, entrada norte", "contexto": "area_publica"}
        self.repo.atualizar(caso["id"], complemento)
        revisado = self.repo.revisar(caso["id"], "Média", "Contexto complementado na central.", "Revisor")
        repetido = self.repo.criar(origem)
        self.assertEqual(repetido["local"], complemento["local"])
        self.assertEqual(repetido["contexto"], "area_publica")
        self.assertEqual(repetido["revisao"], revisado["revisao"])
        self.assertEqual(len(repetido["historico"]), len(revisado["historico"]))

    def test_lote_atualizado_preserva_vinculo_de_passagem_e_exige_nova_revisao(self):
        origem = self.dados('rpa:passagem')
        caso = self.repo.criar(origem)
        vinculo = {'percurso_id': 'ponto-ubs-demo', 'trecho_id': 'rampa', 'condicao': 'bloqueado'}
        self.repo.atualizar(caso['id'], {'passagem': vinculo})
        self.repo.revisar(caso['id'], 'Alta', 'Interrompe a ligação do percurso didático.', 'Revisor')
        atualizado = self.repo.criar({**origem, 'descricao': origem['descricao'] + ' na travessia.'})
        self.assertEqual(atualizado['passagem'], vinculo)
        self.assertIsNone(atualizado['revisao'])
        self.assertTrue(atualizado['exige_revisao'])


if __name__ == "__main__":
    unittest.main()
