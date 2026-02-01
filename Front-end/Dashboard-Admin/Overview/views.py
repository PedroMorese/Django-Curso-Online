"""
Vistas UX del Dashboard de Administración.

Este módulo contiene las vistas UX para:
- Vista general del dashboard (métricas, transacciones, cursos top)
- Gestión de usuarios
- Gestión de cursos
- Suscripciones
- Reportes de ingresos

RESPONSABILIDADES:
- Orquestar datos del backend
- Renderizar templates HTML
- NO contener lógica de negocio
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model
from django.apps import apps
from functools import wraps


def admin_required(view_func):
    """Decorador que requiere rol de admin o staff"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('Auth:login')
        
        is_admin = (
            request.user.is_staff or 
            request.user.is_superuser or
            (hasattr(request.user, 'rol') and request.user.rol == 'ADMIN')
        )
        
        if not is_admin:
            return redirect('home:index')
        
        return view_func(request, *args, **kwargs)
    return wrapper


@admin_required
def overview(request):
    """
    Vista principal del dashboard de administración.
    
    Muestra:
    - Métricas globales (membresías, ingresos, uptime)
    - Transacciones recientes
    - Cursos con mejor rendimiento
    """
    # Importar servicios del backend
    try:
        # Import services through the module system
        import sys
        import importlib.util
        
        # Use apps to get the analytics service
        from django.apps import apps as django_apps
        
        # Try to load analytics service
        try:
            spec = importlib.util.spec_from_file_location(
                "services",
                str(django_apps.get_app_config('Course').path.parent / 'Analytics' / 'services.py')
            )
            if spec and spec.loader:
                analytics_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(analytics_module)
                AnalyticsService = analytics_module.AnalyticsService
                
                # Obtener datos del dominio
                global_metrics = AnalyticsService.get_global_metrics()
                revenue_metrics = AnalyticsService.get_revenue_metrics('quarter')
                recent_transactions = AnalyticsService.get_recent_transactions(5)
                top_courses = AnalyticsService.get_top_courses(4)
            else:
                raise Exception("Could not load analytics")
        except Exception as e:
            raise ImportError(f"Failed to load analytics: {e}")
            
    except Exception:
        # Fallback si los servicios no están disponibles
        global_metrics = {
            'active_memberships': 12840,
            'active_memberships_change': 4.2,
            'expired_memberships': 452,
            'expired_memberships_change': -1.8,
            'platform_uptime': 99.9,
            'uptime_status': 'Stable'
        }
        revenue_metrics = {
            'current_revenue': 128430,
            'goal': 156000,
            'progress_percentage': 82,
            'period': 'quarter'
        }
        recent_transactions = [
            {'user': {'name': 'Jane Doe', 'initials': 'JD'}, 'plan_name': 'Professional Pro', 'status': 'ACTIVE', 'amount': '299.00'},
            {'user': {'name': 'Mike Kelly', 'initials': 'MK'}, 'plan_name': 'Standard Monthly', 'status': 'PENDING', 'amount': '49.00'},
            {'user': {'name': 'Robert Smith', 'initials': 'RS'}, 'plan_name': 'Enterprise Yearly', 'status': 'ACTIVE', 'amount': '1200.00'},
            {'user': {'name': 'Linda Wu', 'initials': 'LW'}, 'plan_name': 'Professional Pro', 'status': 'ACTIVE', 'amount': '299.00'},
        ]
        top_courses = [
            {'title': 'Full Stack Web Development', 'enrolled_count': 1240, 'revenue': 45200, 'change_percentage': 12, 'thumbnail': ''},
            {'title': 'Data Science Masterclass', 'enrolled_count': 980, 'revenue': 32800, 'change_percentage': 8, 'thumbnail': ''},
            {'title': 'UI/UX Design Systems', 'enrolled_count': 850, 'revenue': 24100, 'change_percentage': -2, 'thumbnail': ''},
            {'title': 'Ethical Hacking Intro', 'enrolled_count': 720, 'revenue': 18400, 'change_percentage': 15, 'thumbnail': ''},
        ]
    
    context = {
        'active_nav': 'dashboard',
        'page_title': 'System Control Panel',
        'metrics': global_metrics,
        'revenue': revenue_metrics,
        'transactions': recent_transactions,
        'top_courses': top_courses,
    }
    
    return render(request, 'dashboard_admin/overview.html', context)


@admin_required
def users_list(request):
    """
    Vista de gestión de usuarios.
    """
    User = get_user_model()
    
    users = User.objects.all().order_by('-date_joined')[:50]
    total_users = User.objects.count()
    
    context = {
        'active_nav': 'users',
        'page_title': 'User Management',
        'users': users,
        'total_users': total_users,
    }
    
    return render(request, 'dashboard_admin/users_list.html', context)


@admin_required
def courses_list(request):
    """
    Vista de catálogo de cursos (admin).
    """
    Course = apps.get_model('Course', 'Course')
    
    courses = Course.objects.select_related('profesor').all().order_by('-fecha_creacion')[:50]
    total_courses = Course.objects.count()
    published_count = Course.objects.filter(publicado=True).count()
    draft_count = Course.objects.filter(publicado=False).count()
    
    context = {
        'active_nav': 'courses',
        'page_title': 'Course Catalog',
        'courses': courses,
        'total_courses': total_courses,
        'published_count': published_count,
        'draft_count': draft_count,
    }
    
    return render(request, 'dashboard_admin/courses_list.html', context)


@admin_required
def subscriptions_list(request):
    """
    Vista de suscripciones.
    """
    try:
        UserMembership = apps.get_model('membership', 'UserMembership')
        
        memberships = UserMembership.objects.select_related(
            'user', 'plan'
        ).order_by('-start_date')[:50]
        
        total_subscriptions = UserMembership.objects.count()
        active_count = UserMembership.objects.filter(status='ACTIVE').count()
        pending_count = UserMembership.objects.filter(status='PENDING').count()
    except Exception:
        memberships = []
        total_subscriptions = 0
        active_count = 0
        pending_count = 0
    
    context = {
        'active_nav': 'subscriptions',
        'page_title': 'Subscription History',
        'memberships': memberships,
        'total_subscriptions': total_subscriptions,
        'active_count': active_count,
        'pending_count': pending_count,
    }
    
    return render(request, 'dashboard_admin/subscriptions_list.html', context)


@admin_required
def reports(request):
    """
    Vista de reportes de ingresos.
    """
    User = get_user_model()
    Course = apps.get_model('Course', 'Course')
    
    # Calculate basic stats
    from django.utils import timezone
    from datetime import timedelta
    
    one_month_ago = timezone.now() - timedelta(days=30)
    
    user_stats = {
        'total_users': User.objects.count(),
        'new_users_this_month': User.objects.filter(date_joined__gte=one_month_ago).count()
    }
    
    course_stats = {
        'total_courses': Course.objects.count(),
        'published_courses': Course.objects.filter(publicado=True).count()
    }
    
    # Default revenue values (placeholders)
    revenue_month = {'current_revenue': 45230, 'goal': 52000, 'progress_percentage': 87}
    revenue_quarter = {'current_revenue': 128430, 'goal': 156000, 'progress_percentage': 82}
    revenue_year = {'current_revenue': 452300, 'goal': 600000, 'progress_percentage': 75}
    
    context = {
        'active_nav': 'reports',
        'page_title': 'Revenue Analytics',
        'user_stats': user_stats,
        'course_stats': course_stats,
        'revenue_month': revenue_month,
        'revenue_quarter': revenue_quarter,
        'revenue_year': revenue_year,
    }
    
    return render(request, 'dashboard_admin/reports.html', context)
