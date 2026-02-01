"""
Permisos del dominio Membership.

Permisos personalizados para validar acceso a contenido premium.
"""

from rest_framework import permissions
from .services import MembershipService


class HasActiveMembership(permissions.BasePermission):
    """
    Permiso que verifica si el usuario tiene una membresía activa.
    """
    message = "Necesita una membresía activa para acceder a este contenido."
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        return MembershipService.user_has_active_membership(request.user)


class IsAdminOrHasMembership(permissions.BasePermission):
    """
    Permiso que permite acceso a admins o usuarios con membresía activa.
    """
    message = "Necesita ser administrador o tener una membresía activa."
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Admins siempre tienen acceso
        if request.user.is_staff or request.user.is_superuser:
            return True
        
        # Verificar rol de admin si existe
        if hasattr(request.user, 'rol') and request.user.rol == 'ADMIN':
            return True
        
        return MembershipService.user_has_active_membership(request.user)
