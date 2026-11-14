import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient


class APITest(unittest.TestCase):
    def setUp(self):
        self.pasta = tempfile.TemporaryDirectory()
        self.addCleanup(self.pasta.cleanup)
        self.env = patch.dict("os.environ", {"GOV_MANAGER_KEY": "chave-sintetica-para-teste"})
        self.env.start()
        self.addCleanup(self.env.stop)
        try:
            from central.app import criar_app
        except ModuleNotFoundError:
            self.fail("A API da central ainda não foi implementada.")
        self.client = TestClient(criar_app(Path(self.pasta.name)))
        self.addCleanup(self.client.close)
        self.chave = {"X-Manager-Key": "chave-sintetica-para-teste"}

    def criar(self, **campos):
        entrada = {"descricao": "Passeio da praça com calçada danificada", "bairro": "Bairro fictício",
                   "local": "Praça de demonstração", "contexto": "area_publica", "confirmado": True}
        entrada.update(campos)
        return self.client.post("/api/atendimentos", json=entrada)

    def revisar(self, identificador, **kwargs):
        return self.client.post(f"/api/atendimentos/{identificador}/revisao",
                                json={"prioridade": "Média", "justificativa": "Barreira conferida na demonstração.",
                                      "revisor": "Revisor 1"}, **kwargs)

    def test_confirmacao_especifica_e_obrigatoria(self):
        self.assertEqual(self.criar(confirmado=False).status_code, 422)

    def test_cliente_nao_pode_forjar_a_analise_original(self):
        self.assertEqual(self.criar(triagem_original={"priority": "Alta"}).status_code, 422)

    def test_barreira_preserva_saida_original_e_recebe_controle(self):
        resposta = self.criar(descricao="Calçada sem rampa acessível", contexto="nao_informado")
        self.assertEqual(resposta.status_code, 201)
        caso = resposta.json()
        self.assertFalse(caso["triagem_original"]["review_required"])
        self.assertTrue(caso["exige_revisao"])
        self.assertIsNone(caso["preparacao"]["servico"])

    def test_revisao_sem_chave_nao_altera_decisao(self):
        caso = self.criar().json()
        self.assertEqual(self.revisar(caso["id"]).status_code, 401)
        self.assertIsNone(self.client.get(f'/api/atendimentos/{caso["id"]}').json()["revisao"])

    def test_contestacao_reabre_decisao_sem_apagar_historico(self):
        caso = self.criar().json()
        self.assertEqual(self.revisar(caso["id"], headers=self.chave).status_code, 200)
        resposta = self.client.post(f'/api/atendimentos/{caso["id"]}/contestacao',
                                    json={"motivo": "Preciso de nova análise da barreira."})
        self.assertEqual(resposta.status_code, 200)
        self.assertIsNone(resposta.json()["revisao"])
        self.assertEqual(len(resposta.json()["historico"]), 3)

    def test_encaminhamento_ao_frontend_exige_revisao(self):
        caso = self.criar().json()
        resposta = self.client.post(f'/api/atendimentos/{caso["id"]}/zelabairro', headers=self.chave)
        self.assertEqual(resposta.status_code, 409)

    def test_frontend_real_e_ligado_sem_virar_protocolo_municipal(self):
        caso = self.criar().json()
        self.revisar(caso["id"], headers=self.chave)
        url = f'/api/atendimentos/{caso["id"]}/zelabairro'
        primeiro = self.client.post(url, headers=self.chave)
        segundo = self.client.post(url, headers=self.chave)
        self.assertEqual(primeiro.status_code, 200)
        self.assertEqual(primeiro.json()["frontend"]["id"], segundo.json()["frontend"]["id"])
        self.assertIsNone(primeiro.json()["protocolo_oficial"])

    def test_material_fora_do_manifesto_nao_e_servido(self):
        self.assertEqual(self.client.get("/api/materiais/chave-gestao.txt").status_code, 404)

    def test_arquivo_ilegivel_tem_erro_tratado(self):
        resposta = self.client.post("/api/visao", files={"arquivo": ("foto.png", b"invalido", "image/png")})
        self.assertEqual(resposta.status_code, 422)

    def test_indisponibilidade_da_ia_nao_retorna_resultado_historico(self):
        with patch("central.modulos.perguntar", side_effect=RuntimeError("Serviço local indisponível")):
            resposta = self.client.post("/api/assistente", json={"pergunta": "Como solicitar iluminação?"})
        self.assertEqual(resposta.status_code, 503)
        self.assertIn("erro", resposta.json())

    def test_descricao_excessiva_e_contexto_invalido_sao_rejeitados(self):
        self.assertEqual(self.criar(descricao="a" * 1501).status_code, 422)
        self.assertEqual(self.criar(contexto="servico_inventado").status_code, 422)

    def test_completar_contexto_preserva_id_e_invalida_decisao_antiga(self):
        caso = self.criar(contexto="nao_informado", local="").json()
        self.revisar(caso["id"], headers=self.chave)
        entrada = {"descricao": caso["descricao"], "bairro": caso["bairro"],
                   "local": "Praça de demonstração", "contexto": "area_publica", "confirmado": True}
        resposta = self.client.put(f'/api/atendimentos/{caso["id"]}', json=entrada)
        self.assertEqual(resposta.status_code, 200)
        atualizado = resposta.json()
        self.assertEqual(atualizado["id"], caso["id"])
        self.assertEqual(atualizado["preparacao"]["faltantes"], [])
        self.assertIsNone(atualizado["revisao"])
        self.assertEqual(len(atualizado["historico"]), 3)

    def test_lote_respeita_os_limites_do_pedido_sem_gravar_parcialmente(self):
        csv = ("case_id,description,neighborhood\n001," + "a" * 1501 + ",Bairro fictício\n").encode()
        resposta = self.client.post("/api/lotes", headers=self.chave,
                                    files={"arquivo": ("lote.csv", csv, "text/csv")})
        self.assertEqual(resposta.status_code, 422)
        self.assertEqual(self.client.get("/api/atendimentos").json(), [])

    def test_evidencia_pln_e_carregada_do_material_sem_texto_forjado(self):
        caso = self.criar().json()
        url = f'/api/atendimentos/{caso["id"]}/evidencia-pln'
        self.assertEqual(self.client.post(url, json={"linha_corpus": 1, "text": "forjado"}).status_code, 422)
        resposta = self.client.post(url, json={"linha_corpus": 1})
        self.assertEqual(resposta.status_code, 200)
        self.assertIn("url", resposta.json()["evidencias"][0]["resultado"])


if __name__ == "__main__":
    unittest.main()
