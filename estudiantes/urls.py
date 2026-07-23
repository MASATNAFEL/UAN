from django.urls import path
from . import views


urlpatterns = [
    path("", views.index, name="index"),
    path("info/<str:cedula_ciudadania>/", views.informacion, name="informacion"),
    path("buscar/", views.buscar, name="buscar"),
]