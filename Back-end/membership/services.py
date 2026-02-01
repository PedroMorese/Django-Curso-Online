"""
Servicios del dominio Membership.

Este módulo contiene la lógica de negocio para:
- Gestión de suscripciones
- Validación de acceso a contenido
- Renovaciones y cancelaciones

PRINCIPIO: El servicio es la fuente de verdad para todas las
operaciones de negocio. Las vistas UX solo deben llamar a estos servicios.
"""

from django.utils import timezone
from django.db import transaction
from django.contrib.auth import get_user_model
from datetime import timedelta
from typing import Optional, List, Dict, Any

from .models import MembershipPlan, UserMembership

User = get_user_model()


class MembershipService:
    """
    Servicio para gestión de membresías.
    
    Encapsula toda la lógica de negocio relacionada con
    planes y suscripciones de usuarios.
    """
    
    @staticmethod
    def get_available_plans() -> List[MembershipPlan]:
        """
        Obtiene todos los planes de membresía activos.
        
        Returns:
            QuerySet de planes activos ordenados por display_order
        """
        return MembershipPlan.objects.filter(
            is_active=True
        ).order_by('display_order', 'price')
    
    @staticmethod
    def get_plan_by_slug(slug: str) -> Optional[MembershipPlan]:
        """
        Obtiene un plan de membresía por su slug.
        
        Args:
            slug: Identificador único del plan
            
        Returns:
            MembershipPlan o None si no existe
        """
        try:
            return MembershipPlan.objects.get(slug=slug, is_active=True)
        except MembershipPlan.DoesNotExist:
            return None
    
    @staticmethod
    def get_featured_plan() -> Optional[MembershipPlan]:
        """
        Obtiene el plan destacado (mejor valor).
        
        Returns:
            MembershipPlan marcado como featured o None
        """
        return MembershipPlan.objects.filter(
            is_active=True,
            is_featured=True
        ).first()
    
    @staticmethod
    def get_user_active_membership(user) -> Optional[UserMembership]:
        """
        Obtiene la membresía activa de un usuario.
        
        Args:
            user: Usuario a consultar
            
        Returns:
            UserMembership activa o None
        """
        return UserMembership.objects.filter(
            user=user,
            status='ACTIVE',
            start_date__lte=timezone.now(),
            end_date__gte=timezone.now()
        ).first()
    
    @staticmethod
    def user_has_active_membership(user) -> bool:
        """
        Verifica si un usuario tiene una membresía activa.
        
        Args:
            user: Usuario a verificar
            
        Returns:
            True si tiene membresía activa, False en caso contrario
        """
        return MembershipService.get_user_active_membership(user) is not None
    
    @staticmethod
    def check_content_access(user, course=None) -> Dict[str, Any]:
        """
        Verifica si un usuario tiene acceso al contenido premium.
        
        Args:
            user: Usuario a verificar
            course: Curso específico (opcional, para futuras validaciones)
            
        Returns:
            Dict con has_access, membership (si existe), y mensaje
        """
        if not user or not user.is_authenticated:
            return {
                'has_access': False,
                'membership': None,
                'message': 'Debe iniciar sesión para acceder al contenido.'
            }
        
        membership = MembershipService.get_user_active_membership(user)
        
        if membership:
            return {
                'has_access': True,
                'membership': membership,
                'message': 'Acceso permitido.',
                'days_remaining': membership.days_remaining
            }
        
        return {
            'has_access': False,
            'membership': None,
            'message': 'Necesita una membresía activa para acceder a este contenido.'
        }
    
    @staticmethod
    @transaction.atomic
    def create_membership(
        user,
        plan: MembershipPlan,
        payment_reference: str = None,
        auto_renew: bool = False
    ) -> UserMembership:
        """
        Crea una nueva membresía para un usuario.
        
        Args:
            user: Usuario que adquiere la membresía
            plan: Plan de membresía seleccionado
            payment_reference: Referencia del pago (opcional)
            auto_renew: Si se activa renovación automática
            
        Returns:
            UserMembership creada
        """
        # Verificar si ya tiene membresía activa
        existing = MembershipService.get_user_active_membership(user)
        if existing:
            # Si ya tiene membresía, extender desde la fecha de expiración actual
            start_date = existing.end_date
        else:
            start_date = timezone.now()
        
        membership = UserMembership.objects.create(
            user=user,
            plan=plan,
            start_date=start_date,
            status='PENDING' if not payment_reference else 'ACTIVE',
            auto_renew=auto_renew,
            payment_reference=payment_reference
        )
        
        return membership
    
    @staticmethod
    @transaction.atomic
    def activate_membership(membership: UserMembership, payment_reference: str = None) -> UserMembership:
        """
        Activa una membresía pendiente.
        
        Args:
            membership: Membresía a activar
            payment_reference: Referencia del pago
            
        Returns:
            UserMembership activada
        """
        membership.status = 'ACTIVE'
        if payment_reference:
            membership.payment_reference = payment_reference
        membership.save()
        
        return membership
    
    @staticmethod
    @transaction.atomic
    def cancel_membership(membership: UserMembership) -> UserMembership:
        """
        Cancela una membresía.
        La membresía permanecerá activa hasta su fecha de expiración.
        
        Args:
            membership: Membresía a cancelar
            
        Returns:
            UserMembership cancelada
        """
        membership.cancel()
        return membership
    
    @staticmethod
    @transaction.atomic
    def renew_membership(membership: UserMembership) -> UserMembership:
        """
        Renueva una membresía existente.
        
        Args:
            membership: Membresía a renovar
            
        Returns:
            Nueva UserMembership creada
        """
        return MembershipService.create_membership(
            user=membership.user,
            plan=membership.plan,
            auto_renew=membership.auto_renew
        )
    
    @staticmethod
    def process_expired_memberships() -> int:
        """
        Procesa membresías expiradas.
        Debe ejecutarse periódicamente (cron job o celery task).
        
        Returns:
            Número de membresías procesadas
        """
        expired = UserMembership.objects.filter(
            status='ACTIVE',
            end_date__lt=timezone.now()
        )
        
        count = expired.count()
        expired.update(status='EXPIRED')
        
        return count
    
    @staticmethod
    def get_expiring_memberships(days: int = 7) -> List[UserMembership]:
        """
        Obtiene membresías que expiran en los próximos N días.
        Útil para enviar recordatorios.
        
        Args:
            days: Número de días a consultar
            
        Returns:
            Lista de membresías próximas a expirar
        """
        threshold = timezone.now() + timedelta(days=days)
        
        return UserMembership.objects.filter(
            status='ACTIVE',
            end_date__lte=threshold,
            end_date__gte=timezone.now()
        ).select_related('user', 'plan')
    
    @staticmethod
    def get_membership_stats() -> Dict[str, Any]:
        """
        Obtiene estadísticas globales de membresías.
        Para uso en dashboard de administrador.
        
        Returns:
            Dict con estadísticas
        """
        now = timezone.now()
        
        total_active = UserMembership.objects.filter(
            status='ACTIVE',
            end_date__gte=now
        ).count()
        
        total_expired = UserMembership.objects.filter(
            status='EXPIRED'
        ).count()
        
        expiring_soon = UserMembership.objects.filter(
            status='ACTIVE',
            end_date__lte=now + timedelta(days=7),
            end_date__gte=now
        ).count()
        
        return {
            'active_memberships': total_active,
            'expired_memberships': total_expired,
            'expiring_soon': expiring_soon
        }
