import json
import logging
from pathlib import Path
import tempfile

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from .services import importar_excel

logger = logging.getLogger(__name__)


@login_required
@permission_required("estudiantes.add_estudiante", raise_exception=True)
@permission_required("estudiantes.add_carpeta", raise_exception=True)
@require_http_methods(["GET", "POST"])
def subir_excel(request):
    """
    Vista encargada de procesar la carga masiva de estudiantes y carpetas
    a través de un archivo Excel (.xlsx).
    Valida extensión, tamaño, permisos y gestiona archivos temporales de forma segura.
    """
    resultado = None

    if request.method == "POST":
        archivo = request.FILES.get("archivo")

        # 1. Validar que se haya enviado un archivo
        if not archivo:
            messages.error(request, "Debes seleccionar un archivo Excel.")
            return render(request, "importaciones/subir_excel.html")

        # 2. Validar la extensión del archivo
        extension = Path(archivo.name).suffix.lower()
        if extension != ".xlsx":
            messages.error(request, "El archivo debe tener formato .xlsx.")
            return render(request, "importaciones/subir_excel.html")

        # 3. Validar el límite de tamaño (máximo 10 MB)
        if archivo.size > 10 * 1024 * 1024:
            messages.error(request, "El archivo no puede superar los 10 MB.")
            return render(request, "importaciones/subir_excel.html")

        try:
            # 4. Uso de directorio temporal seguro para procesar el archivo y conflictos
            with tempfile.TemporaryDirectory() as temporal:
                ruta_excel = Path(temporal) / "importacion.xlsx"
                ruta_conflictos = Path(temporal) / "conflictos.json"

                # Guardar chunks del archivo subido en disco temporal
                with ruta_excel.open("wb") as destino:
                    for fragmento in archivo.chunks():
                        destino.write(fragmento)

                # Ejecutar el servicio de importación
                resultado = importar_excel(ruta_excel, ruta_conflictos)

            # 5. Evaluar resultados y emitir mensajes al usuario
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
@require_http_methods(["GET", "POST"])
def ver_errores_importacion(request):
    """
    Vista opcional orientada a renderizar un historial o detalle de conflictos 
    globales guardados en la ruta estática o persistente de media.
    """
    ruta_conflictos = Path(settings.MEDIA_ROOT) / "importaciones" / "conflictos.json"
    
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