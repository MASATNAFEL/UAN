from django import forms
from .models import Estudiante

class FormularioEstudiante(forms.ModelForm):
    class Meta:
         model= Estudiante
         fields='__all__'
         widgets={
              "rdoc":forms.CheckboxInput(),
              "activo":forms.HiddenInput(),
              }
    def __init__(self, *args, **kwargs):
         super().__init__(*args, **kwargs)
         # Recorre automáticamente solo los campos que REALMENTE existen en tu modelo
         for field_name, field in self.fields.items():
              field.widget.attrs['class']='form-control'