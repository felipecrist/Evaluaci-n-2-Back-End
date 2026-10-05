from django.contrib import admin
from .models import Usuario


class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'email', 'dirección', 'fecha_creacion')


admin.site.register(Usuario, UsuarioAdmin)