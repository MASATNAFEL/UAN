from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group

Usuario = get_user_model()


class CrearUsuarioForm(UserCreationForm):
    first_name = forms.CharField(
        label="Nombres",
        max_length=150,
        required=False
    )

    last_name = forms.CharField(
        label="Apellidos",
        max_length=150,
        required=False
    )

    email = forms.EmailField(
        label="Correo electrónico",
        required=False
    )

    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all().order_by("name"),
        label="Grupos y permisos",
        required=False,
        widget=forms.CheckboxSelectMultiple
    )

    class Meta(UserCreationForm.Meta):
        model = Usuario
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "groups",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["username"].label = "Nombre de usuario"
        self.fields["password1"].label = "Contraseña"
        self.fields["password2"].label = "Confirmar contraseña"
class EditarUsuarioForm(forms.ModelForm):
    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all().order_by("name"),
        label="Grupos y permisos",
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = Usuario
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "groups",
            "is_active",
        ]
        labels = {
            "username": "Nombre de usuario",
            "first_name": "Nombres",
            "last_name": "Apellidos",
            "email": "Correo electrónico",
            "is_active": "Cuenta activa",
        }
        widgets = {
            "username": forms.TextInput(attrs={
                "class": "form-control",
            }),
            "first_name": forms.TextInput(attrs={
                "class": "form-control",
            }),
            "last_name": forms.TextInput(attrs={
                "class": "form-control",
            }),
            "email": forms.EmailInput(attrs={
                "class": "form-control",
            }),
            "is_active": forms.CheckboxInput(attrs={
                "class": "form-check-input",
            }),
        }