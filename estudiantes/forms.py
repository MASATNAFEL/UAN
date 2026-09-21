from django import forms
from .models import Estudiante,Carpeta

class FormularioEstudiante(forms.ModelForm):
     """
    Formulario utilizado para registrar y actualizar estudiantes.

    Los campos de auditoría y estado se excluyen del formulario para
    evitar que el usuario modifique directamente la información
    administrada por el sistema.
    """
     class Meta:
         model= Estudiante
         exclude = ['fecha_registro', 'fecha_actualizacion', 'activo']
         widgets={
              "rdoc":forms.CheckboxInput(),
              }
     def __init__(self, *args, **kwargs):
          super().__init__(*args, **kwargs)
          # Recorre automáticamente solo los campos que REALMENTE existen en tu modelo
          for field_name, field in self.fields.items():
               field.widget.attrs['class']='form-control'
     def clean_contacto(self):
          """
          Valida que el número de contacto contenga únicamente dígitos.
          """
          contacto = self.cleaned_data["contacto"]
          if not contacto.isdigit():
               raise forms.ValidationError("El contacto debe contener únicamente números.")
          return contacto
     def clean_nombre(self):
          nombre = self.cleaned_data["nombre"]
          if not nombre.replace(" ", "").isalpha():
               raise forms.ValidationError("El nombre solo debe contener letras.")
          return nombre
     def clean_cedula_ciudadania(self):
          cedula = self.cleaned_data["cedula_ciudadania"]
          if not cedula.isdigit():
               raise forms.ValidationError("La cédula debe contener únicamente números.")
          return cedula
class FormularioCarpeta(forms.ModelForm):
     class Meta:
         model= Carpeta
         exclude = ['fecha_registro', 'fecha_actualizacion', 'activo']
         
     def __init__(self, *args, **kwargs):
         super().__init__(*args, **kwargs)
         # Recorre automáticamente solo los campos que REALMENTE existen en tu modelo
         for field_name, field in self.fields.items():
              field.widget.attrs['class']='form-control'
     def clean_year_start(self):
          year = self.cleaned_data["year_start"]
          if not year.isdigit() or len(year) != 4:
               raise forms.ValidationError("El año debe tener exactamente 4 dígitos.")
          return year
     def clean(self):
          cleaned_data = super().clean()
          year_start = cleaned_data.get("year_start")
          year_end = cleaned_data.get("year_end")
          if year_start and year_end:
               if int(year_end) < int(year_start):
                    raise forms.ValidationError("El año de finalización no puede ser menor que el año de inicio.")
          return cleaned_data
