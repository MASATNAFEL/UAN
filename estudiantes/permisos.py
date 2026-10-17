from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

from estudiantes.models import Estudiante, Carpeta


def crear_roles():
    content_type = ContentType.objects.get_for_model(Estudiante)

    # Obtener los permisos del modelo Estudiante
    permisos = Permission.objects.filter(
        content_type=content_type
    )

    permisos_por_nombre = {
        permiso.codename: permiso
        for permiso in permisos
    }

    # Crear los grupos
    administrador, creado = Group.objects.get_or_create(
            name="Super"
        )
    
    moderador, creado = Group.objects.get_or_create(
        name="Medio"
    )
    consultor, creado = Group.objects.get_or_create(
        name="Consulta"
    )
    for modelo in [Estudiante, Carpeta]:
        content_type = ContentType.objects.get_for_model(modelo)
        permisos = Permission.objects.filter(content_type=content_type)
        permisos_por_nombre = {permiso.codename: permiso for permiso in permisos}
    
    # Moderador: puede hacer todas las operaciones
    moderador.permissions.add(*permisos.filter(codename__in=[
        f"view_{modelo._meta.model_name}",
        f"add_{modelo._meta.model_name}",
        f"change_{modelo._meta.model_name}",
    ]))


    # Consultor: solamente puede visualizar
    consultor.permissions.add(*permisos.filter(codename=f"view_{modelo._meta.model_name}"))