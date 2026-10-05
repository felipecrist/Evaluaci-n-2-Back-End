from django.contrib import admin
from .models import Producto,Noticia


# Register your models here.
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('id','nombre', 'descripcion', 'precio', 'stock')
class NoticiaAdmin(admin.ModelAdmin):
    list_display = ('id','titulo', 'fecha', 'extracto')


admin.site.register(Producto, ProductoAdmin)
admin.site.register(Noticia, NoticiaAdmin)