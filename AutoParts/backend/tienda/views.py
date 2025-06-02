from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status, permissions
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.authentication import TokenAuthentication
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import api_view
from django.contrib.auth import login
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from .models import Producto, Vehiculo, Categoria, Carrito, CarritoItem, PerfilUsuario
from .serializers import ProductoSerializer, VehiculoSerializer
from django.contrib.auth import logout
import re, os

# Create your views here.

def lista_productos(request):
    productos = Producto.objects.all()
    return render(request,'productos.html', {'productos':productos})

class ProductoAPIView(APIView):
    permission_classes = [AllowAny]  # Puedes usar permisos más restrictivos si deseas

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

    def post(self, request):
        serializer = ProductoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class HomeView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        template_dir = settings.TEMPLATES[0]['DIRS'][0]
        full_path = os.path.join(template_dir, 'home.html')
        print("Buscando template en:", full_path)
        print("¿Existe archivo?", os.path.exists(full_path))
        return render(request, 'home.html')
def cerrar_sesion(request):
    logout(request)  # Elimina la sesión del lado del servidor
    response = JsonResponse({'mensaje': 'Sesión cerrada'})
    response.delete_cookie('sessionid')  # Elimina la cookie en el navegador
    return response


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

@method_decorator(csrf_exempt, name='dispatch')
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
    permission_classes = [IsAuthenticated]

    def post(self, request, producto_id):
        user = request.user

        carrito, created = Carrito.objects.get_or_create(user=user, is_active=True)

        print("=== DEBUG ELIMINAR PRODUCTO DEL CARRITO ===")
        print("Usuario autenticado:", user.username)
        print("Producto ID recibido:", producto_id)
        print("Carrito ID:", carrito.id)
        print("Items en el carrito del usuario:")
        for item in CarritoItem.objects.filter(carrito=carrito):
            print(f" - Producto ID: {item.producto.id}, Nombre: {item.producto.nombre}, Cantidad: {item.cantidad}")

        try:
            item = CarritoItem.objects.get(carrito=carrito, producto_id=producto_id)
        except CarritoItem.DoesNotExist:
            print("⚠️ Producto no encontrado en el carrito del usuario.")
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

class TrabajadoresAdminView(APIView):
    permission_classes = [IsAdminUser]  # Solo admins

    def get(self, request):
        perfiles = PerfilUsuario.objects.select_related('user').all()
        data = []
        for perfil in perfiles:
            data.append({
                'id': perfil.user.id,
                'username': perfil.user.username,
                'email': perfil.user.email,
                'trabajador': perfil.trabajador,
                'empresa': perfil.empresa,
            })
        return Response(data)

    def patch(self, request):
        user_id = request.data.get('user_id')
        trabajador = request.data.get('trabajador')
        empresa = request.data.get('empresa')

        if user_id is None:
            return Response({'error': 'Falta user_id'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            perfil = PerfilUsuario.objects.get(user_id=user_id)
        except PerfilUsuario.DoesNotExist:
            return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        if trabajador is not None:
            perfil.trabajador = trabajador
        if empresa is not None:
            perfil.empresa = empresa

        perfil.save()
        return Response({'success': True})

def admin_required(user):
    return user.is_authenticated and user.is_staff 

@login_required
@user_passes_test(admin_required)
def gestion_page(request):
    return render(request, 'gestion_trabajadores.html')

class TrabajadorUpdateView(APIView):
    permission_classes = [IsAdminUser]

    def patch(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
            perfil = user.perfilusuario  # Relación OneToOne
        except User.DoesNotExist:
            return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        except PerfilUsuario.DoesNotExist:
            return Response({'error': 'Perfil no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        actualizado = False

        trabajador = request.data.get('trabajador')
        if trabajador is not None:
            perfil.trabajador = trabajador
            actualizado = True

        empresa = request.data.get('empresa')
        if empresa is not None:
            perfil.empresa = empresa
            actualizado = True

        if not actualizado:
            return Response({'error': 'No se proporcionó ningún campo válido'}, status=status.HTTP_400_BAD_REQUEST)

        perfil.save()
        return Response({'success': 'Estado actualizado'}, status=status.HTTP_200_OK)
    
class EsTrabajador(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and 
                    request.user.is_authenticated and 
                    hasattr(request.user, 'perfilusuario') and 
                    request.user.perfilusuario.trabajador)
    
class ProductoCrudView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [permissions.IsAuthenticated, EsTrabajador]

    def get(self, request):
        productos = Producto.objects.all()
        serializer = ProductoSerializer(productos, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request):
        serializer = ProductoSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProductoDetalleAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated, EsTrabajador]

    def get_object(self, pk):
        try:
            return Producto.objects.get(pk=pk)
        except Producto.DoesNotExist:
            return None

    def get(self, request, pk):
        producto = self.get_object(pk)
        if not producto:
            return Response({'error': 'Producto no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProductoSerializer(producto)
        return Response(serializer.data)

    def put(self, request, pk):
        producto = self.get_object(pk)
        if not producto:
            return Response({'error': 'Producto no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProductoSerializer(producto, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        producto = self.get_object(pk)
        if not producto:
            return Response({'error': 'Producto no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        producto.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    
    
def gestion_prod_page(request):
    categorias = Categoria.objects.all()
    return render(request, 'gestion_productos.html', {'categorias': categorias})

class TokenDesdeSesionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        token, created = Token.objects.get_or_create(user=request.user)
        return Response({'token': token.key})
    
from django.contrib.auth import login  # Asegúrate de tener esto importado

@csrf_exempt
def login_con_sesion(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)  # ← esto crea la sesión
            return redirect('/')  # redirige donde quieras
        else:
            return render(request, 'login.html', {'error': 'Credenciales inválidas'})

    return render(request, 'login.html')
def cerrar_sesion(request):
    logout(request)
    return render(request, 'logout.html')

@api_view(['GET'])
def login_from_session(request):
    if not request.user.is_authenticated:
        return Response({'detail': 'Sesión no activa'}, status=401)

    # Si quieres que genere un token cuando el usuario sigue autenticado por sesión:
    # Aquí podrías devolver el token, pero solo si lo necesitas.
    return Response({'detail': 'Sesión activa pero no se generará token'}, status=403)