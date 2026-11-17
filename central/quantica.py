"""Piloto de seleção de revisões: fila, referência exata e QAOA p=1 em CPU."""
import hashlib
import json
import math
from copy import deepcopy
from numbers import Real
from time import perf_counter

import numpy as np


PESOS = {'Baixa': 1, 'Média': 2, 'Alta': 3}


def evoluir(energias: np.ndarray, gamma: float, beta: float) -> np.ndarray:
    """H^n|0>, fase exp(-iγE) e Rx(2β) em cada qubit, sem amostragem."""
    try:
        if np.iscomplexobj(energias):
            raise ValueError('As energias do Hamiltoniano diagonal devem ser reais.')
        energias = np.asarray(energias, dtype=float)
    except (TypeError, ValueError) as erro:
        raise ValueError('Informe energias reais e finitas.') from erro
    if (energias.ndim != 1 or not 2 <= energias.size <= 256
            or energias.size & (energias.size - 1) or not np.isfinite(energias).all()
            or any(not isinstance(v, Real) or not math.isfinite(v) for v in (gamma, beta))):
        raise ValueError('Use 2 a 256 energias finitas, em potência de dois, e ângulos finitos.')
    try:
        with np.errstate(over='raise', invalid='raise'):
            estado = np.exp(-1j * gamma * energias) / math.sqrt(energias.size)
    except FloatingPointError as erro:
        raise ValueError('Os ângulos de fase ultrapassam o limite numérico do simulador.') from erro
    cosseno, seno = math.cos(beta), -1j * math.sin(beta)
    for passo in (1 << q for q in range(energias.size.bit_length() - 1)):
        blocos = estado.reshape(-1, 2, passo)
        zero, um = blocos[:, 0, :].copy(), blocos[:, 1, :].copy()
        blocos[:, 0, :] = cosseno * zero + seno * um
        blocos[:, 1, :] = seno * zero + cosseno * um
    return estado


def simular(casos: list[dict], itens: list[dict], capacidade: int) -> dict:
    """Compara um recorte conferido pelo gestor; não decide nem modifica pedidos."""
    if type(capacidade) is not int or not 1 <= capacidade <= 480:
        raise ValueError('Informe uma capacidade inteira entre 1 e 480 minutos.')
    if not isinstance(itens, list) or not 1 <= len(itens) <= 8:
        raise ValueError('Selecione de 1 a 8 pedidos para a simulação.')
    if not isinstance(casos, list) or any(not isinstance(c, dict) or not isinstance(c.get('id'), str) for c in casos):
        raise ValueError('Confira os pedidos disponíveis para a simulação.')
    por_id = {c['id']: c for c in casos}
    if len(por_id) != len(casos):
        raise ValueError('Os pedidos disponíveis devem ter IDs únicos.')
    selecionados = []
    ids = set()
    for entrada in itens:
        if (not isinstance(entrada, dict) or not isinstance(entrada.get('id'), str)
                or not entrada['id'].strip() or entrada['id'] in ids or entrada['id'] not in por_id):
            raise ValueError('Selecione IDs de pedidos existentes, sem repetição.')
        if (type(entrada.get('minutos')) is not int or not 1 <= entrada['minutos'] <= 240
                or not isinstance(entrada.get('prioridade'), str) or entrada['prioridade'] not in PESOS
                or type(entrada.get('obrigatorio')) is not bool):
            raise ValueError('Confira prioridade, obrigatoriedade e duração inteira de 1 a 240 minutos de cada pedido.')
        pedido = por_id[entrada['id']]
        if pedido.get('revisao') is not None:
            raise ValueError('O recorte só aceita pedidos pendentes, sem revisão concluída. Faça nova simulação.')
        ids.add(entrada['id'])
        selecionados.append({**{k: pedido.get(k) for k in ('id', 'descricao', 'bairro', 'origem_id', 'criado_em')},
                             **{k: entrada[k] for k in ('minutos', 'prioridade', 'obrigatorio')},
                             'beneficio': PESOS[entrada['prioridade']]})
    if sum(i['minutos'] for i in selecionados if i['obrigatorio']) > capacidade:
        raise ValueError('A capacidade não comporta os pedidos obrigatórios. Aumente os minutos disponíveis.')
    if not any(i['minutos'] <= capacidade for i in selecionados):
        raise ValueError('Pelo menos um pedido do recorte deve caber na capacidade informada.')

    # O timestamp participa: registrar um plano consome esta versão; evidências/histórico não são o conteúdo do pedido.
    snapshot = [deepcopy({k: v for k, v in por_id[i['id']].items() if k not in ('evidencias', 'historico')})
                for i in selecionados]
    entradas = [{k: i[k] for k in ('id', 'minutos', 'prioridade', 'obrigatorio')} for i in selecionados]
    base = hashlib.sha256(json.dumps({'casos': snapshot, 'itens': entradas, 'capacidade': capacidade},
                                   sort_keys=True, ensure_ascii=False, allow_nan=False).encode()).hexdigest()
    n = len(selecionados)
    # O primeiro bit escrito corresponde ao primeiro item exibido, inclusive nos relatórios de probabilidade.
    bits = ((np.arange(2 ** n)[:, None] >> np.arange(n - 1, -1, -1)) & 1)
    duracoes = np.array([i['minutos'] for i in selecionados])
    beneficios = np.array([i['beneficio'] for i in selecionados])
    obrigatorios = np.array([i['obrigatorio'] for i in selecionados])
    minutos = bits @ duracoes
    beneficio = bits @ beneficios
    omissoes = (1 - bits) @ obrigatorios
    viavel = (minutos <= capacidade) & (omissoes == 0)
    penalidade = int(beneficios.sum()) + 1
    energias = -beneficio + penalidade * (np.maximum(0, minutos - capacidade) ** 2 + omissoes)

    def resultado(indice):
        return {'selecionados': [i['id'] for i, bit in zip(selecionados, bits[indice]) if bit],
                'adiados': [i['id'] for i, bit in zip(selecionados, bits[indice]) if not bit],
                'minutos': int(minutos[indice]), 'beneficio': int(beneficio[indice]),
                'bitstring': format(indice, f'0{n}b')}

    escolhidos = {j for j, i in enumerate(selecionados) if i['obrigatorio']}
    usado = sum(selecionados[j]['minutos'] for j in escolhidos)
    fila = sorted(range(n), key=lambda j: (-selecionados[j]['beneficio'],
                                         selecionados[j]['criado_em'] or '', selecionados[j]['id']))
    for j in fila:
        if j not in escolhidos and usado + duracoes[j] <= capacidade:
            escolhidos.add(j)
            usado += int(duracoes[j])
    indice_fila = sum(1 << (n - 1 - j) for j in escolhidos)

    inicio = perf_counter()
    melhor_energia = math.inf
    parametros = None
    probabilidades = None
    # Grade fixa limita o trabalho na hospedagem gratuita; a referência exata não participa da busca.
    for gamma in np.linspace(0., 2 * math.pi, 12, endpoint=False):
        for beta in np.linspace(0., math.pi, 12, endpoint=False):
            probabilidades_candidatas = abs(evoluir(energias, float(gamma), float(beta))) ** 2
            energia = float(probabilidades_candidatas @ energias)
            if energia < melhor_energia:
                melhor_energia = energia
                probabilidades = probabilidades_candidatas
                parametros = {'gamma': float(gamma), 'beta': float(beta)}
    indices_viaveis = np.flatnonzero(viavel)
    indice_qaoa = int(indices_viaveis[np.argmax(probabilidades[viavel])])
    qaoa = resultado(indice_qaoa)
    qaoa.update(probabilidade=float(probabilidades[indice_qaoa]),
                probabilidade_viavel=float(probabilidades[viavel].sum()),
                energia_esperada=melhor_energia, parametros=parametros, p=1, estados=2 ** n,
                runtime_ms=(perf_counter() - inicio) * 1000,
                top5_probabilidades=[{'bitstring': format(int(j), f'0{n}b'),
                                      'probabilidade': float(probabilidades[j]), 'viavel': bool(viavel[j])}
                                     for j in sorted(range(2 ** n), key=lambda j: (-probabilidades[j], j))[:5]])
    indice_exato = min(indices_viaveis, key=lambda j: (-beneficio[j], minutos[j], j))
    pendentes = [c for c in casos if c.get('revisao') is None]
    return {'base': base, 'snapshot': snapshot, 'capacidade': capacidade, 'itens': selecionados,
            'pendentes_total': len(pendentes),
            'fora_do_recorte_ids': sorted(c['id'] for c in pendentes if c['id'] not in ids),
            'metodos': {'fila': resultado(indice_fila), 'classico': resultado(int(indice_exato)), 'qaoa': qaoa},
            'execucao': 'Simulador NumPy em CPU; sem QPU ou garantia de ganho quântico.',
            'criterio': 'Pesos experimentais Baixa=1, Média=2 e Alta=3, conferidos pelo gestor; durações estimadas pelo gestor. '
                        'Fila por prioridade e antiguidade; enumeração exata maximiza a soma dos pesos; '
                        'QAOA p=1 usa o estado factível mais provável após minimizar energia esperada na grade 12×12. '
                        'Probabilidades calculadas do vetor de estado, sem amostragem; não há ótimo garantido no QAOA.'}
