from django.urls import path
from . import views


urlpatterns = [
    path("", views.index, name="index"),
    path("info/<str:cedula_ciudadania>/", views.informacion, name="informacion"),
    path("car/<str:codcarpeta>/", views.informacion1, name="informacion2"),
    path("info/<str:cedula_ciudadania>/edit", views.editar, name="editar"),
    path("info/<str:cedula_ciudadania>/borrar", views.borrar, name="borrar"),
    path("info/<str:codcarpeta>/borrar", views.borrar1, name="borrar1"),
    path("buscar/", views.buscar, name="buscar"),
    path("registro/", views.addestudiante, name="registro"),
    path("carpeta/", views.addcarpeta, name="carpeta"),
    
]