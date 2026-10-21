def menu_dinamico(request):
    if not request.user.is_authenticated:
        return {'menu': []}
    
    # Verificamos a qué grupos pertenece el usuario de forma segura
    es_consulta = request.user.groups.filter(name="Consulta").exists()
    # Usa __iexact para evitar problemas con mayúsculas/minúsculas
    es_medio = request.user.groups.filter(name__iexact="Medio").exists()
    
    estructura_menu = [
        {
            "nombre": "Informacion Estudiantes",
            "url": "index",
            "icono": "bi-people"
        },
        {
            "nombre": "Estudiantes",
            "icono": "bi-mortarboard",
            "submenu": [
                {
                    "nombre": "Buscar Estudiantes",
                    "url": "buscar",
                    "icono": "bi-search",
                    "permisos": "estudiantes.view_estudiante"
                },
                {
                    "nombre": "Registrar Estudiantes",
                    "url": "registro",
                    "icono": "bi-person-plus",
                    "permisos": "estudiantes.add_estudiante"
                }
            ]
        },
        {
            "nombre": "Carpetas",
            "icono": "bi-folder",
            "submenu": [
                {
                    "nombre": "Buscar Carpetas",
                    "url": "consultar",
                    "icono": "bi-search",
                    "permisos": "estudiantes.view_carpeta"
                },
                {
                    "nombre": "Registrar Carpetas",
                    "url": "carpeta",
                    "icono": "bi-folder-plus",
                    "permisos": "estudiantes.add_carpeta"
                }
            ]
        },
        {
            "nombre": "Carga masiva de estudiantes",
            "url": "subirarchivo",
            "icono": "bi-file-earmark-excel",
            "permisos": "estudiantes.add_estudiante",
            "tipo": "masivo"
        },
        {
                "nombre": "Gestion de usuarios",
                "url": "administrar_usuarios",
                "icono": "bi-person-gear",
                "tipo": "admin_usuarios"
                },
            {
                "nombre": "Administrar Grupos",
                "url": "administrar_grupos",
                "icono": "bi-shield-lock",
                "tipo": "admin_grupos"
                },
                {
                    "nombre": "Cerrar Sesion",
                    "url": "logout",
                    "icono": "bi-box-arrow-right",
                    "tipo": "logout"
                }
            ]
        
    menu_filtrado = []

    for item in estructura_menu:
        if "submenu" in item:
            submenus_validos = []
            for sub in item["submenu"]:
                # REGLA 1: Si es del grupo "Consulta", solo permitimos las URLs de búsqueda ("buscar" o "consultar")
                if es_consulta:
                    if sub["url"] in ["buscar", "consultar"]:
                        submenus_validos.append(sub)
                else:
                    # Lógica normal para otros usuarios basada en permisos
                    permiso = sub.get("permisos")
                    if not permiso or request.user.is_superuser or request.user.has_perm(permiso):
                        submenus_validos.append(sub)
            
            if submenus_validos:
                item_copia = item.copy()
                item_copia["submenu"] = submenus_validos
                menu_filtrado.append(item_copia)
        else:
            if es_consulta and item.get("url") == "subirarchivo":
                continue
                
            # Opciones de administración exclusivas para Superusuario (se ocultan si es grupo 'Medio')
            if item.get("tipo") in ["admin_usuarios", "admin_grupos"]:
                if request.user.is_superuser and not es_medio:
                    menu_filtrado.append(item)
            elif item.get("tipo") == "logout":
                menu_filtrado.append(item)
            else:
                permiso = item.get("permisos")
                if not permiso or request.user.is_superuser or request.user.has_perm(permiso):
                    menu_filtrado.append(item)

    # REGLA 2: El grupo "medio" NO puede ver "Administrar usuarios", 
    # aunque sea superusuario (o lo limitamos explícitamente).
    # Solo se muestra si es superusuario Y NO pertenece al grupo "medio".
    mostrar_admin = request.user.is_superuser and not es_medio

    return {
        'menu': menu_filtrado,
        'mostrar_admin': mostrar_admin # Pasamos esta bandera limpia a la plantilla
    }