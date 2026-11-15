"""Planejamento determinístico de um percurso didático, sem certificação de rota."""
import hashlib
import json
from copy import deepcopy


PERCURSO = {
    'id': 'ponto-ubs-demo', 'versao': 1, 'nome': 'Do ponto à unidade de saúde',
    'origem': 'Ponto de ônibus · exemplo', 'destino': 'Unidade de saúde · exemplo',
    'demonstracao': True,
    'fonte': 'Cenário elaborado pelo grupo em 15/11/2026. Traçado esquemático; sem inspeção de calçadas.',
    'criterio': 'Continuidade da passagem pela calçada, sem precisar descer para a pista, segundo as condições informadas.',
    'limite': 'Condições e posições ilustrativas. Não use como orientação de deslocamento ou garantia de acessibilidade.',
    'trechos': [
        {'id': 'acesso', 'nome': '01 · Ponto até a praça', 'condicao_base': 'livre_no_cenario',
         'geometria': [[-23.54400, -46.64400], [-23.54400, -46.64360]]},
        {'id': 'calcada', 'nome': '02 · Calçada da praça', 'condicao_base': 'nao_verificado',
         'geometria': [[-23.54400, -46.64360], [-23.54430, -46.64360]]},
        {'id': 'rampa', 'nome': '03 · Rampa e travessia', 'condicao_base': 'nao_verificado',
         'geometria': [[-23.54430, -46.64360], [-23.54430, -46.64320]]},
        {'id': 'entrada', 'nome': '04 · Chegada à unidade', 'condicao_base': 'livre_no_cenario',
         'geometria': [[-23.54430, -46.64320], [-23.54430, -46.64280]]},
    ],
}
TRECHOS = {t['id'] for t in PERCURSO['trechos']}
CONDICOES = {'bloqueado', 'dificultado', 'nao_verificado'}


def validar_vinculo(vinculo):
    if vinculo is None:
        return None
    if (not isinstance(vinculo, dict) or set(vinculo) != {'percurso_id', 'trecho_id', 'condicao'}
            or vinculo['percurso_id'] != PERCURSO['id'] or vinculo['trecho_id'] not in TRECHOS
            or vinculo['condicao'] not in CONDICOES):
        raise ValueError('Confira o percurso, o trecho e a condição informada para a passagem.')
    return dict(vinculo)


def resumo(estados, desconhecidos):
    barreiras = estados.count('barreira')
    return {'estado': 'interrompido' if barreiras else 'incerto' if desconhecidos else 'sem_barreiras_informadas',
            'barreiras': barreiras, 'desconhecidos': desconhecidos, 'total_trechos': len(estados)}


def avaliar(casos, reparos):
    if len(reparos) != len(set(reparos)) or not set(reparos) <= TRECHOS:
        raise ValueError('Selecione trechos válidos, sem repetição.')
    vinculados = sorted((c for c in casos if c.get('passagem')
                         and c['passagem'].get('percurso_id') == PERCURSO['id']), key=lambda c: c['id'])
    campos = ('id', 'descricao', 'bairro', 'local', 'contexto', 'foto', 'localizacao', 'passagem',
              'triagem_original', 'preparacao', 'revisao', 'situacao', 'frontend', 'evidencias')
    entradas = [{k: c.get(k) for k in campos} for c in vinculados]
    base = hashlib.sha256(json.dumps({'percurso': PERCURSO, 'pedidos': entradas},
                          sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    trechos = []
    for original in PERCURSO['trechos']:
        trecho = deepcopy(original)
        pedidos = [c for c in vinculados if c['passagem']['trecho_id'] == trecho['id']]
        condicoes = {c['passagem']['condicao'] for c in pedidos}
        barreira = bool(condicoes & {'bloqueado', 'dificultado'})
        desconhecido = 'nao_verificado' in condicoes
        atual = 'barreira' if barreira else 'nao_verificado' if desconhecido else trecho['condicao_base']
        simulado = atual
        if barreira and trecho['id'] in reparos:
            simulado = 'nao_verificado' if desconhecido else 'reparo_hipotetico'
        trecho.update(atual=atual, simulado=simulado,
                      tem_condicao_desconhecida=desconhecido or atual == 'nao_verificado', pedidos=[
            {k: c.get(k) for k in ('id', 'descricao', 'passagem', 'revisao', 'foto', 'localizacao')}
            for c in pedidos])
        trechos.append(trecho)
    return {'percurso': deepcopy(PERCURSO), 'base': base, 'trechos': trechos,
            'reparos': [t['id'] for t in trechos if t['id'] in reparos],
            'atual': resumo([t['atual'] for t in trechos], sum(t['tem_condicao_desconhecida'] for t in trechos)),
            'simulado': resumo([t['simulado'] for t in trechos], sum(t['tem_condicao_desconhecida'] for t in trechos)),
            'pendentes_revisao': [c['id'] for c in vinculados if not c.get('revisao')]}
