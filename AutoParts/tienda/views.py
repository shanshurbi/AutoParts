from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.authtoken.models import Token

from django.shortcuts import render
from django.contrib.auth import authenticate
from .models import Producto
from .serializers import ProductoSerializer
# Create your views here.

def lista_productos(request):
    productos = Producto.objects.all()
    return render(request,'productos.html', {'productos':productos})

class ProductoAPIView(APIView):
    def get(self, request):
        productos = Producto.objects.all()
        serializer = ProductoSerializer(productos, many=True)
        return Response(serializer.data)
    
class HomeView(APIView):
    def get (self, request):
        return render (request, 'home.html')

class LoginView(APIView):
    def get (self, request):
        usuario = request.data.get('usuario')
        contraseña = request.data.get('contraseña')

        usuario = authenticate(usuario=usuario, contraseña=contraseña)
        if usuario is not None:
            token, created = Token.objects.get_or_create(usuario=usuario)
            return Response({'token':token.key}, status=status.HTTP_200_OK)
        return Response({'error': 'Usuario o contraseña incorrectos'}, status=status.HTTP_401_UNAUTHORIZED)
    
def login_page(request):
    return render(request, 'login.html')