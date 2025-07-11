from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
import os

def gerar_pdf(pedido, nome_arquivo):
    pasta = "data/pedidos_pdf"
    if not os.path.exists(pasta):
        os.makedirs(pasta)
    caminho_pdf = os.path.join(pasta, nome_arquivo)

    c = canvas.Canvas(caminho_pdf, pagesize=A4)
    largura, altura = A4

    # LOGO + TÍTULO
    logo_path = os.path.join("assets", "logo.png.png")
    logo_height = 2.3 * cm
    y_logo = altura - 3 * cm
    if os.path.exists(logo_path):
        c.drawImage(ImageReader(logo_path), x=2 * cm, y=y_logo, width=logo_height*1.6, height=logo_height, preserveAspectRatio=True)
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(largura / 2 + 2.5*cm, altura - 2.2 * cm, "Comprovante de Pedido - Marmita Fácil")

    y = altura - 4 * cm

    c.setFont("Helvetica-Bold", 13)
    c.drawString(2*cm, y, f"ID do Pedido: {pedido.get('ID Pedido', '')}")
    y -= 0.8*cm

    c.setFont("Helvetica", 12)
    c.drawString(2*cm, y, f"Data/Hora: {pedido.get('Data', '')}")
    y -= 0.7*cm
    c.drawString(2*cm, y, f"Nome: {pedido.get('Nome', '')}")
    y -= 0.7*cm
    c.drawString(2*cm, y, f"Matrícula: {pedido.get('Matrícula', '')}")
    y -= 0.7*cm
    c.drawString(2*cm, y, f"Unidade: {pedido.get('Unidade', '')}")
    y -= 0.7*cm
    c.drawString(2*cm, y, f"Destino da Entrega: {pedido.get('Destino da Entrega', '')}")
    y -= 0.7*cm
    c.drawString(2*cm, y, f"Líder Imediato: {pedido.get('Líder Imediato', '')}")
    y -= 0.7*cm

    c.setFont("Helvetica-Bold", 13)
    c.drawString(2*cm, y, f"ID Marmita: {pedido.get('ID Marmita', '')}")
    y -= 0.8*cm
    c.setFont("Helvetica-Bold", 13)
    c.drawString(2*cm, y, f"Marmita: {pedido.get('Marmita', '')}")
    y -= 0.7*cm
    c.setFont("Helvetica", 12)
    c.drawString(2*cm, y, f"Quantidade: {pedido.get('Quantidade', '')}")
    y -= 0.7*cm
    c.drawString(2*cm, y, f"Status: {pedido.get('Status', '')}")
    y -= 0.7*cm
    obs = pedido.get('Observações', '')
    if obs:
        c.setFont("Helvetica-Bold", 12)
        c.drawString(2*cm, y, "Observações:")
        y -= 0.5*cm
        c.setFont("Helvetica", 12)
        for linha in obs.split('\n'):
            c.drawString(2.8*cm, y, linha)
            y -= 0.5*cm

    y -= 0.7*cm
    c.setFont("Helvetica-Oblique", 10)
    c.drawString(2*cm, y, "Guarde este comprovante. Dúvidas? Procure o seu Gestor ou Administrativo.")

    c.save()
    return caminho_pdf






