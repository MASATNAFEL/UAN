import json
from pathlib import Path

def menu_dinamico(request):
    ruta_menu = Path(__file__).resolve().parent / "menu.json"

    with open(ruta_menu, "r", encoding="utf-8") as archivo:
        menu = json.load(archivo)

    return {"menu": menu}