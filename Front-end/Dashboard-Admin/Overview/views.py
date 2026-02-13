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
            (hasattr(request.user, 'role') and request.user.role == 'ADMIN')
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
                str(django_apps.get_app_config('course_app').path.parent / 'Analytics' / 'services.py')
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
        'active_nav': 'overview',
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
    Vista de gestión de usuarios con búsqueda y filtros.
    """
    from django.db.models import Q
    from django.core.paginator import Paginator
    
    User = get_user_model()
    
    # Obtener parámetros de búsqueda y filtros
    search_query = request.GET.get('search', '').strip()
    role_filter = request.GET.get('role', '').strip()
    status_filter = request.GET.get('status', '').strip()
    
    # Comenzar con todos los usuarios
    users = User.objects.all()
    
    # Aplicar búsqueda (nombre, email, o ID)
    if search_query:
        users = users.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(id__icontains=search_query)
        )
    
    # Aplicar filtro de rol
    if role_filter and role_filter in ['ADMIN', 'PROFESOR', 'CLIENTE']:
        users = users.filter(role=role_filter)
    
    # Aplicar filtro de estado
    if status_filter == 'ACTIVE':
        users = users.filter(is_active=True)
    elif status_filter == 'INACTIVE':
        users = users.filter(is_active=False)
    
    # Ordenar por fecha de registro (más recientes primero)
    users = users.order_by('-date_joined')
    
    # Aplicar paginación (10 usuarios por página)
    paginator = Paginator(users, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    total_users = User.objects.count()
    
    context = {
        'active_nav': 'users',
        'page_title': 'User Management',
        'page_obj': page_obj,
        'total_users': total_users,
        # Pasar valores de filtros para persistencia en el formulario
        'search_query': search_query,
        'role_filter': role_filter,
        'status_filter': status_filter,
    }
    
    return render(request, 'dashboard_admin/users_list.html', context)


@admin_required
def edit_user(request, user_id):
    """
    Vista de edición de usuario.
    Permite al admin modificar información del usuario.
    """
    User = get_user_model()
    
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        from django.contrib import messages
        messages.error(request, 'User not found.')
        return redirect('dashboard_admin:users_list')
    
    if request.method == 'POST':
        # Obtener datos del formulario
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        role = request.POST.get('role', '').upper()
        is_active = request.POST.get('is_active') == 'on'
        
        # Validaciones
        errors = []
        
        if not email:
            errors.append('Email is required.')
        
        if not role or role not in ['ADMIN', 'PROFESOR', 'CLIENTE']:
            errors.append('Invalid role selected.')
        
        # Verificar email único (excluyendo el usuario actual)
        if email and User.objects.filter(email=email).exclude(pk=user_id).exists():
            errors.append('A user with this email already exists.')
        
        if errors:
            from django.contrib import messages
            for error in errors:
                messages.error(request, error)
            
            context = {
                'active_nav': 'users',
                'page_title': 'Edit User',
                'edit_user': user,
                'form_data': {
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': email,
                    'role': role,
                    'is_active': is_active,
                }
            }
            return render(request, 'dashboard_admin/user_edit.html', context)
        
        # Actualizar usuario
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.role = role
        user.is_active = is_active
        user.save()
        
        from django.contrib import messages
        messages.success(request, f'User {user.first_name} {user.last_name} updated successfully!')
        return redirect('dashboard_admin:users_list')
    
    # GET request - mostrar formulario
    context = {
        'active_nav': 'users',
        'page_title': 'Edit User',
        'edit_user': user,
    }
    
    return render(request, 'dashboard_admin/user_edit.html', context)


@admin_required
def create_user(request):
    """
    Vista de creación de usuario.
    Permite al admin crear nuevos usuarios.
    """
    User = get_user_model()
    
    if request.method == 'POST':
        # Obtener datos del formulario
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        role = request.POST.get('role', '').upper()
        is_active = request.POST.get('is_active') == 'on'
        
        # Validaciones
        errors = []
        
        if not email:
            errors.append('Email is required.')
        
        if not password:
            errors.append('Password is required.')
        elif len(password) < 6:
            errors.append('Password must be at least 6 characters long.')
        
        if not role or role not in ['ADMIN', 'PROFESOR', 'CLIENTE']:
            errors.append('Invalid role selected.')
        
        # Verificar email único
        if email and User.objects.filter(email=email).exists():
            errors.append('A user with this email already exists.')
        
        if errors:
            from django.contrib import messages
            for error in errors:
                messages.error(request, error)
            
            context = {
                'active_nav': 'users',
                'page_title': 'Create User',
                'form_data': {
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': email,
                    'role': role,
                    'is_active': is_active,
                }
            }
            return render(request, 'dashboard_admin/user_create.html', context)
        
        # Crear usuario
        try:
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
            )
            user.role = role
            user.is_active = is_active
            user.save()
            
            from django.contrib import messages
            messages.success(request, f'User {user.first_name} {user.last_name} created successfully!')
            return redirect('dashboard_admin:users_list')
        except Exception as e:
            from django.contrib import messages
            messages.error(request, f'Error creating user: {str(e)}')
            
            context = {
                'active_nav': 'users',
                'page_title': 'Create User',
                'form_data': {
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': email,
                    'role': role,
                    'is_active': is_active,
                }
            }
            return render(request, 'dashboard_admin/user_create.html', context)
    
    # GET request - mostrar formulario
    context = {
        'active_nav': 'users',
        'page_title': 'Create User',
    }
    
    return render(request, 'dashboard_admin/user_create.html', context)


@admin_required
def delete_user(request, user_id):
    """
    Vista de eliminación de usuario.
    Permite al admin eliminar usuarios.
    """
    if request.method == 'POST':
        User = get_user_model()
        
        try:
            user = User.objects.get(pk=user_id)
            user_name = f"{user.first_name} {user.last_name}" if user.first_name or user.last_name else user.email
            user.delete()
            
            from django.contrib import messages
            messages.success(request, f'User {user_name} deleted successfully!')
        except User.DoesNotExist:
            from django.contrib import messages
            messages.error(request, 'User not found.')
        except Exception as e:
            from django.contrib import messages
            messages.error(request, f'Error deleting user: {str(e)}')
    
    return redirect('dashboard_admin:users_list')

def courses_list(request):
    """
    Vista de catálogo de cursos (admin) con búsqueda y filtros.
    """
    from django.db.models import Q
    from django.core.paginator import Paginator
    
    Course = apps.get_model('course_app', 'Course')
    
    # Obtener parámetros de búsqueda y filtros
    search_query = request.GET.get('search', '').strip()
    difficulty_filter = request.GET.get('difficulty', '').strip()
    status_filter = request.GET.get('status', '').strip()
    
    # Comenzar con todos los cursos
    courses = Course.objects.select_related('profesor').all()
    
    # Aplicar búsqueda (título, profesor, o ID)
    if search_query:
        courses = courses.filter(
            Q(titulo__icontains=search_query) |
            Q(profesor__first_name__icontains=search_query) |
            Q(profesor__last_name__icontains=search_query) |
            Q(profesor__email__icontains=search_query) |
            Q(id__icontains=search_query)
        )
    
    # Aplicar filtro de dificultad
    if difficulty_filter and difficulty_filter in ['PRINCIPIANTE', 'INTERMEDIO', 'AVANZADO']:
        courses = courses.filter(nivel=difficulty_filter)
    
    # Aplicar filtro de estado
    if status_filter == 'PUBLISHED':
        courses = courses.filter(publicado=True)
    elif status_filter == 'DRAFT':
        courses = courses.filter(publicado=False)
    
    # Ordenar por fecha de creación
    courses = courses.order_by('-fecha_creacion')
    
    # Aplicar paginación (9 cursos por página)
    paginator = Paginator(courses, 9)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    total_courses = Course.objects.count()
    published_count = Course.objects.filter(publicado=True).count()
    draft_count = Course.objects.filter(publicado=False).count()
    
    context = {
        'active_nav': 'courses',
        'page_title': 'Course Catalog',
        'page_obj': page_obj,
        'total_courses': total_courses,
        'published_count': published_count,
        'draft_count': draft_count,
        # Pasar valores de filtros para persistencia
        'search_query': search_query,
        'difficulty_filter': difficulty_filter,
        'status_filter': status_filter,
    }
    
    return render(request, 'dashboard_admin/courses_list.html', context)


@admin_required
def view_course(request, course_id):
    """
    Vista de detalles de curso (admin).
    Muestra información del curso.
    """
    Course = apps.get_model('course_app', 'Course')
    
    try:
        course = Course.objects.select_related('profesor').get(pk=course_id)
    except Course.DoesNotExist:
        from django.contrib import messages
        messages.error(request, 'Course not found.')
        return redirect('dashboard_admin:courses_list')
    
    context = {
        'active_nav': 'courses',
        'page_title': 'Course Details',
        'course': course,
    }
    
    return render(request, 'dashboard_admin/course_view.html', context)


@admin_required
def edit_course(request, course_id):
    """
    Vista de edición de curso (admin).
    Permite editar metadata del curso.
    """
    Course = apps.get_model('course_app', 'Course')
    
    try:
        course = Course.objects.select_related('profesor').get(pk=course_id)
    except Course.DoesNotExist:
        from django.contrib import messages
        messages.error(request, 'Course not found.')
        return redirect('dashboard_admin:courses_list')
    
    if request.method == 'POST':
        # Obtener datos del formulario
        titulo = request.POST.get('titulo', '').strip()
        descripcion = request.POST.get('descripcion', '').strip()
        imagen_portada = request.POST.get('imagen_portada', '').strip()
        nivel = request.POST.get('nivel', '').strip()
        publicado = request.POST.get('publicado') == 'on'
        
        # Validaciones
        errors = []
        
        if not titulo:
            errors.append('Title is required.')
        
        if nivel not in ['PRINCIPIANTE', 'INTERMEDIO', 'AVANZADO']:
            errors.append('Invalid difficulty level.')
        
        if errors:
            from django.contrib import messages
            for error in errors:
                messages.error(request, error)
        else:
            # Actualizar curso
            course.titulo = titulo
            course.descripcion = descripcion
            course.imagen_portada = imagen_portada if imagen_portada else None
            course.nivel = nivel
            course.publicado = publicado
            course.save()
            
            from django.contrib import messages
            messages.success(request, f'Course "{course.titulo}" updated successfully!')
            return redirect('dashboard_admin:courses_list')
    
    context = {
        'active_nav': 'courses',
        'page_title': 'Edit Course',
        'course': course,
    }
    
    return render(request, 'dashboard_admin/course_edit.html', context)


@admin_required
def delete_course(request, course_id):
    """
    Vista de eliminación de curso (admin).
    Permite eliminar cursos.
    """
    if request.method == 'POST':
        Course = apps.get_model('course_app', 'Course')
        
        try:
            course = Course.objects.get(pk=course_id)
            course_title = course.titulo
            course.delete()
            
            from django.contrib import messages
            messages.success(request, f'Course "{course_title}" deleted successfully!')
        except Course.DoesNotExist:
            from django.contrib import messages
            messages.error(request, 'Course not found.')
        except Exception as e:
            from django.contrib import messages
            messages.error(request, f'Error deleting course: {str(e)}')
    
    return redirect('dashboard_admin:courses_list')


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
    Course = apps.get_model('course_app', 'Course')
    
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


@admin_required
def membership_settings(request):
    """
    Vista de configuración de membresías.
    Permite al admin configurar precios y disponibilidad de planes.
    """
    try:
        MembershipPlan = apps.get_model('membership', 'MembershipPlan')
        
        # Obtener o crear planes
        monthly_plan, _ = MembershipPlan.objects.get_or_create(
            slug='monthly',
            defaults={
                'name': 'Monthly',
                'plan_type': 'MONTHLY',
                'price': 29.00,
                'is_active': True,
                'description': 'Flexibility to learn at your own pace.'
            }
        )
        
        annual_plan, _ = MembershipPlan.objects.get_or_create(
            slug='annual',
            defaults={
                'name': 'Annual',
                'plan_type': 'ANNUAL',
                'price': 249.00,
                'original_price': 348.00,
                'is_active': True,
                'is_featured': True,
                'description': 'Maximum value for serious learners.'
            }
        )
        
        if request.method == 'POST':
            # Actualizar plan mensual
            monthly_plan.price = float(request.POST.get('monthly_price', 29.00))
            monthly_plan.original_price = float(request.POST.get('monthly_original_price') or 0) or None
            monthly_plan.is_active = request.POST.get('monthly_active') == '1'
            monthly_plan.save()
            
            # Actualizar plan anual
            annual_plan.price = float(request.POST.get('annual_price', 249.00))
            annual_plan.original_price = float(request.POST.get('annual_original_price') or 0) or None
            annual_plan.is_active = request.POST.get('annual_active') == '1'
            annual_plan.save()
            
            from django.contrib import messages
            messages.success(request, 'Membership settings updated successfully!')
            return redirect('dashboard_admin:membership_settings')
            
    except Exception as e:
        # Fallback si el modelo no existe
        monthly_plan = {
            'price': 29.00,
            'original_price': None,
            'is_active': True
        }
        annual_plan = {
            'price': 249.00,
            'original_price': 348.00,
            'is_active': True
        }
    
    context = {
        'active_nav': 'settings',
        'page_title': 'Membership Settings',
        'monthly_plan': monthly_plan,
        'annual_plan': annual_plan,
    }
    
    return render(request, 'dashboard_admin/membership_settings.html', context)
