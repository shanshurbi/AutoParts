from django.urls import path
from .views import ProductoAPIView, HomeView

urlpatterns=[
    path('', HomeView.as_view(), name='home'),
    path('api/productos', ProductoAPIView.as_view(), name='lista-productos-api'),
]