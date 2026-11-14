from contextlib import closing
from pathlib import Path
import logging
import re
import sqlite3
import tempfile
import unicodedata
import pandas as pd
COLUNAS_OBRIGATORIAS = {'case_id', 'description', 'neighborhood'}
PALAVRAS_POR_CATEGORIA = {'Iluminação pública': ['iluminacao', 'poste', 'postes', 'lampada', 'lampadas', 'luz apagada'], 'Buraco ou pavimento': ['buraco', 'buracos', 'cratera', 'crateras', 'pavimento danificado'], 'Resíduos e limpeza': ['lixo', 'entulho', 'residuos', 'coleta'], 'Acessibilidade': ['rampa', 'rampas', 'calcada', 'calcadas', 'acessibilidade', 'piso tatil']}
CATEGORIAS_PRIORIDADE_MEDIA = ('Iluminação pública', 'Buraco ou pavimento', 'Resíduos e limpeza')
PADRAO_RISCO = '\\b(?:fio[s]? caido[s]?|fio[s]? exposto[s]?|fiacao exposta|risco de choque|faisca[s]?|alagamento[s]?|queda iminente)\\b'
NEGACAO_EXPLICITA = '\\b(?:sem|nao ha) (?:risco de choque|faisca[s]?|alagamento[s]?)\\b'

def normalizar(texto: str) -> str:
    texto = unicodedata.normalize('NFKD', texto.lower())
    texto = ''.join((c for c in texto if not unicodedata.combining(c)))
    texto = re.sub('[^\\w\\s]', ' ', texto)
    return re.sub('\\s+', ' ', texto).strip()

def classificar_solicitacao(descricao: str) -> dict:
    texto = normalizar(descricao)
    pontuacoes = {categoria: sum((bool(re.search(f'\\b{re.escape(termo)}\\b', texto)) for termo in termos)) for categoria, termos in PALAVRAS_POR_CATEGORIA.items()}
    maior_pontuacao = max(pontuacoes.values())
    melhores = [categoria for categoria, pontos in pontuacoes.items() if pontos == maior_pontuacao]
    categoria = melhores[0] if maior_pontuacao and len(melhores) == 1 else 'Outros'
    confianca = min(maior_pontuacao / 2, 1.0) if categoria != 'Outros' else 0.0
    revisao = confianca < 1.0
    texto_risco = re.sub(NEGACAO_EXPLICITA, '', texto)
    if re.search(PADRAO_RISCO, texto_risco):
        prioridade, revisao = ('Alta', True)
    elif any((pontuacoes[categoria] for categoria in CATEGORIAS_PRIORIDADE_MEDIA)):
        prioridade = 'Média'
    else:
        prioridade = 'Baixa'
    return {'category': categoria, 'priority': prioridade, 'confidence': confianca, 'review_required': revisao}
COLUNAS_RELATORIO = ['case_id', 'description', 'neighborhood', 'category', 'priority', 'confidence', 'review_required']

def criar_banco(con: sqlite3.Connection) -> None:
    con.execute('CREATE TABLE IF NOT EXISTS requests (\n        case_id TEXT PRIMARY KEY, description TEXT NOT NULL, neighborhood TEXT NOT NULL,\n        category TEXT NOT NULL, priority TEXT NOT NULL, confidence REAL NOT NULL,\n        review_required INTEGER NOT NULL)')

def executar_pipeline(caminho_csv: Path, pasta_saida: Path, caminho_banco: Path) -> dict:
    logger = logging.Logger('citizentech', logging.INFO)
    arquivo_log = None
    try:
        arquivos_gerados = (caminho_banco, pasta_saida / 'execucao.log', pasta_saida / 'solicitacoes_processadas.csv', pasta_saida / 'registros_rejeitados.csv')
        if caminho_csv.resolve() in {arquivo.resolve() for arquivo in arquivos_gerados}:
            mensagem = 'O CSV de entrada deve ter um caminho diferente dos arquivos gerados.'
            logging.getLogger('citizentech').error(mensagem)
            return {'status': 'erro', 'message': mensagem}
        pasta_saida.mkdir(parents=True, exist_ok=True)
        arquivo_log = logging.FileHandler(pasta_saida / 'execucao.log', encoding='utf-8')
        arquivo_log.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
        logger.addHandler(arquivo_log)
        df = pd.read_csv(caminho_csv, dtype=str, keep_default_na=False, encoding='utf-8-sig')
        faltantes = COLUNAS_OBRIGATORIAS - set(df.columns)
        if faltantes:
            mensagem = 'Colunas obrigatórias ausentes: ' + ', '.join(sorted(faltantes))
            logger.error(mensagem)
            return {'status': 'erro', 'message': mensagem}
        if not isinstance(df.index, pd.RangeIndex):
            mensagem = 'O CSV contém linhas com mais campos do que o cabeçalho.'
            logger.error(mensagem)
            return {'status': 'erro', 'message': mensagem}
        processados, rejeitados, ids_vistos = ([], [], set())
        duplicados = 0
        for numero_linha, row in enumerate(df.to_dict(orient='records'), start=2):
            case_id = row['case_id'].strip()
            descricao = row['description'].strip()
            bairro = row['neighborhood'].strip()
            if not case_id or not descricao or (not bairro):
                rejeitados.append({'row_number': numero_linha, 'case_id': case_id, 'reason': 'case_id, description e neighborhood são obrigatórios'})
                continue
            if case_id in ids_vistos:
                duplicados += 1
                logger.info('Linha %s ignorada por ID repetido no lote', numero_linha)
                continue
            ids_vistos.add(case_id)
            processados.append({'case_id': case_id, 'description': descricao, 'neighborhood': bairro, **classificar_solicitacao(descricao)})
        inseridos = atualizados = 0
        caminho_banco.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=pasta_saida) as pasta_temporaria:
            classificados = Path(pasta_temporaria) / 'solicitacoes_processadas.csv'
            invalidos = Path(pasta_temporaria) / 'registros_rejeitados.csv'
            pd.DataFrame(processados, columns=COLUNAS_RELATORIO).to_csv(classificados, index=False, encoding='utf-8')
            pd.DataFrame(rejeitados, columns=['row_number', 'case_id', 'reason']).to_csv(invalidos, index=False, encoding='utf-8')
            with closing(sqlite3.connect(caminho_banco)) as con, con:
                con.execute('BEGIN IMMEDIATE')
                criar_banco(con)
                for item in processados:
                    valores = tuple((item[coluna] for coluna in COLUNAS_RELATORIO))
                    anterior = con.execute('SELECT description, neighborhood, category,\n                        priority, confidence, review_required FROM requests WHERE case_id = ?', (item['case_id'],)).fetchone()
                    if anterior == valores[1:]:
                        continue
                    con.execute('INSERT INTO requests\n                        (case_id, description, neighborhood, category, priority, confidence, review_required)\n                        VALUES (?, ?, ?, ?, ?, ?, ?)\n                        ON CONFLICT(case_id) DO UPDATE SET\n                            description = excluded.description, neighborhood = excluded.neighborhood,\n                            category = excluded.category, priority = excluded.priority,\n                            confidence = excluded.confidence, review_required = excluded.review_required', valores)
                    inseridos += anterior is None
                    atualizados += anterior is not None
                invalidos.replace(pasta_saida / invalidos.name)
                classificados.replace(pasta_saida / classificados.name)
        logger.info('Lidos=%s válidos=%s novos=%s atualizados=%s rejeitados=%s duplicados=%s', len(df), len(processados), inseridos, atualizados, len(rejeitados), duplicados)
        return {'status': 'ok', 'read': len(df), 'valid': len(processados), 'inserted': inseridos, 'updated': atualizados, 'rejected': len(rejeitados), 'duplicates': duplicados, 'review_required': sum((item['review_required'] for item in processados))}
    except (OSError, sqlite3.Error, pd.errors.EmptyDataError, pd.errors.ParserError, UnicodeDecodeError) as exc:
        if isinstance(exc, FileNotFoundError) and exc.filename and (Path(exc.filename) == caminho_csv):
            mensagem = 'Arquivo de entrada não encontrado.'
        elif isinstance(exc, (pd.errors.EmptyDataError, pd.errors.ParserError, UnicodeDecodeError)):
            mensagem = f'CSV inválido ou ilegível: {exc}'
        else:
            mensagem = f'Falha no processamento: {exc}'
        destino_log = logger if arquivo_log is not None else logging.getLogger('citizentech')
        destino_log.error(mensagem)
        return {'status': 'erro', 'message': mensagem}
    finally:
        if arquivo_log is not None:
            arquivo_log.close()
