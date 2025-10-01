import re
import json
import os
from datetime import datetime
from flask import Flask, request, jsonify

# --- Funciones originales para procesar el chat ---

def parsear_chat(ruta):
    mensajes = []
    patron_cabecera = re.compile(
        r'^\[(\d{1,2}/\d{1,2}/\d{2}), (\d{1,2}:\d{2}:\d{2}\s*[ap]\.\s*m\.)\]\s*(.*?):\s*(.*)$',
        re.UNICODE
    )

    with open(ruta, 'r', encoding='utf-8') as f:
        mensaje_actual = None

        for i, linea in enumerate(f):
            linea = linea.strip()
            if not linea:
                continue

            match = patron_cabecera.match(linea)
            if match:
                if mensaje_actual:
                    mensajes.append(mensaje_actual)

                fecha_str = match.group(1)
                hora_str = match.group(2)
                hora_str = re.sub(r'\s+', ' ', hora_str)
                hora_str = hora_str.replace('p. m.', 'PM').replace('a. m.', 'AM').replace('p.m.', 'PM').replace('a.m.', 'AM')

                autor = match.group(3)
                texto = match.group(4)

                try:
                    fecha_hora = datetime.strptime(f"{fecha_str} {hora_str}", "%d/%m/%y %I:%M:%S %p")
                except ValueError:
                    fecha_hora = f"{fecha_str} {hora_str}"

                mensaje_actual = {
                    "fecha_hora": fecha_hora.isoformat() if isinstance(fecha_hora, datetime) else fecha_hora,
                    "autor": autor,
                    "mensaje": texto
                }
            else:
                if mensaje_actual:
                    mensaje_actual["mensaje"] += "\n" + linea
                else:
                    if i < 10:
                        print(f"Línea no reconocida: {linea}")

        if mensaje_actual:
            mensajes.append(mensaje_actual)

    return mensajes

def detectar_codigos(mensaje):
    incidentes = re.findall(r'INC\d{9,}', mensaje, re.IGNORECASE)
    requerimientos = re.findall(r'REQ\d{9,}', mensaje, re.IGNORECASE)
    return incidentes, requerimientos

def extraer_subestacion(mensaje):
    claves = ['subestación', 'se', 'central', 'edificio técnico', 'cpd', 'sedes', 'torca', 'calera', 'fontibón', 'chicalá']
    mensaje_lower = mensaje.lower()
    for clave in claves:
        if clave in mensaje_lower:
            return clave
    return None

def organizar_datos(mensajes):
    organizados = []
    for m in mensajes:
        incidentes, requerimientos = detectar_codigos(m['mensaje'])
        subestacion = extraer_subestacion(m['mensaje'])
        organizados.append({
            "fecha_hora": m['fecha_hora'],
            "autor": m['autor'],
            "mensaje": m['mensaje'],
            "incidentes": incidentes,
            "requerimientos": requerimientos,
            "subestacion": subestacion
        })
    return organizados

def filtrar_por_autor(datos, autor_buscar):
    return [d for d in datos if d['autor'].lower() == autor_buscar.lower()]

def filtrar_por_fecha(datos, fecha_inicio=None, fecha_fin=None):
    resultados = []
    for d in datos:
        try:
            fecha = datetime.fromisoformat(d['fecha_hora'])
        except Exception:
            continue
        if fecha_inicio and fecha < fecha_inicio:
            continue
        if fecha_fin and fecha > fecha_fin:
            continue
        resultados.append(d)
    return resultados

def filtrar_por_subestacion(datos, subestacion_buscar):
    return [d for d in datos if d['subestacion'] and d['subestacion'].lower() == subestacion_buscar.lower()]

def filtrar_por_incidente(datos, codigo_incidente):
    return [d for d in datos if codigo_incidente in d['incidentes']]

def filtrar_por_requerimiento(datos, codigo_requerimiento):
    return [d for d in datos if codigo_requerimiento in d['requerimientos']]

def mostrar_mensajes(datos, max_mensajes=5):
    for i, d in enumerate(datos[:max_mensajes], 1):
        print(f"Mensaje {i}:")
        print(f"  Fecha y hora: {d['fecha_hora']}")
        print(f"  Autor: {d['autor']}")
        print(f"  Subestación: {d['subestacion']}")
        print(f"  Incidentes: {', '.join(d['incidentes']) if d['incidentes'] else 'Ninguno'}")
        print(f"  Requerimientos: {', '.join(d['requerimientos']) if d['requerimientos'] else 'Ninguno'}")
        print(f"  Mensaje:\n{d['mensaje']}\n{'-'*40}")

# --- Función para obtener ruta absoluta (útil para .exe) ---
import sys

def resource_path(relative_path):
    """Obtiene la ruta absoluta, funciona para desarrollo y para PyInstaller."""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# --- Configuración Flask para la API ---

from flask_cors import CORS  # Opcional, para permitir peticiones desde otros orígenes

app = Flask(__name__)
CORS(app)  # Habilita CORS para todas las rutas

# Carpeta para guardar archivos subidos
carpeta_subidas = resource_path('uploads')
os.makedirs(carpeta_subidas, exist_ok=True)

# Ruta para guardar JSON organizado
ruta_json = resource_path(os.path.join('data', 'datos_organizados.json'))
os.makedirs(os.path.dirname(ruta_json), exist_ok=True)

@app.route('/api/subir_chat', methods=['POST'])
def subir_chat():
    if 'archivo' not in request.files:
        return jsonify({"error": "No se encontró el archivo en la petición"}), 400

    archivo = request.files['archivo']

    if archivo.filename == '':
        return jsonify({"error": "No se seleccionó ningún archivo"}), 400

    if not archivo.filename.endswith('.txt'):
        return jsonify({"error": "Solo se permiten archivos .txt"}), 400

    ruta_guardado = os.path.join(carpeta_subidas, archivo.filename)
    archivo.save(ruta_guardado)

    # Procesar el archivo
    mensajes = parsear_chat(ruta_guardado)
    datos_organizados = organizar_datos(mensajes)

    # Guardar JSON actualizado
    with open(ruta_json, 'w', encoding='utf-8') as f:
        json.dump(datos_organizados, f, indent=4, ensure_ascii=False)

    return jsonify({
        "mensaje": f"Archivo {archivo.filename} subido y procesado correctamente",
        "total_mensajes": len(mensajes),
        "total_organizados": len(datos_organizados)
    }), 200

# --- Código para ejecutar el script y la API ---

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Procesar chat o iniciar API Flask")
    parser.add_argument('--api', action='store_true', help="Iniciar servidor API Flask")
    args = parser.parse_args()

    if args.api:
        # Ejecutar API Flask
        app.run(debug=True, port=5000)
    else:
        # Ejecutar procesamiento normal (como antes)
        ruta_txt = resource_path(os.path.join('data', 'chat_networking.txt'))
        mensajes = parsear_chat(ruta_txt)
        print(f"Se procesaron {len(mensajes)} mensajes.")

        datos_organizados = organizar_datos(mensajes)

        with open(ruta_json, 'w', encoding='utf-8') as f:
            json.dump(datos_organizados, f, indent=4, ensure_ascii=False)

        print(f"Datos organizados guardados en {ruta_json}")

        # Ejemplo: filtrar por autor
        autor = "Yesid Cortes"
        mensajes_autor = filtrar_por_autor(datos_organizados, autor)
        print(f"\nMensajes del autor '{autor}': {len(mensajes_autor)} encontrados.")
        mostrar_mensajes(mensajes_autor, max_mensajes=3)

        # Ejemplo: filtrar por subestación
        subestacion = "central"
        mensajes_subestacion = filtrar_por_subestacion(datos_organizados, subestacion)
        print(f"\nMensajes relacionados con la subestación '{subestacion}': {len(mensajes_subestacion)} encontrados.")
        mostrar_mensajes(mensajes_subestacion, max_mensajes=3)
