from django.contrib import admin
from .models import Producto,Categoria, Marca, Carrito
# Register your models here.

admin.site.register(Producto)
admin.site.register(Categoria)
admin.site.register(Marca)
admin.site.register(Carrito)

admin.site.unregister(Producto)
admin.site.unregister(Carrito)

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio', 'fecha_creacion')
    readonly_fields = ('fecha_creacion',)

@admin.register(Carrito)
class CarritoAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'creado', 'is_active')
    list_filter = ('is_active', 'creado')
    search_fields = ('user__username',)