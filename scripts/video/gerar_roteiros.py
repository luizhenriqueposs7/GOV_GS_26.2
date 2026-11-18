"""Gera PDFs individuais e textos de narração a partir dos roteiros versionados."""
from pathlib import Path
import re
import json
from html import escape
from zipfile import ZipFile, ZIP_DEFLATED

import fitz
from PIL import Image, ImageDraw
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, KeepTogether

RAIZ=Path(__file__).resolve().parents[2]
SAIDA=RAIZ/'output/video/roteiros_individuais'
REVISAO=RAIZ/'.tmp/revisao-roteiros-video'
ESCURO=colors.HexColor('#20282a');LARANJA=colors.HexColor('#F67024')
pdfmetrics.registerFont(TTFont('Archivo',str(RAIZ/'web/vendor/archivo-regular.ttf')))
pdfmetrics.registerFont(TTFont('ArchivoBold',str(RAIZ/'web/vendor/archivo-bold.ttf')))
pdfmetrics.registerFontFamily('Archivo',normal='Archivo',bold='ArchivoBold')
ESTILOS={
 'texto':ParagraphStyle('texto',fontName='Archivo',fontSize=11,leading=16,spaceAfter=9,textColor=ESCURO),
 'titulo':ParagraphStyle('titulo',fontName='ArchivoBold',fontSize=15,leading=20,spaceBefore=14,spaceAfter=12,textColor=ESCURO,keepWithNext=True),
 'fala':ParagraphStyle('fala',fontName='Archivo',fontSize=11.5,leading=17,spaceAfter=12,leftIndent=12,borderColor=LARANJA,borderWidth=1,borderPadding=10,textColor=ESCURO),
 'nota':ParagraphStyle('nota',fontName='Archivo',fontSize=9,leading=13,spaceAfter=8,textColor=colors.HexColor('#515c60'),keepWithNext=True),
 'acoes':ParagraphStyle('acoes',fontName='Archivo',fontSize=11,leading=16,spaceAfter=9,textColor=ESCURO,keepWithNext=True),
}
PESSOAS=[
 ('01-luiz-henrique.md','Luiz Henrique Poss','RM562177','Luiz_Henrique','4min','GenAI, Governança, PLN, Cluster e mobile'),
 ('02-luis-filipe.md','Luis Filipe Chaves Amorim','RM564706','Luis_Filipe','1min28s','Computação Quântica e IoT'),
 ('03-felipe-stefani.md','Felipe Stefani Honorato','RM563380','Felipe','1min02s','RPA e Visão Computacional'),
]
ARQUIVOS_AUDIO={
 '00:00':'00_abertura','00:15':'01_frontend_celular','01:00':'02_rpa','01:24':'03_cluster',
 '01:54':'04_quantica','02:49':'05_generative_ai','03:19':'06_pln','03:44':'07_visao',
 '04:22':'08_iot','04:55':'09_governanca','06:15':'10_encerramento',
}

def marcado(texto):
    texto=escape(texto.replace('–','-').replace('—','-').replace('\u2011','-'))
    texto=re.sub(r'\*\*(.*?)\*\*',r'<b>\1</b>',texto)
    return texto.replace('`','')

def fundo(nome,rm,duracao,disciplinas):
    def desenhar(c,doc):
        w,h=A4;c.saveState()
        if doc.page==1:
            c.setFillColor(ESCURO);c.rect(0,0,w,h,fill=1,stroke=0)
            for i in range(5):
                for j in range(4):
                    c.setFillColor(LARANJA if (i,j) in {(0,2),(3,0),(4,3)} else colors.HexColor('#354447'))
                    c.rect(w-195+i*29,h-155-j*29,23,23,fill=1,stroke=0)
            c.setFillColor(LARANJA);c.setFont('ArchivoBold',13);c.drawString(2.5*cm,h-3*cm,'ZelaBairro / CitizenTech')
            c.setFillColor(colors.white);c.setFont('ArchivoBold',34)
            c.drawString(2.5*cm,h-9.3*cm,'Roteiro individual')
            c.setFont('Archivo',17);c.drawString(2.5*cm,h-10.5*cm,'Voz e demonstração de tela')
            estilo=ParagraphStyle('nome',fontName='ArchivoBold',fontSize=21,leading=28,textColor=colors.white)
            p=Paragraph(escape(nome),estilo);_,altura=p.wrap(w-5*cm,200);p.drawOn(c,2.5*cm,h-13*cm-altura)
            c.setFont('Archivo',13);c.drawString(2.5*cm,h-15.3*cm,rm)
            c.setStrokeColor(LARANJA);c.line(2.5*cm,h-16.3*cm,w-2.5*cm,h-16.3*cm)
            p=Paragraph(escape(disciplinas),ParagraphStyle('disciplinas',fontName='Archivo',fontSize=12,leading=18,textColor=colors.white))
            _,altura=p.wrap(w-5*cm,200);p.drawOn(c,2.5*cm,h-17.2*cm-altura)
            c.setFont('Archivo',11);c.drawString(2.5*cm,5*cm,'Tempo planejado deste integrante: '+duracao)
            c.drawString(2.5*cm,4.25*cm,'Montagem prevista: 6min30s / três integrantes')
            c.setFont('Archivo',9);c.drawString(2.5*cm,2.9*cm,'Apoio para ensaio. Use suas palavras e descreva o resultado real.')
            c.drawString(2.5*cm,2.25*cm,'17 de novembro de 2026')
        else:
            c.setFillColor(ESCURO);c.setFont('Archivo',8);c.drawString(2.5*cm,h-1.6*cm,nome+' / '+rm)
            c.setStrokeColor(LARANJA);c.line(2.5*cm,h-1.9*cm,w-2.2*cm,h-1.9*cm)
            c.setFillColor(colors.HexColor('#515c60'));c.setFont('Archivo',8)
            c.drawString(2.5*cm,1.25*cm,'Roteiro de gravação / ZelaBairro')
            c.drawRightString(w-2.2*cm,1.25*cm,str(doc.page))
        c.restoreState()
    return desenhar

def main():
    SAIDA.mkdir(parents=True,exist_ok=True);REVISAO.mkdir(parents=True,exist_ok=True)
    gerados=[];quadros=[]
    for fonte,nome,rm,curto,duracao,disciplinas in PESSOAS:
        texto=(RAIZ/'docs/video'/fonte).read_text(encoding='utf-8')
        assert rm in texto and nome in texto
        destino=SAIDA/f'Roteiro_{curto}_{rm}.pdf'
        story=[Spacer(1,1),PageBreak(),Paragraph('Como enviar sua narração',ESTILOS['titulo']),
          Paragraph('Grave um áudio separado por cena, com sua voz e ritmo natural. Leia somente a fala, sem os horários ou as instruções de tela. Os tempos são referência para o ensaio, não uma ordem para acelerar. Deixe uma pequena margem no começo e no fim e envie o arquivo original, como M4A, WAV ou MP3.',ESTILOS['texto']),
          Paragraph('Captura da plataforma: assistente. Trecho de foto/GPS no celular: Luiz. Montagem e sincronização serão feitas depois do recebimento dos arquivos. As ações de tela abaixo servem para contextualizar o que sua fala acompanha.',ESTILOS['texto'])]
        falas=[nome+' / '+rm,'FALAS PARA GRAVAR','Grave um arquivo por cena. Não leia títulos, horários ou nomes de arquivo.','']
        trecho_atual='';numero_falas=0
        for bloco in re.split(r'\n\s*\n',texto.strip()):
            if bloco.startswith('# '):continue
            if bloco.startswith('## '):
                trecho_atual=bloco[3:]
                hora=trecho_atual[:5];arquivo=ARQUIVOS_AUDIO[hora]+'_'+curto.lower()+'.m4a'
                story.append(Paragraph(marcado(trecho_atual),ESTILOS['titulo']))
                story.append(Paragraph('Nome sugerido do áudio: '+arquivo,ESTILOS['nota']))
                falas.extend([trecho_atual,'Arquivo: '+arquivo,''])
            else:
                e_fala=bloco.startswith(('**Fala base:**','**Passagem:**'))
                for linha in bloco.splitlines():
                    estilo='fala' if e_fala else 'acoes' if linha.startswith(('**Ações:**','**Tela:**')) else 'texto'
                    paragrafo=Paragraph(marcado(linha),ESTILOS[estilo])
                    story.append(KeepTogether([paragrafo]) if e_fala else paragrafo)
                if e_fala:
                    dito=re.search('“([^”]+)”',bloco)
                    assert dito,bloco
                    falas.extend([dito[1],'']);numero_falas+=1
        assert numero_falas>=2
        doc=SimpleDocTemplate(str(destino),pagesize=A4,leftMargin=2.5*cm,rightMargin=2.2*cm,topMargin=2.6*cm,bottomMargin=2*cm,title='Roteiro individual - '+nome,author=nome)
        desenhar=fundo(nome,rm,duracao,disciplinas);doc.build(story,onFirstPage=desenhar,onLaterPages=desenhar)
        voz=SAIDA/f'Falas_{curto}_{rm}.txt';voz.write_text('\n'.join(falas),encoding='utf-8')
        with fitz.open(destino) as pdf:
            completo='\n'.join(p.get_text() for p in pdf)
            assert rm in completo and 'Fala base:' in completo and len(pdf)>=2
            for i,pagina in enumerate(pdf):
                imagem=REVISAO/f'{curto}-{i+1:02}.png';pagina.get_pixmap(matrix=fitz.Matrix(1.2,1.2),alpha=False).save(imagem)
                im=Image.open(imagem).convert('RGB');im.thumbnail((300,425));quadro=Image.new('RGB',(320,455),'#e4e6e4');quadro.paste(im,((320-im.width)//2,24));ImageDraw.Draw(quadro).text((8,6),f'{curto} / {i+1}',fill='black');quadros.append(quadro)
            gerados.append({'nome':nome,'rm':rm,'pdf':destino.name,'paginas':len(pdf),'falas':voz.name,'blocos_de_fala':numero_falas})
    for inicio in range(0,len(quadros),8):
        contato=Image.new('RGB',(1280,910),'#e4e6e4')
        for j,im in enumerate(quadros[inicio:inicio+8]):contato.paste(im,((j%4)*320,(j//4)*455))
        contato.save(REVISAO/f'contato-{inicio//8+1}.png')
    with ZipFile(SAIDA/'Roteiros_para_os_tres_integrantes.zip','w',ZIP_DEFLATED) as z:
        for item in gerados:
            for campo in ('pdf','falas'):z.write(SAIDA/item[campo],item[campo])
    (SAIDA/'indice.json').write_text(json.dumps(gerados,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(gerados,ensure_ascii=False))

if __name__=='__main__':main()
