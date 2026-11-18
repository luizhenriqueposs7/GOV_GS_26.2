"""Captura controlada do OuviAí 0.6.5, sem voz ou escrita de pedidos.

Executar da raiz do projeto depois de preparar o WAV ESC-50 citado em
docs/evidencias/ouviai-audio-2026-11-17.md como .tmp/iot-porta.wav.
O script preserva capturas existentes em vez de sobrescrevê-las.
"""
from pathlib import Path
import subprocess,json,os,hashlib
from datetime import datetime,timezone

raiz=Path(__file__).resolve().parents[2]; trabalho=raiz/'.tmp/verificacao-midia-2026-11-17'
trabalho.mkdir(parents=True,exist_ok=True)
saida=raiz/'output/video/fontes_independentes'; nome='08_iot_ouviai_inferencia_controlada'
cli=Path('C:/Users/luizh/AppData/Local/npm-cache/_npx/31e32ef8478fbf80/node_modules/@playwright/cli/playwright-cli.js')
# shortcut: CLI/ffmpeg são os caches desta máquina; ajustar esses caminhos em outro ambiente.
audio=raiz/'.tmp/iot-porta.wav'
referencia=json.loads((raiz/'docs/evidencias/ouviai-audio-2026-11-17.json').read_text(encoding='utf-8'))
assert audio.is_file(), 'Prepare o WAV de referência descrito na documentação.'
assert hashlib.sha256(audio.read_bytes()).hexdigest()==referencia['arquivos_teste']['iot-porta.wav']
config={'browser':{'browserName':'chromium','launchOptions':{'channel':'chrome','args':[
    '--use-fake-ui-for-media-stream','--use-fake-device-for-media-stream',
    '--use-file-for-fake-audio-capture='+audio.as_posix()]},
    'contextOptions':{'locale':'pt-BR','serviceWorkers':'block','viewport':{'width':390,'height':844}}}}

config['browser']['contextOptions']['viewport']={'width':1920,'height':1080}
cfg=trabalho/'chrome-iot-atualizado.json';cfg.write_text(json.dumps(config),encoding='utf-8')
arquivo=saida/(nome+'.webm');assert not arquivo.exists(),'Captura já existe: preservar em vez de sobrescrever.'
env=os.environ.copy();env['PLAYWRIGHT_BROWSERS_PATH']=str(raiz/'.tmp/qa-mobile-2026-11-17/browsers')

def executar(*args):
    r=subprocess.run(['node',str(cli),'-s=iot-captura-atual',*map(str,args)],capture_output=True,text=True,encoding='utf-8',cwd=raiz,timeout=160,env=env)
    if r.returncode: raise RuntimeError((r.stdout+'\n'+r.stderr)[-2500:])
    return r.stdout.strip()
def acao(codigo,n):
    p=trabalho/(n+'.js');p.write_text(codigo,encoding='utf-8');return json.loads(executar('run-code','--filename',p,'--raw'))

gravando=False
try:
    executar('open','https://gov262.vercel.app/#ouviai','--browser','chrome','--config',cfg,'--raw')
    acao('''async page=>{
      await page.locator('#ouviai-iniciar').waitFor({state:'visible'});
      const contrato=await (await page.request.get('https://gov262.vercel.app/openapi.json')).json();
      if(contrato.info.version!=='0.6.5')throw new Error('Aguardar publicação da versão 0.6.5.');
      await page.evaluate(()=>{
        const nota=document.createElement('p');nota.className='notice';
        nota.textContent='Teste controlado: áudio de referência no microfone virtual. Inferência real com YAMNet; sem estação física.';
        document.querySelector('.ouviai-disclosure').before(nota);
        document.fonts.ready.then(()=>scrollTo(0,0));
      });return {anotacao_de_gravacao:true};
    }''','preparar-iot')
    executar('video-start',arquivo,'--size=1920x1080','--fps=25','--cursor');gravando=True
    resultado=acao('''async page=>{
      const posts=[];page.on('request',r=>{if(!['GET','HEAD'].includes(r.method()))posts.push({url:r.url(),method:r.method()});});
      await page.waitForTimeout(3500);await page.locator('#ouviai-iniciar').click();
      await page.waitForFunction(()=>document.querySelector('#ouviai-microfone-status').textContent.startsWith('Escutando'),null,{timeout:90000});
      const estadoAntesDoResultado=await page.locator('#ouviai-display').textContent();
      if(estadoAntesDoResultado==='Microfone desligado')throw new Error('Estado de áudio incoerente.');
      await page.waitForFunction(()=>document.querySelector('#ouviai-status').textContent==='Possível batida na porta',null,{timeout:30000});
      const nota=await page.locator('#ouviai-status-nota').textContent();
      await page.waitForTimeout(9000);
      await page.locator('.ouviai-station').scrollIntoViewIfNeeded();await page.waitForTimeout(6500);
      await page.locator('#ouviai-eventos').scrollIntoViewIfNeeded();await page.waitForTimeout(6000);
      await page.locator('#ouviai-parar').click();await page.waitForTimeout(2000);
      if(posts.length)throw new Error('Escrita inesperada durante a captura.');
      return {origem:'https://gov262.vercel.app/#ouviai',entrada:'WAV de referência ESC-50 em microfone virtual do Chrome',
        modelo:'YAMNet float32 v1 / MediaPipe Tasks Audio 1.2.3',nota,
        versao:'0.6.5',estado_antes_do_resultado:estadoAntesDoResultado,
        inferencia_real:true,predicoes_mockadas:false,hardware_fisico:false,uploads:posts,
        microfone_encerrado:await page.locator('#ouviai-iniciar').isEnabled()};
    }''','gravar-iot')
    executar('video-stop');gravando=False
    meta={'arquivo':arquivo.name,'capturado_em_utc':datetime.now(timezone.utc).isoformat(),'fps':25,'resolucao':[1920,1080],
          'audio':False,'velocidade':1.0,'resultado':resultado,
          'substitui_como_cena_atual':'08_iot_ouviai_simulacao.webm','narracao_selecionada':'luis_iot_v2.m4a',
          'legenda_obrigatoria_montagem':'Teste controlado: áudio de referência no microfone virtual. Inferência real com YAMNet.'}
    (saida/(nome+'.json')).write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(meta,ensure_ascii=False))
finally:
    if gravando:
        try: executar('video-stop')
        except Exception: pass
    try: executar('close')
    except Exception: pass
