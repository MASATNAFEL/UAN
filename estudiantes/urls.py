from django.urls import path
from . import views


urlpatterns = [
    path("", views.index, name="index"),
    path("info/<str:cedula_ciudadania>/", views.informacion, name="informacion"),
    path("car/<str:codcarpeta>/", views.inforcarpeta, name="infocarpeta"),
    path("info/<str:cedula_ciudadania>/edit", views.editar, name="editar"),
    path("car/<str:codcarpeta>/edit", views.modificar, name="modificar"),
     
    path("buscar/", views.buscar, name="buscar"),
    path("consultar/", views.consultar, name="consultar"),
    path("registro/", views.addestudiante, name="registro"),
    path("carpeta/", views.addcarpeta, name="carpeta"),
    
]