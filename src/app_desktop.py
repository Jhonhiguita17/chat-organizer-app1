import threading
import webview
from waitress import serve
import sys
import os
import myapp  # tu app Flask

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(base_path, relative_path)

def start_flask():
    serve(myapp.app, host='127.0.0.1', port=8080)

if __name__ == '__main__':
    flask_thread = threading.Thread(target=start_flask)
    flask_thread.daemon = True
    flask_thread.start()

    # Crear ventana webview sin abrir navegador externo
    window = webview.create_window("Chat Organizer App", "http://127.0.0.1:8080", confirm_close=True)
    webview.start(debug=False)
