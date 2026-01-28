"""
Utilitários para geração de PDFs com cabeçalho padronizado
Arquivo: os_app/utils/pdf_utils.py
"""

from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm, cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from io import BytesIO
import os
from django.conf import settings


def criar_cabecalho_padrao(canvas_obj, doc, titulo_relatorio="Relatório", subtitulo=None):
    """
    Cria cabeçalho padronizado com brasão e logo
    
    Args:
        canvas_obj: Objeto canvas do ReportLab
        doc: Documento sendo gerado
        titulo_relatorio: Título do relatório (ex: "Relatório de Professores")
        subtitulo: Subtítulo opcional (ex: "Total: 50 professores")
    """
    canvas_obj.saveState()
    
    # Dimensões da página
    width, height = A4
    
    # ============================================================================
    # CONFIGURAR AQUI OS CAMINHOS DAS IMAGENS
    # ============================================================================
    # OPÇÃO 1: Imagens na pasta static
    # brasao_path = os.path.join(settings.STATIC_ROOT or settings.BASE_DIR, 'static', 'images', 'brasao.jpg')
    # logo_path = os.path.join(settings.STATIC_ROOT or settings.BASE_DIR, 'static', 'images', 'semec.jpg')
    
    # OPÇÃO 2: Imagens na pasta media
    brasao_path = os.path.join(settings.MEDIA_ROOT, 'relatorios', 'brasao.jpg')
    logo_path = os.path.join(settings.MEDIA_ROOT, 'relatorios', 'semec.jpg')
    
    # OPÇÃO 3: URLs absolutas (se as imagens estiverem em servidor web)
    # brasao_path = 'https://seuservidor.com/static/images/brasao.jpg'
    # logo_path = 'https://seuservidor.com/static/images/semec.jpg'
    # ============================================================================
    
    try:
        # Posições
        margem_esquerda = 25 * mm
        margem_direita = width - 25 * mm
        y_topo = height - 20 * mm
        
        # ============================================================
        # BRASÃO (Esquerda)
        # ============================================================
        if os.path.exists(brasao_path):
            try:
                brasao = Image(brasao_path, width=20*mm, height=20*mm)
                brasao.drawOn(canvas_obj, margem_esquerda, y_topo - 20*mm)
            except:
                pass  # Se falhar, continua sem a imagem
        
        # ============================================================
        # TEXTOS ESQUERDA (ao lado do brasão)
        # ============================================================
        x_texto_esquerda = margem_esquerda + 22*mm
        
        # Prefeitura
        canvas_obj.setFont("Helvetica-Bold", 10)
        canvas_obj.drawString(x_texto_esquerda, y_topo - 5*mm, "PREFEITURA MUNICIPAL DE MANACAPURU")
        
        # Secretaria
        canvas_obj.setFont("Helvetica-Bold", 9)
        canvas_obj.drawString(x_texto_esquerda, y_topo - 10*mm, "SECRETARIA MUNICIPAL DE EDUCAÇÃO E CULTURA")
        
        # Subtítulo
        canvas_obj.setFont("Helvetica", 7)
        canvas_obj.drawString(x_texto_esquerda, y_topo - 14*mm, "SEMEC - Sistema de Gestão de Professores")
        
        # ============================================================
        # LOGO SEMEC (Direita)
        # ============================================================
        if os.path.exists(logo_path):
            try:
                # Logo maior (proporção horizontal)
                logo = Image(logo_path, width=50*mm, height=15*mm)
                logo.drawOn(canvas_obj, margem_direita - 50*mm, y_topo - 18*mm)
            except:
                pass  # Se falhar, continua sem a imagem
        
        # ============================================================
        # LINHA SEPARADORA
        # ============================================================
        y_linha = y_topo - 23*mm
        canvas_obj.setStrokeColor(colors.HexColor('#0d6efd'))
        canvas_obj.setLineWidth(2)
        canvas_obj.line(margem_esquerda, y_linha, margem_direita, y_linha)
        
        # ============================================================
        # TÍTULO DO RELATÓRIO
        # ============================================================
        canvas_obj.setFont("Helvetica-Bold", 14)
        canvas_obj.setFillColor(colors.HexColor('#0d6efd'))
        titulo_width = canvas_obj.stringWidth(titulo_relatorio, "Helvetica-Bold", 14)
        canvas_obj.drawString((width - titulo_width) / 2, y_linha - 8*mm, titulo_relatorio)
        
        # Subtítulo (se fornecido)
        if subtitulo:
            canvas_obj.setFont("Helvetica", 9)
            canvas_obj.setFillColor(colors.grey)
            subtitulo_width = canvas_obj.stringWidth(subtitulo, "Helvetica", 9)
            canvas_obj.drawString((width - subtitulo_width) / 2, y_linha - 13*mm, subtitulo)
        
        # ============================================================
        # RODAPÉ
        # ============================================================
        y_rodape = 15 * mm
        canvas_obj.setFont("Helvetica", 8)
        canvas_obj.setFillColor(colors.grey)
        
        # Linha do rodapé
        canvas_obj.setStrokeColor(colors.grey)
        canvas_obj.setLineWidth(0.5)
        canvas_obj.line(margem_esquerda, y_rodape + 5*mm, margem_direita, y_rodape + 5*mm)
        
        # Textos do rodapé
        from datetime import datetime
        data_geracao = datetime.now().strftime("%d/%m/%Y às %H:%M")
        
        canvas_obj.drawString(margem_esquerda, y_rodape, f"Gerado em: {data_geracao}")
        canvas_obj.drawRightString(margem_direita, y_rodape, f"Página {doc.page}")
        
    except Exception as e:
        print(f"Erro ao criar cabeçalho: {e}")
        # Em caso de erro, apenas continua sem cabeçalho
        pass
    
    canvas_obj.restoreState()


def criar_cabecalho_paisagem(canvas_obj, doc, titulo_relatorio="Relatório", subtitulo=None):
    """
    Cria cabeçalho padronizado para orientação PAISAGEM
    
    Args:
        canvas_obj: Objeto canvas do ReportLab
        doc: Documento sendo gerado
        titulo_relatorio: Título do relatório
        subtitulo: Subtítulo opcional (ex: "Total: 50 professores")
    """
    canvas_obj.saveState()
    
    # Dimensões da página em paisagem
    width, height = landscape(A4)
    
    # ============================================================================
    # CONFIGURAR AQUI OS CAMINHOS DAS IMAGENS (mesmo que acima)
    # ============================================================================
    brasao_path = os.path.join(settings.MEDIA_ROOT, 'relatorios', 'brasao.jpg')
    logo_path = os.path.join(settings.MEDIA_ROOT, 'relatorios', 'semec.jpg')
    # ============================================================================
    
    try:
        # Posições (adaptadas para paisagem)
        margem_esquerda = 20 * mm
        margem_direita = width - 20 * mm
        y_topo = height - 15 * mm
        
        # Brasão menor em paisagem
        if os.path.exists(brasao_path):
            try:
                brasao = Image(brasao_path, width=15*mm, height=15*mm)
                brasao.drawOn(canvas_obj, margem_esquerda, y_topo - 15*mm)
            except:
                pass
        
        # Textos esquerda
        x_texto_esquerda = margem_esquerda + 17*mm
        
        canvas_obj.setFont("Helvetica-Bold", 9)
        canvas_obj.drawString(x_texto_esquerda, y_topo - 4*mm, "PREFEITURA MUNICIPAL DE MANACAPURU")
        
        canvas_obj.setFont("Helvetica-Bold", 8)
        canvas_obj.drawString(x_texto_esquerda, y_topo - 9*mm, "SECRETARIA MUNICIPAL DE EDUCAÇÃO E CULTURA")
        
        canvas_obj.setFont("Helvetica", 6)
        canvas_obj.drawString(x_texto_esquerda, y_topo - 12*mm, "SEMEC - Sistema de Gestão de Professores")
        
        # Logo direita
        if os.path.exists(logo_path):
            try:
                logo = Image(logo_path, width=45*mm, height=13*mm)
                logo.drawOn(canvas_obj, margem_direita - 45*mm, y_topo - 14*mm)
            except:
                pass
        
        # Linha separadora
        y_linha = y_topo - 17*mm
        canvas_obj.setStrokeColor(colors.HexColor('#0d6efd'))
        canvas_obj.setLineWidth(1.5)
        canvas_obj.line(margem_esquerda, y_linha, margem_direita, y_linha)
        
        # Título
        canvas_obj.setFont("Helvetica-Bold", 12)
        canvas_obj.setFillColor(colors.HexColor('#0d6efd'))
        titulo_width = canvas_obj.stringWidth(titulo_relatorio, "Helvetica-Bold", 12)
        canvas_obj.drawString((width - titulo_width) / 2, y_linha - 6*mm, titulo_relatorio)
        
        # Subtítulo (se fornecido)
        if subtitulo:
            canvas_obj.setFont("Helvetica", 8)
            canvas_obj.setFillColor(colors.grey)
            subtitulo_width = canvas_obj.stringWidth(subtitulo, "Helvetica", 8)
            canvas_obj.drawString((width - subtitulo_width) / 2, y_linha - 10*mm, subtitulo)
        
        # Rodapé
        y_rodape = 12 * mm
        canvas_obj.setFont("Helvetica", 7)
        canvas_obj.setFillColor(colors.grey)
        
        canvas_obj.setStrokeColor(colors.grey)
        canvas_obj.setLineWidth(0.5)
        canvas_obj.line(margem_esquerda, y_rodape + 4*mm, margem_direita, y_rodape + 4*mm)
        
        from datetime import datetime
        data_geracao = datetime.now().strftime("%d/%m/%Y às %H:%M")
        
        canvas_obj.drawString(margem_esquerda, y_rodape, f"Gerado em: {data_geracao}")
        canvas_obj.drawRightString(margem_direita, y_rodape, f"Página {doc.page}")
        
    except Exception as e:
        print(f"Erro ao criar cabeçalho paisagem: {e}")
        pass
    
    canvas_obj.restoreState()


def gerar_pdf_com_cabecalho(titulo_relatorio, conteudo, orientacao='retrato', subtitulo=None):
    """
    Gera um PDF completo com cabeçalho padronizado
    
    Args:
        titulo_relatorio: Título do relatório
        conteudo: Lista de elementos Platypus (Paragraphs, Tables, etc)
        orientacao: 'retrato' ou 'paisagem'
        subtitulo: Subtítulo opcional (ex: "Total: 50 professores")
    
    Returns:
        BytesIO com o PDF gerado
    """
    buffer = BytesIO()
    
    # Define tamanho da página
    pagesize = landscape(A4) if orientacao == 'paisagem' else A4
    
    # Define função de cabeçalho baseada na orientação
    def cabecalho(canvas_obj, doc):
        if orientacao == 'paisagem':
            criar_cabecalho_paisagem(canvas_obj, doc, titulo_relatorio, subtitulo)
        else:
            criar_cabecalho_padrao(canvas_obj, doc, titulo_relatorio, subtitulo)
    
    # Margens (deixar espaço para cabeçalho e rodapé)
    if orientacao == 'paisagem':
        margem_top = 35 * mm
        margem_bottom = 20 * mm
        margem_left = 20 * mm
        margem_right = 20 * mm
    else:
        margem_top = 45 * mm
        margem_bottom = 25 * mm
        margem_left = 25 * mm
        margem_right = 25 * mm
    
    # Cria documento
    doc = SimpleDocTemplate(
        buffer,
        pagesize=pagesize,
        topMargin=margem_top,
        bottomMargin=margem_bottom,
        leftMargin=margem_left,
        rightMargin=margem_right,
        title=titulo_relatorio
    )
    
    # Gera PDF
    doc.build(conteudo, onFirstPage=cabecalho, onLaterPages=cabecalho)
    
    buffer.seek(0)
    return buffer


# ============================================================================
# ESTILOS PADRÃO PARA RELATÓRIOS
# ============================================================================

def obter_estilos_padrao():
    """Retorna estilos padronizados para uso em relatórios"""
    styles = getSampleStyleSheet()
    
    # Estilo para título
    styles.add(ParagraphStyle(
        name='TituloRelatorio',
        parent=styles['Heading1'],
        fontSize=14,
        textColor=colors.HexColor('#0d6efd'),
        alignment=TA_CENTER,
        spaceAfter=12,
        fontName='Helvetica-Bold'
    ))
    
    # Estilo para subtítulo
    styles.add(ParagraphStyle(
        name='SubtituloRelatorio',
        parent=styles['Heading2'],
        fontSize=11,
        textColor=colors.HexColor('#0d6efd'),
        alignment=TA_LEFT,
        spaceAfter=8,
        fontName='Helvetica-Bold'
    ))
    
    # Estilo para texto normal
    styles.add(ParagraphStyle(
        name='TextoNormal',
        parent=styles['Normal'],
        fontSize=9,
        alignment=TA_LEFT,
        fontName='Helvetica'
    ))
    
    return styles


def obter_estilo_tabela_padrao():
    """Retorna estilo padronizado para tabelas"""
    return TableStyle([
        # Cabeçalho
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0d6efd')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
        
        # Corpo da tabela
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 1), (-1, -1), 'TOP'),
        
        # Bordas
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('LINEBELOW', (0, 0), (-1, 0), 1.5, colors.HexColor('#0d6efd')),
        
        # Zebra
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
        
        # Padding
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ])