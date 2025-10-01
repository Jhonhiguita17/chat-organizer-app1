from pathlib import Path

# Carpeta raíz del proyecto (dos niveles arriba de este archivo)
BASE_DIR = Path(__file__).resolve().parent.parent

# Carpeta data dentro de la raíz
DATA_DIR = BASE_DIR / 'data'

# Crear carpeta data si no existe
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Rutas relativas a archivos dentro de data
RUTA_CHAT = DATA_DIR / 'chat_networking.txt'
RUTA_DATOS = DATA_DIR / 'datos_organizados.json'
RUTA_LOG = DATA_DIR / 'log_usuarios.txt'

SUBESTACIONES = ['Subestación A', 'Subestación B', 'Central 1', 'Central 2']
INCIDENTES = ['incidente', 'falla', 'problema', 'error', 'sobrecarga']
REQUERIMIENTOS = ['requerimiento', 'solicitud', 'pedido', 'necesito', 'mantenimiento']

ADMIN_USER = 'admin'
