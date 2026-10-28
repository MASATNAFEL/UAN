import json
import logging
from pathlib import Path
import tempfile
from openpyxl import Workbook
from django.http import HttpResponse
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from .services import importar_excel, generar_excel_conflictos_json

logger = logging.getLogger(__name__)

# Ruta centralizada para guardar el JSON de conflictos para descargas posteriores
def obtener_ruta_conflictos_global():
    return Path(settings.MEDIA_ROOT) / "importaciones" / "conflictos.json"


@login_required
@permission_required("estudiantes.add_estudiante", raise_exception=True)
@permission_required("estudiantes.add_carpeta", raise_exception=True)
@require_http_methods(["GET", "POST"])
def subir_excel(request):
    """
    Vista encargada de procesar la carga masiva de estudiantes y carpetas
    a través de un archivo Excel (.xlsx).
    """
    resultado = None

    if request.method == "POST":
        archivo = request.FILES.get("archivo")

        if not archivo:
            messages.error(request, "Debes seleccionar un archivo Excel.")
            return render(request, "importaciones/subir_excel.html")

        extension = Path(archivo.name).suffix.lower()
        if extension != ".xlsx":
            messages.error(request, "El archivo debe tener formato .xlsx.")
            return render(request, "importaciones/subir_excel.html")

        if archivo.size > 10 * 1024 * 1024:
            messages.error(request, "El archivo no puede superar los 10 MB.")
            return render(request, "importaciones/subir_excel.html")

        try:
            with tempfile.TemporaryDirectory() as temporal:
                ruta_excel = Path(temporal) / "importacion.xlsx"
                
                # Usar la ruta global en media para que esté disponible en las descargas
                ruta_conflictos = obtener_ruta_conflictos_global()

                with ruta_excel.open("wb") as destino:
                    for fragmento in archivo.chunks():
                        destino.write(fragmento)

                # Ejecutar el servicio de importación
                resultado = importar_excel(ruta_excel, ruta_conflictos)

            if any(c.get("tipo") == "error_importacion" for c in resultado.get("detalle_conflictos", [])):
                messages.error(
                    request,
                    "La importación no se completó. Revisa los errores reportados."
                )
            elif resultado.get("conflictos", 0) > 0:
                messages.warning(
                    request,
                    "La importación terminó con registros omitidos o errores que debes revisar."
                )
            else:
                messages.success(request, "El archivo se importó correctamente.")

        except (ValueError, OSError) as exc:
            messages.error(
                request,
                "No fue posible procesar el archivo. Verifica que sea un Excel válido."
            )
            logger.warning("Error al procesar Excel: %s", exc)

        except Exception:
            logger.exception("Error inesperado durante la carga del Excel.")
            messages.error(request, "Ocurrió un error inesperado al importar el archivo.")

    return render(
        request,
        "importaciones/subir_excel.html",
        {"resultado": resultado}
    )


@login_required
@permission_required("estudiantes.add_estudiante", raise_exception=True)
@permission_required("estudiantes.add_carpeta", raise_exception=True)
@require_http_methods(["GET"])
def ver_errores_importacion(request):
    """Renderiza el listado de conflictos guardados en el JSON global."""
    ruta_conflictos = obtener_ruta_conflictos_global()
    
    conflictos = []
    if ruta_conflictos.exists():
        try:
            with open(ruta_conflictos, "r", encoding="utf-8") as archivo:
                conflictos = json.load(archivo)
        except Exception:
            logger.exception("No se pudo leer el archivo de conflictos JSON.")
            conflictos = []

    return render(request, "importaciones/errores_importacion.html", {
        "conflictos": conflictos
    })


@login_required
@permission_required("estudiantes.add_estudiante", raise_exception=True)
def descargar_plantilla_excel(request):
    """Genera y descarga una plantilla Excel estructurada con los encabezados correctos."""
    wb = Workbook()
    ws = wb.active
    ws.title = "Plantilla Estudiantes"

    encabezados = [
        "Número de Carpeta", "Programa", "Nombre del Estudiante", 
        "Tipo de Documento (CC, TI)", "Cédula o Identificación", "Teléfono", "Correo Electrónico", 
        "Fotocopia Cédula (Sí/No)", "Año de Ingreso", "Año Fin", 
        "Sábana de Notas (Sí/No)", "Guías de Matrícula (Sí/No)", 
        "Recibos de Pago (Sí/No)", "Número de Folios", "Observaciones", "Modelo"
    ]
    ws.append(encabezados)

    ejemplo = [
        "1012345678", "Ingeniería de Sistemas", "Juan Pérez Gómez", 
        "CC", "1012345678", "3001234567", "juan.perez@example.com", 
        "Sí", "2024", "", "Sí", "Sí", "Sí", "15", "Carpeta entregada completa", "presencial"
    ]
    ws.append(ejemplo)

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = 'attachment; filename="plantilla_importacion_estudiantes.xlsx"'
    wb.save(response)
    return response


@login_required
@permission_required("estudiantes.add_estudiante", raise_exception=True)
def descargar_errores_excel(request):
    """
    Utiliza la función estilizada de services.py para retornar 
    el Excel formateado profesionalmente con los errores de importación.
    """
    ruta_conflictos = obtener_ruta_conflictos_global()
    
    try:
        return generar_excel_conflictos_json(ruta_conflictos)
    except FileNotFoundError:
        return render(request, "errores.html", {"mensaje": "No hay reportes de conflictos disponibles para descargar."})