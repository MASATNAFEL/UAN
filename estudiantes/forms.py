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
         exclude = ['fecha_registro', 'fecha_actualizacion']
         widgets={
              "rdoc":forms.CheckboxInput(),
              }
         labels={
              "cedula_ciudadania":"No. de documento",
               "nombre":"Nombre completo",
               "tipocc":"Tipo de documento",
               "rdoc":"Registro de documento",
               "contacto":"Teléfono",
               "email":"Correo electrónico"
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
         exclude = ['fecha_registro', 'fecha_actualizacion']
         widgets={
          'modelo': forms.Select(choices=[
                ('presencial', 'presencial'),
                ('virtual', 'virtual'),
                ('a distancia', 'a distancia'),])
         }
         labels = {
              "codcarpeta":"Codigo de carpeta",
              "estudiante":"Estudiante",
              "year_start":"Año de inicio",
              "year_end":"Año de finalización",
              "notas":"Notas",
              "mat_sem":"Matrícula semestral",
              "rec_pago":"Recibo de pago",
              "folio":"Folio",
              "modelo":"Modalidad",
              "observa":"Observaciones"}
           
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
          año_inicio= cleaned_data.get("year_start")
          año_fin = cleaned_data.get("year_end")
          if año_inicio and año_fin:
               if int(año_fin) < int(año_inicio):
                    raise forms.ValidationError("El año de finalización no puede ser menor que el año de inicio.")
          return cleaned_data
class FormularioCarpetae(forms.ModelForm):
     class Meta:
         model= Carpeta
         exclude = ['fecha_registro', 'fecha_actualizacion',"codcarpeta","estudiante","activo"]
         widgets={
                   'modelo': forms.Select(choices=[
                         ('presencial', 'presencial'),
                         ('virtual', 'virtual'),
                         ('a distancia', 'a distancia'),])
                  }
         labels = {
                       "codcarpeta":"Codigo de carpeta",
                       "estudiante":"Estudiante",
                       "year_start":"Año de inicio",
                       "year_end":"Año de finalización",
                       "notas":"Notas",
                       "mat_sem":"Matrícula semestral",
                       "rec_pago":"Recibo de pago",
                       "folio":"Folio",
                       "modelo":"Modalidad",
                       "observa":"Observaciones"}
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
          año_inicio= cleaned_data.get("year_start")
          año_fin = cleaned_data.get("year_end")
          if año_inicio and año_fin:
               if int(año_fin) < int(año_inicio):
                    raise forms.ValidationError("El año de finalización no puede ser menor que el año de inicio.")
          return cleaned_data

class FormularioEstudianta(forms.ModelForm):
     """
    Formulario utilizado para registrar y actualizar estudiantes.

    Los campos de auditoría y estado se excluyen del formulario para
    evitar que el usuario modifique directamente la información
    administrada por el sistema.
    """
     class Meta:
         model= Estudiante
         exclude = ['fecha_registro', 'fecha_actualizacion', "cedula_ciudadania","activo"]
         widgets={
              "rdoc":forms.CheckboxInput(),
              }
         labels={
              "cedula_ciudadania":"No. de documento",
               "nombre":"Nombre completo",
               "tipocc":"Tipo de documento",
               "rdoc":"Registro de documento",
               "contacto":"Teléfono",
               "email":"Correo electrónico",
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

class CargaExcelForm(forms.Form):
    archivo = forms.FileField(
        label="Selecciona el archivo Excel"
    )

    def clean_archivo(self):
        archivo = self.cleaned_data["archivo"]

        if not archivo.name.lower().endswith(".xlsx"):
            raise forms.ValidationError(
                "Debes subir un archivo Excel .xlsx"
            )

        if archivo.size > 5 * 1024 * 1024:
            raise forms.ValidationError(
                "El archivo no puede superar los 5 MB."
            )

        return archivo

class FormularioCarpetb(forms.ModelForm):
     class Meta:
         model= Carpeta
         exclude = ['fecha_registro', 'fecha_actualizacion',"estudiante","activo"]
         widgets={
                   'modelo': forms.Select(choices=[
                         ('presencial', 'presencial'),
                         ('virtual', 'virtual'),
                         ('a distancia', 'a distancia'),])
                  }
         labels = {
                       "codcarpeta":"Codigo de carpeta",
                       "estudiante":"Estudiante",
                       "year_start":"Año de inicio",
                       "year_end":"Año de finalización",
                       "notas":"Notas",
                       "mat_sem":"Matrícula semestral",
                       "rec_pago":"Recibo de pago",
                       "folio":"Folio",
                       "modelo":"Modalidad",
                       "observa":"Observaciones"}
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
          año_inicio= cleaned_data.get("year_start")
          año_fin = cleaned_data.get("year_end")
          if año_inicio and año_fin:
               if int(año_fin) < int(año_inicio):
                    raise forms.ValidationError("El año de finalización no puede ser menor que el año de inicio.")
          return cleaned_data
