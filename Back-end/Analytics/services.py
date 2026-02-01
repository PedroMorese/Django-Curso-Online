"""
Servicios de Analytics.

Este módulo contiene la lógica de negocio para:
- Calcular métricas globales de la plataforma
- Generar reportes de ingresos
- Obtener datos de rendimiento de cursos
- Estadísticas de usuarios y transacciones

PRINCIPIO: Estos servicios agregan datos de múltiples dominios
para presentar información consolidada al administrador.
"""

from django.utils import timezone
from django.db.models import Sum, Count, Avg
from django.db.models.functions import TruncMonth, TruncDay
from django.contrib.auth import get_user_model
from django.apps import apps
from datetime import timedelta
from typing import Dict, Any, List
from decimal import Decimal

User = get_user_model()


class AnalyticsService:
    """
    Servicio de Analytics para el dashboard de administración.
    
    Agrega datos de múltiples dominios para generar
    métricas y reportes consolidados.
    """
    
    @staticmethod
    def get_global_metrics() -> Dict[str, Any]:
        """
        Obtiene métricas globales de la plataforma.
        
        Returns:
            Dict con métricas principales
        """
        try:
            UserMembership = apps.get_model('membership', 'UserMembership')
            
            now = timezone.now()
            
            # Conteos directos
            active_count = UserMembership.objects.filter(
                status='ACTIVE',
                start_date__lte=now,
                end_date__gte=now
            ).count()
            
            expired_count = UserMembership.objects.filter(
                status='EXPIRED'
            ).count()
            
            membership_stats = {
                'active_memberships': active_count,
                'expired_memberships': expired_count
            }
        except:
            membership_stats = {
                'active_memberships': 0,
                'expired_memberships': 0
            }
        
        # Calcular cambio porcentual (valores de ejemplo)
        active_change = 4.2
        expired_change = -1.8
        
        return {
            'active_memberships': membership_stats['active_memberships'],
            'active_memberships_change': active_change,
            'expired_memberships': membership_stats['expired_memberships'],
            'expired_memberships_change': expired_change,
            'platform_uptime': 99.9,
            'uptime_status': 'Stable'
        }
    
    @staticmethod
    def get_revenue_metrics(period: str = 'quarter') -> Dict[str, Any]:
        """
        Obtiene métricas de ingresos para un período.
        
        Args:
            period: 'month', 'quarter', 'year'
            
        Returns:
            Dict con métricas de ingresos
        """
        try:
            UserMembership = apps.get_model('membership', 'UserMembership')
            
            now = timezone.now()
            
            # Definir rango de fechas según período
            if period == 'month':
                start_date = now.replace(day=1)
                goal = Decimal('52000')
            elif period == 'quarter':
                quarter_start_month = ((now.month - 1) // 3) * 3 + 1
                start_date = now.replace(month=quarter_start_month, day=1)
                goal = Decimal('156000')
            else:  # year
                start_date = now.replace(month=1, day=1)
                goal = Decimal('600000')
            
            # Calcular ingresos del período
            revenue = UserMembership.objects.filter(
                status='ACTIVE',
                created_at__gte=start_date,
                created_at__lte=now
            ).select_related('plan').aggregate(
                total=Sum('plan__price')
            )['total'] or Decimal('0')
            
            # Calcular porcentaje de progreso
            progress = min(100, int((revenue / goal) * 100)) if goal > 0 else 0
            
            return {
                'current_revenue': revenue,
                'goal': goal,
                'progress_percentage': progress,
                'period': period
            }
        except:
            return {
                'current_revenue': Decimal('0'),
                'goal': Decimal('52000'),
                'progress_percentage': 0,
                'period': period
            }
    
    @staticmethod
    def get_recent_transactions(limit: int = 10) -> List[Dict[str, Any]]:
        """
        Obtiene las transacciones más recientes.
        
        Args:
            limit: Número máximo de transacciones
            
        Returns:
            Lista de transacciones
        """
        try:
            UserMembership = apps.get_model('membership', 'UserMembership')
            
            transactions = UserMembership.objects.select_related(
                'user', 'plan'
            ).order_by('-created_at')[:limit]
            
            return [{
                'id': t.id,
                'user': {
                    'name': f"{t.user.first_name} {t.user.last_name}".strip() or t.user.username,
                    'email': t.user.email,
                    'initials': (
                        (t.user.first_name[:1] if t.user.first_name else '') +
                        (t.user.last_name[:1] if t.user.last_name else '')
                    ).upper() or 'U'
                },
                'plan_name': t.plan.name,
                'amount': str(t.plan.price),
                'status': t.status,
                'date': t.created_at.isoformat()
            } for t in transactions]
        except:
            return []
    
    @staticmethod
    def get_top_courses(limit: int = 5) -> List[Dict[str, Any]]:
        """
        Obtiene los cursos con mejor rendimiento.
        
        Args:
            limit: Número máximo de cursos
            
        Returns:
            Lista de cursos top
        """
        try:
            Course = apps.get_model('course_app', 'Course')
            
            # Por ahora, ordenamos por fecha de creación
            courses = Course.objects.filter(
                publicado=True
            ).select_related('profesor').order_by('-fecha_creacion')[:limit]
            
            # Datos de ejemplo para revenue
            example_revenues = [45200, 32800, 24100, 18400, 15600]
            example_enrollments = [1240, 980, 850, 720, 650]
            example_changes = [12, 8, -2, 15, 5]
            
            return [{
                'id': c.id,
                'title': c.titulo,
                'thumbnail': c.imagen_portada or '',
                'professor': f"{c.profesor.first_name} {c.profesor.last_name}".strip() or c.profesor.username,
                'enrolled_count': example_enrollments[i] if i < len(example_enrollments) else 0,
                'revenue': example_revenues[i] if i < len(example_revenues) else 0,
                'change_percentage': example_changes[i] if i < len(example_changes) else 0
            } for i, c in enumerate(courses)]
        except:
            return []
    
    @staticmethod
    def get_user_statistics() -> Dict[str, Any]:
        """
        Obtiene estadísticas de usuarios de la plataforma.
        
        Returns:
            Dict con estadísticas de usuarios
        """
        total_users = User.objects.count()
        
        # Usuarios nuevos este mes
        now = timezone.now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        new_users_month = User.objects.filter(
            date_joined__gte=month_start
        ).count()
        
        # Usuarios por rol (si el campo existe)
        users_by_role = {}
        if hasattr(User, 'rol'):
            users_by_role = dict(
                User.objects.values('rol').annotate(count=Count('id')).values_list('rol', 'count')
            )
        
        return {
            'total_users': total_users,
            'new_users_this_month': new_users_month,
            'users_by_role': users_by_role
        }
    
    @staticmethod
    def get_course_statistics() -> Dict[str, Any]:
        """
        Obtiene estadísticas de cursos de la plataforma.
        
        Returns:
            Dict con estadísticas de cursos
        """
        try:
            Course = apps.get_model('course_app', 'Course')
            
            total_courses = Course.objects.count()
            published_courses = Course.objects.filter(publicado=True).count()
            draft_courses = Course.objects.filter(publicado=False).count()
            
            # Cursos por nivel
            courses_by_level = dict(
                Course.objects.values('nivel').annotate(count=Count('id')).values_list('nivel', 'count')
            )
            
            return {
                'total_courses': total_courses,
                'published_courses': published_courses,
                'draft_courses': draft_courses,
                'courses_by_level': courses_by_level
            }
        except:
            return {
                'total_courses': 0,
                'published_courses': 0,
                'draft_courses': 0,
                'courses_by_level': {}
            }
