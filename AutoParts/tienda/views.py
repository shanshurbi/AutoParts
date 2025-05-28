from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authentication import TokenAuthentication

from django.shortcuts import render
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django_filters.rest_framework import DjangoFilterBackend

from .models import Producto, Vehiculo, Categoria
from .serializers import ProductoSerializer, VehiculoSerializer
from .filters import ProductoFiltro


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