from django.db import models


class Producto(models.Model):
    id = models.CharField(primary_key=True, max_length=20)
    nombre = models.CharField(max_length=100)
    detalle = models.CharField(max_length=200, default='')
    descripcion = models.TextField(default='')
    precio = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    imagen = models.CharField(max_length=255, default='/static/images/default.jpg')
    eliminado = models.BooleanField(default=False)
    stock = models.IntegerField(default=0)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre


class Noticia(models.Model):
    id = models.CharField(primary_key=True, max_length=20)
    titulo = models.CharField(max_length=200)
    fecha = models.CharField(max_length=50, default='')
    extracto = models.TextField(default='')
    imagen = models.CharField(max_length=255, default='/static/images/default.jpg')
    eliminado = models.BooleanField(default=False)

    def __str__(self):
        return self.titulo