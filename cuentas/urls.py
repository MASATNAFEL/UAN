from django.urls import path
from . import views

urlpatterns = [
    path("", views.login_view, name="login"),
    path("login/",views.login_view,name="login"),
    path("logout/",views.logout_view,name="logout"),
    path("home", views.home,name="home"),
    path("usuarios/",views.administrar_usuarios,name="administrar_usuarios"),
    path("usuarios/crear/",views.crear_usuario,name="crear_usuario"),
    path("usuarios/<int:usuario_id>/editar/",views.editar_usuario,name="editar_usuario"),
    path("usuarios/<int:usuario_id>/estado/",views.cambiar_estado_usuario,name="cambiar_estado_usuario"),
    path("grupos/", views.administrar_grupos, name="administrar_grupos"),
    path("grupos/<int:grupo_id>/permisos/", views.editar_permisos_grupo, name="editar_permisos_grupo"),
]