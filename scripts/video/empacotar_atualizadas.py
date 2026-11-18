"""Verifica a nova captura inteira e empacota seis fontes sem incluir vozes."""
from pathlib import Path
import sys,json,hashlib
from datetime import datetime,timezone
from zipfile import ZipFile,ZIP_DEFLATED
import av
sys.path.append(str(Path(sys.base_prefix)/'Lib/site-packages'))
from PIL import Image,ImageDraw

raiz=Path(__file__).resolve().parents[2]; fontes=raiz/'output/video/fontes_independentes'
anterior=json.loads((fontes/'manifesto.json').read_text(encoding='utf-8'))
novo=json.loads((fontes/'08_iot_ouviai_inferencia_controlada.json').read_text(encoding='utf-8'))
video=fontes/novo['arquivo']; n=0;amostras=[]
with av.open(str(video)) as c:
    s=c.streams.video[0];fps=float(s.average_rate);resolucao=[s.codec_context.width,s.codec_context.height]
    assert fps==25 and resolucao==[1920,1080] and len(c.streams.audio)==0
    for f in c.decode(s):
        if n in [0,250,500,750,1000]:
            im=f.to_image();im.thumbnail((600,338));amostras.append((n/fps,im))
        n+=1
duracao=n/fps;assert duracao>=33.067 and novo['resultado']['inferencia_real'] and novo['resultado']['microfone_encerrado']
assert not novo['resultado']['predicoes_mockadas'] and not novo['resultado']['uploads']
novo.update(duracao_segundos=round(duracao,3),quadros_decodificados=n,bytes=video.stat().st_size,sha256=hashlib.sha256(video.read_bytes()).hexdigest())
(fontes/'08_iot_ouviai_inferencia_controlada.json').write_text(json.dumps(novo,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
grade=Image.new('RGB',(610*min(3,len(amostras)),380*((len(amostras)+2)//3)), '#ddd');d=ImageDraw.Draw(grade)
for i,(t,im) in enumerate(amostras):
    x=610*(i%3);y=380*(i//3);grade.paste(im,(x,y+22));d.text((x+8,y+4),f'IoT atual / {t:.1f}s',fill='black')
grade.save(raiz/'.tmp/verificacao-midia-2026-11-17/contato-iot-atualizado.png')
ativos=[c for c in anterior['clipes'] if not c['id'].startswith('08_')]
ativos.append({'id':'08_iot_ouviai_inferencia_controlada','arquivo':novo['arquivo'],'status':'capturado',
               'origem':novo['resultado']['origem'],'duracao_segundos':novo['duracao_segundos'],
               'resultado':novo['resultado'],'legenda_obrigatoria':novo['legenda_obrigatoria_montagem']})
assert len(ativos)==6 and all('simulacao' not in x['arquivo'] for x in ativos)
for c in ativos:c['sha256']=hashlib.sha256((fontes/c['arquivo']).read_bytes()).hexdigest()
manifesto={'atualizado_em_utc':datetime.now(timezone.utc).isoformat(),'resolucao':[1920,1080],'fps':25,'audio':False,
           'velocidade':1.0,'clipes':ativos,'arquivo_anterior_nao_usar_como_inferencia_atual':'08_iot_ouviai_simulacao.webm',
           'audios_recebidos_selecionados_s':149.516,'alvo_partes_luiz_s':240,'soma_planejada_s':389.516,
           'pendentes':['partes de Luiz','gravação móvel e ID','RPA, Quântica e Governança do mesmo pedido',
                       'mixagem, montagem e escuta final','conclusão conjunta e YouTube Não Listado']}
arquivo_manifesto=fontes/'manifesto_atualizado_2026-11-18.json'
arquivo_manifesto.write_text(json.dumps(manifesto,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
leia='''CAPTURAS ATUALIZADAS PARA MONTAGEM - ZELABAIRRO
Fontes brutas sem narração: 1920 x 1080, 25 fps, velocidade 1,0x.
Não constituem o vídeo final.

IoT atual: reconhecimento real com YAMNet no navegador oficial, recebendo WAV de referência no microfone virtual do Chrome. A anotação de teste foi acrescentada pelo gravador, sem alterar resultados do modelo. Manter identificação de teste controlado na montagem. Não houve dispositivo físico ou captura do microfone de um celular real neste ensaio.
Narração selecionada para IoT: áudio_IoT.m4a (33,067 s), recebida separadamente. O pacote não inclui vozes.
O clipe antigo 08_iot_ouviai_simulacao.webm foi excluído deste pacote.

Cluster: execução real em QA local isolado com CSV fictício e workers lógicos. Não é execução HTTP na Vercel.
GenAI/PLN/Visão: consultas reais sem vínculo ao futuro pedido móvel.
Na Visão, o recorte utilizado resultou em Sem fissura sinalizada; não substituir o rótulo na edição.

Os áudios recebidos somam 2min29,516s. Reservar cerca de quatro minutos para todas as partes de Luiz. A soma de 6min29,516s é planejamento, não duração de um vídeo já montado. Cortar esperas somente com identificação, preservando operação e resultados; não acelerar vozes.
Ainda faltam gravação móvel, ID e cenas de RPA/Quântica/Governança ligadas a esse ID, partes de Luiz e montagem final.
'''
destino=raiz/'output/video/Capturas_atualizadas_ZelaBairro_2026-11-18.zip'
with ZipFile(destino,'w',ZIP_DEFLATED) as z:
    for c in ativos:z.write(fontes/c['arquivo'],c['arquivo'])
    z.write(arquivo_manifesto,'manifesto.json');z.write(fontes/'08_iot_ouviai_inferencia_controlada.json','evidencia_iot.json')
    z.writestr('LEIA-ME.txt',leia)
with ZipFile(destino) as z:
    assert z.testzip() is None and len([n for n in z.namelist() if n.endswith('.webm')])==6
print(json.dumps({'captura_iot_segundos':duracao,'quadros_iot':n,'pacote':str(destino),'clipes':len(ativos),'total_fontes_s':sum(x['duracao_segundos'] for x in ativos)},ensure_ascii=False))
