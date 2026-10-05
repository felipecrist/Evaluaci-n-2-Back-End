from django.shortcuts import render, redirect
import re
from .forms import UsuarioForm
from .models import Usuario


def _ensure_default_admin():
    if not Usuario.objects.filter(usuario='admin').exists():
        Usuario.objects.create(
            usuario='admin',
            contraseña='admin',
            dirección='Oficina',
            email='admin@example.com',
            historial=[],
            admin=True,
        )


def _usuario_actual(request):
    usuario_sesion = request.session.get('usuario')
    if not usuario_sesion:
        return None
    try:
        return Usuario.objects.get(usuario=usuario_sesion)
    except Usuario.DoesNotExist:
        return None


def usuarios(request):
    _ensure_default_admin()
    msg = ''
    aviso_login = request.session.pop('aviso_login', '')
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'register':
            form = UsuarioForm(request.POST)
            username = request.POST.get('username', '').strip()
            password = request.POST.get('password', '').strip()
            address = request.POST.get('address', '').strip()
            email = request.POST.get('email', '').strip()

            if not username or not password:
                msg = 'Usuario y contraseña son obligatorios.'
            elif len(username) > 20:
                msg = 'El usuario no puede superar 20 caracteres.'
            elif not re.match(r'^\S+@\S+\.\S+$', email):
                msg = 'Formato de email inválido.'
            elif Usuario.objects.filter(email=email).exists():
                msg = 'El email ya está registrado.'
            elif Usuario.objects.filter(usuario=username).exists():
                msg = 'El usuario ya existe.'
            elif form.is_valid():
                Usuario.objects.create(
                    usuario=form.cleaned_data['usuario'],
                    contraseña=form.cleaned_data['contraseña'],
                    dirección=form.cleaned_data['dirección'] if 'dirección' in form.cleaned_data else '',
                    email=form.cleaned_data['email'],
                    historial=[],
                    admin=False,
                )
                msg = 'Cuenta creada correctamente. Ya puedes iniciar sesión.'
            else:
                msg = form.errors.get('__all__', ['Datos inválidos'])[0] if form.errors else 'Datos inválidos.'
        elif action == 'login':
            username = request.POST.get('username', '').strip()
            password = request.POST.get('password', '').strip()
            usuario = Usuario.objects.filter(usuario=username, contraseña=password).first()
            if usuario:
                request.session['usuario'] = username
                return redirect('/')
            msg = 'Usuario o contraseña incorrectos.'
        elif action == 'logout':
            request.session.pop('usuario', None)
            return redirect('/')

    usuario_actual = _usuario_actual(request)
    return render(request, 'usuario.html', {'msg': msg, 'usuario': usuario_actual, 'USUARIOS': Usuario.objects.all(), 'aviso_login': aviso_login})