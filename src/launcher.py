import sys
import os

# Agrega la carpeta raíz al path para que encuentre el paquete src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.myapp import app
from waitress import serve

if __name__ == '__main__':
    # Detectar si está empaquetado con PyInstaller
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    # Ajustar rutas de templates y static en la app Flask
    app.template_folder = os.path.join(base_path, 'src', 'templates')
    app.static_folder = os.path.join(base_path, 'src', 'static')

    # Servir con waitress en todas las interfaces, puerto 8080
    serve(app, host='0.0.0.0', port=8080)
