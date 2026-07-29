from django import forms
from .models import Estudiante

class FormularioEstudiante(forms.ModelForm):
    class Meta:
         model= Estudiante
         fields = '__all__'
         widgets = {
             'rdoc': forms.CheckboxInput(),
             'activo': forms.HiddenInput(),
         }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():

            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'form-check-input'
            else:
                field.widget.attrs['class'] = 'form-control'