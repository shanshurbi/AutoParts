from django.contrib.auth.models import User
from django.db import models
from django.conf import settings

# Create your models here.
    
class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=500, blank=True, null=True)
    activa = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre
    
class Marca(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=500)
    logo = models.ImageField(upload_to='logos', blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    precio = models.PositiveIntegerField(default=1)
    descripcion = models.CharField(max_length=500)
    stock =  models.PositiveIntegerField()
    imagen = models.ImageField(upload_to='productos/', null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    marca = models.ManyToManyField(Marca, related_name='productos')
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='productos')
    

    def __str__(self):
        return self.nombre
    
class Vehiculo(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    marca = models.ForeignKey(Marca, on_delete=models.CASCADE)
    modelo_auto = models.CharField(max_length=100)
    año_desde = models.IntegerField()
    año_hasta = models.IntegerField()

    def __str__(self):
        return f"{self.producto.nombre} - {self.marca.nombre} {self.modelo_auto} ({self.año_desde}-{self.año_hasta})"
    
class Cliente(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    telefono = models.CharField(max_length=20, blank=True)
    direccion = models.TextField(blank=True)

class Carrito(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True)
    creado = models.DateTimeField(auto_now_add=True)  
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Carrito de {self.user.username} - Activo {self.is_active}"
    
class CarritoItem(models.Model):
    carrito = models.ForeignKey(Carrito, related_name='items', on_delete=models.CASCADE)
    producto = models.ForeignKey('Producto', on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"
    
    def subtotal(self):
        return self.producto.precio * self.cantidad

