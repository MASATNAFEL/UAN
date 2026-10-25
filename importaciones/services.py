
import json
from pathlib import Path

from openpyxl import load_workbook


TELEFONO_PREDETERMINADO = "3000000000"


def convertir_booleano(valor):
    """
    Convierte los valores Sí/No del Excel a booleanos de Python.
    """
    if valor is None or str(valor).strip() == "":
        return False

    valor = str(valor).strip().casefold()

    if valor in ("sí", "si", "s", "true", "1", "x"):
        return True

    if valor in ("no", "n", "false", "0"):
        return False

    raise ValueError(f"Valor booleano no reconocido: {valor}")


def leer_excel(ruta_archivo):
    """
    Lee la primera hoja del Excel y devuelve sus filas como diccionarios.
    La primera fila debe contener los encabezados.
    """
    libro = load_workbook(
        filename=ruta_archivo,
        read_only=True,
        data_only=True,
    )

    hoja = libro.active
    filas = hoja.iter_rows(values_only=True)

    encabezados = next(filas, None)

    if not encabezados:
        libro.close()
        raise ValueError("El archivo Excel está vacío.")

    encabezados = [
        str(valor).strip() if valor is not None else ""
        for valor in encabezados
    ]

    registros = []

    for numero_fila, valores in enumerate(filas, start=2):
        if all(valor is None for valor in valores):
            continue

        registro = {
            encabezado: valor
            for encabezado, valor in zip(encabezados, valores)
            if encabezado
        }

        registro["_fila_excel"] = numero_fila
        registros.append(registro)

    libro.close()
    return registros


def guardar_conflictos_json(conflictos, ruta_archivo):
    """
    Guarda los conflictos detectados para revisión posterior.
    """
    ruta = Path(ruta_archivo)
    ruta.parent.mkdir(parents=True, exist_ok=True)

    with ruta.open("w", encoding="utf-8") as archivo:
        json.dump(
            conflictos,
            archivo,
            ensure_ascii=False,
            indent=4,
            default=str,
        )
