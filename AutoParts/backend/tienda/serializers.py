from rest_framework import serializers
from .models import Producto, Marca, Categoria, Vehiculo, Carrito, CarritoItem

class ProductoSerializer(serializers.ModelSerializer):
    imagen = serializers.ImageField(required=False)
    marca = serializers.PrimaryKeyRelatedField(queryset=Marca.objects.all(), many=True)
    categoria = serializers.PrimaryKeyRelatedField(queryset=Categoria.objects.all())
    
    nombre_categoria = serializers.SerializerMethodField()
    nombre_marcas = serializers.SerializerMethodField()

    class Meta:
        model = Producto
        fields = [
            'id', 'nombre', 'precio', 'descripcion', 'stock', 'imagen',
            'marca', 'categoria', 'fecha_creacion',
            'nombre_categoria', 'nombre_marcas'
        ]

    def get_nombre_categoria(self, obj):
        return obj.categoria.nombre if obj.categoria else None

    def get_nombre_marcas(self, obj):
        return [marca.nombre for marca in obj.marca.all()]
    
class MarcaSerializer(serializers.ModelSerializer):
    class  Meta:
        model = Marca
        fields = '__all__'

class CategoriaSerializer(serializers.Serializer):
    class Meta:
        model = Categoria
        fields = '__all__'

class VehiculoSerializer(serializers.Serializer):
    producto = ProductoSerializer()
    marca = MarcaSerializer()

    class Meta:
        model = Vehiculo
        fields = '__all__'

class CarritoItemSerializer(serializers.ModelSerializer):
    producto = ProductoSerializer(read_only=True)

    class Meta:
        model = CarritoItem
        fields = ['id', 'producto', 'cantidad']

class CarritoSerializer(serializers.ModelSerializer):
    items = CarritoItemSerializer(many=True, read_only=True)

    class Meta:
        model = Carrito
        fields = ['id', 'user', 'is_active', 'items']