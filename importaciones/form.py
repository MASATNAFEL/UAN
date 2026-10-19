from django import forms


class ImportarExcelForm(forms.Form):
    archivo = forms.FileField(
        label="Archivo Excel",
        help_text="Selecciona un archivo .xlsx",
    )

    def clean_archivo(self):
        archivo = self.cleaned_data["archivo"]

        if not archivo.name.lower().endswith(".xlsx"):
            raise forms.ValidationError(
                "Debes seleccionar un archivo Excel .xlsx."
            )

        if archivo.size > 10 * 1024 * 1024:
            raise forms.ValidationError(
                "El archivo no puede superar los 10 MB."
            )

        return archivo