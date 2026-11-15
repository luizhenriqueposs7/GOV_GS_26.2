"""Confere integrações atuais antes da gravação, sem criar pedidos na base principal."""
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import httpx
from central import modulos

RAIZ=Path(__file__).resolve().parent

def verificar_fluxo_integrado():
    resultado=subprocess.run([sys.executable,'-X','utf8',str(RAIZ/'verificar_fluxo.py')],cwd=RAIZ,
        capture_output=True,text=True,encoding='utf-8',timeout=90,
        creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
    if resultado.returncode:
        raise RuntimeError('O fluxo em banco temporário falhou. Execute verificar_fluxo.py para conferir o erro.')
    dados=json.loads(resultado.stdout)
    if dados.get('resultado')!='passou':raise ValueError('O fluxo integrado não confirmou a execução.')
    return {'modo':dados['modo'],'etapas':dados['etapas']}

def executar():
    verificacoes=[]
    def conferir(nome,acao):
        try:verificacoes.append({'nome':nome,'ok':True,'resultado':acao()})
        except Exception as erro:verificacoes.append({'nome':nome,'ok':False,'erro':str(erro)})

    with httpx.Client(base_url='http://127.0.0.1:8840',timeout=100,trust_env=False) as cliente:
        def api(method,path,**kwargs):
            resposta=cliente.request(method,path,**kwargs);resposta.raise_for_status();return resposta.json()

        def central():
            r=api('GET','/api/status')
            if r.get('status')!='ok' or r.get('servico')!='Central CitizenTech':raise ValueError('A porta 8840 não respondeu como a central esperada.')
            return {'endereco':'http://127.0.0.1:8840','status':'ok'}

        def rpa():
            r=modulos.triagem('Calçada sem rampa acessível')
            if not r.get('category') or r.get('priority') not in ('Baixa','Média','Alta'):raise ValueError('A triagem não retornou categoria e prioridade válidas.')
            return {'categoria':r['category'],'prioridade_original':r['priority'],'confianca_heuristica':r['confidence']}

        def pln():
            r=api('GET','/api/fontes',params={'q':'ações comunitárias desastres'})
            if not isinstance(r,list) or not r or not r[0].get('text') or not r[0].get('url'):raise ValueError('A busca não retornou trecho com origem.')
            return {'trechos_encontrados':len(r),'fonte':r[0]['url']}

        def visao():
            imagem=RAIZ/'materiais/visao/data/recortes/017_1362_1816.jpg'
            with imagem.open('rb') as arquivo:r=api('POST','/api/visao',files={'arquivo':('recorte-teste.jpg',arquivo,'image/jpeg')})
            if r.get('modelo')!='ResNet18' or type(r.get('escore')) not in (float,int) or not 0<=r['escore']<=1:raise ValueError('A inferência não retornou o contrato esperado.')
            return {'modelo':r['modelo'],'escore':r['escore'],'classe':r['classe'],'imagem':'recorte do acervo, sem vínculo a um pedido'}

        def genai():
            r=api('POST','/api/assistente',json={'pergunta':'Como solicitar manutenção de iluminação pública?'})
            if r.get('status')!='respondido' or not r.get('fonte',{}).get('url') or r.get('historico') is True:raise ValueError('A IA não apresentou resposta atual com fonte para a pergunta de teste.')
            return {'status':r['status'],'fonte':r['fonte']['url'],'historico':False}

        def materiais():
            r=api('GET','/api/ativos')
            esperados={'rpa','cluster','quantica','frontend','genai','iot','pln','visao','governanca'}
            if not isinstance(r,list) or {m.get('id') for m in r}!=esperados:raise ValueError('O catálogo não apresentou as nove disciplinas.')
            return {'disciplinas':len(r),'participacao':{m['id']:m['modo'] for m in r}}

        for nome,acao in [('Central',central),('RPA',rpa),('Registro, revisão e contestação',verificar_fluxo_integrado),('PLN',pln),('Visão Computacional',visao),('Generative AI',genai),('Materiais',materiais)]:conferir(nome,acao)
    return {'data':datetime.now(timezone.utc).isoformat(),'ok':all(v['ok'] for v in verificacoes),
        'verificacoes':verificacoes,'teste_fisico':'pendente',
        'limites':['IoT permanece externo.','Cluster é simulação.','Quântica é estudo conceitual.','A inferência sinaliza fissuras; não valida um detector de buracos.']}

def main():
    resultado=executar()
    destino=RAIZ/'data/runtime/prontidao.json';destino.parent.mkdir(parents=True,exist_ok=True)
    destino.write_text(json.dumps(resultado,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    for v in resultado['verificacoes']:print(('OK' if v['ok'] else 'FALHOU')+' | '+v['nome']+('' if v['ok'] else ': '+v['erro']))
    print('Diagnóstico completo: data/runtime/prontidao.json. Câmera e GPS físicos dependem do teste no aparelho.')
    return 0 if resultado['ok'] else 1

if __name__=='__main__':sys.exit(main())
