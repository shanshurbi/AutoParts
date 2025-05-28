from rest_framework import serializers
from .models import Producto, Marca, Categoria, Vehiculo, Cliente, Carrito

class ProductoSerializer(serializers.ModelSerializer):
    marca = serializers.StringRelatedField(many=True)
    categoria = serializers.StringRelatedField()
    
    class Meta: 
        model = Producto
        fields = '__all__'
    
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