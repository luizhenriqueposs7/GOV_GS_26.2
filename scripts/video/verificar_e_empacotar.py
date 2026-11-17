"""Decodifica todas as capturas e reúne as fontes, sem retimar ou remontar os vídeos."""
from pathlib import Path
import json
from zipfile import ZipFile, ZIP_DEFLATED
import cv2
from PIL import Image, ImageDraw

RAIZ=Path(__file__).resolve().parents[2]
FONTES=RAIZ/'output/video/fontes_independentes'
REVISAO=RAIZ/'.tmp/revisao-capturas'

def main():
    manifesto=json.loads((FONTES/'manifesto.json').read_text(encoding='utf-8'))
    assert len(manifesto['clipes'])==6 and all(c['status']=='capturado' for c in manifesto['clipes'])
    REVISAO.mkdir(parents=True,exist_ok=True)
    resultados=[];quadros=[]
    for c in manifesto['clipes']:
        caminho=FONTES/c['arquivo'];cap=cv2.VideoCapture(str(caminho));assert cap.isOpened(),caminho
        fps=cap.get(cv2.CAP_PROP_FPS);total=int(cap.get(cv2.CAP_PROP_FRAME_COUNT));assert fps==25 and total>0
        alvos={0,total//2,max(0,total-2)};lidos=0
        while True:
            ok,frame=cap.read()
            if not ok:break
            assert frame.shape[:2]==(1080,1920),c['id']
            if lidos in alvos:
                arquivo=REVISAO/f"{c['id']}-{lidos:05}.jpg";cv2.imwrite(str(arquivo),frame)
                im=Image.open(arquivo).convert('RGB');im.thumbnail((600,338))
                quadro=Image.new('RGB',(620,370),'#e3e6e3');quadro.paste(im,((620-im.width)//2,25));ImageDraw.Draw(quadro).text((8,7),c['id']+' / '+str(round(lidos/fps,2))+'s',fill='black');quadros.append(quadro)
            lidos+=1
        cap.release();assert lidos>=total-2,(c['id'],total,lidos)
        resultados.append({'id':c['id'],'arquivo':c['arquivo'],'fps':fps,'resolucao':[1920,1080],'quadros_decodificados':lidos,'duracao_segundos':round(lidos/fps,2),'bytes':caminho.stat().st_size,'audio':False,'origem':c['origem']})
        print(json.dumps(resultados[-1],ensure_ascii=False),flush=True)
    for inicio in range(0,len(quadros),9):
        grade=Image.new('RGB',(1860,1110),'#e3e6e3')
        for j,im in enumerate(quadros[inicio:inicio+9]):grade.paste(im,((j%3)*620,(j//3)*370))
        grade.save(REVISAO/f'contato-{inicio//9+1}.png')
    (FONTES/'verificacao.json').write_text(json.dumps(resultados,ensure_ascii=False,indent=2),encoding='utf-8')
    linhas=['CAPTURAS INDEPENDENTES - ZELABAIRRO','Fontes brutas, sem narração, a 1,0x. Não constituem o vídeo final.','Resolução nativa: 1920 x 1080 / 25 fps / WebM.','',
      'A abertura, GenAI, PLN, Visão e OuviAí foram gravados na versão oficial https://gov262.vercel.app.',
      'Cluster: execução real do pipeline em base local de QA isolada, com threads e CSV fictício. Não é execução HTTP na Vercel.',
      'OuviAí: captura real da interface conceitual, cujos eventos são simulados. Sem hardware ou reconhecimento de áudio nessa tela.',
      'GenAI/PLN/Visão: consultas sem vínculo com pedido; nenhuma solicitação municipal foi criada.','',
      'ARQUIVOS']
    linhas.extend(f"{r['arquivo']} - {r['duracao_segundos']:.2f}s - {r['origem']}" for r in resultados)
    linhas.extend(['','PENDENTES PARA MONTAR O VÍDEO FINAL',*manifesto['pendentes'],'',
      'Envie o vídeo original do celular, incluindo conferência/envio e recibo/ID. Deixe o pedido aguardando revisão.',
      'Envie os áudios por cena, conforme os PDFs e textos individuais. Não é necessário gravar a tela novamente.',
      'A duração final de 5 a 7 minutos será conferida depois da montagem. A espera pode ser cortada com identificação, preservando ordem e resultados. Não acelerar falas nem inventar execução.'])
    (FONTES/'LEIA-ME.txt').write_text('\n'.join(linhas),encoding='utf-8')
    destino=RAIZ/'output/video/Capturas_independentes_ZelaBairro.zip'
    with ZipFile(destino,'w',ZIP_DEFLATED) as z:
        for r in resultados:z.write(FONTES/r['arquivo'],r['arquivo'])
        for nome in ('manifesto.json','verificacao.json','LEIA-ME.txt'):z.write(FONTES/nome,nome)
    print(json.dumps({'pacote':str(destino),'clipes':len(resultados),'total_fontes_segundos':round(sum(r['duracao_segundos'] for r in resultados),2)},ensure_ascii=False))

if __name__=='__main__':main()
