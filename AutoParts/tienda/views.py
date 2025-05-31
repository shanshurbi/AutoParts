from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authentication import TokenAuthentication, SessionAuthentication

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.http import JsonResponse

from .models import Producto, Vehiculo, Categoria, Carrito, CarritoItem
from .serializers import ProductoSerializer, VehiculoSerializer

import re

# Create your views here.

def lista_productos(request):
    productos = Producto.objects.all()
    return render(request,'productos.html', {'productos':productos})

class ProductoAPIView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        productos = Producto.objects.all()
        categoria_id = request.GET.get("categoria")
        orden = request.GET.get("orden")

        if categoria_id:
            productos = productos.filter(categoria_id=categoria_id)

        if orden == "precio_asc":
            productos = productos.order_by("precio")
        elif orden == "precio_desc":
            productos = productos.order_by("-precio")
        elif orden == "nombre_asc":
            productos = productos.order_by("nombre")
        elif orden == "nombre_desc":
            productos = productos.order_by("-nombre")

        serializer = ProductoSerializer(productos, many=True)
        return Response(serializer.data)
    
class HomeView(APIView):
    permission_classes = [AllowAny]
    def get (self, request):
        return render (request, 'home.html')

class LoginView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):  
        email = request.data.get('usuario')  
        password = request.data.get('contraseña')
        if not email or not password:
            return Response({'error': 'Faltan datos'}, status=status.HTTP_400_BAD_REQUEST)
        user = authenticate(request, username=email, password=password)
        if user is not None:
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=status.HTTP_200_OK)
        return Response({'error': 'Usuario o contraseña incorrectos'}, status=status.HTTP_401_UNAUTHORIZED)
    
def login_page(request):
    return render(request, 'login.html')

class VehiculoView(APIView):
    def get(self, request):
        compatibles = Vehiculo.objects.all()
        serializer = VehiculoSerializer(compatibles, many=True)
        return Response(serializer.data)
    
def catalogo_view(request):
    categoria_id = request.GET.get('categoria')

    productos = Producto.objects.all()
    if categoria_id:
        productos = productos.filter(categoria_id=categoria_id)

    categorias = Categoria.objects.all()

    return render(request, 'catalogo.html', {
        'productos': productos,
        'categorias': categorias,
    })

class RegistroView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        username = request.data.get('usuario')
        password = request.data.get('contraseña')
        email = request.data.get('email')

        if not username or not password or not email:
            return Response({'error': 'Faltan datos'}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(username=username).exists():
            return Response({'error': 'Usuario ya existte'}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(email=email).exists():
            return Response({'error': 'El correo electrónico ya está en uso'}, status=status.HTTP_400_BAD_REQUEST)
        if not re.search(r'[A-Z]', password):
            return Response({'error': 'La contraseña debe contener al menos una letra mayúscula'}, status=status.HTTP_400_BAD_REQUEST)
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return Response({'error': 'La contraseña debe contener al menos un símbolo'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = User.objects.create_user(username=username, password=password, email=email)
        token = Token.objects.create(user=user)
        return Response({'token': token.key}, status=status.HTTP_201_CREATED)
    
def registro_page(request):
    return render(request, 'registro.html')

class PerfilUsuarioView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        print(request.headers)

        user = request.user 
        return Response({
            'usuario': user.username,
            'email': user.email
        })

def perfil_page(request):
    return render(request, 'perfil.html')

def detalle_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    return render(request, 'detalle.html', {'producto': producto})

class CarritoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        carrito, created = Carrito.objects.get_or_create(user=request.user, is_active=True)
        items = CarritoItem.objects.filter(carrito=carrito)
        data = [
            {
                "producto": item.producto.nombre,
                "producto_id": item.producto.id,
                "cantidad": item.cantidad,
                "precio": item.producto.precio,
            }
            for item in items
        ]
        return Response({"carrito": data})
    
class AgregarCarritoView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        producto_id = request.data.get('producto_id')
        cantidad = request.data.get('cantidad', 1)

        if not producto_id:
            return Response({'error': 'Falta producto_id'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            producto = Producto.objects.get(id=producto_id)
        except Producto.DoesNotExist:
            return Response({'error': 'Producto no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        
        carrito, created = Carrito.objects.get_or_create(user=user, is_active=True)

        carrito_item, created = CarritoItem.objects.get_or_create(carrito=carrito, producto=producto)
        if not created:
            carrito_item.cantidad += int(cantidad)
            carrito_item.save()
        
        return Response({'message': 'Producto agregado al carrito'}, status=status.HTTP_200_OK)
    
class RemoverDelCarritoView(APIView):
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, producto_id):
        user = request.user
        carrito, created = Carrito.objects.get_or_create(user=user, is_active=True)

        try:
            item = CarritoItem.objects.get(carrito=carrito, producto_id=producto_id)
        except CarritoItem.DoesNotExist:
            return Response({'error': 'El producto no está en el carrito'}, status=status.HTTP_404_NOT_FOUND)

        if item.cantidad > 1:
            item.cantidad -= 1
            item.save()
        else:
            item.delete()

        return redirect('carrito')
    
def carrito_page(request):
    if not request.user.is_authenticated:
        return redirect('login')

    try:
        carrito = Carrito.objects.get(user=request.user, is_active=True)
        carrito_items = CarritoItem.objects.filter(carrito=carrito)
    except Carrito.DoesNotExist:
        carrito_items = []

    return render(request, 'carrito.html', {
        'carrito_items': carrito_items
    })

class CarritoContadorView(APIView):
    def get(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({'count': 0})
        
        carrito = Carrito.objects.filter(user=request.user, is_active=True).first()
        if not carrito:
            return JsonResponse({'count': 0})
        
        count = sum(item.cantidad for item in CarritoItem.objects.filter(carrito=carrito))
        return JsonResponse({'count':count})