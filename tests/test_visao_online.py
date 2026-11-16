import io
import json
import os
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch

import numpy as np
from PIL import Image


class VisaoOnlineTest(unittest.TestCase):
    def setUp(self):
        try:
            from central import visao_online
        except ImportError:
            self.fail("O adaptador de Visão online ainda não foi implementado.")
        self.visao = visao_online

    def test_imagem_invalida_e_rejeitada_antes_de_carregar_modelo(self):
        with patch.object(self.visao, "modelo", side_effect=AssertionError("carregou")):
            with self.assertRaises(ValueError):
                self.visao.analisar_imagem(b"nao e foto")

    def test_nuvem_baixa_somente_onnx_pinned_quando_nao_esta_no_bundle(self):
        with tempfile.TemporaryDirectory() as pasta:
            cache = Path(pasta) / "tmp/crack_resnet18.onnx"

            def peso(nome, url, sha, tamanho, *, deadline):
                self.assertIn("/07064804a9eafe8d1618bd39a1f22c8c7b17864d/", url)
                self.assertEqual(sha, "1e5b4acda6e11ff3d83f029c69dc2a60bf5bd6e870ea6010647520de327a2007")
                self.assertEqual(tamanho, 44700649)
                self.assertEqual(deadline, 150)
                return cache

            with patch.object(self.visao, "ARTEFATOS", Path(pasta) / "bundle"), patch.dict(os.environ, {"VERCEL": "1"}), \
                    patch.object(self.visao, "monotonic", return_value=100), patch.object(self.visao, "garantir_peso", peso):
                self.assertEqual(self.visao.caminho_pesos(), cache)

    def test_preprocessamento_rgb_preserva_resize_e_normalizacao_entregues(self):
        from materiais.visao.visao import preprocessamento
        imagem = Image.fromarray(np.arange(9 * 17 * 3, dtype=np.uint8).reshape(9, 17, 3))
        esperado = preprocessamento(160)(imagem).unsqueeze(0).numpy()
        np.testing.assert_array_equal(self.visao.preprocessar(imagem), esperado)

    def test_escore_e_decisao_usam_indice_positivo_e_limiar_do_checkpoint(self):
        class Sessao:
            def run(self, saidas, entrada):
                self.entrada = entrada["imagem"]
                return [np.array([[0.0, 0.0]], dtype=np.float32)]

        sessao = Sessao()
        arquivo = io.BytesIO()
        Image.new("RGB", (30, 20), "white").save(arquivo, format="PNG")
        with patch.object(self.visao, "modelo", return_value=(sessao, {"positive_idx": 0, "threshold": 0.49, "image_size": 160})):
            resultado = self.visao.analisar_imagem(arquivo.getvalue())
        self.assertEqual(sessao.entrada.shape, (1, 3, 160, 160))
        self.assertEqual(resultado["escore"], 0.5)
        self.assertTrue(resultado["alerta"])
        self.assertEqual(resultado["classe"], "Possível fissura")
        self.assertEqual(resultado["limiar"], 0.49)
        self.assertEqual(resultado["resolucao"], 160)
        self.assertEqual(resultado["modelo"], "ResNet18")
        self.assertFalse(resultado["historico"])

    def test_saida_corrompida_nao_vira_inferencia(self):
        class Sessao:
            def run(self, saidas, entrada):
                return [np.array([[float("nan"), 0]], dtype=np.float32)]

        arquivo = io.BytesIO()
        Image.new("RGB", (5, 5)).save(arquivo, format="PNG")
        with patch.object(self.visao, "modelo", return_value=(Sessao(), {"positive_idx": 0, "threshold": 0.49, "image_size": 160})), \
                self.assertRaises(RuntimeError):
            self.visao.analisar_imagem(arquivo.getvalue())

    def test_falha_do_runtime_onnx_vira_indisponibilidade_explicita(self):
        from onnxruntime.capi.onnxruntime_pybind11_state import InvalidArgument

        class Sessao:
            def run(self, saidas, entrada):
                raise InvalidArgument("Detalhe interno do runtime")

        arquivo = io.BytesIO()
        Image.new("RGB", (5, 5)).save(arquivo, format="PNG")
        with patch.object(self.visao, "modelo", return_value=(Sessao(), {"positive_idx": 0, "threshold": 0.49, "image_size": 160})), \
                self.assertRaisesRegex(RuntimeError, "Nenhuma inferência"):
            self.visao.analisar_imagem(arquivo.getvalue())

    def test_artefato_real_preserva_escores_e_decisoes_perto_do_limiar(self):
        caminho = self.visao.ARTEFATOS / "paridade.json"
        self.assertTrue(caminho.is_file(), "Exporte e verifique o checkpoint antes de publicar.")
        paridade = json.loads(caminho.read_text(encoding="utf-8"))
        self.assertEqual(paridade["divergencias_decisao"], 0)
        self.assertLessEqual(paridade["erro_absoluto_maximo"], 1e-5)
        self.assertGreaterEqual(paridade["imagens_reais"], 20)
        self.assertTrue(paridade["proximas_limiar"])
        raiz = Path(__file__).resolve().parents[1]
        from materiais.visao.visao import carregar_modelo, classificar
        modelo, parametros, preprocessar = carregar_modelo()
        for caso in paridade["proximas_limiar"][:4]:
            with self.subTest(imagem=caso["arquivo"]):
                conteudo = (raiz / caso["arquivo"]).read_bytes()
                with Image.open(io.BytesIO(conteudo)) as imagem:
                    original = classificar(imagem, modelo, parametros, preprocessar)
                atual = self.visao.analisar_imagem(conteudo)
                self.assertAlmostEqual(atual["escore"], original["escore"], delta=1e-5)
                self.assertEqual(atual["alerta"], original["alerta"])


if __name__ == "__main__":
    unittest.main()
