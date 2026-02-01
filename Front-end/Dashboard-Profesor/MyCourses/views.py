"""
Vistas UX del Dashboard de Profesor.

Este módulo contiene las vistas UX para:
- Listado de cursos del profesor
- Creación de nuevo curso
- Gestión de clases de un curso
- Perfil del profesor

RESPONSABILIDADES:
- Orquestar datos del backend (filtrados por profesor)
- Renderizar templates HTML
- NO contener lógica de negocio
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.apps import apps
from functools import wraps


def profesor_required(view_func):
    """Decorador que requiere rol de profesor"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('Auth:login')
        
        is_profesor = (
            request.user.is_staff or 
            (hasattr(request.user, 'role') and request.user.role in ['PROFESOR', 'ADMIN'])
        )
        
        if not is_profesor:
            messages.error(request, 'No tienes permisos para acceder a esta sección.')
            return redirect('home:index')
        
        return view_func(request, *args, **kwargs)
    return wrapper


@profesor_required
def my_courses(request):
    """
    Vista de listado de cursos del profesor autenticado.
    
    Muestra todos los cursos creados por el profesor,
    con opción de filtrar por estado (publicado/borrador).
    """
    Course = apps.get_model('course_app', 'Course')
    
    # Filtrar cursos del profesor autenticado
    courses = Course.objects.filter(
        profesor=request.user
    ).order_by('-fecha_creacion')
    
    # Contar por estado
    total_courses = courses.count()
    published_count = courses.filter(publicado=True).count()
    draft_count = courses.filter(publicado=False).count()
    
    context = {
        'active_nav': 'courses',
        'page_title': 'My Courses',
        'courses': courses,
        'total_courses': total_courses,
        'published_count': published_count,
        'draft_count': draft_count,
    }
    
    return render(request, 'dashboard_profesor/my_courses.html', context)


@profesor_required
def create_course(request):
    """
    Vista para crear un nuevo curso.
    """
    Course = apps.get_model('course_app', 'Course')
    
    if request.method == 'POST':
        titulo = request.POST.get('titulo', '').strip()
        descripcion = request.POST.get('descripcion', '').strip()
        nivel = request.POST.get('nivel', 'PRINCIPIANTE')
        imagen_portada = request.POST.get('imagen_portada', '').strip()
        
        if not titulo:
            messages.error(request, 'El título es requerido.')
        else:
            course = Course.objects.create(
                titulo=titulo,
                descripcion=descripcion,
                nivel=nivel,
                imagen_portada=imagen_portada or None,
                profesor=request.user,
                publicado=False
            )
            messages.success(request, f'Curso "{titulo}" creado exitosamente.')
            return redirect('dashboard_profesor:course_detail', course_id=course.id)
    
    context = {
        'active_nav': 'new_course',
        'page_title': 'Create New Course',
        'nivel_choices': [
            ('PRINCIPIANTE', 'Principiante'),
            ('INTERMEDIO', 'Intermedio'),
            ('AVANZADO', 'Avanzado'),
        ]
    }
    
    return render(request, 'dashboard_profesor/create_course.html', context)


@profesor_required
def course_detail(request, course_id):
    """
    Vista de detalle y gestión de un curso específico.
    """
    Course = apps.get_model('course_app', 'Course')
    Class = apps.get_model('class_app', 'Class')
    
    course = get_object_or_404(Course, id=course_id, profesor=request.user)
    
    # Manejar creación de clases (POST)
    if request.method == 'POST' and request.POST.get('action') == 'add_class':
        titulo = request.POST.get('titulo', '').strip()
        orden = request.POST.get('orden', '1')
        imagen_portada = request.POST.get('imagen_portada', '').strip()
        
        if titulo:
            Class.objects.create(
                curso=course,
                titulo=titulo,
                orden=int(orden),
                imagen_portada=imagen_portada or None
            )
            messages.success(request, f'Clase "{titulo}" añadida exitosamente.')
            return redirect('dashboard_profesor:course_detail', course_id=course.id)
        else:
            messages.error(request, 'El título de la clase es obligatorio.')
    
    # Obtener clases del curso
    classes = Class.objects.filter(curso=course).order_by('orden')
    
    context = {
        'active_nav': 'courses',
        'page_title': course.titulo,
        'course': course,
        'classes': classes,
    }
    
    return render(request, 'dashboard_profesor/course_detail.html', context)


@profesor_required
def toggle_publish(request, course_id):
    """
    Alterna el estado de publicación de un curso.
    """
    Course = apps.get_model('course_app', 'Course')
    
    course = get_object_or_404(Course, id=course_id, profesor=request.user)
    
    if course.publicado:
        course.despublicar()
        messages.success(request, f'Curso "{course.titulo}" despublicado.')
    else:
        course.publicar()
        messages.success(request, f'Curso "{course.titulo}" publicado.')
    
    return redirect('dashboard_profesor:course_detail', course_id=course_id)


@profesor_required
def profile(request):
    """
    Vista de perfil del profesor usando el nuevo template minimalista.
    """
    # Intentar obtener la membresía activa del usuario (aunque sea profesor)
    UserMembership = apps.get_model('membership', 'UserMembership')
    membership = UserMembership.objects.filter(user=request.user, status='ACTIVE').first()

    context = {
        'active_nav': 'profile',
        'page_title': 'My Profile',
        'membership': membership,
    }
    
    return render(request, 'profile_view.html', context)
