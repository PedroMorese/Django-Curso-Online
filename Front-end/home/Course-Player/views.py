"""
Vistas UX del Reproductor de Cursos.

Este módulo contiene las vistas UX para:
- Reproducción de clases
- Navegación entre lecciones
- Recursos descargables

RESPONSABILIDADES:
- Validar acceso del usuario (membresía)
- Cargar datos de clase y curso
- Renderizar reproductor
- NO contener lógica de negocio
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.apps import apps


@login_required
def course_player(request, course_id, class_id=None):
    """
    Vista del reproductor de clase.
    
    Muestra el video de la clase con navegación
    entre lecciones y recursos disponibles.
    """
    Course = apps.get_model('course_app', 'Course')
    
    # Obtener el curso
    course = get_object_or_404(Course, id=course_id, publicado=True)
    
    # Verificar acceso (membresía activa) - opcional
    try:
        UserMembership = apps.get_model('membership', 'UserMembership')
        from django.utils import timezone
        
        has_active = UserMembership.objects.filter(
            user=request.user,
            status='ACTIVE',
            start_date__lte=timezone.now(),
            end_date__gte=timezone.now()
        ).exists()
        
        if not has_active:
            messages.warning(request, 'Necesitas una membresía activa para acceder a este contenido.')
            return redirect('home:membership_plans')
    except Exception:
        # Si no hay sistema de membresías, permitir acceso
        pass
    
    # Obtener todas las clases del curso
    try:
        Class = apps.get_model('class_app', 'Class')
        all_classes = Class.objects.filter(curso=course).order_by('orden')
    except:
        all_classes = []
    
    # Determinar clase actual
    current_class = None
    if class_id:
        try:
            Class = apps.get_model('class_app', 'Class')
            current_class = get_object_or_404(Class, id=class_id, curso=course)
        except:
            pass
    elif all_classes:
        current_class = all_classes.first()
    
    # Calcular clase anterior y siguiente
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
    
    # Calcular progreso
    total_classes = all_classes.count() if hasattr(all_classes, 'count') else len(list(all_classes))
    current_index = 0
    if current_class:
        try:
            current_index = list(all_classes).index(current_class) + 1
        except ValueError:
            current_index = 1
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
def course_overview(request, course_id):
    """
    Vista general del curso (lista de clases).
    """
    Course = apps.get_model('course_app', 'Course')
    
    course = get_object_or_404(Course, id=course_id, publicado=True)
    
    try:
        Class = apps.get_model('class_app', 'Class')
        classes = Class.objects.filter(curso=course).order_by('orden')
    except:
        classes = []
    
    context = {
        'course': course,
        'classes': classes,
    }
    
    return render(request, 'course_player/overview.html', context)
