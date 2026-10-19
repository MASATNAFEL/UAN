
import json
import re
from datetime import date
from pathlib import Path
import unicodedata
from django.db import transaction
from openpyxl import load_workbook
from estudiantes.models import Estudiante, Carpeta


TELEFONO_PREDETERMINADO = "3000000000"
CORREO_PREDETERMINADO = "notiene@notiene.com"

def normalizar_encabezado(valor):
    """Normaliza encabezados de Excel para reconocer variantes."""
    texto = str(valor or "").strip().casefold()

    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(
        caracter
        for caracter in texto
        if not unicodedata.combining(caracter)
    )

    texto = re.sub(r"[^a-z0-9]+", "_", texto)
    return texto.strip("_")

def convertir_booleano(valor):
    """
    Convierte los valores Sí/No del Excel a booleanos de Python.
    """
    if valor is None or str(valor).strip() == "":
        return False
    if isinstance(valor, bool):
        return valor

    valor = str(valor).strip().casefold()

    if valor in ("sí", "si", "s", "true", "1", "x"):
        return True

    if valor in ("no", "n", "false", "0"):
        return False

    raise ValueError(f"Valor booleano no reconocido: {valor}")

def convertir_entero(valor, campo, fila, obligatorio=False):
    """Convierte números de Excel a enteros sin aceptar decimales."""
    if valor is None or str(valor).strip() == "":
        if obligatorio:
            raise ValueError(
                f"Falta el campo obligatorio '{campo}'."
            )
        return None

    try:
        numero = int(str(valor).strip())
    except (ValueError, TypeError):
        try:
            numero_decimal = float(valor)
            if not numero_decimal.is_integer():
                raise ValueError
            numero = int(numero_decimal)
        except (ValueError, TypeError):
            raise ValueError(
                f"Fila {fila}: '{campo}' debe ser un número entero."
            )

    return numero

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
    try:
        hoja = libro.active
        filas = hoja.iter_rows(values_only=True)
        encabezados = next(filas, None)

        if not encabezados:
            libro.close()
            raise ValueError("El archivo Excel está vacío.")

        encabezados = [
            normalizar_encabezado(valor)
            for valor in encabezados
        ]

        alias = {
            "no": "numero",
            "codigo_que_reposa_en_la_carpeta": "codcarpeta",
            "programa": "programa",
            "nombre_del_estudiante": "nombre",
            "documento_tarjeta_de_indentidad_o_cedula_de_ciudadania": "tipocc",
            "numero_de_identificacion": "cedula_ciudadania",
            "indique_si_en_la_carpeta_reposa_fotocopia_de_cedula_tarjeta_de_identidad": "rdoc",
            "ano_de_ingreso_en_la_universidad": "year_start",
            "ano_en_que_dejo_de_estudiar": "year_end",
            "indique_si_en_la_carpeta_reposa_sabana_de_notas_o_reporte_de_notas": "notas",
            "indique_si_en_la_carpeta_reposa_guias_de_matricula_de_los_periodos_cursados": "mat_sem",
            "indique_si_en_la_carpeta_reposa_recibos_de_pago_de_los_periodos_cursados": "rec_pago",
            "numero_de_folios_que_reposan_en_la_carpeta": "folio",
            "observaciones": "observa",
        }

        encabezados = [
            alias.get(encabezado, encabezado)
            for encabezado in encabezados
        ]

        if len(encabezados) != len(set(encabezados)):
            raise ValueError(
                "Hay columnas duplicadas después de normalizar "
                "los encabezados del Excel."
            )
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
            telefono = registro.get("contacto")
            correo = registro.get("email")
            registro["contacto"] = (
                str(telefono).strip()
                if telefono is not None and str(telefono).strip()
                else TELEFONO_PREDETERMINADO
                )
            registro["email"] = (
                str(correo).strip()
                if correo is not None and str(correo).strip()
                else CORREO_PREDETERMINADO
                )
            
            registros.append(registro)
        return registros
    finally:
        libro.close()

def generar_codigo_carpeta(cedula):
    """
    Usa la cédula como código base.
    Si está ocupada, agrega un contador hasta hallar uno libre.
    """
    try:
        base = int(cedula)
    except (ValueError, TypeError):
        raise ValueError(
            f"La cédula '{cedula}' debe ser numérica "
            "para generar un código de carpeta."
        )

    contador = 0

    while True:
        codigo = base if contador == 0 else int(f"{base}{contador}")

        if not Carpeta.objects.filter(pk=codigo).exists():
            return codigo

        contador += 1


def guardar_conflictos_json(conflictos, ruta_archivo):
    """Guarda los conflictos para revisarlos posteriormente."""
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
def validar_registros(registros):
    validos = []
    errores = []

    anio_actual = date.today().year

    obligatorios = [
        "codcarpeta",
        "programa",
        "nombre",
        "tipocc",
        "cedula_ciudadania",
        "year_start",
    ]

    campos_booleanos = ["rdoc", "notas", "mat_sem", "rec_pago"]

    for registro in registros:
        fila = registro.get("_fila_excel", "?")
        errores_fila = []

        # Campos obligatorios
        for campo in obligatorios:
            valor = registro.get(campo)

            if valor is None or not str(valor).strip():
                # El código de carpeta puede generarse automáticamente.
                if campo == "codcarpeta":
                    continue

                errores_fila.append(
                    f"El campo '{campo}' es obligatorio."
                )

        # Validar cédula
        cedula = registro.get("cedula_ciudadania")

        if cedula is not None:
            cedula = str(cedula).strip()

            if cedula.endswith(".0"):
                cedula = cedula[:-2]

            if cedula and (
                not cedula.isdigit() or len(cedula) > 15
            ):
                errores_fila.append(
                    "La cédula debe ser numérica y tener "
                    "máximo 15 dígitos."
                )

        # Validar años
        anios = {}

        for campo in ["year_start", "year_end"]:
            valor = registro.get(campo)

            if valor is None or not str(valor).strip():
                if campo == "year_start":
                    errores_fila.append(
                        "El año de inicio es obligatorio."
                    )
                continue

            texto = str(valor).strip()

            try:
                numero = float(texto)

                if not numero.is_integer():
                    raise ValueError

                anio = int(numero)

                if len(str(anio)) != 4 or not (
                    1900 <= anio <= anio_actual
                ):
                    raise ValueError

                anios[campo] = str(anio)

            except (ValueError, TypeError):
                errores_fila.append(
                    f"'{campo}' debe ser un año válido de cuatro dígitos."
                )

        if (
            "year_start" in anios
            and "year_end" in anios
            and anios["year_end"] < anios["year_start"]
        ):
            errores_fila.append(
                "El año de finalización no puede ser anterior "
                "al año de inicio."
            )
        # Validar número de folios
        folios = registro.get("folio")

        if folios is not None and str(folios).strip():
            try:
                numero = float(str(folios).strip())

                if not numero.is_integer() or numero < 0:
                    raise ValueError

            except (ValueError, TypeError):
                errores_fila.append(
                    "El número de folios debe ser un "
                    "entero no negativo."
                )

        # Validar Sí/No
        for campo in campos_booleanos:
            try:
                convertir_booleano(registro.get(campo))
            except ValueError as exc:
                errores_fila.append(
                    f"Campo '{campo}': {exc}"
                )

        if errores_fila:
            errores.append({
                "fila_excel": fila,
                "tipo": "error_validacion",
                "mensajes": errores_fila,
            })
        else:
            validos.append(registro)

    return validos, errores

def revisar_conflictos(registros_validos):
    conflictos = []
    cedulas_anio_excel = set()
    codigos_excel = set()

    for registro in registros_validos:
        fila = registro.get("_fila_excel", "?")

        cedula = str(
            registro.get("cedula_ciudadania") or ""
        ).strip()

        if cedula.endswith(".0"):
            cedula = cedula[:-2]

        anio = str(registro.get("year_start")).strip()

        # 1. Detectar la misma cédula y año en el Excel
        clave = (cedula, anio)

        if clave in cedulas_anio_excel:
            conflictos.append({
                "fila_excel": fila,
                "tipo": "duplicado_en_excel",
                "mensaje": (
                    "La cédula y el año de ingreso "
                    "ya aparecen en otra fila del archivo."
                ),
            })
        else:
            cedulas_anio_excel.add(clave)

        # 2. Detectar códigos repetidos dentro del Excel
        codigo_valor = registro.get("codcarpeta")

        if codigo_valor is not None and str(codigo_valor).strip():
            try:
                codigo = convertir_entero(
                    codigo_valor,
                    "codcarpeta",
                    fila,
                    obligatorio=True,
                )
            except ValueError as exc:
                conflictos.append({
                    "fila_excel": fila,
                    "tipo": "codigo_invalido",
                    "mensaje": str(exc),
                })
                continue

            if codigo in codigos_excel:
                conflictos.append({
                    "fila_excel": fila,
                    "tipo": "codigo_repetido_en_excel",
                    "mensaje": (
                        f"El código de carpeta {codigo} "
                        "está repetido en el archivo."
                    ),
                })
            else:
                codigos_excel.add(codigo)

            # 3. Comprobar si el código ya existe en la BD
            if Carpeta.objects.filter(pk=codigo).exists():
                conflictos.append({
                    "fila_excel": fila,
                    "tipo": "codigo_existente",
                    "mensaje": (
                        f"El código de carpeta {codigo} "
                        "ya existe en la base de datos."
                    ),
                })

        # 4. Comprobar si ya existe la carpeta del estudiante
        estudiante = Estudiante.objects.filter(
            pk=cedula
        ).first()

        if estudiante and Carpeta.objects.filter(
            estudiante=estudiante,
            year_start=anio,
        ).exists():
            conflictos.append({
                "fila_excel": fila,
                "tipo": "carpeta_existente",
                "mensaje": (
                    f"El estudiante {cedula} ya tiene "
                    f"una carpeta del año {anio}."
                ),
            })

    return conflictos
def importar_excel(ruta_excel, ruta_conflictos):
    registros = leer_excel(ruta_excel)

    validos, errores_validacion = validar_registros(registros)
    conflictos = list(errores_validacion)

    # Revisar conflictos antes de modificar la base de datos.
    conflictos.extend(revisar_conflictos(validos))

    filas_con_conflictos = {
        conflicto["fila_excel"]
        for conflicto in conflictos
    }

    registros_importables = [
        registro
        for registro in validos
        if registro["_fila_excel"] not in filas_con_conflictos
    ]

    estudiantes_creados = 0
    carpetas_creadas = 0

    try:
        with transaction.atomic():
            for registro in registros_importables:
                fila = registro["_fila_excel"]

                cedula = str(
                    registro["cedula_ciudadania"]
                ).strip()

                if cedula.endswith(".0"):
                    cedula = cedula[:-2]

                # Obtener o crear el estudiante.
                estudiante = Estudiante.objects.filter(
                    pk=cedula
                ).first()

                if estudiante is None:
                    estudiante = Estudiante.objects.create(
                        cedula_ciudadania=cedula,
                        nombre=str(registro["nombre"]).strip(),
                        tipocc=str(registro["tipocc"]).strip(),
                        rdoc=convertir_booleano(
                            registro.get("rdoc")
                        ),
                        programa=str(registro["programa"]).strip(),
                        contacto=registro["contacto"],
                        email=registro["email"],
                    )
                    estudiantes_creados += 1

                year_start = str(
                    registro["year_start"]
                ).strip()

                codigo_excel = registro.get("codcarpeta")

                if (
                    codigo_excel is None
                    or not str(codigo_excel).strip()
                ):
                    codigo = generar_codigo_carpeta(cedula)
                else:
                    codigo = convertir_entero(
                        codigo_excel,
                        "codcarpeta",
                        fila,
                        obligatorio=True,
                    )

                year_end = registro.get("year_end")

                if year_end is not None:
                    year_end = str(year_end).strip() or None

                folio = convertir_entero(
                    registro.get("folio"),
                    "folio",
                    fila,
                )

                if folio is None:
                    folio = 0

                Carpeta.objects.create(
                    codcarpeta=codigo,
                    estudiante=estudiante,
                    year_start=year_start,
                    year_end=year_end,
                    notas=convertir_booleano(
                        registro.get("notas")
                    ),
                    mat_sem=convertir_booleano(
                        registro.get("mat_sem")
                    ),
                    rec_pago=convertir_booleano(
                        registro.get("rec_pago")
                    ),
                    folio=folio,
                    modelo=str(
                        registro.get("modelo") or "presencial"
                    ).strip(),
                    observa=registro.get("observa"),
                )

                carpetas_creadas += 1

    except Exception as exc:
        conflictos.append({
            "tipo": "error_importacion",
            "mensaje": str(exc),
        })

        # Si falla la transacción, no se consideran
        # confirmados los registros creados.
        estudiantes_creados = 0
        carpetas_creadas = 0

    finally:
        guardar_conflictos_json(
            conflictos,
            ruta_conflictos,
        )

    return {
        "total_leidos": len(registros),
        "total_validos": len(validos),
        "errores_validacion": len(errores_validacion),
        "estudiantes_creados": estudiantes_creados,
        "carpetas_creadas": carpetas_creadas,
        "conflictos": len(conflictos),
        "detalle_conflictos": conflictos,
    }
