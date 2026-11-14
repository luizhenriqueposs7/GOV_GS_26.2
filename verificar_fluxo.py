"""Verifica funções reais das rotas e persistência; não substitui teste HTTP."""
import json
import os
import secrets
import tempfile
from pathlib import Path


def main():
    chave = secrets.token_urlsafe(32)
    os.environ["GOV_MANAGER_KEY"] = chave
    from central.app import Pedido, Revisao, Contestacao, criar_app

    base = Path(__file__).resolve().parent
    temporarios = base / ".tmp"
    temporarios.mkdir(exist_ok=True)
    os.environ["TEMP"] = os.environ["TMP"] = str(temporarios)
    tempfile.tempdir = str(temporarios)
    with tempfile.TemporaryDirectory(dir=temporarios) as pasta:
        app = criar_app(Path(pasta))

        def chamar(metodo, caminho, *args):
            rota = next(r for r in app.routes if getattr(r, "path", None) == caminho and metodo in getattr(r, "methods", []))
            return rota.endpoint(*args)

        entrada = Pedido(descricao="Passeio de praça com calçada danificada", bairro="Bairro fictício", confirmado=True)
        caso = chamar("POST", "/api/atendimentos", entrada)
        assert caso["preparacao"]["faltantes"] == ["contexto", "local"]
        entrada.local = "Praça de demonstração, entrada norte"
        entrada.contexto = "area_publica"
        atualizado = chamar("PUT", "/api/atendimentos/{identificador}", caso["id"], entrada)
        assert atualizado["id"] == caso["id"] and atualizado["preparacao"]["servico"]["id"] == "931"
        revisado = chamar("POST", "/api/atendimentos/{identificador}/revisao", caso["id"],
                          Revisao(prioridade="Média", justificativa="Contexto conferido neste cenário fictício.", revisor="Revisor da demonstração"), chave)
        assert revisado["revisao"]["prioridade"] == "Média"
        ligado = chamar("POST", "/api/atendimentos/{identificador}/zelabairro", caso["id"], chave)
        repetido = chamar("POST", "/api/atendimentos/{identificador}/zelabairro", caso["id"], chave)
        assert ligado["frontend"]["id"] == repetido["frontend"]["id"]
        assert ligado["protocolo_oficial"] is None
        contestado = chamar("POST", "/api/atendimentos/{identificador}/contestacao", caso["id"],
                            Contestacao(motivo="É necessário conferir outra alternativa de passagem."))
        assert contestado["revisao"] is None and "frontend" not in contestado
        rampa = chamar("POST", "/api/atendimentos", Pedido(descricao="Calçada sem rampa acessível", bairro="Bairro fictício", confirmado=True))
        assert rampa["triagem_original"]["priority"] == "Baixa"
        assert rampa["triagem_original"]["review_required"] is False and rampa["exige_revisao"] is True
        assert rampa["preparacao"]["servico"] is None
        indicadores = chamar("GET", "/api/indicadores")
        assert indicadores["total"] == 2 and indicadores["revisados"] == 0
        print(json.dumps({"resultado": "passou", "modo": "Funções reais das rotas e bancos temporários; sem transporte HTTP",
                          "dados": "fictícios", "etapas": ["registrar", "completar", "revisar", "persistir no ZelaBairro",
                          "repetir confirmação sem duplicação", "contestar", "preservar RPA e bloquear serviço de rampa"],
                          "indicadores_finais": indicadores}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
