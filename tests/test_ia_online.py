import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from types import ModuleType, SimpleNamespace
from unittest.mock import Mock, patch
from urllib.error import HTTPError, URLError


class IAOnlineTest(unittest.TestCase):
    def setUp(self):
        try:
            from central import ia_online
        except ImportError:
            self.fail("O adaptador de IA online ainda não foi implementado.")
        self.ia = ia_online

    def resposta(self, identificador="LUZ.1", **alteracoes):
        dados = {"model": "qwen/qwen3.8-27b", "choices": [{
            "finish_reason": "stop", "message": {"content": json.dumps({"id": identificador})},
        }]}
        dados.update(alteracoes)
        return io.BytesIO(json.dumps(dados).encode())

    def test_selecao_envia_apenas_ids_elegiveis_em_schema_estrito(self):
        trechos = [SimpleNamespace(id="LUZ.1", secao="Reparo", texto="Peça o reparo pelo SP156.")]

        def remoto(requisicao, timeout):
            self.assertEqual(requisicao.full_url, "https://api.groq.com/openai/v1/chat/completions")
            self.assertEqual(timeout, 45)
            self.assertEqual(requisicao.get_header("Authorization"), "Bearer chave-teste")
            corpo = json.loads(requisicao.data)
            self.assertEqual(corpo["model"], "qwen/qwen3.8-27b")
            self.assertEqual(corpo["reasoning_effort"], "none")
            schema = corpo["response_format"]["json_schema"]
            self.assertTrue(schema["strict"])
            self.assertEqual(schema["schema"]["properties"]["id"]["enum"],
                             ["LUZ.1", "SEM_EVIDENCIA", "FORA_ESCOPO", "ESCLARECER"])
            self.assertIn("Peça o reparo pelo SP156.", corpo["messages"][1]["content"])
            return self.resposta()

        with patch.dict(os.environ, {"GROQ_API_KEY": "chave-teste"}), patch.object(self.ia, "urlopen", remoto):
            self.assertEqual(self.ia.selecionar("Como pedir reparo?", trechos), "LUZ.1")

    def test_falhas_remotas_nao_devolvem_orientacao_historica(self):
        trechos = [SimpleNamespace(id="LUZ.1", secao="Reparo", texto="Trecho real.")]
        falhas = [
            HTTPError("https://api.groq.com", 429, "Limite", {}, None),
            HTTPError("https://api.groq.com", 401, "Não autorizado", {}, None),
            URLError("timeout"),
        ]
        for erro in falhas:
            with self.subTest(erro=type(erro).__name__), patch.dict(os.environ, {"GROQ_API_KEY": "teste"}), \
                    patch.object(self.ia, "urlopen", side_effect=erro):
                with self.assertRaises(RuntimeError):
                    self.ia.selecionar("Iluminação apagada", trechos)

    def test_rejeita_modelo_trocado_id_inventado_e_resposta_truncada(self):
        trechos = [SimpleNamespace(id="LUZ.1", secao="Reparo", texto="Trecho real.")]
        respostas = [self.resposta("FALSA.1"), self.resposta(model="outro/modelo"),
                     self.resposta(choices=[{"finish_reason": "length", "message": {"content": '{"id":"LUZ.1"}'}}]),
                     io.BytesIO(b"x" * 65537)]
        for resposta in respostas:
            with self.subTest(resposta=resposta), patch.dict(os.environ, {"GROQ_API_KEY": "teste"}), \
                    patch.object(self.ia, "urlopen", return_value=resposta):
                with self.assertRaises(RuntimeError):
                    self.ia.selecionar("Iluminação apagada", trechos)

    def test_chave_ausente_e_entrada_invalida_falham_antes_de_carregar_encoder(self):
        with patch.dict(os.environ, {}, clear=True), patch.object(self.ia, "bot", side_effect=AssertionError("carregou")):
            with self.assertRaisesRegex(RuntimeError, "GROQ_API_KEY"):
                self.ia.perguntar("Como solicitar iluminação?")
        for texto in (None, " ", "x" * 501):
            with self.subTest(texto=texto), self.assertRaises(ValueError):
                self.ia.perguntar(texto)

    def test_importacao_original_nao_substitui_modulo_triagem_existente(self):
        sentinela = ModuleType("triagem")
        self.ia.original.cache_clear()
        try:
            with patch.dict(sys.modules, {"triagem": sentinela}):
                sys.modules.pop("_zelabairro_genai_original", None)
                original = self.ia.original()
                self.assertIs(sys.modules["triagem"], sentinela)
                self.assertEqual(original.classificar_solicitacao("Calçada sem rampa acessível")["category"], "Acessibilidade")
        finally:
            self.ia.original.cache_clear()

    def test_fluxo_reutiliza_fonte_e_filtros_originais(self):
        original = self.ia.original()
        assistente = original.Assistente(original.carregar_corpus(), selecionar=self.ia.selecionar, hibrido=False)

        def remoto(requisicao, timeout):
            opcoes = json.loads(requisicao.data)["response_format"]["json_schema"]["schema"]["properties"]["id"]["enum"]
            return self.resposta(opcoes[0])

        with patch.dict(os.environ, {"GROQ_API_KEY": "teste"}), patch.object(self.ia, "bot", return_value=assistente), \
                patch.object(self.ia, "urlopen", remoto):
            resultado = self.ia.perguntar("Como solicitar reparo de poste com lâmpada apagada?")
            self.assertEqual(resultado["status"], "respondido")
            self.assertEqual(resultado["resposta"], resultado["fonte"]["texto"])
            self.assertEqual(resultado["modelo"], "qwen/qwen3.8-27b")
            self.assertFalse(resultado["historico"])
            self.assertEqual(self.ia.perguntar("Sou de Curitiba e preciso de iluminação")["status"], "fora_escopo")
            self.assertEqual(self.ia.perguntar("Meu CPF é 123.456.789-01")["status"], "privacidade")
            with self.assertRaises(ValueError):
                self.ia.perguntar("Como acompanhar?", "FONTE_INEXISTENTE")

    def test_encoder_preparado_mantem_busca_hibrida_sem_rede_no_runtime(self):
        with patch.dict(os.environ, {"HF_HUB_OFFLINE": "1"}):
            assistente = self.ia.bot()
            self.assertIsNotNone(assistente.indice.vetores)
            ranking = assistente.indice.buscar("Como solicitar reparo de uma lâmpada apagada?")
        self.assertTrue(ranking)
        self.assertTrue(any("ilumin" in trecho.titulo.lower() for trecho, _ in ranking))

    def test_encoder_ausente_falha_sem_tentar_resolver_ou_baixar_modelo(self):
        original = self.ia.original()
        with tempfile.TemporaryDirectory() as pasta, patch.object(self.ia, "ARTEFATOS", Path(pasta)), \
                patch.dict(os.environ, {"VERCEL": "0"}), \
                patch("fastembed.common.model_management.ModelManagement.download_model", side_effect=AssertionError("Tentou resolver modelo")), \
                self.assertRaisesRegex(RuntimeError, "encoder.*preparado"):
            original.TextEmbedding(original.EMBEDDINGS)

    def test_nuvem_prepara_encoder_pinned_no_tmp_sem_resolver_huggingface(self):
        nomes = []
        with tempfile.TemporaryDirectory() as pasta:
            cache = Path(pasta) / "tmp"

            def peso(nome, url, sha, tamanho, *, deadline):
                nomes.append(nome.rsplit("/", 1)[1])
                self.assertIn("/resolve/faf4aa4225822f3bc6376869cb1164e8e3feedd0/", url)
                self.assertEqual(len(sha), 64)
                self.assertGreater(tamanho, 0)
                self.assertEqual(deadline, 150)
                destino = cache / nome
                destino.parent.mkdir(parents=True, exist_ok=True)
                destino.touch()
                return destino

            with patch.object(self.ia, "ARTEFATOS", Path(pasta) / "bundle"), patch.dict(os.environ, {"VERCEL": "1"}), \
                    patch.object(self.ia, "monotonic", return_value=100), patch.object(self.ia, "garantir_peso", peso):
                snapshot = self.ia.caminho_encoder()
            self.assertTrue(snapshot.is_relative_to(cache))
            self.assertCountEqual(nomes, ["config.json", "model_optimized.onnx", "special_tokens_map.json", "tokenizer_config.json", "tokenizer.json"])

    def test_cinco_assets_compartilham_um_prazo_total(self):
        agora, prazos = [0], []

        def peso(nome, url, sha, tamanho, *, deadline):
            prazos.append(deadline)
            agora[0] += 20
            if agora[0] >= deadline:
                raise RuntimeError("Prazo total excedido")
            return Path("/tmp/encoder") / nome

        with tempfile.TemporaryDirectory() as pasta, patch.object(self.ia, "ARTEFATOS", Path(pasta)), \
                patch.dict(os.environ, {"VERCEL": "1"}), patch.object(self.ia, "monotonic", side_effect=lambda: agora[0]), \
                patch.object(self.ia, "garantir_peso", peso), self.assertRaisesRegex(RuntimeError, "Prazo"):
            self.ia.caminho_encoder()
        self.assertEqual(prazos, [50, 50, 50])

    def test_carga_concorrente_espera_no_maximo_45_segundos(self):
        trava = SimpleNamespace(acquire=Mock(return_value=False), release=Mock())
        with patch.object(self.ia, "_CARGA", trava), self.assertRaisesRegex(RuntimeError, "45 segundos"):
            self.ia.bot()
        trava.acquire.assert_called_once_with(timeout=45)
        trava.release.assert_not_called()

    def test_encoder_especifico_nao_cria_cache_no_diretorio_original(self):
        original = self.ia.original()
        with tempfile.TemporaryDirectory() as pasta:
            proibido = Path(pasta) / "arquivo"
            proibido.write_bytes(b"nao e diretorio")
            encoder = original.TextEmbedding(original.EMBEDDINGS, cache_dir=str(proibido), lazy_load=True)
            self.assertNotEqual(Path(encoder.model.cache_dir), proibido)
            self.assertEqual(proibido.read_bytes(), b"nao e diretorio")

    def test_preparacao_rejeita_download_com_hash_diferente_sem_aceitar_peso(self):
        from scripts import preparar_modelos_online as preparar
        with tempfile.TemporaryDirectory() as pasta:
            cache = Path(pasta)
            with patch.object(preparar, "CACHE_ENCODER", cache), \
                    patch.object(preparar, "ARQUIVOS_ENCODER", {"model_optimized.onnx": "0" * 64}), \
                    patch.object(preparar, "urlopen", return_value=io.BytesIO(b"peso divergente")), \
                    self.assertRaises(ValueError):
                preparar.preparar_embeddings()
            self.assertFalse((cache / "refs-ready.json").exists())
            self.assertFalse(list(cache.rglob("*.partial")))
            self.assertFalse(list(cache.rglob("*.onnx")))

    def test_preparacao_recusa_encoder_que_muda_vetores_originais(self):
        from scripts import preparar_modelos_online as preparar
        assistente = self.ia.bot()
        with patch.object(assistente.indice, "vetores", assistente.indice.vetores + 0.01), self.assertRaises(ValueError):
            preparar.verificar_encoder(assistente)

    def test_paridade_portatil_aceita_arredondamento_fp16_sem_mudar_rankings(self):
        from scripts import preparar_modelos_online as preparar
        assistente = self.ia.bot()
        vetores = assistente.indice.vetores.copy()
        vetores[0, 0] += 0.0002
        with patch.object(assistente.indice, "vetores", vetores), patch.object(Path, "write_text"):
            resultado = preparar.verificar_encoder(assistente)
        self.assertTrue(resultado["rankings_identicos"])
        self.assertLessEqual(resultado["erro_absoluto_maximo_vetores"], 1e-3)
        self.assertGreaterEqual(resultado["cosseno_minimo_corpus"], 0.99999)

    def test_paridade_portatil_recusa_nan_e_forma_divergente(self):
        from scripts import preparar_modelos_online as preparar
        assistente = self.ia.bot()
        nan = assistente.indice.vetores.copy()
        nan[0, 0] = float("nan")
        for vetores in (nan, assistente.indice.vetores[:-1]):
            with self.subTest(forma=vetores.shape), patch.object(assistente.indice, "vetores", vetores), self.assertRaises(ValueError):
                preparar.verificar_encoder(assistente)

    def test_paridade_portatil_recusa_desvio_angular_mesmo_com_erro_absoluto_pequeno(self):
        from scripts import preparar_modelos_online as preparar
        assistente = self.ia.bot()
        with patch.object(assistente.indice, "vetores", assistente.indice.vetores + 0.0009), self.assertRaises(ValueError):
            preparar.verificar_encoder(assistente)


if __name__ == "__main__":
    unittest.main()
