from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import authenticate,login,logout,get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib import messages
from .forms import CrearUsuarioForm,EditarUsuarioForm
from django.views.decorators.http import require_POST
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test

Usuario = get_user_model()

def login_view(request):
    if request.user.is_authenticated:
        return redirect('index')
    if request.method=="POST":
        username=request.POST.get("username")
        password=request.POST.get("password")
        user=authenticate(request,username=username,password=password)
        if user is not None:
            login(request,user)
            return redirect("index")
        return render(request,"cuentas/login.html", {"error":"usuario o contraseña incorrecta"})
    return render(request,"cuentas/login.html")
def logout_view(request):
    logout(request)
    return redirect("login")
def home(request):
    return render(request,"index.html")
def es_superusuario(user):
    return user.is_authenticated and user.is_superuser


@user_passes_test(es_superusuario, login_url="login")
def administrar_usuarios(request):
    usuarios = Usuario.objects.prefetch_related("groups").order_by("username")

    return render(
        request,
        "cuentas/usuarios.html",
        {
            "usuarios": usuarios,
        }
    )


@user_passes_test(es_superusuario, login_url="login")
def crear_usuario(request):
    if request.method == "POST":
        form = CrearUsuarioForm(request.POST)

        if form.is_valid():
            usuario = form.save()
            messages.success(
                request,
                f"El usuario {usuario.username} fue creado correctamente."
            )
            return redirect("administrar_usuarios")
    else:
        form = CrearUsuarioForm()

    return render(
        request,
        "cuentas/crear_usuario.html",
        {
            "form": form,
        }
    )

@user_passes_test(es_superusuario, login_url="login")
def editar_usuario(request, usuario_id):
    usuario = get_object_or_404(Usuario, pk=usuario_id)

    if usuario.is_superuser:
        messages.error(request, "Las cuentas de superusuario no se pueden modificar aquí.")
        return redirect("administrar_usuarios")

    if request.method == "POST":
        # Ojo: Si el POST vino del botón de cambiar contraseña, lo diferenciamos o manejamos aparte.
        # Una forma limpia es evaluar qué form se envió:
        if "new_password1" in request.POST: # Campo característico de SetPasswordForm
            password_form = SetPasswordForm(usuario, request.POST)
            if password_form.is_valid():
                password_form.save()
                messages.success(request, f"La contraseña de {usuario.username} fue actualizada correctamente.")
                return redirect("editar_usuario", usuario_id=usuario.id)
            form = EditarUsuarioForm(instance=usuario) # Mantiene el otro form listo
        else:
            form = EditarUsuarioForm(request.POST, instance=usuario)
            password_form = SetPasswordForm(usuario)
            if form.is_valid():
                form.save()
                messages.success(request, f"El usuario {usuario.username} fue actualizado correctamente.")
                return redirect("administrar_usuarios")
    else:
        form = EditarUsuarioForm(instance=usuario)
        password_form = SetPasswordForm(usuario)

    return render(
        request,
        "cuentas/editar_usuario.html",
        {
            "form": form,
            "password_form": password_form,
            "usuario": usuario,
        }
    )
@user_passes_test(es_superusuario, login_url="login")
@require_POST
def cambiar_estado_usuario(request, usuario_id):
    usuario = get_object_or_404(Usuario, pk=usuario_id)

    if usuario.is_superuser:
        messages.error(
            request,
            "No puedes cambiar el estado de una cuenta de superusuario."
        )
    else:
        usuario.is_active = not usuario.is_active
        usuario.save(update_fields=["is_active"])

        estado = "activado" if usuario.is_active else "desactivado"
        messages.success(
            request,
            f"El usuario {usuario.username} fue {estado} correctamente."
        )

    return redirect("administrar_usuarios")

@login_required
@user_passes_test(lambda u: u.is_superuser) # Opcional: solo para superusuarios
def administrar_grupos(request):
    grupos = Group.objects.all()
    return render(request, 'cuentas/administrar_grupos.html', {'grupos': grupos})
@login_required
@user_passes_test(lambda u: u.is_superuser)
def editar_permisos_grupo(request, grupo_id):
    grupo = get_object_or_404(Group, pk=grupo_id)
    
    permisos_disponibles = Permission.objects.filter(content_type__app_label='estudiantes')

    if request.method == 'POST':
        permisos_ids = request.POST.getlist('permisos')
        grupo.permissions.set(permisos_ids)
        return redirect('administrar_grupos')

    # Traducimos los nombres de los permisos al español para la interfaz
    for permiso in permisos_disponibles:
        nombre = permiso.name
        nombre = nombre.replace('Can add', 'Puede agregar')
        nombre = nombre.replace('Can change', 'Puede modificar')
        nombre = nombre.replace('Can delete', 'Puede eliminar')
        nombre = nombre.replace('Can view', 'Puede ver')
        # Puedes añadir más reemplazos si tienes más palabras en inglés
        permiso.nombre_traducido = nombre

    return render(request, 'cuentas/editar_permisos_grupo.html', {
        'grupo': grupo,
        'permisos_disponibles': permisos_disponibles
    })
@user_passes_test(es_superusuario, login_url="login")
@require_POST
def eliminar_usuario(request, usuario_id):
    """Permite al superusuario eliminar a un usuario (con restricciones de seguridad)."""
    usuario = get_object_or_404(Usuario, pk=usuario_id)

    # Evitar que el superusuario se elimine a sí mismo
    if usuario == request.user:
        messages.error(request, "No puedes eliminar tu propia cuenta de superusuario.")
    elif usuario.is_superuser:
        messages.error(request, "No puedes eliminar cuentas de otros superusuarios desde aquí.")
    else:
        nombre = usuario.username
        usuario.delete()
        messages.success(request, f"El usuario {nombre} fue eliminado correctamente.")

    return redirect("administrar_usuarios")


@user_passes_test(es_superusuario, login_url="login")
def cambiar_password_usuario(request, usuario_id):
    """Permite al superusuario cambiar la contraseña de cualquier usuario."""
    usuario = get_object_or_404(Usuario, pk=usuario_id)

    if request.method == "POST":
        # SetPasswordForm no pide la contraseña anterior (ideal para administradores)
        form = SetPasswordForm(usuario, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f"La contraseña del usuario {usuario.username} fue actualizada correctamente.")
            return redirect("administrar_usuarios")
    else:
        form = SetPasswordForm(usuario)

    return render(
        request, 
        "cuentas/cambiar_password.html", 
        {"form": form, "usuario": usuario}
    )