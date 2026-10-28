import csv
import json
import re
from datetime import date
from pathlib import Path
import unicodedata
from django.db import transaction
from openpyxl import load_workbook
import openpyxl
from estudiantes.models import Estudiante, Carpeta
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from django.http import HttpResponse

TELEFONO_PREDETERMINADO = "3000000000"
CORREO_PREDETERMINADO = "notiene@notiene.com"

def normalizar_encabezado(valor):
    """Normaliza encabezados de Excel para reconocer variantes."""
    texto = str(valor or "").strip().casefold()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(
        caracter for caracter in texto
        if not unicodedata.combining(caracter)
    )
    texto = re.sub(r"[^a-z0-9]+", "_", texto)
    return texto.strip("_")
def truncar_texto(valor, max_len=30):
    """Trunca un texto al número máximo de caracteres permitido por la BD."""
    if valor is None:
        return ""
    texto = str(valor).strip()
    return texto[:max_len]
def normalizar_cedula(valor):
    """Limpia y normaliza el valor de la cédula."""
    if valor is None:
        return ""
    cedula = str(valor).strip()
    if cedula.endswith(".0"):
        cedula = cedula[:-2]
    cedula = re.sub(r"[^0-9]", "", cedula)
    return cedula

def convertir_booleano(valor):
    """Convierte los valores Sí/No del Excel a booleanos de Python."""
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

def generar_consecutivo_codigo(codigo_base):
    """Genera un código de carpeta consecutivo si el código base ya existe en la BD."""
    try:
        base = int(codigo_base)
    except (ValueError, TypeError):
        return codigo_base

    contador = 1
    while True:
        nuevo_codigo = int(f"{base}{contador}")
        if not Carpeta.objects.filter(pk=nuevo_codigo).exists():
            return nuevo_codigo
        contador += 1

def normalizar_anio(valor):
    """Limpia y normaliza el año."""
    if valor is None:
        return ""
    texto = str(valor).strip()
    if texto.endswith(".0"):
        texto = texto[:-2]
    if "-" in texto:
        texto = texto.split("-")[0].strip()
    return texto

def convertir_entero(valor, campo, fila, obligatorio=False):
    """Convierte números de Excel a enteros sin aceptar decimales."""
    if valor is None or str(valor).strip() == "":
        if obligatorio:
            raise ValueError(f"Falta el campo obligatorio '{campo}'.")
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
            raise ValueError(f"Fila {fila}: '{campo}' debe ser un número entero.")

    return numero

def leer_excel(ruta_archivo):
    """Lee la primera hoja del Excel y mapea estrictamente los encabezados."""
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

        encabezados_normalizados = [
            normalizar_encabezado(valor)
            for valor in encabezados
        ]

        alias = {
            "no": "numero",
            "numero": "numero",
            "codigo_que_reposa_en_la_carpeta": "codcarpeta",
            "cod_carpeta": "codcarpeta",
            "codigo_carpeta": "codcarpeta",
            "programa": "programa",
            "nombre_del_estudiante": "nombre",
            "nombre": "nombre",
            "documento_tarjeta_de_indentidad_o_cedula_de_ciudadania": "tipocc",
            "tipocc": "tipocc",
            "tipo_documento": "tipocc",
            "numero_de_identificacion": "cedula_ciudadania",
            "cedula": "cedula_ciudadania",
            "cedula_ciudadania": "cedula_ciudadania",
            "telefono": "contacto",
            "celular": "contacto",
            "contacto": "contacto",
            "correo": "email",
            "correo_electronico": "email",
            "email": "email",
            "indique_si_en_la_carpeta_reposa_fotocopia_de_cedula_tarjeta_de_identidad": "rdoc",
            "rdoc": "rdoc",
            "fotocopia_cedula": "rdoc",
            "ano_de_ingreso_en_la_universidad": "year_start",
            "ano_ingreso": "year_start",
            "year_start": "year_start",
            "ano_en_que_dejo_de_estudiar": "year_end",
            "ano_fin": "year_end",
            "year_end": "year_end",
            "indique_si_en_la_carpeta_reposa_sabana_de_notas_o_reporte_de_notas": "notas",
            "notas": "notas",
            "sabana_notas": "notas",
            "indique_si_en_la_carpeta_reposa_guias_de_matricula_de_los_periodos_cursados": "mat_sem",
            "mat_sem": "mat_sem",
            "guias_matricula": "mat_sem",
            "indique_si_en_la_carpeta_reposa_recibos_de_pago_de_los_periodos_cursados": "rec_pago",
            "rec_pago": "rec_pago",
            "recibos_pago": "rec_pago",
            "numero_de_folios_que_reposan_en_la_carpeta": "folio",
            "folio": "folio",
            "folios": "folio",
            "observaciones": "observa",
            "observa": "observa",
            "modelo": "modelo",
        }

        encabezados_mapeados = [
            alias.get(encabezado) for encabezado in encabezados_normalizados
        ]

        registros = []

        for numero_fila, valores in enumerate(filas, start=2):
            if all(valor is None for valor in valores):
                continue

            registro = {}
            for campo_interno, valor in zip(encabezados_mapeados, valores):
                if campo_interno:
                    # Aplicamos truncado preventivo según el campo para evitar desbordar la BD
                    if campo_interno == "modelo":
                        registro[campo_interno] = truncar_texto(valor, 30)
                    elif campo_interno == "tipocc":
                        registro[campo_interno] = truncar_texto(valor, 20)  # Coincide con max_length=20
                    elif campo_interno == "programa":
                        registro[campo_interno] = truncar_texto(valor, 30)  # Coincide con max_length=30 de tu modelo
                    elif campo_interno == "nombre":
                        registro[campo_interno] = truncar_texto(valor, 30)  # Coincide con max_length=30 de tu modelo
                    elif campo_interno == "contacto":
                        registro[campo_interno] = truncar_texto(valor, 15)  # Coincide con max_length=15 de tu modelo
                    elif campo_interno == "email":
                        registro[campo_interno] = truncar_texto(valor, 254)
                    else:
                        registro[campo_interno] = valor

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
    """Usa la cédula como código base."""
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
    """Guarda los conflictos en formato JSON."""
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

def guardar_reporte_errores_csv(conflictos, ruta_salida_csv):
    """Genera un archivo CSV limpio y estructurado con los errores encontrados."""
    ruta = Path(ruta_salida_csv)
    ruta.parent.mkdir(parents=True, exist_ok=True)

    with ruta.open("w", encoding="utf-8-sig", newline="") as archivo_csv:
        writer = csv.writer(archivo_csv, delimiter=";")
        writer.writerow(["Fila Excel", "Tipo de Conflicto", "Detalle del Mensaje"])

        for conflicto in conflictos:
            fila = conflicto.get("fila") or conflicto.get("fila_excel", "General")
            tipo = conflicto.get("tipo", "desconocido")
            
            mensajes = []
            if "mensajes" in conflicto and isinstance(conflicto["mensajes"], list):
                mensajes.extend(conflicto["mensajes"])
            elif "mensaje" in conflicto:
                mensajes.append(conflicto["mensaje"])
            elif "error" in conflicto:
                mensajes.append(conflicto["error"])
            
            texto_mensaje = " | ".join(mensajes) if mensajes else "Sin detalles"
            writer.writerow([fila, tipo, texto_mensaje])

    print(f"Reporte CSV de errores guardado en: {ruta_salida_csv}")

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

        for campo in obligatorios:
            valor = registro.get(campo)
            if valor is None or not str(valor).strip():
                if campo == "codcarpeta":
                    continue
                errores_fila.append(f"El campo '{campo}' es obligatorio.")

        cedula = normalizar_cedula(registro.get("cedula_ciudadania"))
        if cedula and (not cedula.isdigit() or len(cedula) > 15):
            errores_fila.append("La cédula debe ser numérica y tener máximo 15 dígitos.")

        anios = {}
        for campo in ["year_start", "year_end"]:
            valor = registro.get(campo)
            if valor is None or not str(valor).strip():
                if campo == "year_start":
                    errores_fila.append("El año de inicio es obligatorio.")
                continue

            texto = normalizar_anio(valor)
            try:
                numero = float(texto)
                if not numero.is_integer():
                    raise ValueError
                anio = int(numero)
                if len(str(anio)) != 4 or not (1900 <= anio <= anio_actual):
                    raise ValueError

                anio_str = str(anio)
                anios[campo] = anio_str
                registro[campo] = anio_str
            except (ValueError, TypeError):
                errores_fila.append(f"'{campo}' debe ser un año válido de cuatro dígitos.")

        if "year_start" in anios and "year_end" in anios and anios["year_end"] < anios["year_start"]:
            errores_fila.append("El año de finalización no puede ser anterior al año de inicio.")

        folios = registro.get("folio")
        if folios is not None and str(folios).strip():
            try:
                numero = float(str(folios).strip())
                if not numero.is_integer() or numero < 0:
                    raise ValueError
            except (ValueError, TypeError):
                errores_fila.append("El número de folios debe ser un entero no negativo.")

        for campo in campos_booleanos:
            try:
                convertir_booleano(registro.get(campo))
            except ValueError as exc:
                errores_fila.append(f"Campo '{campo}': {exc}")

        if errores_fila:
            errores.append({
                "fila_excel": fila,
                "tipo": "error_validacion",
                "mensajes": errores_fila,
                "datos_fila": registro,  # <--- Guardamos los datos originales
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
        cedula = normalizar_cedula(registro.get("cedula_ciudadania"))
        anio = str(registro.get("year_start")).strip()
        programa_excel = str(registro.get("programa", "")).strip().casefold()

        clave = (cedula, anio)
        if clave in cedulas_anio_excel:
            conflictos.append({
                "fila_excel": fila,
                "tipo": "duplicado_en_excel",
                "mensaje": "La cédula y el año de ingreso ya aparecen en otra fila del archivo.",
                "datos_fila": registro,
            })
        else:
            cedulas_anio_excel.add(clave)

        codigo_valor = registro.get("codcarpeta")
        if codigo_valor is not None and str(codigo_valor).strip():
            try:
                codigo = convertir_entero(codigo_valor, "codcarpeta", fila, obligatorio=True)
            except ValueError as exc:
                conflictos.append({
                    "fila_excel": fila,
                    "tipo": "codigo_invalido",
                    "mensaje": str(exc),
                    "datos_fila": registro,
                })
                continue

            if codigo in codigos_excel:
                conflictos.append({
                    "fila_excel": fila,
                    "tipo": "codigo_repetido_en_excel",
                    "mensaje": f"El código de carpeta {codigo} está repetido en el archivo.",
                    "datos_fila": registro,
                })
            else:
                codigos_excel.add(codigo)

            carpeta_existente = Carpeta.objects.filter(pk=codigo).first()
            if carpeta_existente:
                anio_existente = str(carpeta_existente.year_start).strip()
                programa_existente = str(carpeta_existente.estudiante.programa).strip().casefold()

                if anio_existente == anio and programa_existente == programa_excel:
                    conflictos.append({
                        "fila_excel": fila,
                        "tipo": "carpeta_existente",
                        "mensaje": f"El código de carpeta {codigo} ya existe en la base de datos para el mismo año ({anio}) y programa.",
                        "datos_fila": registro,
                    })
                else:
                    registro["_usar_consecutivo"] = True

    return conflictos

def importar_excel(ruta_excel, ruta_reporte_salida):
    registros = leer_excel(ruta_excel)

    validos, errores_validacion = validar_registros(registros)
    conflictos = list(errores_validacion)

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

    for registro in registros_importables:
        fila = registro["_fila_excel"]
        try:
            with transaction.atomic():
                cedula = normalizar_cedula(registro.get("cedula_ciudadania"))
                estudiante = Estudiante.objects.filter(pk=cedula).first()

                if estudiante is None:
                    estudiante = Estudiante.objects.create(
                        cedula_ciudadania=cedula,
                        # Truncamos los campos por seguridad para que nunca superen el límite de la BD
                        nombre=truncar_texto(registro["nombre"], 150),       # Asume que nombre soporta más, ajústalo si es menor
                        tipocc=truncar_texto(registro["tipocc"], 10),         # CC, TI, etc.
                        rdoc=convertir_booleano(registro.get("rdoc")),
                        programa=truncar_texto(registro["programa"], 50),     # Ajusta el límite según tu modelo programa (ej. 50 o 100)
                        contacto=truncar_texto(registro["contacto"], 20),
                        email=truncar_texto(registro["email"], 254),
                    )
                    estudiantes_creados += 1

                year_start = str(registro["year_start"]).strip()
                codigo_excel = registro.get("codcarpeta")

                if codigo_excel is None or not str(codigo_excel).strip():
                    codigo = generar_codigo_carpeta(cedula)
                else:
                    codigo = convertir_entero(codigo_excel, "codcarpeta", fila, obligatorio=True)
                    if registro.get("_usar_consecutivo"):
                        codigo = generar_consecutivo_codigo(codigo)

                year_end = registro.get("year_end")
                if year_end is not None:
                    year_end = str(year_end).strip() or None

                folio = convertir_entero(registro.get("folio"), "folio", fila)
                if folio is None:
                    folio = 0

                Carpeta.objects.create(
                    codcarpeta=codigo,
                    estudiante=estudiante,
                    year_start=year_start,
                    year_end=year_end,
                    notas=convertir_booleano(registro.get("notas")),
                    mat_sem=convertir_booleano(registro.get("mat_sem")),
                    rec_pago=convertir_booleano(registro.get("rec_pago")),
                    folio=folio,
                    modelo=truncar_texto(registro.get("modelo") or "presencial", 30), # <--- Aquí limitamos a 30 por seguridad
                    observa=registro.get("observa"), # Si observa es TextField, no necesita límite
                )

        except Exception as row_exc:
            conflictos.append({
                "fila_excel": fila,
                "tipo": "error_base_datos",
                "mensaje": f"Error al guardar: {str(row_exc)}",
                "datos_fila": registro,
            })

    # Guardar reporte de errores
    try:
        guardar_reporte_errores_csv(conflictos, ruta_reporte_salida)
        # Opcional guardar JSON si se requiere para el reporte en Excel
        ruta_json = Path(ruta_reporte_salida).with_suffix(".json")
        guardar_conflictos_json(conflictos, ruta_json)
    except Exception as exc:
        print(f"Error generando archivos de reporte: {exc}")

    return {
        "total_leidos": len(registros),
        "total_validos": len(validos),
        "errores_validacion": len(errores_validacion),
        "estudiantes_creados": estudiantes_creados,
        "carpetas_creadas": carpetas_creadas,
        "conflictos": len(conflictos),
        "detalle_conflictos": conflictos,
    }

def generar_excel_conflictos_json(ruta_json_conflictos):
    """
    Lee el archivo JSON de conflictos, construye un libro de Excel (.xlsx) estilizado
    mostrando el error y todos los datos originales de la fila que falló.
    """
    ruta = Path(ruta_json_conflictos)
    if not ruta.exists():
        raise FileNotFoundError(f"No se encontró el archivo de conflictos en {ruta_json_conflictos}")
        
    with ruta.open("r", encoding="utf-8") as archivo:
        conflictos = json.load(archivo)

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Reporte de Errores y Datos"
    
    ws.views.sheetView[0].showGridLines = True

    fuente_cabecera = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    relleno_cabecera = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
    fuente_celda = Font(name="Calibri", size=11)
    
    alineacion_centro = Alignment(horizontal="center", vertical="center")
    alineacion_izquierda = Alignment(horizontal="left", vertical="center")
    
    borde_fino = Border(
        left=Side(style='thin', color='D9D9D9'),
        right=Side(style='thin', color='D9D9D9'),
        top=Side(style='thin', color='D9D9D9'),
        bottom=Side(style='thin', color='D9D9D9')
    )

    # Definir la cabecera uniendo las columnas de error + los campos del Excel original
    columnas = [
        "Fila Excel", "Tipo de Conflicto", "Detalle / Mensaje de Error",
        "N° Carpeta", "Programa", "Nombre Estudiante", "Tipo Doc", 
        "Cédula", "Teléfono", "Correo", "Fotocopia Cédula", 
        "Año Inicio", "Año Fin", "Notas", "Guías Matrícula", 
        "Recibos Pago", "Folios", "Observaciones", "Modelo"
    ]
    ws.append(columnas)

    for cell in ws[1]:
        cell.font = fuente_cabecera
        cell.fill = relleno_cabecera
        cell.alignment = alineacion_centro
    ws.row_dimensions[1].height = 28

    for index, conf in enumerate(conflictos, start=2):
        fila_origen = conf.get("fila_excel") or conf.get("fila") or "N/A"
        tipo_err = conf.get("tipo") or "Conflicto de Datos"
        
        # Procesar mensajes
        mensajes = []
        if "mensajes" in conf and isinstance(conf["mensajes"], list):
            mensajes.extend(conf["mensajes"])
        elif "mensaje" in conf:
            mensajes.append(conf["mensaje"])
        elif "error" in conf:
            mensajes.append(conf["error"])
        
        mensaje_err = " | ".join(mensajes) if mensajes else "Dato inválido"
        
        # Extraer los datos de la fila original guardados en el diccionario
        datos = conf.get("datos_fila", {})
        
        fila_excel_datos = [
            fila_origen,
            tipo_err,
            mensaje_err,
            datos.get("codcarpeta", ""),
            datos.get("programa", ""),
            datos.get("nombre", ""),
            datos.get("tipocc", ""),
            datos.get("cedula_ciudadania", ""),
            datos.get("contacto", ""),
            datos.get("email", ""),
            datos.get("rdoc", ""),
            datos.get("year_start", ""),
            datos.get("year_end", ""),
            datos.get("notas", ""),
            datos.get("mat_sem", ""),
            datos.get("rec_pago", ""),
            datos.get("folio", ""),
            datos.get("observa", ""),
            datos.get("modelo", ""),
        ]
        
        ws.append(fila_excel_datos)
        
        # Aplicar estilos y alineaciones
        for col in range(1, len(columnas) + 1):
            celda = ws.cell(row=index, column=col)
            celda.font = fuente_celda
            celda.border = borde_fino
            if col <= 3:
                celda.alignment = alineacion_centro if col != 3 else alineacion_izquierda
            else:
                celda.alignment = alineacion_izquierda
                
        ws.row_dimensions[index].height = 20

    # Autoajustar el ancho de las columnas
    for col in ws.columns:
        max_len = max(len(str(cell.value or '')) for cell in col)
        col_letter = openpyxl.utils.get_column_letter(col[0].column)
        ws.column_dimensions[col_letter].width = max(max_len + 4, 15)

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = 'attachment; filename="Reporte_Errores_Con_Datos.xlsx"'
    
    wb.save(response)
    return response