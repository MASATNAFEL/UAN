from django import forms
from .models import Estudiante

class FormularioEstudiante(forms.ModelForm):
    class Meta:
         model= Estudiante
         fields=["cedula_ciudadania","nombre","tipocc","rdoc","programa","codcarpeta","contacto","email"]