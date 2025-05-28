from django.urls import path
from .views import ProductoAPIView, HomeView, LoginView, login_page, catalogo_view, RegistroView, registro_page, PerfilUsuarioView, perfil_page

urlpatterns=[
    path('', HomeView.as_view(), name='home'),
    path('api/productos/', ProductoAPIView.as_view(), name='lista-productos-api'),
    path('api/login/', LoginView.as_view(), name='api-login' ),
    path('login/', login_page, name='login'),
    path('catalogo/', catalogo_view, name='catalogo'),
    path('registro/', registro_page, name='registro'),
    path('api/registro/', RegistroView.as_view(), name='api-registro'),
    path('api/perfil/', PerfilUsuarioView.as_view(), name='api-perfil'),
    path('perfil', perfil_page, name='perfil')
]