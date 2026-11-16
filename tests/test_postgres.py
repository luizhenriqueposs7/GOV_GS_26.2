"""Integração real: GOV_TEST_DATABASE_URL deve apontar para Postgres local.

O teste cria e remove somente um banco novo, com nome aleatório. Sem essa
configuração, os testes de integração são explicitamente ignorados.
"""
import importlib.util
import os
import unittest
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from pathlib import Path
from threading import Event
from unittest.mock import patch
from urllib.parse import parse_qsl, urlencode, urlsplit
from uuid import uuid4


class ConfiguracaoPostgresTest(unittest.TestCase):
    def test_dsn_invalido_e_rejeitado_antes_de_abrir_conexao(self):
        self.assertIsNotNone(importlib.util.find_spec('central.postgres'),
                             'O repositório Postgres ainda não foi implementado.')
        from central.postgres import RepositorioPostgres
        for dsn in ('', 'sqlite:///arquivo', 'postgresql:///sem-servidor'):
            with self.subTest(dsn=dsn), self.assertRaises(ValueError):
                RepositorioPostgres(dsn)


@unittest.skipUnless(os.getenv('GOV_TEST_DATABASE_URL'),
                     'Postgres real não configurado: GOV_TEST_DATABASE_URL.')
class PostgresRealTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import psycopg
        from psycopg import sql
        from psycopg.rows import dict_row

        dsn = os.environ['GOV_TEST_DATABASE_URL']
        if urlsplit(dsn).hostname not in {'localhost', '127.0.0.1', '::1'}:
            raise ValueError('Os testes só criam bancos temporários em Postgres local.')
        cls.admin_dsn = dsn
        cls.nome_banco = 'citizentech_test_' + uuid4().hex
        with psycopg.connect(dsn, autocommit=True) as con:
            con.execute(sql.SQL('CREATE DATABASE {}').format(sql.Identifier(cls.nome_banco)))
        cls.addClassCleanup(cls.remover_banco)
        cls.dsn = urlsplit(dsn)._replace(path='/' + cls.nome_banco).geturl()
        cls.conectar = staticmethod(lambda: psycopg.connect(cls.dsn, row_factory=dict_row))
        migracoes = sorted((Path(__file__).resolve().parents[1] / 'supabase/migrations').glob('*.sql'))
        if not migracoes:
            raise AssertionError('A migração Postgres ainda não foi criada.')
        with cls.conectar() as con:
            for migracao in migracoes:
                con.execute(migracao.read_text(encoding='utf-8'))

    @classmethod
    def remover_banco(cls):
        import psycopg
        from psycopg import sql
        with psycopg.connect(cls.admin_dsn, autocommit=True) as con:
            con.execute(sql.SQL('DROP DATABASE {} WITH (FORCE)').format(sql.Identifier(cls.nome_banco)))

    def setUp(self):
        from central.postgres import RepositorioPostgres
        self.repo = RepositorioPostgres(self.dsn)
        with self.conectar() as con:
            con.execute('TRUNCATE citizentech.eventos, citizentech.envios, '
                        'citizentech.atendimentos, citizentech.planos_passagem, '
                        'citizentech.relatos RESTART IDENTITY')

    def dados(self, **alteracoes):
        return {
            'descricao': 'Calçada sem rampa acessível: 50%? :id',
            'bairro': 'Bairro fictício', 'local': 'Praça de demonstração',
            'contexto': 'area_publica',
            'triagem_original': {'category': 'Acessibilidade', 'priority': 'Baixa'},
            'preparacao': {'faltantes': [], 'fonte': None}, **alteracoes,
        }

    def revisado(self, **alteracoes):
        caso = self.repo.criar(self.dados(**alteracoes))
        return self.repo.revisar(caso['id'], 'Alta', 'Barreira conferida no cenário.', 'Revisor')

    def relatos(self):
        with self.conectar() as con:
            return con.execute('SELECT * FROM citizentech.relatos').fetchall()

    def test_dialeto_preserva_dados_ordem_historico_e_tls(self):
        primeiro = self.repo.criar(self.dados())
        segundo = self.repo.criar(self.dados(descricao='Segundo atendimento de demonstração'))
        self.assertEqual([c['id'] for c in self.repo.listar()], [segundo['id'], primeiro['id']])
        self.assertEqual(self.repo.obter(primeiro['id'])['descricao'], self.dados()['descricao'])
        self.assertEqual(len(self.repo.obter(primeiro['id'])['historico']), 1)
        self.assertEqual(primeiro['modo'], 'Demonstração online')
        self.assertIn('demonstração online', self.repo.indicadores()['alcance'])
        with self.repo.conexao() as con:
            self.assertTrue(con.execute('SELECT ssl FROM pg_stat_ssl WHERE pid = pg_backend_pid()').fetchone()['ssl'])

    def test_schema_privado_sem_permissao_publica_e_com_rls(self):
        with self.conectar() as con:
            publico = con.execute("SELECT count(*) AS total FROM pg_namespace n, "
                "LATERAL aclexplode(coalesce(n.nspacl, acldefault('n', n.nspowner))) a "
                "WHERE n.nspname = 'citizentech' AND a.grantee = 0").fetchone()
            tabelas = con.execute("SELECT relname, relrowsecurity FROM pg_class c "
                "JOIN pg_namespace n ON n.oid = c.relnamespace "
                "WHERE n.nspname = 'citizentech' AND c.relkind = 'r'").fetchall()
        self.assertEqual(publico['total'], 0)
        self.assertEqual(len(tabelas), 5)
        self.assertTrue(all(t['relrowsecurity'] for t in tabelas))

    def test_rollback_desfaz_caso_evento_e_chave_de_reenvio(self):
        with self.assertRaisesRegex(RuntimeError, 'Falha proposital'):
            with self.repo.conexao():
                self.repo.criar(self.dados(envio_id='envio-desfeito'))
                raise RuntimeError('Falha proposital')
        self.assertEqual(self.repo.listar(), [])
        with self.conectar() as con:
            for tabela in ('eventos', 'envios'):
                self.assertEqual(con.execute('SELECT count(*) AS total FROM citizentech.' + tabela).fetchone()['total'], 0)
        self.assertTrue(self.repo.criar(self.dados(envio_id='envio-desfeito'))['id'])

    def test_erro_sql_nao_expoe_consulta_ou_credenciais_na_resposta(self):
        with self.assertRaises(RuntimeError) as erro:
            with self.repo.conexao() as con:
                con.execute('SELECT dado_privado_que_nao_pode_aparecer')
        self.assertNotIn('dado_privado', str(erro.exception))
        self.assertNotIn(self.dsn, str(erro.exception))
        self.assertTrue(erro.exception.__suppress_context__)

    def test_tls_nao_rebaixa_validacao_de_certificado_configurada(self):
        from central.postgres import RepositorioPostgres
        partes = urlsplit(self.dsn)
        parametros = dict(parse_qsl(partes.query))
        parametros.update(sslmode='verify-full',
                          sslrootcert=str(Path(__file__).with_name(uuid4().hex + '.crt')))
        repo = RepositorioPostgres(partes._replace(query=urlencode(parametros)).geturl())
        with self.assertRaises(RuntimeError):
            with repo.conexao() as con:
                con.execute('SELECT 1')

    def test_envio_concorrente_e_idempotente_e_rejeita_conteudo_diferente(self):
        from central.postgres import RepositorioPostgres
        from central.registros import EnvioConflitante
        dados = self.dados(envio_id='envio-repetido')
        with ThreadPoolExecutor(max_workers=4) as pool:
            resultados = list(pool.map(lambda _: RepositorioPostgres(self.dsn).criar(dados), range(4)))
        self.assertEqual(len({c['id'] for c in resultados}), 1)
        self.assertEqual(len(self.repo.listar()), 1)
        self.assertEqual(len(resultados[-1]['historico']), 1)
        with self.assertRaises(EnvioConflitante):
            self.repo.criar({**dados, 'descricao': 'Outros dados para o mesmo envio'})

    def test_confirmacao_reusa_frontend_original_sem_duplicar_ou_alterar_modulo_global(self):
        from materiais.frontend.backend.providers import repository
        conectar_original = repository._conectar
        caso = self.revisado()
        confirmado = self.repo.confirmar_frontend(caso['id'])
        repetido = self.repo.confirmar_frontend(caso['id'])
        self.assertEqual(confirmado, repetido)
        self.assertEqual(len(self.relatos()), 1)
        self.assertEqual(confirmado['frontend']['categoria'], 'Calçada')
        self.assertEqual(confirmado['frontend']['status'], 'Recebido')
        self.assertEqual(confirmado['frontend']['origem'],
                         'Persistência do ZelaBairro em Postgres; protocolo da demonstração')
        self.assertEqual(confirmado['frontend']['cidadao_id'], caso['id'] + ':' + caso['revisao']['data'])
        self.assertIs(repository._conectar, conectar_original)

    def test_confirmacao_rejeita_revisao_ausente_ou_informacoes_faltantes(self):
        from central.registros import EnvioConflitante
        for caso in (self.repo.criar(self.dados()), self.revisado(preparacao={'faltantes': ['contexto']})):
            with self.subTest(caso=caso['id']), self.assertRaises(EnvioConflitante):
                self.repo.confirmar_frontend(caso['id'])
        self.assertEqual(self.relatos(), [])

    def test_confirmacao_aplica_validacao_original_antes_de_persistir(self):
        caso = self.revisado(descricao='curta')
        with self.assertRaises(ValueError):
            self.repo.confirmar_frontend(caso['id'])
        self.assertEqual(self.relatos(), [])
        self.assertNotIn('frontend', self.repo.obter(caso['id']))

    def test_falha_apos_insert_frontend_desfaz_relato_vinculo_e_evento(self):
        caso = self.revisado()
        salvar = self.repo._salvar

        def falhar_apos_salvar(con, registro, acao, *args):
            salvar(con, registro, acao, *args)
            if acao == 'Registro confirmado no ZelaBairro':
                raise RuntimeError('Falha proposital depois do vínculo')

        with patch.object(self.repo, '_salvar', falhar_apos_salvar), self.assertRaises(RuntimeError):
            self.repo.confirmar_frontend(caso['id'])
        self.assertEqual(self.relatos(), [])
        self.assertEqual(self.repo.obter(caso['id']), caso)
        self.assertTrue(self.repo.confirmar_frontend(caso['id'])['frontend']['id'])

    def test_contestacao_vence_confirmacao_em_outra_instancia(self):
        from central.postgres import RepositorioPostgres
        from central.registros import EnvioConflitante
        caso = self.revisado()
        iniciado = Event()

        def confirmar():
            iniciado.set()
            return RepositorioPostgres(self.dsn).confirmar_frontend(caso['id'])

        with ThreadPoolExecutor(max_workers=1) as pool:
            with self.repo.conexao() as con:
                con.execute('BEGIN IMMEDIATE')
                self.repo.contestar(caso['id'], 'A passagem precisa de nova análise.')
                futuro = pool.submit(confirmar)
                self.assertTrue(iniciado.wait(3))
                with self.assertRaises(TimeoutError):
                    futuro.result(timeout=0.2)
            with self.assertRaises(EnvioConflitante):
                futuro.result(timeout=5)
        self.assertEqual(self.relatos(), [])
        self.assertNotIn('frontend', self.repo.obter(caso['id']))

    def test_cas_herdado_rejeita_revisao_invalidada(self):
        caso = self.revisado()
        self.repo.contestar(caso['id'], 'A decisão precisa ser conferida novamente.')
        with self.assertRaises(ValueError):
            self.repo.vincular_frontend(caso['id'], {'id': 'protocolo-obsoleto'}, caso['revisao'])
        self.assertNotIn('frontend', self.repo.obter(caso['id']))

    def test_novo_pedido_concorrente_invalida_base_do_plano(self):
        from central.passagem import avaliar
        from central.postgres import RepositorioPostgres
        from central.registros import EnvioConflitante
        self.revisado(passagem={'percurso_id': 'ponto-ubs-demo', 'trecho_id': 'rampa', 'condicao': 'bloqueado'})
        base = avaliar(self.repo.listar(), ['rampa'])['base']
        iniciado = Event()

        def planejar():
            iniciado.set()
            return RepositorioPostgres(self.dsn).planejar_passagem(base, ['rampa'], 'Revisor', 'Intervenção proposta.')

        with ThreadPoolExecutor(max_workers=1) as pool:
            with self.repo.conexao():
                self.revisado(passagem={'percurso_id': 'ponto-ubs-demo', 'trecho_id': 'calcada', 'condicao': 'bloqueado'})
                futuro = pool.submit(planejar)
                self.assertTrue(iniciado.wait(3))
                with self.assertRaises(TimeoutError):
                    futuro.result(timeout=0.2)
            with self.assertRaises(EnvioConflitante):
                futuro.result(timeout=5)
        self.assertEqual(self.repo.planos_passagem(), [])

    def test_plano_valido_continua_disponivel_em_outra_instancia(self):
        from central.passagem import avaliar
        from central.postgres import RepositorioPostgres
        self.revisado(passagem={'percurso_id': 'ponto-ubs-demo', 'trecho_id': 'rampa', 'condicao': 'bloqueado'})
        base = avaliar(self.repo.listar(), ['rampa'])['base']
        plano = self.repo.planejar_passagem(base, ['rampa'], 'Revisor', 'Intervenção do cenário didático.')
        self.assertEqual(RepositorioPostgres(self.dsn).planos_passagem(), [plano])


if __name__ == '__main__':
    unittest.main()
