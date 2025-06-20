from pyexpat.errors import messages
import uuid
from django.urls import reverse
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status, permissions
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.authentication import TokenAuthentication
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import login
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from transbank.webpay.webpay_plus.transaction import Transaction,WebpayOptions
from transbank.common.integration_type import IntegrationType
from .models import Pedido, Producto, Vehiculo, Categoria, Carrito, CarritoItem, PerfilUsuario
from .serializers import ProductoSerializer, VehiculoSerializer
from django.contrib.auth import logout
import re, os
import random
import string

CommerCode = '597055555532'
ApiKeySecret = '579B532A7440BB0C9079DED94D31EA1615BACEB56610332264630D42D0A36B1C'
options = WebpayOptions(CommerCode,ApiKeySecret,IntegrationType.TEST)
transaction = Transaction(options)
# Create your views here.

def lista_productos(request):
    productos = Producto.objects.all()
    return render(request,'productos.html', {'productos':productos})
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def perfil_usuario(request):
    return Response({
        "usuario": request.user.username,
        "email": request.user.email
    })
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

    def post(self, request):
        serializer = ProductoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ProductoMayoristaAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not hasattr(request.user, 'perfilusuario') or not request.user.perfilusuario.empresa:
            return Response({'error': 'Acceso restringido a cuentas mayoristas'}, status=403)

        productos = Producto.objects.all()

        data = []
        for producto in productos:
            data.append({
                "id": producto.id,
                "nombre": producto.nombre,
                "descripcion": producto.descripcion,
                "imagen": producto.imagen.url if producto.imagen else None,
                "precio_mayorista": producto.precio_mayorista,
                "stock": producto.stock,
                "categoria": producto.categoria.nombre
            })

        return Response(data)
def productos_mayoristas_page(request):
    token, _ = Token.objects.get_or_create(user=request.user)
    return render(request, 'mayorista_productos.html', {
        'token': token.key
    })
    
class HomeView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        productos = Producto.objects.all()[:8] 
        es_empresa = False
        if request.user.is_authenticated and hasattr(request.user, 'perfilusuario'):
            es_empresa = request.user.perfilusuario.empresa

        return render(request, 'home.html', {
            'productos': productos,
            'es_empresa': es_empresa,
        })
def cerrar_sesion(request):
    logout(request)  # Elimina la sesión del lado del servidor
    response = JsonResponse({'mensaje': 'Sesión cerrada'})
    response.delete_cookie('sessionid')  # Elimina la cookie en el navegador
    return response

def generar_order_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=20))

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

    es_empresa = False
    if request.user.is_authenticated and hasattr(request.user, 'perfilusuario'):
        es_empresa = request.user.perfilusuario.empresa  # o .trabajador si usas otro flag

    return render(request, 'catalogo.html', {
        'productos': productos,
        'categorias': categorias,
        'es_empresa': es_empresa,  # ← esto es importante
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
            return Response({'error': 'Usuario ya existe'}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=email).exists():
            return Response({'error': 'El correo electrónico ya está en uso'}, status=status.HTTP_400_BAD_REQUEST)

        if not re.search(r'[A-Z]', password):
            return Response({'error': 'La contraseña debe contener al menos una letra mayúscula'}, status=status.HTTP_400_BAD_REQUEST)

        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return Response({'error': 'La contraseña debe contener al menos un símbolo'}, status=status.HTTP_400_BAD_REQUEST)

        # Crear el usuario
        user = User.objects.create_user(username=username, password=password, email=email)

        # 🔥 Crear el perfil asociado
        PerfilUsuario.objects.create(user=user)  # ← Este es el paso que faltaba

        # Crear token
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
    es_empresa = False
    if request.user.is_authenticated and hasattr(request.user, 'perfilusuario'):
        es_empresa = request.user.perfilusuario.empresa
    return render(request, "detalle.html", {
        "producto": producto,
        "es_empresa": es_empresa,
    })

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
                "precio": item.precio, 
            }
            for item in items
        ]
        return Response({"carrito": data})

    
class AgregarCarritoView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        producto_id = request.data.get('producto_id')
        cantidad = int(request.data.get('cantidad', 1))

        if not producto_id:
            return Response({'error': 'Falta producto_id'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            producto = Producto.objects.get(id=producto_id)
        except Producto.DoesNotExist:
            return Response({'error': 'Producto no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        
        carrito, created = Carrito.objects.get_or_create(user=user, is_active=True)

        # DETERMINA EL PRECIO SEGÚN EL USUARIO
        if hasattr(user, 'perfilusuario') and user.perfilusuario.empresa:
            precio = producto.precio_mayorista
        else:
            precio = producto.precio

        carrito_item, created = CarritoItem.objects.get_or_create(
            carrito=carrito, producto=producto,
            defaults={'cantidad': cantidad, 'precio': precio}
        )
        if not created:
            carrito_item.cantidad += cantidad
            carrito_item.precio = precio 
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

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def aumentar_producto(request, producto_id):
    print("➡️ aumentar_producto()")
    carrito, _ = Carrito.objects.get_or_create(user=request.user, is_active=True)

    item, created = CarritoItem.objects.get_or_create(
        carrito=carrito,
        producto_id=producto_id,
        defaults={'cantidad': 1}
    )

    producto = item.producto  # Accede al producto desde el item

    if not created:
        if item.cantidad < producto.stock:
            item.cantidad += 1
            item.save()
            print(f"🟢 Cantidad actualizada: {item.cantidad}")
            return Response({"detalle": "Cantidad aumentada"})
        else:
            print("❌ No se puede aumentar: stock máximo alcanzado")
            return Response({"error": "No hay suficiente stock disponible"}, status=400)
    else:
        print("🆕 Producto agregado al carrito")
        return Response({"detalle": "Producto agregado"})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def disminuir_producto(request, producto_id):
    print("➡️ disminuir_producto()")
    item = get_object_or_404(CarritoItem, carrito__user=request.user, producto_id=producto_id)

    if item.cantidad > 1:
        item.cantidad -= 1
        item.save()
        print(f"🔽 Cantidad disminuida a: {item.cantidad}")
    else:
        item.delete()
        print("🗑️ Producto eliminado por cantidad = 0")

    return Response({"detalle": "Cantidad disminuida"})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def remover_producto(request, producto_id):
    print("➡️ remover_producto()")
    item = get_object_or_404(CarritoItem, carrito__user=request.user, producto_id=producto_id)
    item.delete()
    print("🧹 Producto eliminado del carrito")

    return Response({"detalle": "Producto eliminado"})

def pagar_transbank(request, order_id):
    cart = request.session.get("cart", [])
    user_id = request.user.get("user_id")
    cliente = request.session.get("cliente", {})
    resumen = request.session.get("resumen", {})
    session_id = f"{user_id}-{uuid.uuid4()}"
    return_url = request.build_absolute_uri(f"/carrito/confirmar/")  # Donde llegará después del pago

    if not cart or not user_id:
        return Response({"error": "Datos de sesión no encontrados"}, status=400)

    # Calcula total
    total = sum(item["precio"] * item["cantidad"] for item in cart)

    tx = Transaction()
    tx.configure_for_testing()  # ⚠️ Cambia a producción cuando estés listo

    response = tx.create(buy_order=order_id, session_id=session_id, amount=total, return_url=return_url)

    url = response["url"] + "?token_ws=" + response["token"]
    return Response({"url": url})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def crear_pedido(request):
    data = request.data
    user = request.user

    email = data.get("email")
    monto = data.get("monto")
    metodo = data.get("metodo_pago")

    if not email or not monto or not metodo:
        return Response({"error": "Faltan datos para crear el pedido"}, status=400)

    # Generar order_id válido para Transbank
    order_id = generar_order_id()

    # Crear y guardar el pedido en la base de datos
    pedido = Pedido.objects.create(
        order_id=order_id,
        email=email,
        monto=monto,
        estado="pendiente"
    )

    # Guardar información mínima en sesión para usar en el redireccionamiento
    request.session["order_id"] = order_id
    request.session["email"] = email
    request.session["monto"] = monto
    request.session["metodo_pago"] = metodo
    request.session["user_id"] = user.id

    return Response({"order_id": order_id})
@login_required
def pagar_view(request, order_id):
    print("💡 order_id recibido:", order_id)

    email = request.session.get("email")
    monto = request.session.get("monto")
    metodo = request.session.get("metodo_pago")

    if not email or not monto or not metodo:
        print("❌ Datos de sesión incompletos:")
        print("email:", email)
        print("monto:", monto)
        print("metodo:", metodo)
        return redirect("/carrito/")

    try:
        session_id = f"{request.user.id}-{uuid.uuid4()}"
        return_url = request.build_absolute_uri("/pago_exitoso/")

        response = transaction.create(
            buy_order=order_id,
            session_id=session_id,
            amount=int(monto),
            return_url=return_url
        )

        # Redirige a la URL que devuelve Transbank
        url = response["url"] + "?token_ws=" + response["token"]
        return redirect(url)

    except Exception as e:
        print("❌ Error al crear la transacción:", e)
        return redirect("/carrito/")
    
def pago_exitoso(request):
    token_ws = request.GET.get('token_ws')
    tbk_token = request.GET.get('TBK_TOKEN')

    if not token_ws:
        # El usuario anuló o rechazó el pago
        from django.contrib import messages
        messages.error(request, "El pago fue anulado o rechazado. Puedes intentar nuevamente.")
        return redirect("/carrito/")

    transaction = Transaction(options)
    result = transaction.commit(token_ws)

    if result['status'] == 'AUTHORIZED':
        # ...tu lógica de éxito...
        cart = request.session.get("cart", [])
        email = request.session.get("email", "")
        monto = request.session.get("monto", "")
        metodo = request.session.get("metodo_pago", "")
        order_id = request.session.get("order_id", "")

        productos = []
        for item in cart:
            productos.append({
                "producto": item.get("producto", "Producto desconocido"),
                "precio": item.get("precio", 0),
                "cantidad": item.get("cantidad", 1),
                "subtotal": item.get("precio", 0) * item.get("cantidad", 1)
            })

        return render(request, "pago_exitoso.html", {
            "email": email,
            "monto": monto,
            "order_id": order_id,
            "metodo": metodo,
            "productos": productos
        })
    else:
        from django.contrib import messages
        messages.error(request, "El pago fue rechazado o anulado. Puedes intentar nuevamente.")
        return redirect("/carrito/")