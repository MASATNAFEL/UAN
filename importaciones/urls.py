from django.urls import path
from . import views

urlpatterns = [
    path("",views.subir_excel,name="subirarchivo"),
    path("importacion/errores/", views.ver_errores_importacion, name="ver_errores_importacion"),
]