#actualizacion con analisis de inventario funcionando

import AVMSpeechMath as sm
import AVMYT as yt
import speech_recognition as sr
import pyttsx3
import wikipedia
import pyjokes
import mysql.connector  
import os
import geopandas as gpd
import matplotlib.pyplot as plt
import tempfile 
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime
from time import time
from openpyxl import Workbook
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
start_time = time()
engine = pyttsx3.init()
# Datos del Asistente Virtual
name = 'ale'
attemts = 0

# Aqui asigno el color de las letras del Asistente Virtual
red_color = "\033[1;31;40m"

# Obtengo Voces de Windows Instalados
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[3].id)

# Aqui configuro la voz para hablar en velocidad standar
engine.setProperty('rate', 178)
# Aqui es para el volumen de la voz
engine.setProperty('volume', 0.7)

def speak(text):
    engine.say(text)
    engine.runAndWait()

# INI Obtener microfono
def get_audio():
    r = sr.Recognizer()
    status = False

    with sr.Microphone() as source:
        print(f"{red_color}({attemts}) Dime...{red_color}")
        r.adjust_for_ambient_noise(source, duration=1)
        audio = r.listen(source)
        rec = ""

        try:
            rec = r.recognize_google(audio, language='es-ES').lower()
            
            if name in rec:
                rec = rec.replace(f"{name} ", "").replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")
                status = True
            else:
                print(f"Vuelve a intentarlo, no reconozco: {rec}")
        except Exception as e:
            print(f"Error: {str(e)}")
    return {'text': rec, 'status': status}
# FIN Obtener microfono

# INI Conexión a la base de datos
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="ale_asistente"
)
cursor = db.cursor()
# FIN Conexión a la base de datos

# INI RF019 Metodo para obtener el stock del producto 
def obtener_datos_base_datos():
    consulta = "SELECT nombre, stock FROM producto"
    cursor.execute(consulta)
    resultados = cursor.fetchall()
    return resultados
# FIN RF019 Metodo para obtener el stock del producto 

# INI RF019 Metodo para obtener el stock por producto ingresado
def consultar_stock(producto):
    consulta = "SELECT stock FROM producto WHERE nombre = %s"
    cursor.execute(consulta, (producto,))
    resultado = cursor.fetchone()
    return resultado
# FIN RF019  Metodo para obtener el stock por producto ingresado

# INI RF018 Metodo para obtener el cliente por venta
def consultar_venta_cliente(cliente_venta):
    consulta = "SELECT c.nombre AS nombre, COUNT(p.id) AS total_compras, SUM(p.total) AS total_gastado FROM cliente c LEFT JOIN pedido p ON c.id = p.cliente_id where c.nombre = %s GROUP BY c.id" 
    cursor.execute(consulta, (cliente_venta,))
    resultado = cursor.fetchone()
    return resultado
# FIN RF018 Metodo para obtener el cliente por venta

# INI RF017 Metodo para obtener rentabilidad
def consultar_rentabilidad_producto(nombre_producto):
    consulta = "SELECT nombre as nombre, SUM(precio_adquirido * stock) AS costo_total, SUM(precio * stock) AS ingreso_total, (SUM(precio * stock) - SUM(precio_adquirido * stock)) AS rentabilidad FROM producto WHERE nombre = %s GROUP BY id, nombre"
    cursor.execute(consulta, (nombre_producto,))
    resultado = cursor.fetchone()
    return resultado
# FIN RF017 Metodo para obtener rentabilidad

# INI RF019 Metodo para obtener excel  
def generar_excel(data):
    workbook = Workbook()
    sheet = workbook.active
    sheet.append(["Producto", "Stock"])  # Aqui creo los encabezados del Excel

    for row in data:
        sheet.append(row)

    excel_file = "reporte_productos.xlsx"
    workbook.save(excel_file)
    return excel_file
# FIN RF019 Metodo para obtener excel  

# INI RF018 Metodo para datos de cliente y su comportamiento
def consultar_venta_cliente(cliente_venta):
    consulta = "SELECT c.nombre AS nombre, COUNT(p.id) AS total_compras, SUM(p.total) AS total_gastado FROM cliente c LEFT JOIN pedido p ON c.id = p.cliente_id where c.nombre = %s GROUP BY c.id" 
    cursor.execute(consulta, (cliente_venta,))
    resultado = cursor.fetchone()
    return resultado
# FIN RF018 Metodo para datos de cliente y su comportamiento

# INI RF015 Metodo para Consultar el Producto Más Vendido y la Promoción
def consultar_producto_mas_vendido():
    consulta_producto_mas_vendido = "SELECT dp.producto_id, p.nombre AS producto_nombre, SUM(dp.cantidad) AS total_vendido, dp.promocion FROM detallepedido dp JOIN producto p ON dp.producto_id = p.id GROUP BY dp.producto_id, dp.promocion ORDER BY total_vendido DESC LIMIT 1;"
    cursor.execute(consulta_producto_mas_vendido)
    resultado = cursor.fetchone()
    return resultado
# FIN RF015 Metodo para Consultar el Producto Más Vendido y la Promoción

# INI RF016 Metodo para Consultar la Satisfaccion de un Cliente Especifico
def consultar_satisfaccion_cliente(cliente):
    consulta_satisfaccion_cliente = "SELECT nombre_cliente, CASE WHEN promedio_satisfaccion >= 4.5 THEN 'Muy satisfecho' WHEN promedio_satisfaccion >= 3.5 THEN 'Satisfecho' WHEN promedio_satisfaccion >= 2.5 THEN 'Neutral'  WHEN promedio_satisfaccion >= 1.5 THEN 'Insatisfecho' ELSE 'Muy insatisfecho' END AS promedio_satisfaccion_texto FROM ( SELECT cliente.nombre AS nombre_cliente, AVG(CASE WHEN pedido.satisfaccion = 'Muy satisfecho' THEN 5 WHEN pedido.satisfaccion = 'Satisfecho' THEN 4 WHEN pedido.satisfaccion = 'Neutral' THEN 3 WHEN pedido.satisfaccion = 'Insatisfecho' THEN 2 WHEN pedido.satisfaccion = 'Muy insatisfecho' THEN 1 ELSE 0 END) AS promedio_satisfaccion FROM pedido JOIN  cliente ON pedido.cliente_id = cliente.id WHERE  cliente.nombre = %s GROUP BY  cliente.nombre) AS subconsulta"
    cursor.execute(consulta_satisfaccion_cliente,(cliente,))
    resultado = cursor.fetchone()
    return resultado
# FIN RF016 Metodo para Consultar la Satisfaccion de un Cliente Especifico

# INI RF014 Metodo para Consultar Datos de Ventas e Ingresos
def consultar_ventas_ingresos():
    consulta_ventas = "SELECT SUM(total) AS total_vendido, SUM(monto_total) AS total_facturado FROM pedido JOIN factura ON pedido.id = factura.pedido_id;"
    cursor.execute(consulta_ventas)
    resultado = cursor.fetchone()
    return resultado
# FIN RF014 Metodo para Consultar Datos de Ventas e Ingresos


def obtener_ciudad():
    cursor.execute("SELECT ciudad, COUNT(*) FROM cliente GROUP BY ciudad")
    return cursor.fetchall()

def obtener_coordenadas(ciudad):
    geolocator = Nominatim(user_agent="myGeocoder")
    try:
        location = geolocator.geocode(ciudad)
        if location:
            return (location.latitude, location.longitude)
        else:
            print(f"No se encontraron coordenadas para {ciudad}")
            return (0, 0)
    except (GeocoderTimedOut, GeocoderServiceError):
        print(f"Error al buscar coordenadas para {ciudad}")
        return (0, 0)

def generar_mapa(datos):
    ciudades = [fila[0] for fila in datos]
    conteos = [fila[1] for fila in datos]

    coordenadas = {ciudad: obtener_coordenadas(ciudad) for ciudad in ciudades}

    world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
    peru = world[world['name'] == 'Peru']

    puntos_ciudades = gpd.GeoDataFrame({
        'ciudad': ciudades,
        'conteo': conteos,
        'geometry': [gpd.points_from_xy([coordenadas[ciudad][1]], [coordenadas[ciudad][0]])[0] for ciudad in ciudades]
    })

    fig, ax = plt.subplots(1, 1, figsize=(10, 6))
    peru.plot(ax=ax, color='lightgrey')
    puntos_ciudades.plot(ax=ax, color='red', markersize=puntos_ciudades['conteo'] * 10)

    for x, y, label, conteo in zip(puntos_ciudades.geometry.x, puntos_ciudades.geometry.y, puntos_ciudades['ciudad'], puntos_ciudades['conteo']):
        ax.text(x, y, f"{label}: {conteo}", fontsize=12, ha='right', color='black')

    ax.set_title('Distribución de Clientes por Ciudad')
    ax.set_axis_off()

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    plt.savefig(temp_file.name)
    temp_file.close()

    return temp_file.name

def generar_pdf(datos, mapa_path):
    pdf_path = "reporte_demografico_peru.pdf"
    c = canvas.Canvas(pdf_path, pagesize=letter)
    width, height = letter

    c.drawString(100, 750, "Reporte Demográfico")
    c.drawString(100, 730, "Distribución de Clientes por Ciudad")

    y = 700
    for ciudad, conteo in datos:
        c.drawString(100, y, f"{ciudad}: {conteo}")
        y -= 20

    c.drawImage(mapa_path, 100, y - 300, width=400, height=300)
    c.showPage()
    c.save()

    print("PDF generado exitosamente.")
    return pdf_path

#INI RF06 Generar informe de Analisis de inventario y pedidos

def consultar_inventario():
    cursor.execute("SELECT nombre, stock, precio FROM producto")
    return cursor.fetchall()

def consultar_pedidos():
    cursor.execute("SELECT p.id, c.nombre, p.total FROM pedido p JOIN cliente c ON p.cliente_id = c.id")
    return cursor.fetchall()

def generar_pdf_analisis(datos_inventario, datos_pedidos):
    pdf_path = "analisis_inventario_pedidos.pdf"
    c = canvas.Canvas(pdf_path, pagesize=letter)
    width, height = letter

    c.drawString(200, 750, "Análisis de Inventario y Pedidos")
    c.drawString(100, 730, "Inventario Actual")

    y = 700
    for nombre, stock, precio in datos_inventario:
        c.drawString(100, y, f"Producto: {nombre}, Stock: {stock}, Precio de Venta: {precio}")
        y -= 20

    y -= 20
    c.drawString(100, y, "Pedidos Realizados")

    y -= 20
    for pedido_id, cliente, total in datos_pedidos:
        c.drawString(100, y, f"Pedido ID: {pedido_id},  Cliente: {cliente}, Total: {total}")
        y -= 20

    c.showPage()
    c.save()

    print("PDF de análisis de inventario y pedidos generado exitosamente.")
    return pdf_path

#FIN RF06 Generar informe de Analisis de inventario y pedidos


#RF024
def generar_reporte_clientes_ciudad():
    consulta = "SELECT ciudad, COUNT(*) FROM cliente GROUP BY ciudad"
    cursor.execute(consulta)
    resultados = cursor.fetchall()

    pdf_path = "reporte_clientes_por_ciudad.pdf"
    c = canvas.Canvas(pdf_path, pagesize=letter)
    width, height = letter

    c.drawString(100, 750, "Reporte de Clientes por Ciudad")
    y = 730
    for ciudad, total_clientes in resultados:
        c.drawString(100, y, f"{ciudad}: {total_clientes}")
        y -= 20

    c.showPage()
    c.save()

    print("PDF generado exitosamente.")
    return pdf_path
#FIN RF024

# INI RF023 Segmentar a los clientes segun su comportamiento de compra
def obtener_clientes_por_categoria():
    consulta = """
SELECT 
    cat.nombre AS Categoria, 
    COUNT(DISTINCT p.cliente_id) AS Clientes
FROM 
    categoria cat
LEFT JOIN 
    producto prod ON cat.id = prod.categoria_id
LEFT JOIN 
    detallepedido dp ON prod.id = dp.producto_id
LEFT JOIN 
    pedido p ON dp.pedido_id = p.id
GROUP BY 
    cat.nombre;
    """
    cursor.execute(consulta)
    return cursor.fetchall()

# Función para generar el archivo Excel
def generar_excel_clientes_categoria(datos):
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Clientes por Categoría"
    sheet.append(["Categoría", "Cliente"])  # Encabezados del Excel

    for row in datos:
        sheet.append(row)

    excel_file = "clientes_por_categoria.xlsx"
    workbook.save(excel_file)
    print("Excel generado exitosamente.")
    return excel_file
# FIN RF023 Segmentar a los clientes segun su comportamiento de compra

#INI Cantidad de productos comprados por cliente
def consultar_prueba(cliente):
    consulta = "SELECT c.nombre, SUM(dp.cantidad) AS total_productos_vendidos FROM cliente c INNER JOIN pedido p ON c.id = p.cliente_id INNER JOIN detallepedido dp ON p.id = dp.pedido_id WHERE c.nombre = %s GROUP BY c.nombre "
    cursor.execute(consulta, (cliente,))
    resultado = cursor.fetchone()
    return resultado

#FIN Cantidad de productos comprados por cliente

# INI RF04 Recomendar producto a cliente
def consultar_recomendaciones(cliente_id):
    consulta_producto_mas_vendido = """SELECT DISTINCT p2.nombre FROM detallepedido dp JOIN producto p1 ON dp.producto_id = p1.id JOIN producto p2 ON p1.categoria_id = p2.categoria_id JOIN pedido pe ON dp.pedido_id = pe.id JOIN cliente c ON pe.cliente_id = c.id WHERE c.nombre = %s AND p1.id != p2.id; """
    cursor.execute(consulta_producto_mas_vendido, (cliente_id,))
    resultado = cursor.fetchall()
    return resultado
# FIN RF04 Recomendar producto a cliente

while True:
    rec_json = get_audio()

    rec = rec_json['text']
    status = rec_json['status']

    if status:
        if 'estas ahi' in rec:
            speak('Por supuesto')

        elif 'que' in rec:
            if 'hora' in rec:
                hora = datetime.now().strftime('%I:%M %p')
                speak(f"Son las {hora}")

        elif 'busca' in rec:
            order = rec.replace('busca', '')
            wikipedia.set_lang("es")
            info = wikipedia.summary(order, 1)
            speak(info)

        elif 'chiste' in rec:
            chiste = pyjokes.get_joke("es")
            speak(chiste)

        elif 'cuanto es' in rec:
            speak(sm.getResult(rec))
#RF019 Datos de inventario
        elif 'dame el stock de' in rec:
            producto = rec.replace('dame el stock de', '').strip()
            resultado = consultar_stock(producto)
            if resultado:
                speak(f"El stock de {producto} es {resultado[0]}")
            else:
                speak(f"No se encontró el producto {producto} en la base de datos.")
#RF019 Datos de gestion de Stock      
        elif 'genera reporte de stock' in rec:
            def generar_reporte():
                data = obtener_datos_base_datos()
                excel_file = generar_excel(data)
                if excel_file:
                    os.startfile(excel_file)
                    speak("Generando Reporte en Excel...")
                else:
                    speak("Error al generar el archivo Excel.")
            generar_reporte()
#RF018 Datos de cliente y su comportamiento
        elif 'cuanto compro' in rec:
            cliente = rec.replace('cuanto compro', '').strip()
            resultado = consultar_venta_cliente(cliente)
            if resultado:
                nombre = resultado[0]
                total_compras = resultado[1]
                total_gastado = resultado[2]
                speak(f"El cliente {nombre} ha realizado {total_compras} compras y ha gastado un total de {total_gastado} soles.")
            else:
                speak(f"No se encontraron datos para el cliente {cliente}.")
#RF017 Datos de costo y su rentabilidad falta
        elif 'rentabilidad de producto' in rec:
            nombre_producto = rec.replace('rentabilidad de producto', '').strip()
            resultado = consultar_rentabilidad_producto(nombre_producto)
            if resultado:
                    nombre = resultado[0]
                    costo_total = resultado[1]
                    ingreso_total = resultado[2]
                    rentabilidad = resultado[3]
                    speak(f"Para el producto {nombre}, el costo total es {costo_total}, el ingreso total es {ingreso_total} y la rentabilidad es {rentabilidad}.")
            else:
                speak("No se encontraron resultados.")
#RF015 Datos de Marketing y Promociones
        elif 'producto mas vendido' in rec: 
            producto_mas_vendido = consultar_producto_mas_vendido()
            if producto_mas_vendido:
                producto_id = producto_mas_vendido[0]
                nombre_producto = producto_mas_vendido[1]
                total_vendido = producto_mas_vendido[2]
                promocion = producto_mas_vendido[3]
                speak(f"El producto más vendido es {nombre_producto} con {total_vendido} unidades vendidas durante la promoción {promocion}.")
            else:
                speak("No se encontraron resultados.")
#RF016 Datos de Satisfaccion de Clientes falta 
        elif 'satisfaccion de cliente' in rec:  
            cliente = rec.replace('satisfaccion de cliente', '').strip()
            resultado = consultar_satisfaccion_cliente(cliente)
            if resultado:
                cliente = resultado[0]
                promedio_satisfaccion = resultado[1]
                speak(f"La satisfacción de {cliente} en promedio es {promedio_satisfaccion}.")
            else:
                speak(f"No se encontraron resultados para {cliente}.")
#RF014 Datos de Satisfaccion de Clientes falta
        elif 'ventas e ingresos' in rec: 
            ventas_ingresos = consultar_ventas_ingresos()
            if ventas_ingresos:
                total_vendido = ventas_ingresos[0]
                total_facturado = ventas_ingresos[1]
                speak(f"El total vendido es de {total_vendido} y el total facturado es de {total_facturado}.")
            else:
                speak("No se encontraron resultados.")

        elif 'genera pdf' in rec:
            datos = obtener_ciudad()
            mapa_path = generar_mapa(datos)
            pdf_path = generar_pdf(datos, mapa_path)
            speak("Generando Reporte...")
            os.startfile(pdf_path)  # Abre el archivo PDF
            os.remove(mapa_path)
#INI RF06 Generar informe de Analisis de inventario y pedidos
        elif 'analisis de inventario y pedidos' in rec:
            speak("Generando análisis de inventario y pedidos, un momento...")
            datos_inventario = consultar_inventario()
            datos_pedidos = consultar_pedidos()
            pdf_path = generar_pdf_analisis(datos_inventario, datos_pedidos)
            if pdf_path:
                os.startfile(pdf_path)
                speak("Análisis de inventario y pedidos generado exitosamente.")
            else:
                speak("Error al generar el análisis de inventario y pedidos.")

#FIN RF06 Generar informe de Analisis de inventario y pedidos

# INI Generar reporte de clientes por ciudad
        elif 'reporte de clientes por ciudad' in rec:
            pdf_path = generar_reporte_clientes_ciudad()
            if pdf_path:
                os.startfile(pdf_path)
                speak("Reporte de clientes por ciudad generado exitosamente.")
            else:
                speak("Error al generar el reporte de clientes por ciudad.")
# FIN Generar reporte de clientes por ciudad

# INI RF023 Segmentar a los clientes segun su comportamiento de compra
        elif 'reporte de clientes' in rec:
            datos = obtener_clientes_por_categoria()
            excel_file = generar_excel_clientes_categoria(datos)
            if excel_file:
                os.startfile(excel_file)
                speak("Reporte de clientes por categoría generado exitosamente.")
            else:
                speak("Error al generar el reporte de clientes por categoría.")
# FIN RF023 Segmentar a los clientes segun su comportamiento de compra

#INI Cantidad de productos comprados por cliente
        elif 'productos comprados por' in rec:
            cliente = rec.replace('productos comprados por', '').strip()
            resultado = consultar_prueba(cliente)
            if resultado:
                speak(f"La cantidad de productos comprados por {cliente} es {resultado[1]}")
            else:
                speak(f"No se encontró productos para el cliente {cliente} ")

#FIN Cantidad de productos comprados por cliente

#RF04 Recomendar producto a cliente
        elif 'recomendar producto para' in rec:
            cliente_id = rec.replace('recomendar producto para', '').strip()
            resultado = consultar_recomendaciones(cliente_id)
            if resultado:
                speak(f"la Opcion de producto para {cliente_id} es {resultado[0]}")
            else:
                speak(f"No se encontró productos para recomendar {cliente_id} ")
                
#FIN RF04 Recomendar producto a cliente

        elif 'descansa' in rec:
            speak("Gracias, Saliendo...")
            break    


        else:
                    print(f"Vuelve a intentarlo, no reconozco: {rec}")
        
        attemts = 0
    else:
        attemts += 1

print(f"{red_color} ASISTENTE VIRTUAL CULMINADO CON UNA DURACIÓN DE: { int(time() - start_time) } SEGUNDOS {red_color}")
