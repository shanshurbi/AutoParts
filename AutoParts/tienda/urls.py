from django.urls import path
from .views import ProductoAPIView, HomeView, LoginView

urlpatterns=[
    path('', HomeView.as_view(), name='home'),
    path('api/productos', ProductoAPIView.as_view(), name='lista-productos-api'),
    path('login/', LoginView.as_view(), name='login' )
]