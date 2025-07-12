from fpdf import FPDF
import os
from datetime import datetime

class FacturaPDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 14)
        self.cell(0, 10, "FACTURA MÉDICA", ln=True, align="C")
        self.ln(5)

    def footer(self):
        self.set_y(-30)
        self.set_font("Arial", "", 9)
        self.multi_cell(0, 5, "The Julls\n250 Executive Park Blvd, Suite 3400\nSan Francisco CA 94134, Estados Unidos\nTel: +593959599146 | Correo: jaime.mendoza@udla.edu.ec", align="C")

def generar_pdf(data_factura, lineas, carpeta_destino="facturas"):
    os.makedirs(carpeta_destino, exist_ok=True)

    # Extracción segura de datos
    nombre_factura = data_factura.get('name', 'SIN_NOMBRE')
    fecha = data_factura.get('invoice_date', 'SIN_FECHA')
    fecha_vencimiento = data_factura.get('invoice_date_due', 'SIN_FECHA')
    cliente = data_factura.get('partner_id', ['-', 'SIN_CLIENTE'])[1]
    subtotal = data_factura.get('amount_untaxed', 0.0)
    total = data_factura.get('amount_total', 0.0)
    pendiente = data_factura.get('amount_residual', 0.0)
    pagado = total - pendiente

    pdf = FacturaPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Datos generales
    pdf.cell(100, 10, f"Número: {nombre_factura}", ln=True)
    pdf.cell(100, 10, f"Fecha de emisión: {fecha}", ln=True)
    pdf.cell(100, 10, f"Fecha de vencimiento: {fecha_vencimiento}", ln=True)
    pdf.cell(100, 10, f"Cliente: {cliente}", ln=True)

    pdf.ln(5)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 10, "DETALLE DE PRODUCTOS", ln=True)

    # Encabezado de tabla
    pdf.set_font("Arial", "B", 10)
    pdf.cell(90, 8, "Descripción", 1)
    pdf.cell(30, 8, "Cantidad", 1)
    pdf.cell(35, 8, "Precio Unitario", 1)
    pdf.cell(35, 8, "Subtotal", 1)
    pdf.ln()

    # Filas de productos
    pdf.set_font("Arial", "", 10)
    for linea in lineas:
        descripcion = linea.get("name", "N/A")
        cantidad = linea.get("quantity", 0)
        precio = linea.get("price_unit", 0)
        subtotal_linea = cantidad * precio

        pdf.cell(90, 8, descripcion, 1)
        pdf.cell(30, 8, f"{cantidad:.2f}", 1, align='R')
        pdf.cell(35, 8, f"${precio:.2f}", 1, align='R')
        pdf.cell(35, 8, f"${subtotal_linea:.2f}", 1, align='R')
        pdf.ln()

    # Totales
    pdf.ln(5)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(155, 8, "Subtotal", 1)
    pdf.cell(35, 8, f"${subtotal:.2f}", 1, align='R')
    pdf.ln()
    pdf.cell(155, 8, "Total", 1)
    pdf.cell(35, 8, f"${total:.2f}", 1, align='R')
    pdf.ln()
    pdf.cell(155, 8, "Pagado", 1)
    pdf.cell(35, 8, f"${pagado:.2f}", 1, align='R')
    pdf.ln()
    pdf.cell(155, 8, "Pendiente", 1)
    pdf.cell(35, 8, f"${pendiente:.2f}", 1, align='R')

    # Guardar PDF
    nombre_archivo = f"factura_{nombre_factura.replace('/', '_')}.pdf"
    ruta_archivo = os.path.join(carpeta_destino, nombre_archivo)
    pdf.output(ruta_archivo)
    print(f"✅ PDF generado: {ruta_archivo}")
    return ruta_archivo
