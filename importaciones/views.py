import logging
import tempfile
from pathlib import Path

from django.conf import settings
from django.contrib import messages
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required, permission_required

from .services import importar_excel

logger = logging.getLogger(__name__)

@login_required
@permission_required('estudiantes.add_estudiante', raise_exception=True)
@permission_required('estudiantes.add_carpeta', raise_exception=True)
@require_http_methods(["GET", "POST"])
def subir_excel(request):
    resultado = None

    if request.method == "POST":
        archivo = request.FILES.get("archivo")

        if not archivo:
            messages.error(
                request,
                "Debes seleccionar un archivo Excel."
            )
            return render(
                request,
                "importaciones/subir_excel.html"
            )

        # Validación básica del archivo.
        extension = Path(archivo.name).suffix.lower()

        if extension != ".xlsx":
            messages.error(
                request,
                "El archivo debe tener formato .xlsx."
            )
            return render(
                request,
                "importaciones/subir_excel.html"
            )

        # Límite de 10 MB para la carga.
        if archivo.size > 10 * 1024 * 1024:
            messages.error(
                request,
                "El archivo no puede superar los 10 MB."
            )
            return render(
                request,
                "importaciones/subir_excel.html"
            )

        try:
            # Crear un archivo temporal en el servidor.
            with tempfile.TemporaryDirectory() as temporal:
                ruta_excel = Path(temporal) / "importacion.xlsx"
                ruta_conflictos = (
                    Path(temporal) / "conflictos.json"
                )

                with ruta_excel.open("wb") as destino:
                    for fragmento in archivo.chunks():
                        destino.write(fragmento)

                resultado = importar_excel(
                    ruta_excel,
                    ruta_conflictos
                )

            # El importador captura errores de importación y los
            # devuelve en detalle_conflictos.
            if any(
                conflicto.get("tipo") == "error_importacion"
                for conflicto in resultado["detalle_conflictos"]
            ):
                messages.error(
                    request,
                    "La importación no se completó. "
                    "Revisa los errores reportados."
                )
            elif resultado["conflictos"] > 0:
                messages.warning(
                    request,
                    "La importación terminó con registros "
                    "omitidos o errores que debes revisar."
                )
            else:
                messages.success(
                    request,
                    "El archivo se importó correctamente."
                )

        except (ValueError, OSError) as exc:
            messages.error(
                request,
                "No fue posible procesar el archivo. "
                "Verifica que sea un Excel válido."
            )
            logger.warning(
                "Error al procesar Excel: %s",
                exc
            )

        except Exception:
            logger.exception(
                "Error inesperado durante la carga del Excel."
            )
            messages.error(
                request,
                "Ocurrió un error inesperado al importar "
                "el archivo."
            )

    return render(
        request,
        "importaciones/subir_excel.html",
        {"resultado": resultado}
    )


