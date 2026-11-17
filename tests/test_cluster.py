import copy
import hashlib
import io
import threading
import unittest
from unittest.mock import patch
from uuid import UUID

import httpx
import pandas as pd

from central import modulos


CSV = ("\ufeffcase_id,description,neighborhood\n"
       " 001 ,Calçada sem rampa acessível,Centro\n"
       "002,,Centro\n"
       "003,Lixo e entulho,Centro\n"
       "004,Poste apagado,Norte\n"
       "002,Buraco na rua,Leste\n"
       "001,Outro relato,Centro\n"
       "005,Texto livre,Centro\n"
       "006,,Centro\n"
       "003,Lixo duplicado,Centro\n"
       ",Sem identificador,Centro\n").encode("utf-8")


class ClusterTest(unittest.TestCase):
    def setUp(self):
        try:
            from central import cluster
        except ImportError:
            self.fail("O coordenador de cluster ainda não foi implementado.")
        self.cluster = cluster

    def test_worker_reutiliza_pipeline_com_triagem_tipificada_e_identidade(self):
        resultado = self.cluster.processar_worker(CSV, 1, "lote-teste")
        self.assertEqual(resultado["registros"][0]["triagem_original"], {
            "category": "Acessibilidade", "priority": "Baixa", "confidence": 1.0,
            "review_required": False})
        self.assertEqual(resultado["entrada_sha256"], hashlib.sha256(CSV).hexdigest())
        self.assertEqual((resultado["worker"], resultado["lote_id"]), (1, "lote-teste"))
        UUID(resultado["instancia"])
        self.assertGreaterEqual(resultado["tempo_ms"], 0)
        self.assertEqual(resultado["instancia"], self.cluster.processar_worker(CSV, 2, "outro")["instancia"])

    def test_dois_e_quatro_workers_equivalem_ao_pipeline_serial(self):
        serial = modulos.importar_lote(CSV)
        for workers in (2, 4):
            with self.subTest(workers=workers):
                resultado = self.cluster.executar(CSV, workers)
                registros = [{k: v for k, v in item.items() if k != "triagem_original"}
                             for item in resultado["registros"]]
                self.assertEqual(registros, serial["registros"])
                self.assertEqual(resultado["resumo"], serial["resumo"])
                self.assertEqual([x["case_id"] for x in registros], ["001", "003", "004", "002", "005"])
                self.assertEqual([x["row_number"] for x in resultado["rejeitados"]], [3, 9, 11])
                self.assertEqual([str(x["row_number"]) for x in resultado["rejeitados"]],
                                 [x["row_number"] for x in serial["rejeitados"]])
                self.assertEqual(resultado["workers_solicitados"], workers)
                self.assertEqual(resultado["workers_executados"], workers)
                self.assertEqual([x["worker"] for x in resultado["execucoes"]], list(range(1, workers + 1)))
                self.assertIn("threads", resultado["modo"].lower())
                self.assertTrue(all(x["contagens"]["updated"] == 0 for x in resultado["execucoes"]))

    def test_round_robin_agrupa_ids_aparados_preservando_ordem_e_nao_dispara_vazios(self):
        grupos = {}
        def chamar(conteudo, worker, lote_id):
            grupos[worker] = pd.read_csv(io.BytesIO(conteudo), dtype=str, keep_default_na=False).to_dict("records")
            return self.cluster.processar_worker(conteudo, worker, lote_id)
        resultado = self.cluster.executar(CSV, 2, chamar)
        self.assertIn("workers lógicos", resultado["modo"])
        self.assertIn("invocações", resultado["modo"].lower())
        self.assertEqual([x["case_id"].strip() for x in grupos[1]], ["001", "003", "001", "005", "003", ""])
        self.assertEqual([x["case_id"].strip() for x in grupos[2]], ["002", "004", "002", "006"])
        resultado = self.cluster.executar(b"case_id,description,neighborhood\n001,Relato,Centro\n", 4)
        self.assertEqual(resultado["workers_executados"], 1)
        self.assertEqual(resultado["execucoes"][0]["worker"], 1)

    def test_parser_preserva_na_zeros_aspas_e_quebras_dentro_do_campo(self):
        entrada = b'case_id,description,neighborhood\n007,"Relato, com\nquebra",NA\n008,Outro,NULL\n'
        resultado = self.cluster.executar(entrada, 2)
        self.assertEqual([(x["case_id"], x["description"], x["neighborhood"]) for x in resultado["registros"]],
                         [("007", "Relato, com\nquebra", "NA"), ("008", "Outro", "NULL")])

    def test_cabecalho_sem_registros_nao_dispara_workers(self):
        def chamar(*args):
            self.fail("Não deve disparar worker vazio.")
        resultado = self.cluster.executar(b"case_id,description,neighborhood\n", 4, chamar)
        self.assertEqual(resultado["workers_executados"], 0)
        self.assertEqual(resultado["resumo"]["read"], 0)
        self.assertEqual(resultado["registros"], [])

    def test_limites_e_csv_invalido_falham_antes_de_disparar_workers(self):
        invalidos = [b"", b"x" * (1024 * 1024 + 1), b"id,texto\n1,abc\n",
                     b"case_id,description,neighborhood\n1,a,b,c\n", b"\xff",
                     b'case_id,description,neighborhood\n1,"aspas,Centro\n',
                     b"case_id,description,neighborhood\n" + b"1,a,b\n" * 1001]
        def chamar(*args):
            self.fail("Entrada inválida não deve disparar worker.")
        for entrada in invalidos:
            with self.subTest(entrada=entrada[:60]), self.assertRaises(ValueError):
                self.cluster.executar(entrada, 2, chamar)
        for workers in (0, 1, 3, 5, True, 2.0, "2"):
            with self.subTest(workers=workers), self.assertRaises(ValueError):
                self.cluster.executar(CSV, workers, chamar)

    def test_limite_de_mil_registros_e_aceito(self):
        entrada = b"case_id,description,neighborhood\n" + b"001,Relato,Centro\n" * 1000
        self.assertEqual(self.cluster.executar(entrada, 2)["resumo"]["duplicates"], 999)

    def test_csv_no_limite_nao_estoura_worker_ao_serializar_aspas_em_campo_nao_cotado(self):
        cabecalho = b"case_id,description,neighborhood\n"
        inicio = b"001,a"
        final = b",Centro\n"
        aspas, sobra = divmod(1024 * 1024 - len(cabecalho) - 1000 * (len(inicio) + len(final)), 1000)
        entrada = cabecalho + b"".join(inicio + b'"' * (aspas + (i < sobra)) + final for i in range(1000))
        self.assertEqual(len(entrada), 1024 * 1024)
        resultado = self.cluster.executar(entrada, 2)
        self.assertEqual(resultado["resumo"]["valid"], 1)
        self.assertEqual(resultado["resumo"]["duplicates"], 999)
        self.assertEqual(resultado["registros"][0]["description"], 'a' + '"' * (aspas + 1))

    def test_csv_no_limite_sem_lf_final_nao_cresce_ao_particionar(self):
        inicio = (b"case_id,description,neighborhood\n"
                  b"001,Calcada danificada no teste,Centro\n001,")
        final = b",Centro"
        entrada = inicio + b"a" * (1024 * 1024 - len(inicio) - len(final)) + final
        self.assertEqual(len(entrada), 1024 * 1024)
        resultado = self.cluster.executar(entrada, 2)
        self.assertEqual(resultado["resumo"]["valid"], 1)
        self.assertEqual(resultado["resumo"]["duplicates"], 1)
        self.assertEqual(resultado["registros"][0]["description"], "Calcada danificada no teste")

    def test_espera_todos_os_workers_e_nao_retorna_parcial_em_falha(self):
        terminou = threading.Event()
        falhou = threading.Event()
        def chamar(conteudo, worker, lote_id):
            if worker == 1:
                falhou.set()
                raise RuntimeError("indisponível")
            self.assertTrue(falhou.wait(3))
            resultado = self.cluster.processar_worker(conteudo, worker, lote_id)
            terminou.set()
            return resultado
        with self.assertRaises(RuntimeError):
            self.cluster.executar(CSV, 2, chamar)
        self.assertTrue(terminou.is_set())

    def test_rejeita_identidade_incorreta_ids_estranhos_repetidos_ou_ausentes(self):
        def lote_incorreto(r): r["lote_id"] = "outro"
        def worker_incorreto(r): r["worker"] = 99
        def hash_incorreto(r): r["entrada_sha256"] = "0" * 64
        def id_estranho(r): r["registros"][0]["case_id"] = "999"
        def id_repetido(r): r["registros"].append(copy.deepcopy(r["registros"][0]))
        def id_ausente(r): r["registros"].pop()
        def alterado(r): r["registros"][0]["description"] = "Outra descrição"
        for adulterar in (lote_incorreto, worker_incorreto, hash_incorreto, id_estranho, id_repetido, id_ausente, alterado):
            def chamar(conteudo, worker, lote_id):
                resultado = self.cluster.processar_worker(conteudo, worker, lote_id)
                if worker == 1:
                    adulterar(resultado)
                return resultado
            with self.subTest(adulterar=adulterar.__name__), self.assertRaises(RuntimeError):
                self.cluster.executar(CSV, 2, chamar)

    def test_rejeita_schema_tipos_e_contagens_bogus(self):
        def rejeitado_incorreto(r): r["rejeitados"][0]["row_number"] = 999
        def resumo_incorreto(r): r["resumo"]["read"] = 999
        def tempo_incorreto(r): r["tempo_ms"] = float("nan")
        def instancia_incorreta(r): r["instancia"] = ""
        def triagem_incorreta(r): r["registros"][0]["triagem_original"]["review_required"] = "False"
        def confianca_incorreta(r): r["registros"][0]["triagem_original"]["confidence"] = float("nan")
        def prioridade_incorreta(r): r["registros"][0]["triagem_original"]["priority"] = "Urgente"
        def registros_incorretos(r): r["registros"] = {}
        for adulterar in (rejeitado_incorreto, resumo_incorreto, tempo_incorreto, instancia_incorreta,
                          triagem_incorreta, confianca_incorreta, prioridade_incorreta, registros_incorretos):
            def chamar(conteudo, worker, lote_id):
                resultado = self.cluster.processar_worker(conteudo, worker, lote_id)
                if worker == 1:
                    adulterar(resultado)
                return resultado
            with self.subTest(adulterar=adulterar.__name__), self.assertRaises(RuntimeError):
                self.cluster.executar(CSV, 2, chamar)

    def test_worker_rejeita_booleano_ambiguo_do_pipeline(self):
        resultado = modulos.importar_lote(CSV)
        resultado["registros"][0]["review_required"] = "talvez"
        with patch.object(modulos, "importar_lote", return_value=resultado), self.assertRaises(ValueError):
            self.cluster.processar_worker(CSV, 1, "lote")

    def test_http_fixa_destino_sem_proxy_redirect_e_preserva_csv(self):
        observado = {}
        def responder(request):
            import json
            observado["request"] = request
            observado["payload"] = json.loads(request.content)
            return httpx.Response(200, json={"ok": True})
        cliente_real = httpx.Client
        def cliente(**opcoes):
            observado["opcoes"] = opcoes
            return cliente_real(**opcoes, transport=httpx.MockTransport(responder))
        with patch.object(self.cluster.httpx, "Client", side_effect=cliente):
            saida = self.cluster.chamar_http(CSV, 2, "lote", "chave-teste")
        self.assertEqual(saida, {"ok": True})
        self.assertEqual(str(observado["request"].url), "https://gov262.vercel.app/api/cluster/worker")
        self.assertEqual(observado["request"].headers["X-Manager-Key"], "chave-teste")
        self.assertEqual(observado["payload"], {"csv": CSV.decode("utf-8"), "worker": 2, "lote_id": "lote"})
        self.assertEqual(observado["opcoes"], {"trust_env": False, "follow_redirects": False, "timeout": 45})

    def test_http_rejeita_redirect_erro_e_json_invalido(self):
        cliente_real = httpx.Client
        for status, conteudo in ((307, b"{}"), (500, b"{}"), (200, b"nao-json")):
            def responder(request):
                return httpx.Response(status, content=conteudo, headers={"location": "https://exemplo.invalid"})
            def cliente(**opcoes):
                return cliente_real(**opcoes, transport=httpx.MockTransport(responder))
            with self.subTest(status=status), patch.object(self.cluster.httpx, "Client", side_effect=cliente), self.assertRaises(RuntimeError):
                self.cluster.chamar_http(CSV, 1, "lote", "chave-teste")


if __name__ == "__main__":
    unittest.main()
