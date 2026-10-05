from django import forms
from .models import Usuario


class UsuarioForm(forms.ModelForm):
    usuario = forms.CharField(
        max_length=20,
        min_length=1,
        error_messages={'max_length': 'El usuario no puede superar 20 caracteres.'}
    )
    email = forms.EmailField(
        error_messages={'invalid': 'Ingrese un email válido.'}
    )

    class Meta:
        model = Usuario
        fields = ['usuario', 'contraseña', 'dirección', 'email', 'historial', 'admin']
        widgets = {
            'contraseña': forms.PasswordInput(),
        }

    def clean_usuario(self):
        usuario = self.cleaned_data.get('usuario', '').strip()
        if len(usuario) > 20:
            raise forms.ValidationError('El usuario no puede superar 20 caracteres.')
        return usuario

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip()
        if not email:
            raise forms.ValidationError('El email es obligatorio.')
        return email
