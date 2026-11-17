"""Captura consultas oficiais e Cluster em QA isolado, sem áudio ou montagem final."""
import json
import os
from pathlib import Path
import subprocess
import sys
from datetime import datetime, timezone

import cv2

RAIZ=Path(__file__).resolve().parents[2]
SAIDA=RAIZ/'output/video/fontes_independentes'
TRABALHO=RAIZ/'.tmp/gravacao-independentes'
# shortcut: CLI e navegadores desta máquina; ajustar os caminhos ao mudar de computador.
CLI=Path('C:/Users/luizh/AppData/Local/npm-cache/_npx/31e32ef8478fbf80/node_modules/@playwright/cli/playwright-cli.js')
SESSAO='gravacao-gs'
URL='https://gov262.vercel.app'
QA='http://127.0.0.1:8851'

PREPARAR=r'''async page=>{
 page.setDefaultTimeout(15000);
 await page.goto('URL/#VISTA');await page.evaluate(()=>document.fonts.ready);
 await page.locator('[data-panel="VISTA"]').waitFor({state:'visible'});
 await page.evaluate(()=>{document.querySelectorAll('details[open]').forEach(n=>n.open=false);scrollTo(0,0);});
 if('VISTA'==='evidencias')await page.locator('#evidencia-caso').selectOption('',{force:true});
 return {tela_preparada:true};
}'''

CENAS=[
 ('00_abertura','pedido','Luiz Henrique',r'''async page=>{
   await page.waitForTimeout(4500);
   await page.locator('#camera-vazia').scrollIntoViewIfNeeded();
   await page.waitForTimeout(4500);
   await page.locator('.entry-heading').scrollIntoViewIfNeeded();
   await page.waitForTimeout(5000);
   return {tela:'Registrar',cadastro_executado:false};
 }'''),
 ('03_cluster_2_4_workers','revisao','Luiz Henrique',r'''async page=>{
   page.setDefaultTimeout(150000);await page.waitForTimeout(2500);
   await page.locator('#lote-arquivo').setInputFiles('CSV');
   const execucoes=[];
   for(const workers of ['2','4']){
     await page.locator('#cluster-workers').selectOption(workers);
     await page.waitForTimeout(1800);
     const espera=page.waitForResponse(r=>r.url().endsWith('/api/cluster/lotes')&&r.request().method()==='POST',{timeout:150000});
     await page.getByRole('button',{name:'Processar lote com a chave acima',exact:true}).click();
     const resposta=await espera;
     if(resposta.status()!==200)throw new Error('Lote HTTP '+resposta.status()+': '+await resposta.text());
     const dados=await resposta.json();
     if(dados.workers_executados!==Number(workers)||dados.atendimentos.length!==8)throw new Error('Distribuição inesperada.');
     await page.waitForFunction(()=>document.querySelector('#lote-resultado').textContent.includes('Lote concluído')&&!document.querySelector('#lote-form button[type=submit]').disabled);
     await page.locator('#lote-resultado').scrollIntoViewIfNeeded();
     await page.waitForTimeout(7000);
     execucoes.push({workers:dados.workers_executados,ids:dados.atendimentos,tempo_ms:dados.tempo_ms,tempo_persistencia_ms:dados.tempo_persistencia_ms,tempo_total_ms:dados.tempo_total_ms,modo:dados.modo});
   }
   if(JSON.stringify(execucoes[0].ids)!==JSON.stringify(execucoes[1].ids))throw new Error('IDs não preservados.');
   return {csv:'docs/exemplos/cluster-revisoes.csv',dados:'demonstração',ids_preservados:true,execucoes};
 }'''),
 ('05_generative_ai','evidencias','Luiz Henrique',r'''async page=>{
   await page.waitForTimeout(2500);
   await page.locator('#apoio-orientacao > summary').click();
   await page.locator('#pergunta').fill('Como solicitar manutenção de uma calçada danificada em praça pública de São Paulo?');
   await page.waitForTimeout(2500);
   const espera=page.waitForResponse(r=>r.url().endsWith('/api/assistente')&&r.request().method()==='POST',{timeout:150000});
   await page.locator('#assistente-form button[type=submit]').click();
   const resposta=await espera;
   if(resposta.status()!==200)throw new Error('Assistente HTTP '+resposta.status()+': '+await resposta.text());
   const dados=await resposta.json();
   if(dados.status!=='respondido'||!dados.fonte?.url)throw new Error('Resposta sem orientação/fonte.');
   await page.locator('#assistente-resultado a').waitFor();
   await page.locator('#assistente-resultado').scrollIntoViewIfNeeded();
   await page.waitForTimeout(11000);
   await page.locator('#assistente-resultado a').hover();
   await page.waitForTimeout(3500);
   return {pergunta:'Calçada danificada em praça pública',vinculo_pedido:null,status:dados.status,modelo:dados.modelo,resposta:dados.resposta,fonte:dados.fonte};
 }'''),
 ('06_pln','evidencias','Luiz Henrique',r'''async page=>{
   await page.waitForTimeout(2500);
   await page.locator('#apoio-fontes > summary').click();
   await page.locator('#busca').fill('enchentes');
   await page.waitForTimeout(2000);
   const espera=page.waitForResponse(r=>r.url().includes('/api/fontes?q='));
   await page.locator('#fontes-form button[type=submit]').click();
   const resposta=await espera;if(resposta.status()!==200)throw new Error('Corpus HTTP '+resposta.status());
   const dados=await resposta.json();if(!dados.length||!dados[0].url)throw new Error('Busca sem fonte.');
   const primeiro=page.locator('#fontes-resultado .source-card').first();
   await primeiro.waitFor();await primeiro.scrollIntoViewIfNeeded();
   await page.waitForTimeout(8500);
   await primeiro.locator('a').hover();await page.waitForTimeout(3500);
   if(dados.length>1){await page.locator('#fontes-resultado .source-card').nth(1).scrollIntoViewIfNeeded();await page.waitForTimeout(6500);}
   return {consulta:'enchentes',vinculo_pedido:null,resultados:dados.length,origens:dados.slice(0,2).map(d=>({linha_corpus:d.linha_corpus,fonte:d.fonte,url:d.url,paginas:d.paginas,secao:d.secao}))};
 }'''),
 ('07_visao_computacional','evidencias','Felipe',r'''async page=>{
   await page.waitForTimeout(2500);
   await page.locator('#apoio-visao > summary').click();
   await page.locator('#imagem').setInputFiles('IMAGEM');
   await page.waitForTimeout(2500);
   const espera=page.waitForResponse(r=>r.url().endsWith('/api/visao')&&r.request().method()==='POST',{timeout:150000});
   await page.locator('#visao-form button[type=submit]').click();
   const resposta=await espera;
   if(resposta.status()!==200)throw new Error('Visão HTTP '+resposta.status()+': '+await resposta.text());
   const dados=await resposta.json();if(!dados.modelo||!dados.classe)throw new Error('Inferência sem modelo/classe.');
   await page.locator('#visao-resultado details').waitFor();
   await page.locator('#visao-resultado').scrollIntoViewIfNeeded();await page.waitForTimeout(8500);
   await page.locator('#visao-resultado summary').click();await page.waitForTimeout(6500);
   return {imagem:'017_1135_2497.jpg',vinculo_pedido:null,...dados};
 }'''),
 ('08_iot_ouviai_simulacao','ouviai','Luis Filipe',r'''async page=>{
   let posts=0;page.on('request',r=>{if(r.method()==='POST')posts++;});
   await page.evaluate(()=>scrollTo(0,200));await page.waitForTimeout(4000);
   await page.getByRole('button',{name:'Simular campainha',exact:true}).click();
   await page.waitForFunction(()=>document.querySelector('#ouviai-display').textContent==='Campainha');
   await page.waitForTimeout(5500);
   await page.getByRole('button',{name:'Simular batida na porta',exact:true}).click();await page.waitForTimeout(4500);
   await page.getByRole('button',{name:'Simular som ambiente',exact:true}).click();await page.waitForTimeout(4500);
   await page.locator('#ouviai-eventos').scrollIntoViewIfNeeded();await page.waitForTimeout(5500);
   if(posts)throw new Error('IoT demonstrativo não deve enviar eventos ao servidor.');
   return {interface_real:true,eventos:'simulados',modelo_audio_executado:false,hardware_conectado:false,pedidos_criados:0};
 }'''),
]

def main():
    assert CLI.is_file(),'Playwright CLI indisponível.'
    SAIDA.mkdir(parents=True,exist_ok=True);TRABALHO.mkdir(parents=True,exist_ok=True)
    env=os.environ.copy();env['PLAYWRIGHT_BROWSERS_PATH']=str(RAIZ/'.tmp/qa-mobile-2026-11-17/browsers')
    config=TRABALHO/'browser.json'
    config.write_text(json.dumps({'browser':{'browserName':'chromium','launchOptions':{'channel':'chrome'},'contextOptions':{'viewport':{'width':1920,'height':1080},'locale':'pt-BR','timezoneId':'America/Sao_Paulo'}}}),encoding='utf-8')
    def cli(*args,timeout=210):
        r=subprocess.run(['node',str(CLI),'-s='+SESSAO,*map(str,args)],cwd=TRABALHO,env=env,capture_output=True,text=True,encoding='utf-8',timeout=timeout)
        if r.returncode:raise RuntimeError((r.stdout+'\n'+r.stderr)[-2200:])
        return r.stdout.strip()
    def executar(codigo,nome='acao.js'):
        p=TRABALHO/nome;p.write_text(codigo,encoding='utf-8')
        return json.loads(cli('run-code','--filename',p,'--raw'))
    manifesto={'capturado_em_utc':datetime.now(timezone.utc).isoformat(),'url_oficial':URL,'cluster_ambiente':QA,'resolucao':[1920,1080],'fps':25,'audio':False,'velocidade':1.0,'endpoints_filmados_sem_mock':True,'clipes':[],'pendentes':['celular e Frontend','RPA do pedido móvel','planejamento incluindo pedido móvel','Governança, contestação e encerramento','narrações dos integrantes','montagem e duração finais']}
    anteriores={}
    if '--resume' in sys.argv and (SAIDA/'manifesto.json').is_file():
        original=(SAIDA/'manifesto.json').read_text(encoding='utf-8')
        anteriores={i['id']:i for i in json.loads(original)['clipes']}
        backup=TRABALHO/'manifesto-primeira-tentativa.json'
        if not backup.exists():backup.write_text(original,encoding='utf-8')
    try:
        cli('open',URL+'/#pedido','--browser','chrome','--config',config,'--raw')
        for nome,vista,pessoa,codigo in CENAS:
            anterior=anteriores.get(nome)
            if anterior and anterior['status']=='capturado' and (SAIDA/anterior['arquivo']).is_file():
                manifesto['clipes'].append(anterior)
                print(json.dumps({'id':nome,'status':'preservado','duracao_segundos':anterior['duracao_segundos']}),flush=True)
                continue
            origem=QA if nome.startswith('03_') else URL
            item={'id':nome,'apresentador':pessoa,'arquivo':nome+'.webm','origem':origem,'status':'em_captura'}
            gravando=False
            try:
                executar(PREPARAR.replace('URL',origem).replace('VISTA',vista))
                if nome.startswith('03_'):
                    executar("async page=>{await page.locator('#chave').fill('chave-qa-mobile-sintetica');await page.locator('#lote-detalhes > summary').click();await page.locator('#lote-detalhes').scrollIntoViewIfNeeded();return {ambiente_qa_preparado:true};}")
                if vista=='ouviai':
                    executar("async page=>{await page.getByRole('button',{name:'Limpar demonstração',exact:true}).click();await page.evaluate(()=>scrollTo(0,200));return {simulacao_limpa:true};}")
                existente=SAIDA/item['arquivo']
                if existente.exists():existente.rename(existente.with_name(existente.stem+'.tentativa-'+datetime.now(timezone.utc).strftime('%H%M%S')+'.webm'))
                cli('video-start',SAIDA/item['arquivo'],'--size=1920x1080','--fps=25','--cursor');gravando=True
                codigo=codigo.replace('CSV',(RAIZ/'docs/exemplos/cluster-revisoes.csv').as_posix()).replace('IMAGEM',(RAIZ/'materiais/visao/data/recortes/017_1135_2497.jpg').as_posix())
                item['resultado']=executar(codigo,nome+'.js')
                item['status']='capturado'
            except Exception as erro:
                item['status']='falha';item['erro']=str(erro)
            finally:
                if gravando:
                    try:cli('video-stop')
                    except Exception as erro:item.update(status='falha',erro=str(erro))
                caminho=SAIDA/item['arquivo']
                if caminho.is_file():
                    v=cv2.VideoCapture(str(caminho));fps=v.get(cv2.CAP_PROP_FPS);quadros=int(v.get(cv2.CAP_PROP_FRAME_COUNT));ok,_=v.read()
                    item.update(duracao_segundos=round(quadros/fps,2) if fps else 0,resolucao=[int(v.get(cv2.CAP_PROP_FRAME_WIDTH)),int(v.get(cv2.CAP_PROP_FRAME_HEIGHT))],bytes=caminho.stat().st_size,primeiro_quadro_decodificado=ok)
                    v.release()
                    if not ok or not quadros:item['status']='falha'
                manifesto['clipes'].append(item)
                (SAIDA/'manifesto.json').write_text(json.dumps(manifesto,ensure_ascii=False,indent=2),encoding='utf-8')
                print(json.dumps({k:item[k] for k in ('id','status','duracao_segundos') if k in item},ensure_ascii=False),flush=True)
    finally:
        cli('close','--raw')
    assert all(c['status']=='capturado' for c in manifesto['clipes']),'Há capturas pendentes; conferir manifesto.'
    assert len(manifesto['clipes'])==6

if __name__=='__main__':main()
