"""Diagrama o relatório de Governança; requer ReportLab e pypdf no ambiente de documentos."""
import re
from html import escape
from pathlib import Path

from pypdf import PdfReader
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Flowable, Image, KeepTogether

RAIZ = Path(__file__).resolve().parents[1]
SAIDA = RAIZ / "output/pdf/ZelaBairro_Relatorio_Governanca.pdf"
LARGURA = A4[0] - 5 * cm
LARANJA = colors.HexColor("#F67024")
ESCURO = colors.HexColor("#19221C")
try:
    pdfmetrics.registerFont(TTFont("Geometrica", "C:/Windows/Fonts/bahnschrift.ttf"))
    TITULO = "Geometrica"
except (OSError, ValueError):
    TITULO = "Helvetica-Bold"

estilos = {
    "texto": ParagraphStyle("texto", fontName="Times-Roman", fontSize=12, leading=18, alignment=TA_JUSTIFY, firstLineIndent=1.25*cm, spaceAfter=9, textColor=ESCURO),
    "h1": ParagraphStyle("h1", fontName=TITULO, fontSize=18, leading=23, spaceBefore=0, spaceAfter=21, textColor=ESCURO),
    "h2": ParagraphStyle("h2", fontName=TITULO, fontSize=14, leading=19, spaceBefore=14, spaceAfter=12, textColor=ESCURO),
    "legenda": ParagraphStyle("legenda", fontName="Times-Roman", fontSize=10, leading=13, spaceBefore=6, spaceAfter=8, alignment=TA_LEFT),
    "lista": ParagraphStyle("lista", fontName="Times-Roman", fontSize=12, leading=18, spaceAfter=12, alignment=TA_LEFT),
    "referencia": ParagraphStyle("referencia", fontName="Times-Roman", fontSize=12, leading=14.5, spaceAfter=12, alignment=TA_LEFT, splitLongWords=True),
    "celula": ParagraphStyle("celula", fontName="Times-Roman", fontSize=10, leading=13, spaceAfter=0),
    "cabecalho": ParagraphStyle("cabecalho", fontName="Helvetica-Bold", fontSize=9, leading=12, textColor=colors.white),
}


def marcado(texto):
    texto = escape(texto)
    return re.sub(r"\[([^\]]+)\]\((https?://[^\s)]+)\)", r'<link href="\2" color="#305B38">\1</link>', texto)


class Fluxo(Flowable):
    def __init__(self):
        super().__init__()
        self.width = LARGURA
        self.height = 145

    def draw(self):
        c = self.canv
        largura = (self.width - 36) / 4
        for i, titulo in enumerate(("Relato", "RPA e contexto", "Revisão", "Registro local")):
            x = i * (largura + 12)
            c.setFillColor(ESCURO if i == 2 else colors.HexColor("#E9EDE6"))
            c.rect(x, 92, largura, 38, fill=1, stroke=0)
            c.setFillColor(colors.white if i == 2 else ESCURO)
            c.setFont("Helvetica", 9)
            c.drawCentredString(x + largura/2, 107, titulo)
            if i < 3:
                c.setStrokeColor(LARANJA); c.line(x+largura+1, 111, x+largura+11, 111)
        c.setFont("Helvetica", 8)
        c.setFillColor(colors.HexColor("#4D5A4C"))
        c.drawString(0, 72, "Apoio ao registro: fontes municipais, corpus de PLN, Visão e serviço de GenAI.")
        c.setStrokeColor(colors.HexColor("#C1CABB"));c.line(0, 60, self.width, 60)
        c.setFont("Helvetica", 8.5)
        c.drawString(0, 41, "IoT: áudio com modelo alternativo  |  Cluster: workers lógicos  |  Quântica: QAOA simulado")
        c.setFont("Helvetica", 8)
        c.drawString(0, 22, "Passagem Livre compara reparos e conserva a decisão. Chamado municipal: canal oficial.")


def tabela(linhas):
    dados = [[x.strip() for x in l.strip().strip("|").split("|")] for l in linhas]
    dados = [r for r in dados if not all(re.fullmatch(r"[:\- ]+", x) for x in r)]
    cells = [[Paragraph(marcado(x), estilos["cabecalho"] if i == 0 else estilos["celula"]) for x in row] for i, row in enumerate(dados)]
    t = Table(cells, colWidths=[LARGURA*.29, LARGURA*.37, LARGURA*.34], repeatRows=1, hAlign="LEFT")
    t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),ESCURO),("VALIGN",(0,0),(-1,-1),"TOP"),("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.HexColor("#F0F2EE"),colors.white]),("LINEBELOW",(0,0),(-1,0),2,LARANJA),("LINEBELOW",(0,1),(-1,-1),.4,colors.HexColor("#CCD2C8")),("LEFTPADDING",(0,0),(-1,-1),8),("RIGHTPADDING",(0,0),(-1,-1),8),("TOPPADDING",(0,0),(-1,-1),8),("BOTTOMPADDING",(0,0),(-1,-1),8)]))
    return t


def fundo(c, doc):
    pagina = doc.page
    c.saveState()
    if pagina == 1:
        w,h=A4;c.setFillColor(ESCURO);c.rect(0,0,w,h,fill=1,stroke=0)
        for i in range(7):
            for j in range(5):
                c.setFillColor(LARANJA if (i,j) in {(1,1),(4,0),(6,3)} else colors.HexColor("#2D4031"))
                c.rect(w-227+i*35,h-235-j*35,29,29,fill=1,stroke=0)
        c.setFillColor(LARANJA);c.setFont(TITULO,14);c.drawString(3*cm,h-3*cm,"FIAP / GLOBAL SOLUTION 2026")
        c.setFillColor(colors.white);c.setFont(TITULO,38);c.drawString(3*cm,h-11*cm,"Central")
        c.drawString(3*cm,h-12.6*cm,"CitizenTech")
        c.setFont("Helvetica",14);c.drawString(3*cm,h-14*cm,"Planejamento de acesso,")
        c.drawString(3*cm,h-14.7*cm,"pedidos e revisão")
        c.setStrokeColor(LARANJA);c.line(3*cm,h-16*cm,w-2*cm,h-16*cm)
        c.setFont("Helvetica",10);c.drawString(3*cm,h-17*cm,"GOVERNANÇA EM IA E BUSINESS ANALYTICS")
        for i,nome in enumerate(("Luiz Henrique Poss | RM562177","Luis Filipe Chaves Amorim | RM564706","Felipe Stefani Honorato | RM563380")):
            c.drawString(3*cm,5.4*cm-i*18,nome)
        c.drawString(3*cm,2.1*cm,"SÃO PAULO / 2026")
    else:
        c.setFillColor(colors.HexColor("#6B7468"));c.setFont("Helvetica",7)
        c.drawString(3*cm,A4[1]-1.9*cm,"CITIZENTECH / GOVERNANÇA EM IA E BUSINESS ANALYTICS")
        c.setStrokeColor(LARANJA);c.setLineWidth(1);c.line(3*cm,A4[1]-2.2*cm,A4[0]-2*cm,A4[1]-2.2*cm)
        if pagina >= 6:
            c.setFont("Times-Roman",10);c.drawRightString(A4[0]-2*cm,A4[1]-1.9*cm,str(pagina-1))
        c.setFillColor(colors.HexColor("#6B7468"));c.setFont("Helvetica",6.5)
        if pagina == 2:
            c.setFillColor(ESCURO);c.setFont("Times-Roman",12)
            for i,nome in enumerate(("Luiz Henrique Poss · RM562177","Luis Filipe Chaves Amorim · RM564706","Felipe Stefani Honorato · RM563380")):
                c.drawCentredString(A4[0]/2,A4[1]-4*cm-i*20,nome)
            c.setFont(TITULO,18);c.drawCentredString(A4[0]/2,A4[1]-8*cm,"CENTRAL CITIZENTECH")
            c.setFont("Times-Roman",12);c.drawCentredString(A4[0]/2,A4[1]-9*cm,"Planejamento de acesso, pedidos e revisão")
            natureza=Paragraph("Relatório de integração dos trabalhos da Global Solution, apresentado à disciplina de Governança em IA e Business Analytics da FIAP. O documento descreve a participação dos módulos e os limites da aplicação construída.",ParagraphStyle("natureza",fontName="Times-Roman",fontSize=12,leading=18,alignment=TA_JUSTIFY))
            _,altura=natureza.wrap(8*cm,500);natureza.drawOn(c,A4[0]-10*cm,A4[1]-11*cm-altura)
            nota=Paragraph("Percurso didático. A validação do projeto foi técnica, em ambiente de demonstração.",estilos["legenda"])
            _,altura=nota.wrap(LARGURA,100);nota.drawOn(c,3*cm,6*cm-altura)
            c.setFont("Times-Roman",12);c.drawCentredString(A4[0]/2,3*cm,"São Paulo · 2026")
    c.restoreState()


def main():
    paginas = (RAIZ / "docs/relatorio-base.md").read_text(encoding="utf-8").split("<!-- pagina -->")
    assert len(paginas) == 14
    story = []
    for numero, pagina in enumerate(paginas, 1):
        if numero > 1: story.append(PageBreak())
        if numero in (1, 2): story.append(Spacer(1, 1));continue
        blocos = re.split(r"\n\s*\n", pagina.strip())
        for bloco in blocos:
            bloco=bloco.strip()
            if bloco.startswith("|"):
                story.append(tabela(bloco.splitlines()));continue
            if bloco == "[[figura-fluxo]]":story.append(Fluxo());continue
            if bloco == "[[figura-visao]]":
                imagem=Image(str(RAIZ / "materiais/visao/data/recortes/017_1135_2497.jpg"),width=115,height=115)
                imagem.hAlign="CENTER";story.append(imagem);continue
            chave="texto"
            if bloco.startswith("## "):chave="h2";bloco=bloco[3:]
            elif bloco.startswith("# "):chave="h1";bloco=bloco[2:]
            elif bloco.startswith(("Fonte:","Figura ","Tabela ","Quadro ")):chave="legenda"
            elif numero in (3,4,5):chave="lista"
            elif numero == 14:chave="referencia"
            story.append(Paragraph(marcado(bloco),estilos[chave]))
    SAIDA.parent.mkdir(parents=True,exist_ok=True)
    doc=SimpleDocTemplate(str(SAIDA),pagesize=A4,leftMargin=3*cm,rightMargin=2*cm,topMargin=3*cm,bottomMargin=2*cm,title="Central CitizenTech - Governança",author="Luiz Henrique Poss; Luis Filipe Chaves Amorim; Felipe Stefani Honorato")
    doc.build(story,onFirstPage=fundo,onLaterPages=fundo)
    leitor=PdfReader(SAIDA)
    assert len(leitor.pages)==14, f"A paginação mudou para {len(leitor.pages)}. Ajuste o conteúdo e o sumário."
    for i,p in enumerate(leitor.pages,1):
        assert (p.extract_text() or "").strip(),f"Página {i} vazia"
    print(f"PDF criado: {len(leitor.pages)} páginas.")


if __name__=="__main__":main()
