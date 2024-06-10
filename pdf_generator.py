from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

def generate_pdf(data):
    # Nombre del archivo PDF
    pdf_file = "stock_report.pdf"
    
    # Crear un lienzo para el PDF
    c = canvas.Canvas(pdf_file, pagesize=letter)
    
    # Título del PDF
    c.setFont("Helvetica", 16)
    c.drawString(100, 750, "Stock")
    
    # Crear tabla
    width, height = letter
    table_data = [['Producto', 'Stock']]
    table_data.extend(data)  # Agregar datos de la base de datos a la tabla
    
    c.setFont("Helvetica", 12)
    table_y = 730
    for row in table_data:
        table_x = 100
        for cell in row:
            c.drawString(table_x, table_y, str(cell))
            table_x += 200
        table_y -= 20
    
    # Guardar el PDF
    c.save()
    
    return pdf_file  # Devolver el nombre del archivo PDF
