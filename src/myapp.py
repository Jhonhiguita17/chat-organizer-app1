import sys
import os
import socket
import requests  # NUEVO: Para sincronización con Render
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory, abort, jsonify  # NUEVO: jsonify para APIs
import json
from datetime import datetime
from math import ceil
import unicodedata
import shutil
from pathlib import Path

# Añadir carpeta raíz del proyecto al path para importar main.py
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import main

def get_resource_path():
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    else:
        return os.path.abspath(os.path.dirname(__file__))

def get_data_path():
    if getattr(sys, 'frozen', False):
        return os.path.join(os.path.dirname(sys.executable), 'data')
    else:
        return os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))

def get_descargas_path():
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, 'descargas')
    else:
        return os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'descargas'))

resource_path = get_resource_path()  # carpeta src
data_path = get_data_path()
ruta_descargas = get_descargas_path()

static_folder = os.path.join(resource_path, "static")
template_folder = os.path.join(resource_path, "templates")

ruta_data = data_path

ruta_json = os.path.join(ruta_data, "datos_organizados.json")
ruta_log_usuarios = os.path.join(ruta_data, "log_usuarios.txt")
ruta_chat_original = os.path.join(ruta_data, "chat_networking.txt")

os.makedirs(ruta_data, exist_ok=True)

app = Flask(
    __name__,
    static_folder=static_folder,
    template_folder=template_folder
)

app.secret_key = 'cambia_esto_por_una_clave_muy_segura'  # Cambia por una clave segura

# NUEVO: Configuraciones para sincronización con Render
URL_RENDER = os.environ.get('URL_RENDER', 'https://tu-app.onrender.com')  # Cambia por tu URL real de Render
SYNC_TOKEN = os.environ.get('SYNC_TOKEN', 'mi_token_secreto_2024')  # Token secreto para auth (cámbialo y configúralo en env vars)

def cargar_datos_json_local():  # RENOMBRADO: Tu función original, ahora como fallback local
    if not os.path.isfile(ruta_json):
        contenido_inicial = [
            {
                "autor": "Juan Perez",
                "mensaje": "Falla detectada en la subestación Central Norte",
                "subestacion": "Central Norte",
                "fecha_hora": "2024-06-01T10:00:00",
                "incidentes": ["INC0001"],
                "requerimientos": ["REQ0001"]
            },
            {
                "autor": "Ana Gomez",
                "mensaje": "Revisión realizada en CE Sur",
                "subestacion": "CE Sur",  # CORREGIDO: Cambiado de "ce" a "subestacion" para consistencia
                "fecha_hora": "2024-06-02T11:00:00",
                "incidentes": [],
                "requerimientos": []
            }
        ]
        with open(ruta_json, 'w', encoding='utf-8') as f:
            json.dump(contenido_inicial, f, indent=4, ensure_ascii=False)
    try:
        with open(ruta_json, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error cargando JSON local: {e}")
        return []

# NUEVO: Cargar datos iniciales locales (fallback)
datos = cargar_datos_json_local()

# NUEVO: Función para descargar JSON desde Render (sincronización)
def fetch_datos_from_render():
    """Descarga JSON desde Render. Retorna lista o None si falla."""
    try:
        response = requests.get(f"{URL_RENDER}/api/datos_json", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"JSON sincronizado desde Render: {len(data)} mensajes")
            return data
        else:
            print(f"Error fetch de Render: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error conectando a Render: {e} (usando datos locales)")
        return None

# NUEVO: Función para enviar JSON actualizado a Render
def push_datos_to_render(datos):
    """Sube JSON actualizado a Render. Retorna True si éxito."""
    try:
        headers = {'Authorization': f'Bearer {SYNC_TOKEN}'}  # Token en header para auth
        response = requests.post(f"{URL_RENDER}/api/actualizar_json", json=datos, headers=headers, timeout=10)
        if response.status_code == 200:
            print(f"JSON sincronizado a Render: {len(datos)} mensajes")
            return True
        else:
            print(f"Error push a Render: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"Error enviando a Render: {e}")
        return False

def es_tecnico(mensaje):
    palabras_tecnicas = [
        'subestación', 'falla', 'incidente', 'requerimiento', 'fibra óptica',
        'error', 'actividad', 'avances', 'supera', 'reemplaza', 'torre', 'fuente',
        'sw', 'quitar', 'retira', 'reemplazo', 'fallas', 'problema'
    ]
    texto = (mensaje.get('mensaje') or '').lower()
    return any(palabra in texto for palabra in palabras_tecnicas)

def parse_fecha(fecha_str):
    try:
        return datetime.strptime(fecha_str, '%Y-%m-%dT%H:%M:%S')
    except Exception:
        return None

def normalizar_texto(texto):
    if not texto or not isinstance(texto, str):
        return ''
    texto = texto.strip().lower()
    texto = unicodedata.normalize('NFD', texto)
    texto = ''.join(c for c in texto if unicodedata.category(c) != 'Mn')
    return texto

def get_carpeta_descargas_usuario():
    home = Path.home()
    descargas = home / "Downloads"
    if descargas.exists():
        return str(descargas)
    documentos = home / "Documents"
    if documentos.exists():
        return str(documentos)
    return str(home)

def get_carpeta_miapp_descargas():
    carpeta = Path(get_carpeta_descargas_usuario()) / "MiAppDescargas"
    carpeta.mkdir(parents=True, exist_ok=True)
    return str(carpeta)

def copiar_archivo_a_carpeta_fija(nombre_archivo):
    ruta_origen = os.path.join(ruta_descargas, nombre_archivo)
    if not os.path.isfile(ruta_origen):
        raise FileNotFoundError(f"Archivo no encontrado: {ruta_origen}")

    carpeta_destino = get_carpeta_miapp_descargas()
    ruta_destino = os.path.join(carpeta_destino, nombre_archivo)

    shutil.copy2(ruta_origen, ruta_destino)
    return ruta_destino

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form.get('usuario', '').strip()
        password = request.form.get('password', '').strip()
        
        if not usuario:
            error = "Por favor ingrese un usuario válido."
            return render_template('login.html', error=error)
        
        if password == 'T3l3m4t1c4' and password.isalnum():
            session['usuario'] = usuario
            try:
                with open(ruta_log_usuarios, 'a', encoding='utf-8') as f_log:
                    ahora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    f_log.write(f"{ahora} - {usuario}\n")
            except Exception as e:
                print(f"Error guardando log usuario: {e}")
            return redirect(url_for('index'))
        else:
            error = "Usuario o contraseña incorrectos. La contraseña debe ser alfanumérica."
            return render_template('login.html', error=error)
    
    return render_template('login.html')

@app.route('/')
def index():
    # NUEVO: Cargar datos dinámicamente desde Render (sincronización)
    datos_actualizados = fetch_datos_from_render()
    if datos_actualizados:
        datos = datos_actualizados
        # Guardar local para uso offline
        try:
            with open(ruta_json, 'w', encoding='utf-8') as f:
                json.dump(datos, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error guardando JSON local después de sync: {e}")
    else:
        datos = cargar_datos_json_local()  # Fallback local si no hay internet

    usuario = session.get('usuario')
    if not usuario:
        return redirect(url_for('login'))

    autor = normalizar_texto(request.args.get('autor', ''))
    subestacion = normalizar_texto(request.args.get('subestacion', ''))
    fecha_desde = (request.args.get('fecha_desde') or '').strip()
    fecha_hasta = (request.args.get('fecha_hasta') or '').strip()
    incidente = normalizar_texto(request.args.get('incidente', ''))
    requerimiento = normalizar_texto(request.args.get('requerimiento', ''))
    pagina = request.args.get('pagina', 1, type=int)
    mensajes_por_pagina = 10

    mensajes_tecnicos = [m for m in datos if es_tecnico(m)]

    filtros_activos = any([autor, subestacion, fecha_desde, fecha_hasta, incidente, requerimiento])
    mensajes_filtrados = []

    for m in mensajes_tecnicos:
        texto = normalizar_texto(m.get('mensaje'))
        if 'imagen omitida' in texto:
            continue

        autor_m = normalizar_texto(m.get('autor'))
        if autor and autor not in autor_m:
            continue

        subestacion_m = normalizar_texto(m.get('subestacion') or '')
        if subestacion and subestacion not in subestacion_m and subestacion not in texto:
            continue

        incidentes_m = [normalizar_texto(i) for i in m.get('incidentes', []) if isinstance(i, str)]
        if incidente and incidente not in incidentes_m and incidente not in texto:
            continue

        requerimientos_m = [normalizar_texto(r) for r in m.get('requerimientos', []) if isinstance(r, str)]  # CORREGIDO: Agregado default []
        if requerimiento and requerimiento not in requerimientos_m and requerimiento not in texto:
            continue

        fecha_msg = parse_fecha(m.get('fecha_hora') or '')
        if fecha_desde:
            try:
                fecha_desde_dt = datetime.strptime(fecha_desde, '%Y-%m-%d')
            except Exception:
                fecha_desde_dt = None
            if not fecha_msg or (fecha_desde_dt and fecha_msg < fecha_desde_dt):
                continue
        if fecha_hasta:
            try:
                fecha_hasta_dt = datetime.strptime(fecha_hasta, '%Y-%m-%d')
            except Exception:
                fecha_hasta_dt = None
            if not fecha_msg or (fecha_hasta_dt and fecha_msg > fecha_hasta_dt):
                continue

        mensajes_filtrados.append(m)

    mensajes_filtrados.sort(key=lambda x: x.get('fecha_hora') or '', reverse=True)

    if not filtros_activos:
        mensajes_filtrados = mensajes_filtrados[:mensajes_por_pagina]
        total_paginas = 1
    else:
        total_paginas = ceil(len(mensajes_filtrados) / mensajes_por_pagina)
        start = (pagina - 1) * mensajes_por_pagina
        end = start + mensajes_por_pagina
        mensajes_filtrados = mensajes_filtrados[start:end]

    carpeta_descargas = get_carpeta_miapp_descargas()

    return render_template(
        'index.html',
        mensajes=mensajes_filtrados,
        usuario=usuario,
        autor=autor,
        subestacion=subestacion,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        incidente=incidente,
        requerimiento=requerimiento,
        pagina=pagina,
        total_paginas=total_paginas,
        carpeta_descargas=carpeta_descargas,
        url_render=URL_RENDER  # NUEVO: Para usar en HTML (ej: links o detección)
    )

@app.route('/logout')
def logout():
    session.pop('usuario', None)
    return redirect(url_for('login'))

# CAMBIADO: Ruta de subida (sin /api/, para que coincida con form HTML)
@app.route('/subir_chat', methods=['POST'])
def subir_chat():
    if 'archivo' not in request.files:
        flash("No se encontró el archivo en la petición", "error")
        return redirect(url_for('index'))

    archivo = request.files['archivo']

    if archivo.filename == '':
        flash("No se seleccionó ningún archivo", "error")
        return redirect(url_for('index'))

    if not archivo.filename.endswith('.txt'):
        flash("Solo se permiten archivos .txt", "error")
        return redirect(url_for('index'))

    try:
        if not os.path.exists(ruta_data):
            os.makedirs(ruta_data)

        archivo.save(ruta_chat_original)

        mensajes = main.parsear_chat(ruta_chat_original)
        datos_organizados = main.organizar_datos(mensajes)

        # Guardar local para actualización inmediata
        with open(ruta_json, 'w', encoding='utf-8') as f:
            json.dump(datos_organizados, f, indent=4, ensure_ascii=False)

        # NUEVO: Actualizar variable global local
        datos = datos_organizados

        # NUEVO: Sincronizar con Render (propaga a todas las PCs)
        if push_datos_to_render(datos_organizados):
            flash(f"Archivo subido y sincronizado globalmente con Render. Total mensajes: {len(mensajes)}", "success")
        else:
            flash(f"Archivo subido y procesado localmente. Total mensajes: {len(mensajes)}. Sincronización con Render falló (verifica internet/token). Refresca después para sync.", "warning")

        return redirect(url_for('index'))

    except Exception as e:
        flash(f"Error procesando el archivo: {e}", "error")
        return redirect(url_for('index'))

# NUEVO: Ruta API para descargar JSON central (accesible por PCs locales)
@app.route('/api/datos_json')
def api_datos_json():
    try:
        datos_central = cargar_datos_json_local()  # En Render, esto es el central
        return jsonify(datos_central)
    except Exception as e:
        print(f"Error en API datos_json: {e}")
        abort(500, str(e))

# NUEVO: Ruta API para actualizar JSON central (solo con token, POST desde PCs)
@app.route('/api/actualizar_json', methods=['POST'])
def api_actualizar_json():
    # Verifica token de sincronización
    auth_header = request.headers.get('Authorization')
    if not auth_header or auth_header != f'Bearer {SYNC_TOKEN}':
        abort(401, "Token de sincronización inválido")

    try:
        datos_nuevos = request.json
        if not isinstance(datos_nuevos, list):
            abort(400, "Datos deben ser una lista de mensajes")

        # Guarda en el archivo central (en Render)
        with open(ruta_json, 'w', encoding='utf-8') as f:
            json.dump(datos_nuevos, f, indent=4, ensure_ascii=False)

        print(f"JSON actualizado en Render desde PC: {len(datos_nuevos)} mensajes")
        return jsonify({"success": True, "mensaje": f"Actualizado: {len(datos_nuevos)} mensajes"}), 200

    except Exception as e:
        print(f"Error actualizando JSON: {e}")
        abort(500, str(e))

# Ruta para descargar archivos desde la carpeta 'descargas'
@app.route('/descargar/<path:nombre_archivo>')
def descargar(nombre_archivo):
    try:
        return send_from_directory(ruta_descargas, nombre_archivo, as_attachment=True)
    except FileNotFoundError:
        abort(404)

# Rutas para servir manifest.json y service-worker.js desde la carpeta src (resource_path)
@app.route('/manifest.json')
def manifest():
    return send_from_directory(resource_path, 'manifest.json')

@app.route('/service-worker.js')
def service_worker():
    return send_from_directory(resource_path, 'service-worker.js')

if __name__ == '__main__':
    # NUEVO: Detectar modo (local o Render)
    modo = "Render (cloud)" if os.environ.get('RENDER') == 'true' else "Local"
    print(f"Modo: {modo}")
    print(f"URL Render configurada: {URL_RENDER}")
    print(f"Token sync configurado: {'Sí' if SYNC_TOKEN else 'No (usa default)'}")

    def get_local_ip():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except:
            return "No se pudo obtener IP (verifica conexión)"

    local_ip = get_local_ip()
    print(f"Iniciando servidor Flask accesible en toda la red WiFi:")
    print(f"  - Local (tu PC): http://127.0.0.1:8080")
    print(f"  - Red (otros dispositivos): http://{local_ip}:8080")
    print(f"  - Asegúrate de que todos estén en la misma WiFi y permite puerto 8080 en firewall.")
    print(f"  - Para detener: Ctrl+C")

    app.debug = True
    app.run(host='0.0.0.0', port=8080)