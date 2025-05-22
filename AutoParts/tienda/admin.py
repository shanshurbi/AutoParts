from django.contrib import admin
from .models import Producto,Categoria
# Register your models here.

admin.site.register(Producto)
admin.site.register(Categoria)

admin.site.unregister(Producto)

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio', 'fecha_creacion')
    readonly_fields = ('fecha_creacion',)