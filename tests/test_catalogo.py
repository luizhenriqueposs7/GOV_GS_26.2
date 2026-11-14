import unittest


class CatalogoTest(unittest.TestCase):
    def preparar(self, descricao, contexto="nao_informado", local="Praça de demonstração"):
        try:
            from central.catalogo import preparar
        except ModuleNotFoundError:
            self.fail("A preparação de pedidos ainda não foi implementada.")
        return preparar(descricao, contexto, local)

    def test_calcada_sem_contexto_pede_esclarecimento(self):
        resposta = self.preparar("A calçada está quebrada")
        self.assertIsNone(resposta["servico"])
        self.assertIn("calçada", resposta["pergunta"])

    def test_calcada_em_praca_tem_servico_especifico(self):
        resposta = self.preparar("Passeio danificado", "area_publica")
        self.assertEqual(resposta["servico"]["id"], "931")
        self.assertIn("servico=931", resposta["fonte"])

    def test_obstaculo_explicito_tem_servico_de_fiscalizacao(self):
        resposta = self.preparar("Vasos bloqueiam a passagem", "obstaculo")
        self.assertEqual(resposta["servico"]["id"], "2634")

    def test_ausencia_de_rampa_nao_e_tratada_como_objeto(self):
        resposta = self.preparar("Calçada sem rampa acessível")
        self.assertIsNone(resposta["servico"])
        self.assertIn("contexto", resposta["faltantes"])

    def test_manutencao_e_instalacao_de_luz_sao_diferentes(self):
        manutencao = self.preparar("Poste apagado", "iluminacao_existente")
        instalacao = self.preparar("A passagem nunca teve iluminação", "nova_iluminacao")
        self.assertEqual(manutencao["servico"]["id"], "ILU_MANUTENCAO")
        self.assertEqual(instalacao["servico"]["id"], "ILU_AMPLIACAO")

    def test_endereco_da_ocorrencia_e_sinalizado_quando_falta(self):
        resposta = self.preparar("Passeio danificado", "area_publica", local="")
        self.assertIn("local", resposta["faltantes"])

    def test_rampa_ausente_nao_vira_manutencao_so_por_ser_area_publica(self):
        resposta = self.preparar("Calçada sem rampa acessível", "area_publica")
        self.assertIsNone(resposta["servico"])
        self.assertIn("enquadramento", resposta["faltantes"])


if __name__ == "__main__":
    unittest.main()
