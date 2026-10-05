from django.db import models


class Usuario(models.Model):
    usuario = models.CharField(max_length=20, unique=True)
    contraseña = models.CharField(max_length=128)
    dirección = models.CharField(max_length=200, blank=True, default='')
    email = models.EmailField(unique=True)
    historial = models.JSONField(default=list, blank=True)
    admin = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.usuario