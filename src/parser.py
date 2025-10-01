import re
from src.config import SUBESTACIONES, INCIDENTES, REQUERIMIENTOS
from src.utils import detectar_subestacion, detectar_categoria

def parsear_chat(ruta_archivo):
    patron = re.compile(r'^(\d{1,2}/\d{1,2}/\d{2,4}), (\d{1,2}:\d{2}) - (.*?): (.*)$')
    datos = []
    try:
        with open(ruta_archivo, 'r', encoding='utf-8') as f:
            for linea in f:
                linea = linea.strip()
                match = patron.match(linea)
                if match:
                    fecha, hora, autor, mensaje = match.groups()
                    subestacion = detectar_subestacion(mensaje, SUBESTACIONES)
                    categoria = detectar_categoria(mensaje, INCIDENTES, REQUERIMIENTOS)
                    datos.append({
                        'fecha': fecha,
                        'hora': hora,
                        'autor': autor,
                        'mensaje': mensaje,
                        'subestacion': subestacion,
                        'categoria': categoria
                    })
    except FileNotFoundError:
        print(f"Archivo no encontrado: {ruta_archivo}")
    return datos
