from django.urls import path
from .views import ProductoAPIView, HomeView, LoginView, login_page, catalogo_view

urlpatterns=[
    path('', HomeView.as_view(), name='home'),
    path('api/productos', ProductoAPIView.as_view(), name='lista-productos-api'),
    path('api/login/', LoginView.as_view(), name='api-login' ),
    path('login/', login_page, name='login'),
    path('catalogo/', catalogo_view, name='catalogo')
]