import json
import hashlib
import sqlite3
from collections import Counter
from contextlib import closing, contextmanager
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from .catalogo import preparar
from .passagem import avaliar, validar_vinculo


def agora():
    return datetime.now(timezone.utc).isoformat()


def reabrir_atendimento(caso, evidencia):
    if caso.get('atendimento'):
        evidencia['atendimento_anterior'] = caso['atendimento']
        caso['atendimento'] = {k: v for k, v in caso['atendimento'].items() if k in ('demonstracao', 'protocolo')}
        caso['atendimento'].update(etapa='reaberto', atualizado_em=agora())


class EnvioConflitante(ValueError):
    pass


class Repositorio:
    def __init__(self, caminho: Path):
        self.caminho = Path(caminho)
        self.caminho.parent.mkdir(parents=True, exist_ok=True)
        with self.conexao() as con:
            con.executescript("""
                CREATE TABLE IF NOT EXISTS atendimentos (
                    id TEXT PRIMARY KEY, origem_id TEXT UNIQUE, conteudo TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS eventos (
                    numero INTEGER PRIMARY KEY AUTOINCREMENT,
                    atendimento_id TEXT NOT NULL REFERENCES atendimentos(id),
                    conteudo TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS envios (
                    id TEXT PRIMARY KEY,
                    atendimento_id TEXT NOT NULL REFERENCES atendimentos(id),
                    assinatura TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS planos_passagem (
                    id TEXT PRIMARY KEY, conteudo TEXT NOT NULL
                );
            """)

    @contextmanager
    def conexao(self):
        with closing(sqlite3.connect(self.caminho, timeout=10)) as con:
            con.row_factory = sqlite3.Row
            con.execute("PRAGMA foreign_keys = ON")
            with con:
                yield con

    def _salvar(self, con, caso, acao, dados, autor="Sistema da demonstração"):
        caso["atualizado_em"] = agora()
        registro = {k: v for k, v in caso.items() if k != "historico"}
        con.execute(
            "INSERT INTO atendimentos (id, origem_id, conteudo) VALUES (?, ?, ?) ON CONFLICT(id) DO UPDATE SET conteudo = excluded.conteudo",
            (caso["id"], caso.get("origem_id"), json.dumps(registro, ensure_ascii=False)),
        )
        evento = {"acao": acao, "autor": autor, "data": caso["atualizado_em"], "dados": dados}
        con.execute("INSERT INTO eventos (atendimento_id, conteudo) VALUES (?, ?)",
                    (caso["id"], json.dumps(evento, ensure_ascii=False)))

    def _obter(self, con, identificador):
        row = con.execute("SELECT conteudo FROM atendimentos WHERE id = ?", (identificador,)).fetchone()
        if row is None:
            raise KeyError("Atendimento não encontrado.")
        caso = json.loads(row["conteudo"])
        caso["historico"] = [json.loads(x["conteudo"]) for x in con.execute(
            "SELECT conteudo FROM eventos WHERE atendimento_id = ? ORDER BY numero", (identificador,)
        )]
        return caso

    def criar(self, dados: dict, somente_se_novo=False) -> dict:
        entrada = {chave: dados.get(chave) for chave in (
            "descricao", "bairro", "local", "contexto", "triagem_original", "preparacao", "origem_id", "foto", "localizacao", "passagem", "sugestao_foto"
        )}
        entrada['passagem'] = validar_vinculo(entrada['passagem'])
        if not entrada["descricao"] or not entrada["bairro"]:
            raise ValueError("Informe a descrição e o bairro.")
        with self.conexao() as con:
            con.execute("BEGIN IMMEDIATE")
            envio_id = dados.get('envio_id')
            # Ausência de vínculo mantém a assinatura usada pelos envios anteriores ao Passagem Livre.
            dados_assinatura = {k: v for k, v in entrada.items() if k not in {'passagem', 'sugestao_foto'} or v is not None}
            assinatura = hashlib.sha256(json.dumps(dados_assinatura, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
            if envio_id:
                envio = con.execute('SELECT atendimento_id, assinatura FROM envios WHERE id = ?', (envio_id,)).fetchone()
                if envio:
                    if envio['assinatura'] != assinatura:
                        raise EnvioConflitante('Este envio já foi registrado com outros dados. Confira o pedido antes de iniciar outro envio.')
                    return self._obter(con, envio['atendimento_id'])
            entrada_origem = {k: entrada[k] for k in ("descricao", "bairro")}
            lote_rpa = str(entrada.get("origem_id") or "").startswith("rpa:")
            row = con.execute("SELECT id FROM atendimentos WHERE origem_id = ?", (entrada["origem_id"],)).fetchone()
            if row:
                anterior = self._obter(con, row["id"])
                if somente_se_novo:
                    return anterior
                if lote_rpa:
                    fonte_anterior = anterior.get("entrada_origem", {k: anterior[k] for k in entrada_origem})
                    if fonte_anterior == entrada_origem:
                        return anterior
                    entrada.update(local=anterior["local"], contexto=anterior["contexto"])
                    entrada.update(foto=anterior.get('foto'), localizacao=anterior.get('localizacao'),
                                   passagem=anterior.get('passagem'), sugestao_foto=anterior.get('sugestao_foto'))
                    entrada["preparacao"] = preparar(entrada["descricao"], entrada["contexto"], entrada["local"])
                if all(anterior.get(k) == v for k, v in entrada.items()):
                    return anterior
                caso = {**anterior, **entrada}
                acao = "Lote atualizado"
                evidencia = {"entrada_anterior": {k: anterior.get(k) for k in entrada},
                             "revisao_anterior": anterior.get("revisao"), "frontend_anterior": anterior.get("frontend")}
                reabrir_atendimento(caso, evidencia)
                caso.pop("frontend", None)
            else:
                caso = {**entrada, "id": str(uuid4()), "criado_em": agora(), "protocolo_oficial": None}
                acao = "Atendimento registrado"
                evidencia = {"triagem_original": entrada["triagem_original"], "origem_id": entrada["origem_id"],
                             'foto': entrada['foto'], 'localizacao': entrada['localizacao']}
                if entrada.get('sugestao_foto'):
                    evidencia['sugestao_foto'] = entrada['sugestao_foto']
            if lote_rpa:
                caso["entrada_origem"] = entrada_origem
            analise = entrada["triagem_original"] or {}
            caso.update(
                exige_revisao=bool(entrada.get('passagem') or analise.get("review_required") or analise.get("category") == "Acessibilidade"),
                revisao=None,
                situacao="Aguardando revisão",
                modo="Demonstração local",
            )
            self._salvar(con, caso, acao, evidencia)
            if envio_id:
                con.execute('INSERT INTO envios (id, atendimento_id, assinatura) VALUES (?, ?, ?)', (envio_id, caso['id'], assinatura))
            return self._obter(con, caso["id"])

    def listar(self) -> list[dict]:
        with self.conexao() as con:
            return [json.loads(row["conteudo"]) for row in con.execute(
                "SELECT conteudo FROM atendimentos ORDER BY rowid DESC"
            )]

    def obter(self, identificador: str) -> dict | None:
        with self.conexao() as con:
            try:
                return self._obter(con, identificador)
            except KeyError:
                return None

    def atualizar(self, identificador, dados):
        campos = ("descricao", "bairro", "local", "contexto", "triagem_original", "preparacao", "foto", "localizacao", "passagem", "sugestao_foto")
        with self.conexao() as con:
            con.execute("BEGIN IMMEDIATE")
            caso = self._obter(con, identificador)
            dados = {**{k: caso.get(k) for k in campos}, **dados}
            dados['passagem'] = validar_vinculo(dados.get('passagem'))
            if all(caso.get(k) == dados[k] for k in campos):
                return caso
            evidencia = {"entrada_anterior": {k: caso.get(k) for k in campos},
                         "revisao_anterior": caso.get("revisao"), "frontend_anterior": caso.pop("frontend", None)}
            caso.update({k: dados[k] for k in campos})
            reabrir_atendimento(caso, evidencia)
            analise = dados["triagem_original"]
            caso.update(revisao=None, exige_revisao=bool(dados.get('passagem') or analise.get("review_required") or analise.get("category") == "Acessibilidade"),
                        situacao="Aguardando revisão")
            self._salvar(con, caso, "Informações atualizadas", evidencia, "Solicitante da demonstração")
            return self._obter(con, identificador)

    def revisar(self, identificador, prioridade, justificativa, revisor):
        if prioridade not in ("Baixa", "Média", "Alta"):
            raise ValueError("Selecione uma prioridade válida.")
        if len(justificativa.strip()) < 10 or len(revisor.strip()) < 2:
            raise ValueError("Informe o responsável e uma justificativa de pelo menos 10 caracteres.")
        with self.conexao() as con:
            con.execute("BEGIN IMMEDIATE")
            caso = self._obter(con, identificador)
            revisao = {"prioridade": prioridade, "justificativa": justificativa.strip(),
                       "revisor": revisor.strip(), "data": agora()}
            caso["revisao"] = revisao
            caso["situacao"] = "Revisado; faltam informações" if caso["preparacao"].get("faltantes") else "Preparado para encaminhar"
            evidencia = {**revisao, 'frontend_anterior': caso.pop('frontend', None)}
            if caso.get('atendimento', {}).get('etapa') == 'correcao_verificada':
                reabrir_atendimento(caso, evidencia)
            self._salvar(con, caso, 'Decisão revisada', evidencia, revisor.strip())
            return self._obter(con, identificador)

    def contestar(self, identificador, motivo):
        if len(motivo.strip()) < 10:
            raise ValueError("Explique o motivo em pelo menos 10 caracteres.")
        with self.conexao() as con:
            con.execute("BEGIN IMMEDIATE")
            caso = self._obter(con, identificador)
            evidencia = {"motivo": motivo.strip(), "revisao_anterior": caso.get("revisao"),
                         "frontend_anterior": caso.pop("frontend", None)}
            reabrir_atendimento(caso, evidencia)
            caso.update(revisao=None, exige_revisao=True, situacao="Nova revisão solicitada")
            self._salvar(con, caso, "Nova análise solicitada", evidencia, "Solicitante da demonstração")
            return self._obter(con, identificador)

    def informar_protocolo(self, identificador, protocolo, demonstracao=False):
        if not 1 <= len(protocolo.strip()) <= 80:
            raise ValueError("Informe um protocolo de até 80 caracteres.")
        with self.conexao() as con:
            con.execute("BEGIN IMMEDIATE")
            caso = self._obter(con, identificador)
            atendimento = caso.get('atendimento') or {}
            anterior = atendimento.get('protocolo') or caso.get('protocolo_oficial')
            if anterior:
                if bool(atendimento.get('demonstracao')) != demonstracao:
                    raise ValueError('Use outro pedido para demonstrar o fluxo. Não misture protocolo declarado e demonstração.')
                if atendimento and anterior['numero'] == protocolo.strip():
                    return caso
                if atendimento.get('etapa') == 'correcao_verificada':
                    raise ValueError('Solicite nova análise antes de substituir o protocolo de um caso encerrado.')
            registro = {"numero": protocolo.strip(), "origem": "Informado pelo usuário",
                        "verificado_no_orgao": False, "data": agora()}
            if demonstracao:
                registro['origem'] = 'Protocolo fictício de demonstração'
            caso['protocolo_oficial'] = None if demonstracao else registro
            caso['atendimento'] = dict(etapa='protocolo_informado', demonstracao=demonstracao, protocolo=registro)
            self._salvar(con, caso, 'Protocolo de demonstração anotado' if demonstracao else 'Protocolo externo informado',
                         {**registro, 'atendimento_anterior': atendimento}, 'Solicitante')
            return self._obter(con, identificador)

    def registrar_retorno(self, identificador, etapa, relato, foto=None):
        if etapa not in {'em_atendimento', 'sem_solucao', 'correcao_informada'} or not 10 <= len(relato.strip()) <= 1000:
            raise ValueError('Informe a situação e um relato de 10 a 1000 caracteres.')
        with self.conexao() as con:
            con.execute('BEGIN IMMEDIATE')
            caso = self._obter(con, identificador)
            atendimento = caso.get('atendimento')
            if not atendimento:
                raise ValueError('Anote um protocolo declarado ou de demonstração antes de registrar o retorno.')
            if atendimento['etapa'] == 'correcao_verificada':
                raise ValueError('Solicite nova análise para reabrir este acompanhamento.')
            if etapa == 'correcao_informada' and (not foto or foto.get('sha256') == (caso.get('foto') or {}).get('sha256')):
                raise ValueError('Anexe uma nova foto do local após a correção, diferente da foto inicial.')
            if etapa != 'correcao_informada' and foto:
                raise ValueError('Use a foto posterior somente ao informar uma possível correção.')
            retorno = dict(relato=relato.strip(), foto=foto, data=agora(), origem='Relato do usuário, sem confirmação do órgão')
            caso['atendimento'] = {k: v for k, v in atendimento.items() if k in ('demonstracao', 'protocolo')}
            caso['atendimento'].update(etapa=etapa, retorno=retorno)
            self._salvar(con, caso, 'Retorno do atendimento anotado',
                         {**caso['atendimento'], 'atendimento_anterior': atendimento}, 'Solicitante')
            return self._obter(con, identificador)

    def verificar_correcao(self, identificador, revisor, justificativa, base):
        if not 2 <= len(revisor.strip()) <= 80 or not 10 <= len(justificativa.strip()) <= 500:
            raise ValueError('Informe responsável e justificativa da conferência.')
        with self.conexao() as con:
            con.execute('BEGIN IMMEDIATE')
            caso = self._obter(con, identificador)
            if caso['atualizado_em'] != base:
                raise EnvioConflitante('O pedido ou a foto posterior mudou. Atualize e confira a evidência atual antes de confirmar.')
            atendimento = caso.get('atendimento') or {}
            if (atendimento.get('etapa') != 'correcao_informada' or not atendimento.get('retorno', {}).get('foto')
                    or not caso.get('revisao') or not caso.get('frontend')):
                raise ValueError('Conclua a revisão, confirme o registro local e anexe uma foto posterior antes de conferir a correção.')
            conferencia = dict(revisor=revisor.strip(), justificativa=justificativa.strip(), data=agora(),
                               alcance='Conferência humana do protótipo; não é vistoria técnica nem confirmação municipal')
            atendimento.update(etapa='correcao_verificada', conferencia=conferencia)
            self._salvar(con, caso, 'Correção conferida no protótipo', conferencia, revisor.strip())
            return self._obter(con, identificador)

    def vincular_frontend(self, identificador, registro, revisao):
        with self.conexao() as con:
            con.execute("BEGIN IMMEDIATE")
            caso = self._obter(con, identificador)
            if not revisao or caso.get("revisao") != revisao:
                raise ValueError("A decisão mudou durante a confirmação. Confira a revisão atual e tente novamente.")
            if caso.get("frontend", {}).get("id") == registro["id"]:
                return caso
            caso["frontend"] = {**registro, "origem": "Persistência do ZelaBairro; protocolo local"}
            self._salvar(con, caso, "Registro confirmado no ZelaBairro", caso["frontend"], caso["revisao"]["revisor"])
            return self._obter(con, identificador)

    def adicionar_evidencia(self, identificador, modulo, resultado):
        with self.conexao() as con:
            con.execute("BEGIN IMMEDIATE")
            caso = self._obter(con, identificador)
            evidencia = {"modulo": modulo, "data": agora(), "resultado": resultado}
            caso.setdefault("evidencias", []).append(evidencia)
            self._salvar(con, caso, "Evidência vinculada", evidencia)
            return self._obter(con, identificador)

    def planos_passagem(self):
        with self.conexao() as con:
            return [json.loads(row['conteudo']) for row in con.execute(
                'SELECT conteudo FROM planos_passagem ORDER BY rowid DESC')]

    def planejar_passagem(self, base, reparos, revisor, justificativa):
        with self.conexao() as con:
            con.execute('BEGIN IMMEDIATE')
            casos = [json.loads(row['conteudo']) for row in con.execute('SELECT conteudo FROM atendimentos')]
            resultado = avaliar(casos, reparos)
            if resultado['base'] != base:
                raise EnvioConflitante('Os pedidos mudaram. Atualize o percurso e confira a simulação antes de decidir.')
            if resultado['pendentes_revisao']:
                raise EnvioConflitante('Revise todos os pedidos vinculados antes de registrar o plano.')
            if not reparos or not any(t['atual'] == 'barreira' and t['id'] in reparos for t in resultado['trechos']):
                raise ValueError('Selecione pelo menos um trecho com barreira informada.')
            plano = {'id': str(uuid4()), 'data': agora(), 'base': base, 'reparos': resultado['reparos'],
                     'revisor': revisor, 'justificativa': justificativa, 'resultado': resultado}
            con.execute('INSERT INTO planos_passagem (id, conteudo) VALUES (?, ?)',
                        (plano['id'], json.dumps(plano, ensure_ascii=False)))
            return plano

    def indicadores(self) -> dict:
        casos = self.listar()
        revisados = [c for c in casos if c.get("revisao")]
        corrigidos = sum(c["revisao"]["prioridade"] != c["triagem_original"].get("priority") for c in revisados)
        return {
            "total": len(casos), "revisados": len(revisados),
            "revisoes_pendentes": sum(c["exige_revisao"] and not c.get("revisao") for c in casos),
            "sugestoes_corrigidas": corrigidos, "denominador_correcoes": len(revisados),
            "protocolos_informados": sum(bool(c.get("protocolo_oficial")) for c in casos),
            'protocolos_demonstracao': sum(bool(c.get('atendimento', {}).get('demonstracao')) for c in casos),
            'sem_protocolo': sum(not c.get('atendimento') and not c.get('protocolo_oficial') for c in casos),
            'correcoes_informadas': sum(c.get('atendimento', {}).get('etapa') == 'correcao_informada' for c in casos),
            'correcoes_conferidas': sum(c.get('atendimento', {}).get('etapa') == 'correcao_verificada' and not c['atendimento'].get('demonstracao') for c in casos),
            'correcoes_demo': sum(c.get('atendimento', {}).get('etapa') == 'correcao_verificada' and c['atendimento'].get('demonstracao') for c in casos),
            "com_fonte": sum(bool(c["preparacao"].get("fonte")) for c in casos),
            "por_categoria": dict(Counter(c["triagem_original"].get("category", "Sem categoria") for c in casos)),
            "por_situacao": dict(Counter(c["situacao"] for c in casos)),
            "alcance": "Registros desta demonstração local. Não mede demanda municipal, reparos executados ou benefício validado em campo.",
        }
