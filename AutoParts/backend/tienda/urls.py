from django.urls import path
from . import views
from .views import ProductoAPIView, HomeView, LoginView, login_page, catalogo_view, RegistroView, registro_page, PerfilUsuarioView, perfil_page, detalle_producto, CarritoView, AgregarCarritoView, RemoverDelCarritoView, carrito_page, CarritoContadorView

urlpatterns=[
    path('', HomeView.as_view(), name='home'),
    path('api/productos/', ProductoAPIView.as_view(), name='lista-productos-api'),
    path('api/login/', LoginView.as_view(), name='api-login' ),
    path('login/', login_page, name='login'),
    path('catalogo/', catalogo_view, name='catalogo'),
    path('registro/', registro_page, name='registro'),
    path('api/registro/', RegistroView.as_view(), name='api-registro'),
    path('api/perfil/', PerfilUsuarioView.as_view(), name='api-perfil'),
    path('perfil', perfil_page, name='perfil'),
    path('producto/<int:producto_id>', detalle_producto, name='detalle_producto'),
    path('api/carrito/', CarritoView.as_view(), name='api-carrito'),
    path('carrito/agregar/', AgregarCarritoView.as_view(), name='agregar-carrito'),
    path('carrito/remover/<int:producto_id>/', RemoverDelCarritoView.as_view(), name='remover-carrito'),
    path('carrito/', carrito_page, name='carrito'),
    path('carrito/contador/', CarritoContadorView.as_view(), name='contador-carrito'),

]