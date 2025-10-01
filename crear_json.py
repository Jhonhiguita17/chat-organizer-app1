import json
import os

ruta_json = r'C:\xampp\htdocs\ChatOrganizerApp\data\datos.json'  # Cambia por la ruta que usa tu programa

if not os.path.exists(ruta_json) or os.path.getsize(ruta_json) == 0:
    with open(ruta_json, 'w', encoding='utf-8') as f:
        json.dump([], f)
    print(f"Archivo JSON creado o inicializado en {ruta_json}")
else:
    print(f"Archivo JSON ya existe y no está vacío: {ruta_json}")
