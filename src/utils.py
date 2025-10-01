import json
import datetime
import os

def guardar_datos(datos, ruta_datos):
    try:
        with open(ruta_datos, 'w', encoding='utf-8') as f:
            json.dump(datos, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Error guardando datos: {e}")
        return False

def cargar_datos(ruta_datos):
    if os.path.exists(ruta_datos):
        try:
            with open(ruta_datos, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error cargando datos: {e}")
    return None

def registrar_acceso(usuario, ruta_log):
    try:
        ahora = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(ruta_log, 'a', encoding='utf-8') as f:
            f.write(f'{ahora} - Usuario: {usuario}\n')
    except Exception as e:
        print(f"Error registrando acceso: {e}")

def detectar_subestacion(texto, subestaciones):
    for sub in subestaciones:
        if sub.lower() in texto.lower():
            return sub
    return 'No especificado'

def detectar_categoria(texto, incidentes, requerimientos):
    texto_lower = texto.lower()
    if any(palabra in texto_lower for palabra in incidentes):
        return 'Incidente'
    if any(palabra in texto_lower for palabra in requerimientos):
        return 'Requerimiento'
    return 'Otro'
