from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from .forms import CrearUsuarioForm
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from .forms import EditarUsuarioForm

Usuario = get_user_model()

def login_view(request):
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

    # No permitir modificar cuentas de superusuario
    # desde este módulo.
    if usuario.is_superuser:
        messages.error(
            request,
            "Las cuentas de superusuario no se pueden modificar aquí."
        )
        return redirect("administrar_usuarios")

    if request.method == "POST":
        form = EditarUsuarioForm(request.POST, instance=usuario)

        if form.is_valid():
            form.save()
            messages.success(
                request,
                f"El usuario {usuario.username} fue actualizado correctamente."
            )
            return redirect("administrar_usuarios")
    else:
        form = EditarUsuarioForm(instance=usuario)

    return render(
        request,
        "cuentas/editar_usuario.html",
        {
            "form": form,
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
