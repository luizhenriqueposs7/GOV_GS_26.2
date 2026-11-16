"""Persistência compartilhada que conserva o domínio da demonstração local."""
import importlib.util
import re
from contextlib import contextmanager, nullcontext
from contextvars import ContextVar
from pathlib import Path
from urllib.parse import urlsplit
from uuid import uuid4

import psycopg
from psycopg.conninfo import conninfo_to_dict
from psycopg.rows import dict_row

from .registros import EnvioConflitante, Repositorio


RAIZ = Path(__file__).resolve().parents[1]
TRAVA_ESCRITA = 7420916111601
TABELAS = re.compile(r'\b(FROM|INTO|UPDATE|JOIN)\s+(atendimentos|eventos|envios|planos_passagem|relatos)\b', re.I)


class Conexao:
    def __init__(self, conexao):
        self.conexao = conexao

    def execute(self, consulta, parametros=None):
        if consulta.strip().upper() == 'BEGIN IMMEDIATE':
            return self.conexao.execute('SELECT pg_advisory_xact_lock(%s)', (TRAVA_ESCRITA,))
        # shortcut: SQL fixo dos repositórios entregues; ampliar somente ao mudar esse contrato.
        consulta = TABELAS.sub(r'\1 citizentech.\2', consulta).replace('rowid', 'ordem')
        if isinstance(parametros, dict):
            consulta = re.sub(r':([a-zA-Z_]\w*)', r'%(\1)s', consulta)
        else:
            consulta = consulta.replace('?', '%s')
        return self.conexao.execute(consulta, parametros)


class RepositorioPostgres(Repositorio):
    def __init__(self, dsn):
        try:
            partes = urlsplit(dsn)
            valido = partes.scheme in {'postgres', 'postgresql'} and partes.hostname
            partes.port
        except (TypeError, ValueError):
            valido = False
        if not valido:
            raise ValueError('Configure uma URL PostgreSQL válida para a demonstração online.')
        self.dsn = dsn
        self._ativa = ContextVar('transacao_citizentech', default=None)

    @contextmanager
    def conexao(self):
        ativa = self._ativa.get()
        if ativa is not None:
            yield ativa
            return
        try:
            tls = conninfo_to_dict(self.dsn).get('sslmode')
            if tls not in {'require', 'verify-ca', 'verify-full'}:
                tls = 'require'
            with psycopg.connect(self.dsn, row_factory=dict_row, prepare_threshold=None,
                                 sslmode=tls, connect_timeout=10) as original:
                original.execute("SET LOCAL lock_timeout = '10s'")
                original.execute("SET LOCAL statement_timeout = '20s'")
                conexao = Conexao(original)
                token = self._ativa.set(conexao)
                try:
                    yield conexao
                finally:
                    self._ativa.reset(token)
        except psycopg.Error:
            raise RuntimeError('O banco da demonstração está indisponível. Tente novamente.') from None

    def _salvar(self, con, caso, acao, dados, autor='Sistema da demonstração'):
        caso['modo'] = 'Demonstração online'
        if acao == 'Registro confirmado no ZelaBairro':
            caso['frontend']['origem'] = 'Persistência do ZelaBairro em Postgres; protocolo da demonstração'
        return super()._salvar(con, caso, acao, dados, autor)

    def indicadores(self):
        resultado = super().indicadores()
        resultado['alcance'] = resultado['alcance'].replace('demonstração local', 'demonstração online')
        return resultado

    def confirmar_frontend(self, identificador):
        from materiais.frontend.backend.schemas.relato import CriarRelatoRequest

        with self.conexao() as con:
            con.execute('BEGIN IMMEDIATE')
            caso = self._obter(con, identificador)
            if not caso.get('revisao') or caso['preparacao']['faltantes']:
                raise EnvioConflitante('Revise a decisão e complete as informações antes de confirmar no ZelaBairro.')
            mapa = {'Acessibilidade': 'Calçada', 'Buraco ou pavimento': 'Buraco', 'Iluminação pública': 'Iluminação'}
            entrada = CriarRelatoRequest.model_validate({
                'cidadao_id': caso['id'] + ':' + caso['revisao']['data'],
                'descricao': caso['descricao'], 'bairro': caso['bairro'],
                'categoria': mapa.get(caso['triagem_original']['category'], 'Outro'),
                'prioridade': caso['revisao']['prioridade'], 'resumo': caso['descricao'][:300],
            })
            caminho = RAIZ / 'materiais/frontend/backend/providers/repository.py'
            especificacao = importlib.util.spec_from_file_location('_frontend_' + uuid4().hex, caminho)
            modulo = importlib.util.module_from_spec(especificacao)
            especificacao.loader.exec_module(modulo)
            modulo._conectar = lambda: nullcontext(con)
            existentes = modulo.listar_por_cidadao(entrada.cidadao_id)
            registro = existentes[0] if existentes else modulo.criar_relato(entrada.model_dump())
            return self.vincular_frontend(identificador, registro, caso['revisao'])
