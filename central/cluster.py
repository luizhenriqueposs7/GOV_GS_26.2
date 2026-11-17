"""Coordenação sem persistência; cada worker usa o SQLite temporário do RPA."""

import hashlib
import io
import math
import os
import time
from concurrent.futures import ThreadPoolExecutor, wait
from uuid import UUID, uuid4

import httpx
import pandas as pd

from . import modulos
from materiais.rpa.pipeline import COLUNAS_OBRIGATORIAS, PALAVRAS_POR_CATEGORIA


_INSTANCIAS = {}
_CONTAGENS = ("read", "valid", "inserted", "updated", "rejected", "duplicates", "review_required")
_MOTIVO_REJEICAO = "case_id, description e neighborhood são obrigatórios"


def _ler_csv(conteudo: bytes) -> pd.DataFrame:
    if not isinstance(conteudo, bytes) or not conteudo or len(conteudo) > 1024 * 1024:
        raise ValueError("Envie um CSV de até 1 MiB.")
    try:
        dados = pd.read_csv(io.BytesIO(conteudo), dtype=str, keep_default_na=False, encoding="utf-8-sig")
    except (pd.errors.EmptyDataError, pd.errors.ParserError, UnicodeDecodeError) as exc:
        raise ValueError("CSV inválido ou ilegível.") from exc
    if not COLUNAS_OBRIGATORIAS <= set(dados.columns):
        raise ValueError("O CSV precisa de case_id, description e neighborhood.")
    if not isinstance(dados.index, pd.RangeIndex):
        raise ValueError("O CSV contém linhas com mais campos do que o cabeçalho.")
    if len(dados) > 1000:
        raise ValueError("O lote aceita até 1.000 registros.")
    return dados


def _triagem(registro: dict) -> dict:
    categoria, prioridade = registro["category"], registro["priority"]
    if categoria not in (*PALAVRAS_POR_CATEGORIA, "Outros") or prioridade not in ("Baixa", "Média", "Alta"):
        raise ValueError("Classificação inválida do worker.")
    confianca, revisao = registro["confidence"], registro["review_required"]
    if isinstance(confianca, bool) or not isinstance(confianca, (str, int, float)):
        raise ValueError("Confiança inválida do worker.")
    confianca = float(confianca)
    if not math.isfinite(confianca) or not 0 <= confianca <= 1:
        raise ValueError("Confiança inválida do worker.")
    if type(revisao) is not bool:
        if not isinstance(revisao, str) or revisao not in ("True", "False"):
            raise ValueError("Indicador de revisão inválido do worker.")
        revisao = revisao == "True"
    return {"category": categoria, "priority": prioridade, "confidence": confianca,
            "review_required": revisao}


def processar_worker(conteudo: bytes, worker: int, lote_id: str) -> dict:
    inicio = time.perf_counter()
    if type(worker) is not int or not 1 <= worker <= 4 or not isinstance(lote_id, str) or not lote_id.strip():
        raise ValueError("Identificação de worker ou lote inválida.")
    _ler_csv(conteudo)
    resultado = modulos.importar_lote(conteudo)
    for registro in resultado["registros"]:
        registro["triagem_original"] = _triagem(registro)
    # O UUID identifica o processo; não comprova máquina física distinta.
    instancia = _INSTANCIAS.setdefault(os.getpid(), str(uuid4()))
    return {**resultado, "worker": worker, "lote_id": lote_id,
            "entrada_sha256": hashlib.sha256(conteudo).hexdigest(), "instancia": instancia,
            "tempo_ms": (time.perf_counter() - inicio) * 1000}


def _serializar(linhas: list) -> bytes:
    colunas = ("case_id", "description", "neighborhood")
    def campo(valor):
        # Pandas aceita aspas internas sem cotação; recotá-las pode dobrar um lote de 1 MiB.
        if valor.startswith('"') or any(c in valor for c in ",\r\n"):
            return '"' + valor.replace('"', '""') + '"'
        return valor
    return (",".join(colunas) + "\n" + "".join(
        ",".join(campo(linha[coluna]) for coluna in colunas) + "\n" for _, linha in linhas)).removesuffix("\n").encode("utf-8")


def _validar_resposta(resposta: dict, conteudo: bytes, worker: int, lote_id: str, linhas: list) -> tuple:
    if (not isinstance(resposta, dict) or type(resposta.get("worker")) is not int
            or resposta["worker"] != worker or resposta.get("lote_id") != lote_id
            or resposta.get("entrada_sha256") != hashlib.sha256(conteudo).hexdigest()):
        raise ValueError("Resposta de outro worker, lote ou entrada.")
    UUID(resposta["instancia"])
    tempo = resposta["tempo_ms"]
    if type(tempo) not in (int, float) or not math.isfinite(tempo) or tempo < 0:
        raise ValueError("Tempo inválido do worker.")
    registros, rejeitados, resumo = resposta["registros"], resposta["rejeitados"], resposta["resumo"]
    if not isinstance(registros, list) or not isinstance(rejeitados, list) or not isinstance(resumo, dict):
        raise ValueError("Estrutura inválida do worker.")
    esperados, invalidos, duplicados = {}, {}, 0
    for numero_local, (numero_original, linha) in enumerate(linhas, start=2):
        valores = {campo: linha[campo].strip() for campo in COLUNAS_OBRIGATORIAS}
        case_id = valores["case_id"]
        if not all(valores.values()):
            invalidos[numero_local] = (numero_original, case_id)
        elif case_id in esperados:
            duplicados += 1
        else:
            esperados[case_id] = (numero_original, valores)
    vistos, ordenados = set(), []
    for registro in registros:
        if not isinstance(registro, dict):
            raise ValueError("Registro inválido do worker.")
        case_id = registro["case_id"]
        if case_id not in esperados or case_id in vistos:
            raise ValueError("ID inesperado ou repetido na resposta do worker.")
        numero, original = esperados[case_id]
        if any(registro.get(campo) != valor for campo, valor in original.items()):
            raise ValueError("O worker alterou a primeira ocorrência válida do ID.")
        triagem = registro["triagem_original"]
        if (not isinstance(triagem, dict) or type(triagem.get("confidence")) is not float
                or type(triagem.get("review_required")) is not bool or triagem != _triagem(registro)):
            raise ValueError("Triagem sem tipos ou valores válidos.")
        vistos.add(case_id)
        ordenados.append((numero, registro))
    if vistos != set(esperados):
        raise ValueError("IDs ausentes na resposta do worker.")
    linhas_vistas, rejeicoes = set(), []
    for rejeitado in rejeitados:
        if not isinstance(rejeitado, dict):
            raise ValueError("Rejeitado inválido do worker.")
        numero = rejeitado["row_number"]
        if type(numero) is str and numero.isdecimal():
            numero = int(numero)
        if type(numero) is not int or numero not in invalidos or numero in linhas_vistas:
            raise ValueError("Linha rejeitada inesperada ou repetida.")
        original, case_id = invalidos[numero]
        if rejeitado["case_id"] != case_id or rejeitado["reason"] != _MOTIVO_REJEICAO:
            raise ValueError("Rejeição alterada pelo worker.")
        linhas_vistas.add(numero)
        rejeicoes.append({**rejeitado, "row_number": original})
    if linhas_vistas != set(invalidos):
        raise ValueError("Linhas rejeitadas ausentes na resposta do worker.")
    # inserted/updated são do SQLite temporário de cada execução, nunca da central.
    contagens = {"read": len(linhas), "valid": len(esperados), "inserted": len(esperados),
                 "updated": 0, "rejected": len(invalidos), "duplicates": duplicados,
                 "review_required": sum(r["triagem_original"]["review_required"] for r in registros)}
    if (resumo.get("status") != "ok" or any(type(resumo.get(campo)) is not int
            or resumo[campo] != valor for campo, valor in contagens.items())):
        raise ValueError("Contagens inconsistentes do worker.")
    return ordenados, rejeicoes, {"worker": worker, "instancia": resposta["instancia"],
                                 "tempo_ms": tempo, "contagens": {"status": "ok", **contagens}}


def executar(conteudo: bytes, workers: int, chamar_worker=None) -> dict:
    inicio = time.perf_counter()
    if type(workers) is not int or workers not in (2, 4):
        raise ValueError("Escolha 2 ou 4 workers.")
    dados = _ler_csv(conteudo)
    atribuicoes, grupos = {}, {}
    for numero, linha in enumerate(dados.to_dict(orient="records"), start=2):
        case_id = linha["case_id"].strip()
        if case_id not in atribuicoes:
            atribuicoes[case_id] = len(atribuicoes) % workers + 1
        grupos.setdefault(atribuicoes[case_id], []).append((numero, linha))
    lote_id = str(uuid4())
    chamar = processar_worker if chamar_worker is None else chamar_worker
    registros, rejeitados, execucoes = [], [], []
    partes = {worker: _serializar(linhas) for worker, linhas in grupos.items()}
    try:
        with ThreadPoolExecutor(max_workers=4) as executor:
            futuros = {worker: executor.submit(chamar, parte, worker, lote_id) for worker, parte in partes.items()}
            wait(futuros.values())
            respostas = {worker: futuro.result() for worker, futuro in futuros.items()}
        for worker in sorted(grupos):
            processados, invalidos, execucao = _validar_resposta(respostas[worker], partes[worker], worker,
                                                               lote_id, grupos[worker])
            registros.extend(processados)
            rejeitados.extend(invalidos)
            execucoes.append(execucao)
    except Exception as exc:
        raise RuntimeError("O lote falhou: nenhum resultado parcial pode ser gravado.") from exc
    resumo = {"status": "ok", **{campo: sum(x["contagens"][campo] for x in execucoes) for campo in _CONTAGENS}}
    return {"registros": [item for _, item in sorted(registros, key=lambda x: x[0])],
            "rejeitados": sorted(rejeitados, key=lambda x: x["row_number"]), "resumo": resumo,
            "execucoes": execucoes, "workers_solicitados": workers, "workers_executados": len(grupos),
            "lote_id": lote_id, "tempo_ms": (time.perf_counter() - inicio) * 1000,
            "modo": ("Threads locais · RPA original" if chamar_worker is None else
                     "Invocações concorrentes de workers lógicos · sem garantia de máquinas físicas distintas")}


def chamar_http(conteudo: bytes, worker: int, lote_id: str, chave: str) -> dict:
    try:
        with httpx.Client(trust_env=False, follow_redirects=False, timeout=45) as cliente:
            resposta = cliente.post("https://gov262.vercel.app/api/cluster/worker",
                                    headers={"X-Manager-Key": chave},
                                    json={"csv": conteudo.decode("utf-8"), "worker": worker, "lote_id": lote_id})
            resposta.raise_for_status()
            return resposta.json()
    except (httpx.HTTPError, ValueError) as exc:
        raise RuntimeError("Falha na requisição ao worker de cluster.") from exc
