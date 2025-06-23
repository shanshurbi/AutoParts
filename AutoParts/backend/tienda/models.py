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
    precio_mayorista = models.PositiveIntegerField(default=1)
    descripcion = models.CharField(max_length=500)
    stock =  models.PositiveIntegerField()
    imagen = models.ImageField(upload_to='productos/', null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    marca = models.ManyToManyField(Marca, related_name='productos')
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='productos')
    peso = models.DecimalField( max_digits=5, decimal_places=2)
    largo = models.PositiveIntegerField()
    ancho = models.PositiveIntegerField()
    alto = models.PositiveIntegerField()
    

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
    precio = models.PositiveIntegerField(default=1) 

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"
    
    def subtotal(self):
        return self.precio * self.cantidad 
    

class PerfilUsuario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    trabajador = models.BooleanField(default=False)
    empresa = models.BooleanField(db_default=False)
    telefono = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.user.username
    

class Pedido(models.Model):
    order_id = models.CharField(max_length=26, unique=True)  # ID alfanumérico para Transbank
    email = models.EmailField()
    monto = models.PositiveIntegerField()
    estado = models.CharField(max_length=20, default="pendiente")  # puede ser: pendiente, pagado, fallido, etc.
    fecha = models.DateTimeField(auto_now_add=True)
    retiro_en_tienda = models.BooleanField( default=False)
    envio_domicilio = models.BooleanField( default=False )
    direccion = models.CharField(max_length=225, blank=True, null=True)
    comuna = models.CharField(max_length=100, blank=True, null=True)
    region = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Pedido {self.order_id} - {self.email} - {self.estado}"