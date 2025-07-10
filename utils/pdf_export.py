from fpdf import FPDF
import os
from datetime import datetime

def gerar_pdf(pedido: dict, nome_arquivo: str):
    pdf = FPDF()
    pdf.add_page()

    # LOGO
    logo_path = "assets/logo.png.png"
    if os.path.exists(logo_path):
        pdf.image(logo_path, x=10, y=8, w=25)

    pdf.set_y(35)

    # TÍTULO
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Comprovante de Pedido", ln=True, align="C")
    pdf.ln(10)

    # DADOS DO PEDIDO
    pdf.set_font("Arial", size=12)
    for chave, valor in pedido.items():
        pdf.set_text_color(0, 0, 0)
        pdf.cell(60, 10, f"{chave}:", ln=0)
        pdf.set_text_color(80, 80, 80)
        pdf.cell(100, 10, f"{valor}", ln=1)

    pasta = "data/pedidos_pdf"
    os.makedirs(pasta, exist_ok=True)

    caminho = os.path.join(pasta, nome_arquivo)
    pdf.output(caminho)
    return caminho
