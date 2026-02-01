"""
Vistas UX del módulo Home.

Vistas públicas para la landing, catálogo de cursos, membresías y curso player.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.apps import apps
from django.db import IntegrityError
import json


def home(request):
    """Renderiza el template principal de la home/dashboard."""
    return render(request, 'Home.html')


def register(request):
    """Renderiza la home pero indica que debe abrirse el modal de registro."""
    return render(request, 'Home.html', {'open_register': True})


def login(request):
    """Renderiza la home pero indica que debe abrirse el modal de login."""
    return render(request, 'Home.html', {'open_login': True})


def course_catalog(request):
    """
    Vista del catálogo de cursos públicos.
    Muestra todos los cursos publicados para que los usuarios exploren.
    """
    Course = apps.get_model('Course', 'Course')
    
    courses = Course.objects.filter(publicado=True).select_related('profesor').order_by('-fecha_creacion')
    
    # Filtros opcionales
    nivel = request.GET.get('nivel')
    if nivel:
        courses = courses.filter(nivel=nivel)
    
    context = {
        'courses': courses,
        'page_title': 'Course Catalog',
        'selected_nivel': nivel,
        'nivel_choices': [
            ('PRINCIPIANTE', 'Principiante'),
            ('INTERMEDIO', 'Intermedio'),
            ('AVANZADO', 'Avanzado'),
        ]
    }
    
    return render(request, 'catalog/course_list.html', context)


def course_preview(request, course_id):
    """
    Vista de preview/detalle de un curso.
    Muestra información del curso antes de suscribirse.
    """
    Course = apps.get_model('Course', 'Course')
    
    course = get_object_or_404(Course, id=course_id, publicado=True)
    
    # Obtener clases del curso
    try:
        Class = apps.get_model('class_app', 'Class')
        classes = Class.objects.filter(curso=course).order_by('orden')
    except:
        classes = []
    
    context = {
        'course': course,
        'classes': classes,
        'page_title': course.titulo,
    }
    
    return render(request, 'catalog/course_preview.html', context)


# ===========================================
# Membership views (inline)
# ===========================================

def membership_plans_redirect(request):
    """
    Vista de planes de membresía disponibles.
    """
    try:
        MembershipPlan = apps.get_model('membership', 'MembershipPlan')
        UserMembership = apps.get_model('membership', 'UserMembership')
        from django.utils import timezone
        
        plans_qs = MembershipPlan.objects.filter(is_active=True).order_by('price')
        
        plans = []
        featured_plan = None
        
        for p in plans_qs:
            plan_data = {
                'id': p.id,
                'name': p.name,
                'slug': p.slug,
                'description': p.description,
                'price': p.price,
                'original_price': p.original_price,
                'savings': p.savings,
                'plan_type': p.plan_type,
                'features': p.features_list,
                'is_featured': p.is_featured
            }
            plans.append(plan_data)
            
            if p.is_featured:
                featured_plan = plan_data
        
        user_membership = None
        if request.user.is_authenticated:
            user_membership = UserMembership.objects.filter(
                user=request.user,
                status='ACTIVE',
                start_date__lte=timezone.now(),
                end_date__gte=timezone.now()
            ).first()
            
    except Exception:
        plans = [
            {
                'id': 1,
                'name': 'Monthly',
                'slug': 'monthly',
                'description': 'Flexibility to learn at your own pace.',
                'price': 29,
                'plan_type': 'MONTHLY',
                'features': [
                    'All-Access to all courses',
                    'Downloadable resources',
                    'Course completion certificates'
                ],
                'is_featured': False
            },
            {
                'id': 2,
                'name': 'Annual',
                'slug': 'annual',
                'description': 'Maximum value for serious learners.',
                'price': 249,
                'original_price': 348,
                'savings': 99,
                'plan_type': 'ANNUAL',
                'features': [
                    'All-Access to all courses',
                    'Downloadable resources',
                    'Course completion certificates',
                    'Priority support access'
                ],
                'is_featured': True
            }
        ]
        featured_plan = plans[1]
        user_membership = None
    
    context = {
        'page_title': 'Membership Plans',
        'plans': plans,
        'featured_plan': featured_plan,
        'user_membership': user_membership,
    }
    
    return render(request, 'membership/plans.html', context)


def membership_subscribe_redirect(request, plan_slug):
    """Inicia el proceso de suscripción a un plan."""
    if not request.user.is_authenticated:
        messages.info(request, 'Inicia sesión para suscribirte.')
        return redirect('home:login')
    
    try:
        MembershipPlan = apps.get_model('membership', 'MembershipPlan')
        UserMembership = apps.get_model('membership', 'UserMembership')
        from django.utils import timezone
        from dateutil.relativedelta import relativedelta
        
        plan = MembershipPlan.objects.filter(slug=plan_slug, is_active=True).first()
        if not plan:
            messages.error(request, 'Plan no encontrado.')
            return redirect('home:membership_plans')
        
        existing = UserMembership.objects.filter(
            user=request.user,
            status='ACTIVE',
            start_date__lte=timezone.now(),
            end_date__gte=timezone.now()
        ).first()
        
        if existing:
            messages.info(request, 'Ya tienes una membresía activa.')
            return redirect('home:membership_plans')
        
        start_date = timezone.now()
        if plan.plan_type == 'MONTHLY':
            end_date = start_date + relativedelta(months=1)
        elif plan.plan_type == 'ANNUAL':
            end_date = start_date + relativedelta(years=1)
        else:
            end_date = start_date + relativedelta(months=1)
        
        UserMembership.objects.create(
            user=request.user,
            plan=plan,
            start_date=start_date,
            end_date=end_date,
            status='ACTIVE',
            payment_reference='DEMO-' + str(request.user.id)
        )
        
        messages.success(request, f'¡Suscripción a {plan.name} activada!')
        return redirect('home:index')
        
    except Exception:
        messages.error(request, 'Servicio no disponible.')
        return redirect('home:membership_plans')


# ===========================================
# Course Player views (inline)
# ===========================================

@login_required
def course_player_redirect(request, course_id):
    """Vista del reproductor de clase."""
    Course = apps.get_model('Course', 'Course')
    
    course = get_object_or_404(Course, id=course_id, publicado=True)
    
    try:
        Class = apps.get_model('class_app', 'Class')
        all_classes = Class.objects.filter(curso=course).order_by('orden')
    except:
        all_classes = []
    
    current_class = None
    if all_classes:
        current_class = all_classes.first()
    
    prev_class = None
    next_class = None
    
    if current_class and all_classes and all_classes.count() > 1:
        classes_list = list(all_classes)
        try:
            current_index = classes_list.index(current_class)
            if current_index > 0:
                prev_class = classes_list[current_index - 1]
            if current_index < len(classes_list) - 1:
                next_class = classes_list[current_index + 1]
        except ValueError:
            pass
    
    total_classes = all_classes.count() if hasattr(all_classes, 'count') else len(list(all_classes))
    current_index = 1 if current_class else 0
    progress = int((current_index / total_classes) * 100) if total_classes > 0 else 0
    
    context = {
        'course': course,
        'current_class': current_class,
        'all_classes': all_classes,
        'prev_class': prev_class,
        'next_class': next_class,
        'progress': progress,
        'current_index': current_index,
        'total_classes': total_classes,
    }
    
    return render(request, 'course_player/player.html', context)


@login_required
def course_player_class_redirect(request, course_id, class_id):
    """Vista del reproductor con clase específica."""
    Course = apps.get_model('Course', 'Course')
    
    course = get_object_or_404(Course, id=course_id, publicado=True)
    
    try:
        Class = apps.get_model('class_app', 'Class')
        all_classes = Class.objects.filter(curso=course).order_by('orden')
        current_class = get_object_or_404(Class, id=class_id, curso=course)
    except:
        all_classes = []
        current_class = None
    
    prev_class = None
    next_class = None
    
    if current_class and all_classes and all_classes.count() > 1:
        classes_list = list(all_classes)
        try:
            current_index = classes_list.index(current_class)
            if current_index > 0:
                prev_class = classes_list[current_index - 1]
            if current_index < len(classes_list) - 1:
                next_class = classes_list[current_index + 1]
        except ValueError:
            pass
    
    total_classes = all_classes.count() if hasattr(all_classes, 'count') else 0
    idx = 0
    if current_class:
        try:
            idx = list(all_classes).index(current_class) + 1
        except:
            idx = 1
    progress = int((idx / total_classes) * 100) if total_classes > 0 else 0
    
    context = {
        'course': course,
        'current_class': current_class,
        'all_classes': all_classes,
        'prev_class': prev_class,
        'next_class': next_class,
        'progress': progress,
        'current_index': idx,
        'total_classes': total_classes,
    }
    
    return render(request, 'course_player/player.html', context)
