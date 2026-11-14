"""Cartas oficiais consultadas para preparar pedidos, sem enviá-los ao órgão."""
import re

DATA_CONSULTA = "2026-11-14"
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
        "responsavel": "Conferir a carta oficial específica",
        "url": "https://sp156.prefeitura.sp.gov.br/portal/servicos/informacao?servico=3170",
        "orientacao": "A carta de tapa-buraco em via comum remete faixas exclusivas e corredores a este serviço. Confira os requisitos diretamente no portal antes de abrir a solicitação.",
        "canal": "Portal SP156",
    },
    "area_publica": {
        "id": "931", "nome": "Manutenção de calçada pública",
        "responsavel": "Secretaria Municipal das Subprefeituras",
        "url": "https://sp156.prefeitura.sp.gov.br/portal/servicos/informacao?servico=931",
        "orientacao": "Para passeios de praças e áreas públicas abrangidas pela carta. Confirme o local e descreva a imperfeição e o ponto de referência.",
        "canal": "Portal SP156, telefone 156 ou atendimento presencial",
    },
    "frente_imovel": {
        "id": "906", "nome": "Calçada particular danificada ou inexistente",
        "responsavel": "Consultar a carta oficial do serviço",
        "url": "https://sp156.prefeitura.sp.gov.br/portal/servicos/informacao?servico=906",
        "orientacao": "A carta de manutenção pública remete os casos de calçada em frente a imóvel a este serviço. Confira os requisitos no portal antes de registrar.",
        "canal": "Portal SP156",
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
        "url": "https://prefeitura.sp.gov.br/web/spregula/w/iluminacao_publica/perguntas_frequentes/355960",
        "orientacao": "Para defeito em equipamento de iluminação existente. Informe o endereço da ocorrência; a equipe responsável avalia a situação.",
        "canal": "Canais de manutenção Ilumina SP indicados na carta oficial",
    },
    "nova_iluminacao": {
        "id": "ILU_AMPLIACAO", "nome": "Melhoria ou ampliação da iluminação pública",
        "responsavel": "SP Regula",
        "url": "https://prefeitura.sp.gov.br/web/spregula/w/iluminacao_publica/perguntas_frequentes/355960",
        "orientacao": "Para local sem iluminação ou pedido de melhoria. O enquadramento e a necessidade de instalação dependem de vistoria técnica.",
        "canal": "Canais SP156 e atendimento presencial indicados na carta oficial",
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
