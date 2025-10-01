import os

# Obtiene la ruta absoluta de la carpeta raíz del proyecto (dos niveles arriba de este archivo)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Carpeta data dentro de la raíz
DATA_DIR = os.path.join(BASE_DIR, 'data')

# Rutas relativas
RUTA_CHAT = os.path.join(DATA_DIR, 'chat_networking.txt')
RUTA_DATOS = os.path.join(DATA_DIR, 'datos_organizados.json')
RUTA_LOG = os.path.join(DATA_DIR, 'log_usuarios.txt')

SUBESTACIONES = ['Subestación A', 'Subestación B', 'Central 1', 'Central 2']
INCIDENTES = ['incidente', 'falla', 'problema', 'error', 'sobrecarga']
REQUERIMIENTOS = ['requerimiento', 'solicitud', 'pedido', 'necesito', 'mantenimiento']

ADMIN_USER = 'admin'
