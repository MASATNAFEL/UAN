from django.urls import path
from . import views

app_name= "estudiantes"
urlpatterns = [
    path("", views.index, name="index"),
    path("<cedula>/", views.detalles, name="detalles"),

]