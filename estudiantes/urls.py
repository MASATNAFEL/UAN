from django.urls import path
from . import views


urlpatterns = [
    # Página principal
    path("", views.index, name="index"),
    # Consulta de información
    path("info/<str:cedula_ciudadania>/", views.informacion, name="informacion"),
    path("car/<int:codcarpeta>/", views.infocarpeta, name="infocarpeta"),
    # Actualización
    path("info/<str:cedula_ciudadania>/edit/", views.editar, name="editar"),
    path("car/<int:codcarpeta>/edit/", views.modificar, name="modificar"),
    # Borrado
    path("info/<str:cedula_ciudadania>/borrar/", views.borrar, name="borrar"),
    path("car/<int:codcarpeta>/borrar", views.eliminar, name="eliminar"),
    # Busqueda
    path("buscar/", views.buscar, name="buscar"),
    path("consultar/", views.consultar, name="consultar"),
    # Registro
    path("registro/", views.addestudiante, name="registro"),
    path("carpeta/", views.addcarpeta, name="carpeta"),
    
]