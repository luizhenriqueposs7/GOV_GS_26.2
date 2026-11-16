import hashlib
import io
from http.client import HTTPResponse, IncompleteRead
import tempfile
import unittest
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch


class PesosOnlineTest(unittest.TestCase):
    def setUp(self):
        try:
            from central import pesos_online
        except ImportError:
            self.fail("O cache verificado de pesos ainda não foi implementado.")
        self.pesos = pesos_online

    def test_download_atomico_e_reutilizacao_concorrente_sem_baixar_duas_vezes(self):
        dados = b"peso fixo de teste"
        sha = hashlib.sha256(dados).hexdigest()
        chamadas = []

        def remoto(url, timeout):
            chamadas.append(url)
            return io.BytesIO(dados)

        with tempfile.TemporaryDirectory() as pasta, patch.object(self.pesos, "CACHE", Path(pasta)), \
                patch.object(self.pesos, "urlopen", remoto):
            with ThreadPoolExecutor(max_workers=4) as executor:
                destinos = list(executor.map(lambda _: self.pesos.garantir_peso("encoder/peso.onnx", "https://example.invalid/peso", sha, len(dados)), range(4)))
            self.assertEqual(destinos[0].read_bytes(), dados)
            self.assertTrue(all(p == destinos[0] for p in destinos))
            self.assertEqual(len(chamadas), 1)
            self.assertFalse(list(Path(pasta).rglob("*.partial")))

    def test_peso_corrompido_e_tamanho_errado_nao_viram_cache_valido(self):
        for dados in (b"peso falso", b"x" * 20, b"x" * 21):
            with self.subTest(dados=dados), tempfile.TemporaryDirectory() as pasta, \
                    patch.object(self.pesos, "CACHE", Path(pasta)), patch.object(self.pesos, "urlopen", return_value=io.BytesIO(dados)):
                with self.assertRaisesRegex(RuntimeError, "peso"):
                    self.pesos.garantir_peso("modelo.onnx", "https://example.invalid/peso", "0" * 64, 20)
                self.assertFalse((Path(pasta) / "modelo.onnx").exists())
                self.assertFalse(list(Path(pasta).rglob("*.partial")))

    def test_cache_invalido_e_substituido_por_peso_pinned_sem_copias_antigas(self):
        dados = b"peso correto"
        with tempfile.TemporaryDirectory() as pasta, patch.object(self.pesos, "CACHE", Path(pasta)), \
                patch.object(self.pesos, "urlopen", return_value=io.BytesIO(dados)):
            destino = Path(pasta) / "modelo.onnx"
            destino.write_bytes(b"cache divergente")
            atual = self.pesos.garantir_peso("modelo.onnx", "https://example.invalid/peso", hashlib.sha256(dados).hexdigest(), len(dados))
            self.assertEqual(atual.read_bytes(), dados)

    def test_caminho_fora_do_cache_e_rejeitado(self):
        with self.assertRaises(ValueError):
            self.pesos.garantir_peso("../dados.sqlite", "https://example.invalid/peso", "0" * 64, 1)

    def test_conexao_interrompida_vira_indisponibilidade_sem_partial(self):
        class Interrompida(io.BytesIO):
            def read(self, tamanho):
                if self.tell() == 0:
                    return super().read(3)
                raise IncompleteRead(b"incompleto")

            read1 = read

        with tempfile.TemporaryDirectory() as pasta, patch.object(self.pesos, "CACHE", Path(pasta)), \
                patch.object(self.pesos, "urlopen", return_value=Interrompida(b"incompleto")):
            with self.assertRaises(RuntimeError):
                self.pesos.garantir_peso("modelo.onnx", "https://example.invalid/peso", "0" * 64, 20)
            self.assertFalse(list(Path(pasta).rglob("*.partial")))

    def test_http_response_fecha_socket_apos_content_length_sem_invalidar_peso(self):
        class Socket:
            def __init__(self, dados):
                self.dados, self.fechado, self.timeouts = dados, False, []

            def makefile(self, modo):
                socket = self

                class Fluxo(io.BytesIO):
                    raw = SimpleNamespace(_sock=socket)

                    def close(self):
                        socket.fechado = True
                        super().close()

                return Fluxo(b"HTTP/1.1 200 OK\r\nContent-Length: " + str(len(self.dados)).encode() + b"\r\n\r\n" + self.dados)

            def settimeout(self, timeout):
                if self.fechado:
                    raise OSError("Bad file descriptor")
                self.timeouts.append(timeout)

        for dados in (b"peso completo", b"p" * (1024 * 1024 + 3)):
            with self.subTest(tamanho=len(dados)), tempfile.TemporaryDirectory() as pasta:
                socket = Socket(dados)
                resposta = HTTPResponse(socket)
                resposta.begin()
                with patch.object(self.pesos, "CACHE", Path(pasta)), patch.object(self.pesos, "urlopen", return_value=resposta):
                    destino = self.pesos.garantir_peso("modelo.onnx", "https://example.invalid/peso", hashlib.sha256(dados).hexdigest(), len(dados))
                self.assertEqual(destino.read_bytes(), dados)
                self.assertTrue(socket.fechado)
                self.assertIsNone(resposta.fp)
                self.assertEqual(len(socket.timeouts), (len(dados) + 1024 * 1024 - 1) // (1024 * 1024))
                self.assertFalse(list(Path(pasta).rglob("*.partial")))

    def test_download_lento_respeita_prazo_total_e_limpa_partial(self):
        agora, timeouts = [0.0], []

        class Lenta(io.BytesIO):
            fp = SimpleNamespace(raw=SimpleNamespace(_sock=SimpleNamespace(settimeout=timeouts.append)))

            def read1(self, tamanho):
                agora[0] += 22
                return super().read1(1)

        with tempfile.TemporaryDirectory() as pasta, patch.object(self.pesos, "CACHE", Path(pasta)), \
                patch.object(self.pesos, "monotonic", side_effect=lambda: agora[0]), \
                patch.object(self.pesos, "urlopen", return_value=Lenta(b"abc")) as abrir:
            with self.assertRaisesRegex(RuntimeError, "prazo"):
                self.pesos.garantir_peso("modelo.onnx", "https://example.invalid/peso", hashlib.sha256(b"abc").hexdigest(), 3)
            self.assertEqual(abrir.call_args.kwargs["timeout"], 10)
            self.assertEqual(timeouts, [10, 10, 6])
            self.assertFalse((Path(pasta) / "modelo.onnx").exists())
            self.assertFalse(list(Path(pasta).rglob("*.partial")))

    def test_espera_de_thread_tem_prazo_e_nao_libera_lock_alheio(self):
        trava = SimpleNamespace(acquire=Mock(return_value=False), release=Mock())
        with patch.object(self.pesos, "_LOCK", trava), patch.object(self.pesos, "monotonic", return_value=100):
            with self.assertRaisesRegex(RuntimeError, "prazo"):
                self.pesos.garantir_peso("modelo.onnx", "https://example.invalid/peso", "0" * 64, 1)
        trava.acquire.assert_called_once_with(timeout=50)
        trava.release.assert_not_called()

    def test_espera_do_lock_linux_e_nao_bloqueante_e_limitada(self):
        agora = [0.0]
        fcntl = SimpleNamespace(LOCK_EX=2, LOCK_NB=4, flock=Mock(side_effect=BlockingIOError()))

        def avancar(tempo):
            agora[0] += tempo

        with tempfile.TemporaryDirectory() as pasta, patch.object(self.pesos, "CACHE", Path(pasta)), \
                patch.object(self.pesos, "os", SimpleNamespace(name="posix")), patch.dict(sys.modules, {"fcntl": fcntl}), \
                patch.object(self.pesos, "monotonic", side_effect=lambda: agora[0]), patch.object(self.pesos, "sleep", avancar), \
                patch.object(self.pesos, "urlopen") as abrir:
            with self.assertRaisesRegex(RuntimeError, "prazo"):
                self.pesos.garantir_peso("modelo.onnx", "https://example.invalid/peso", "0" * 64, 1, deadline=0.12)
            self.assertAlmostEqual(agora[0], 0.12)
            self.assertTrue(all(chamada.args[1] == 6 for chamada in fcntl.flock.call_args_list))
            abrir.assert_not_called()


if __name__ == "__main__":
    unittest.main()
