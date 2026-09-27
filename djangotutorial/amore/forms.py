from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Producto

INPUT_STYLE = "padding:0.85rem 1rem;border:1px solid var(--line);font-family:inherit;font-size:1rem;width:100%;"


class RegistroForm(UserCreationForm):
    """
    Formulario de registro público. Los usuarios que se crean por acá
    quedan SIEMPRE con is_staff=False e is_superuser=False (ver save()),
    así que pueden loguearse y votar/comentar, pero no administrar el
    catálogo de productos — eso sigue reservado a cuentas staff creadas
    desde /admin/.
    """

    email = forms.EmailField(required=False, label="Correo electrónico (opcional)")

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]
        labels = {
            "username": "Nombre de usuario",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({"style": INPUT_STYLE})

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_staff = False
        user.is_superuser = False
        if commit:
            user.save()
        return user


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ["nombre", "tipo", "descripcion", "precio", "disponible"]
        widgets = {
            "nombre": forms.TextInput(attrs={"style": INPUT_STYLE, "placeholder": "Ej: Ramo Eterno de Rosas"}),
            "tipo": forms.Select(attrs={"style": INPUT_STYLE}),
            "descripcion": forms.Textarea(attrs={"style": INPUT_STYLE + "resize:vertical;", "rows": 4}),
            "precio": forms.NumberInput(attrs={"style": INPUT_STYLE, "step": "0.01", "min": "0"}),
            "disponible": forms.CheckboxInput(),
        }
        labels = {
            "nombre": "Nombre del producto",
            "tipo": "Tipo de producto",
            "descripcion": "Descripción",
            "precio": "Precio (CLP)",
            "disponible": "¿Disponible para la venta?",
        }

    def clean_precio(self):
        precio = self.cleaned_data["precio"]
        if precio <= 0:
            raise forms.ValidationError("El precio debe ser mayor a 0.")
        return precio
