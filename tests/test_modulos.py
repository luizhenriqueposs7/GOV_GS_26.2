import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


class ModulosTest(unittest.TestCase):
    def setUp(self):
        try:
            from central import modulos
        except ImportError:
            self.fail("A integração dos módulos ainda não foi implementada.")
        self.modulos = modulos

    def test_triagem_reutiliza_o_resultado_original(self):
        saida = self.modulos.triagem("Calçada sem rampa acessível")
        self.assertEqual(saida, {"category": "Acessibilidade", "priority": "Baixa", "confidence": 1.0, "review_required": False})

    def test_lote_preserva_ids_rejeita_vazios_e_identifica_repeticao(self):
        entrada = b"case_id,description,neighborhood\n001,Poste apagado,Centro\n002,,Centro\n001,Outro relato,Centro\n"
        saida = self.modulos.importar_lote(entrada)
        self.assertEqual(saida["resumo"]["valid"], 1)
        self.assertEqual(saida["resumo"]["rejected"], 1)
        self.assertEqual(saida["resumo"]["duplicates"], 1)
        self.assertEqual(saida["registros"][0]["case_id"], "001")

    def test_csv_sem_cabecalho_obrigatorio_e_rejeitado(self):
        with self.assertRaises(ValueError):
            self.modulos.importar_lote(b"id,texto\n1,exemplo\n")

    def test_busca_retorna_trecho_e_procedencia_real(self):
        trechos = self.modulos.buscar_fontes("ações comunitárias desastres")
        self.assertGreater(len(trechos), 0)
        self.assertTrue(trechos[0]["url"].startswith("https://"))
        self.assertTrue(trechos[0]["paginas"])
        self.assertIn("text", trechos[0])

    def test_corpus_invalido_nao_produz_resultado_parcial(self):
        with tempfile.TemporaryDirectory() as pasta:
            p = Path(pasta) / "ruim.jsonl"
            p.write_text('{"text":"trecho sem origem"}\n', encoding="utf-8")
            with patch.object(self.modulos, "CORPUS", p), self.assertRaises(ValueError):
                self.modulos.buscar_fontes("trecho")

    def test_fonte_html_sem_paginacao_continua_consultavel(self):
        import json
        with tempfile.TemporaryDirectory() as pasta:
            p = Path(pasta) / "fonte.jsonl"
            p.write_text(json.dumps({"text": "Canais públicos de orientação comunitária.",
                                    "fonte": "orientacao.html", "secao": "Canais", "paginas": None,
                                    "url": "https://www.gov.br/exemplo"}), encoding="utf-8")
            with patch.object(self.modulos, "CORPUS", p):
                resultado = self.modulos.buscar_fontes("orientação comunitária")
            self.assertEqual(resultado[0]["secao"], "Canais")
            self.assertIsNone(resultado[0]["paginas"])

    def test_imagem_ilegivel_e_rejeitada_antes_da_inferencia(self):
        with self.assertRaises(ValueError):
            self.modulos.analisar_imagem(b"nao e uma imagem")

    def test_frontend_reutilizado_nao_duplica_confirmacao_repetida(self):
        import sqlite3
        dados = {"cidadao_id": "caso-demo:revisao-1", "descricao": "Calçada sem rampa acessível",
                 "bairro": "Bairro fictício", "categoria": "Calçada", "prioridade": "Média",
                 "resumo": "Barreira de circulação revisada na demonstração"}
        with tempfile.TemporaryDirectory() as pasta:
            banco = Path(pasta) / "frontend.sqlite"
            primeiro = self.modulos.registrar_no_frontend(dados, banco)
            segundo = self.modulos.registrar_no_frontend(dados, banco)
            self.assertEqual(primeiro["id"], segundo["id"])
            self.assertEqual(primeiro["status"], "Recebido")
            from contextlib import closing
            with closing(sqlite3.connect(banco)) as con:
                self.assertEqual(con.execute("SELECT count(*) FROM relatos").fetchone()[0], 1)

    def test_servico_de_ia_nao_pode_apontar_para_host_arbitrario(self):
        with patch.dict("os.environ", {"CITIZENTECH_GENAI_URL": "https://exemplo.invalid"}):
            with self.assertRaises(ValueError):
                self.modulos.perguntar("Como pedir manutenção da iluminação?", None)

    def test_piloto_quantico_identifica_simulador_sem_alegar_qpu(self):
        quantica = next(x for x in self.modulos.ativos() if x["id"] == "quantica")
        self.assertEqual(quantica["modo"], "QAOA em simulador")
        self.assertIn('Não usa QPU', quantica['limite'])
        self.assertTrue(quantica["materiais"])

    def test_ia_rejeita_status_inventado_e_resposta_vazia(self):
        import io, json
        from unittest.mock import MagicMock
        for saida in ({"status": "qualquer", "resposta": "Orientação sem contrato", "fonte": None},
                      {"status": "respondido", "resposta": "", "fonte": {"texto": "", "url": "https://prefeitura.sp.gov.br/exemplo"}}):
            opener = MagicMock()
            opener.open.return_value = io.BytesIO(json.dumps(saida).encode())
            with self.subTest(saida=saida), patch.object(self.modulos, "build_opener", return_value=opener), self.assertRaises(RuntimeError):
                self.modulos.perguntar("Como solicitar manutenção?")

    def test_visao_rejeita_saida_sem_contrato_em_vez_de_sinalizar_sucesso(self):
        import io
        from PIL import Image
        imagem = io.BytesIO(); Image.new("RGB", (10, 10)).save(imagem, format="PNG")
        for saida in ({"erro": "modelo inválido"}, {"classe": "Possível fissura", "escore": float("nan")}):
            with self.subTest(saida=saida), patch.object(self.modulos, "executar_worker", return_value=saida), self.assertRaises(RuntimeError):
                self.modulos.analisar_imagem(imagem.getvalue())


if __name__ == "__main__":
    unittest.main()
