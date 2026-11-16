"""Cartas oficiais consultadas para preparar pedidos, sem enviá-los ao órgão."""
import re

DATA_CONSULTA = "2026-11-16"
CONTEXTO = {
    "asfalto_comum": {
        "id": "952", "nome": "Tapa-buraco em via comum",
        "responsavel": "Secretaria Municipal das Subprefeituras",
        "url": "https://sp156.prefeitura.sp.gov.br/portal/servicos/informacao?servico=952",
        "orientacao": "Para buraco no asfalto de via comum. Informe endereço completo e descrição. A vistoria e a execução dependem da equipe responsável; coordenadas e foto não substituem o endereço.",
        "canal": "Portal ou aplicativo SP156, telefone 156 e atendimento presencial",
    },
    "corredor_onibus": {
        "id": "3170", "nome": "Tapa-buraco em faixa exclusiva ou corredor de ônibus",
        "responsavel": "SPTrans",
        "url": "https://sp156.prefeitura.sp.gov.br/portal/servicos/informacao?servico=3170",
        "orientacao": "Para faixa exclusiva ou corredor. Informe data, hora, via, número próximo e ponto de referência da imperfeição.",
        "canal": "Portal SP156 ou telefone 156",
    },
    "area_publica": {
        "id": "931", "nome": "Manutenção de calçada pública",
        "responsavel": "Secretaria Municipal das Subprefeituras",
        "url": "https://sp156.prefeitura.sp.gov.br/portal/servicos/informacao?servico=931",
        "orientacao": "Para passeios de praças e grandes avenidas com canteiros, sem imóveis. Informe endereço, referência, imperfeição e obstáculo à acessibilidade. Em frente a imóvel, inclusive equipamento público, a manutenção cabe ao respectivo imóvel. Tampas de concessionária exigem outro encaminhamento.",
        "canal": "Portal SP156, telefone 156 ou atendimento presencial",
    },
    "frente_imovel": {
        "id": "906", "nome": "Calçada particular danificada ou inexistente",
        "responsavel": "Consultar a carta oficial do serviço",
        "url": "https://sp156.prefeitura.sp.gov.br/portal/servicos/informacao?servico=906",
        "orientacao": "Destino indicado pelas cartas de calçada pública e de obstáculos. A carta 906 retornou acesso indisponível na consulta de 16/11/2026; requisitos e responsável permanecem pendentes de confirmação.",
        "canal": "Confirmar pelo telefone 156 ou consultar a carta no portal",
    },
    "obstaculo": {
        "id": "2634", "nome": "Avaliação de obstáculo na calçada",
        "responsavel": "Secretaria Municipal das Subprefeituras",
        "url": "https://sp156.prefeitura.sp.gov.br/portal/servicos/informacao?servico=2634",
        "orientacao": "Para objetos como vasos e barras que bloqueiam a circulação. Informe o endereço da ocorrência e descreva o obstáculo.",
        "canal": "Portal SP156, telefone 156 ou atendimento presencial",
    },
    "iluminacao_existente": {
        "id": "ILU_MANUTENCAO", "nome": "Manutenção de iluminação pública",
        "responsavel": "SP Regula e concessionária de iluminação",
        "url": "https://prefeitura.sp.gov.br/web/spregula/w/iluminacao_publica/renovar/4603",
        "orientacao": "Para defeito em equipamento de iluminação existente. Informe o endereço da ocorrência; a equipe responsável avalia a situação.",
        "canal": "0800 779 0156 (24 horas) ou aplicativo IluminaSP; endereço completo e referência",
    },
    "nova_iluminacao": {
        "id": "ILU_AMPLIACAO", "nome": "Melhoria ou ampliação da iluminação pública",
        "responsavel": "SP Regula",
        "url": "https://prefeitura.sp.gov.br/web/spregula/w/iluminacao_publica/ampliar/4611",
        "orientacao": "Para local sem iluminação ou pedido de melhoria. O enquadramento e a necessidade de instalação dependem de vistoria técnica.",
        "canal": "Subprefeitura, Descomplica ou secretariaexecutiva@spregula.sp.gov.br; formulário SAIP e aprovação técnica",
    },
}


def preparar(descricao: str, contexto: str, local: str) -> dict:
    if contexto != "nao_informado" and contexto not in CONTEXTO:
        raise ValueError("Selecione um contexto disponível.")
    servico = CONTEXTO.get(contexto)
    faltantes = []
    pergunta = None
    if not servico:
        faltantes.append("contexto")
        pergunta = (
            "Qual é o contexto do problema? Na calçada, diferencie dano em área pública, "
            "frente de imóvel e objeto bloqueando a passagem. No asfalto, diferencie via comum e corredor de ônibus. Para iluminação, confirme "
            "se o equipamento existe e está com defeito ou se é um pedido de instalação."
        )
    if not local.strip():
        faltantes.append("local")
    if re.search(r"\brampas?\b", descricao.casefold()):
        servico = None
        faltantes.append("enquadramento")
        pergunta = "Para o pedido relacionado à rampa, confirme o serviço com o atendimento oficial antes de encaminhar. A informação disponível não permite definir esse enquadramento."
    return {
        "servico": servico,
        "pergunta": pergunta,
        "faltantes": faltantes,
        "fonte": servico["url"] if servico else None,
        "data_consulta": DATA_CONSULTA,
        "situacao": "Preparado para conferência" if not faltantes else "Precisa de informações",
        "observacao": "Esta preparação não abre um chamado oficial. Confira o serviço e suas informações antes de enviar pelo canal responsável.",
    }


def ficha_encaminhamento(caso: dict) -> str:
    preparacao = preparar(caso['descricao'], caso['contexto'], caso.get('local') or '')
    servico = preparacao.get('servico') or {}
    atendimento = caso.get('atendimento') or {}
    protocolo = atendimento.get('protocolo') or caso.get('protocolo_oficial') or {}
    geo = caso.get('localizacao') or {}
    return '\n'.join([
        'ZelaBairro | Ficha para encaminhamento assistido',
        'DEMONSTRAÇÃO — não encaminhar um caso fictício.' if atendimento.get('demonstracao') else 'Preparação do solicitante — conferir antes de usar no canal oficial.',
        'Esta ficha não comprova recebimento, vistoria ou reparo por um órgão.',
        f"Registro local: {caso['id']}", f"Relato: {caso['descricao']}",
        f"Bairro/região: {caso['bairro']}", f"Endereço e referência: {caso.get('local') or 'PENDENTE'}",
        f"Coordenadas confirmadas pelo usuário: {geo.get('latitude', 'não informadas')}, {geo.get('longitude', '')}",
        'GPS e foto não substituem endereço completo nem medição no local.',
        f"Serviço sugerido: {servico.get('nome', 'CONFIRMAR COM O ATENDIMENTO OFICIAL')}",
        f"Responsável indicado: {servico.get('responsavel', 'Pendente de enquadramento')}",
        f"Canal: {servico.get('canal', 'Telefone 156 para orientação em São Paulo')}",
        f"Requisitos: {servico.get('orientacao', caso['preparacao'].get('pergunta') or 'Confirmar no canal oficial')}",
        f"Fonte: {servico.get('url', '')}", f'Consulta do catálogo: {DATA_CONSULTA}',
        f"Conferência local: {'concluída' if caso.get('frontend') and caso.get('revisao') else 'PENDENTE'}",
        f"Protocolo {'de demonstração' if atendimento.get('demonstracao') else 'declarado, sem validação no órgão'}: {protocolo.get('numero', 'Não informado')}",
        f"Situação declarada: {atendimento.get('etapa', 'Sem protocolo informado')}",
        f"Retorno: {atendimento.get('retorno', {}).get('relato', 'Não informado')}",
        'Anexos: baixar a foto inicial separadamente na plataforma; respeitar os limites do canal oficial.',
        'O solicitante conclui o envio no canal responsável e anota o protocolo aqui. Sem sincronização automática.',
    ]) + '\n'
