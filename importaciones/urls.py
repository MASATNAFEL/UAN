from django.urls import path
from . import views

urlpatterns = [
    path("",views.subir_excel,name="subirarchivo"),
    path("importacion/errores/", views.ver_errores_importacion, name="ver_errores_importacion"),
    path("descargar-plantilla/", views.descargar_plantilla_excel, name="descargar_plantilla_excel"),
    path("descargar-errores/", views.descargar_errores_excel, name="descargar_errores_excel"),
]