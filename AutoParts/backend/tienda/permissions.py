from rest_framework.permissions import BasePermission

class EsTrabajador(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            hasattr(request.user, 'perfilusuario') and
            request.user.perfilusuario.trabajador
        )