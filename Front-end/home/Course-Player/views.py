"""
Vistas UX del Reproductor de Cursos.

Este módulo contiene las vistas UX para:
- Reproducción de clases
- Navegación entre lecciones
- Recursos descargables
- Emisión de certificados de participación

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
from django.utils import timezone


# ─────────────────────────────────────────────────────────────────────────────
# Helper: verificación de membresía activa
# ─────────────────────────────────────────────────────────────────────────────

def _require_active_membership(request):
    """
    Verifica que el usuario tenga una membresía ACTIVE cuya end_date no haya pasado.

    Retorna True si tiene acceso.
    Retorna False si no tiene membresía activa (la función NO redirige,
    el caller decide qué hacer).

    Nunca silencia errores de importación/ORM — si hay un problema en el
    sistema de membresías, lanza la excepción para que sea visible.
    """
    UserMembership = apps.get_model('membership', 'UserMembership')
    now = timezone.now()

    return UserMembership.objects.filter(
        user=request.user,
        status='ACTIVE',
        start_date__lte=now,
        end_date__gte=now,
    ).exists()


# ─────────────────────────────────────────────────────────────────────────────
# Vistas
# ─────────────────────────────────────────────────────────────────────────────

@login_required
def course_player(request, course_id, class_id=None):
    """
    Vista del reproductor de clase.

    Requiere membresía ACTIVE. Si el usuario canceló su membresía,
    es redirigido a la página de planes sin importar si antes tenía acceso.
    """
    Course = apps.get_model('course_app', 'Course')

    # Verificar membresía ANTES de cargar cualquier dato de curso.
    # No se captura la excepción: si el modelo falla, Django mostrará
    # el error real en vez de dar acceso indebido.
    if not _require_active_membership(request):
        messages.warning(
            request,
            'Necesitas una membresía activa para acceder a este contenido. '
            'Tu membresía puede haber expirado o sido cancelada.'
        )
        return redirect('home:membership_plans')

    # Obtener el curso
    course = get_object_or_404(Course, id=course_id, publicado=True)

    # Obtener todas las clases del curso
    try:
        Class = apps.get_model('class_app', 'Class')
        all_classes = Class.objects.filter(curso=course).order_by('orden')
    except Exception:
        all_classes = []

    # Determinar clase actual
    current_class = None
    if class_id:
        try:
            Class = apps.get_model('class_app', 'Class')
            current_class = get_object_or_404(Class, id=class_id, curso=course)
        except Exception:
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

    # Es la última clase → habilitar botón "Complete Course"
    is_last_class = (next_class is None and current_class is not None)

    context = {
        'course': course,
        'current_class': current_class,
        'all_classes': all_classes,
        'prev_class': prev_class,
        'next_class': next_class,
        'progress': progress,
        'current_index': current_index,
        'total_classes': total_classes,
        'is_last_class': is_last_class,
    }

    return render(request, 'course_player/player.html', context)


@login_required
def course_overview(request, course_id):
    """
    Vista general del curso (lista de clases).

    Requiere membresía activa, igual que el reproductor.
    """
    # Verificar membresía — misma regla que course_player
    if not _require_active_membership(request):
        messages.warning(
            request,
            'Necesitas una membresía activa para acceder a este contenido.'
        )
        return redirect('home:membership_plans')

    Course = apps.get_model('course_app', 'Course')
    course = get_object_or_404(Course, id=course_id, publicado=True)

    try:
        Class = apps.get_model('class_app', 'Class')
        classes = Class.objects.filter(curso=course).order_by('orden')
    except Exception:
        classes = []

    context = {
        'course': course,
        'classes': classes,
    }

    return render(request, 'course_player/overview.html', context)


@login_required
def course_certificate(request, course_id):
    """
    Emite (o recupera) el certificado de participación del usuario para un curso.

    - GET  → muestra el certificado ya emitido (o lo emite si no existe).
    - POST → mismo comportamiento; se usa cuando viene del botón "Complete Course".

    Requiere membresía activa para evitar que usuarios sin membresía
    generen certificados accediendo directamente a la URL.
    """
    # ── 1. Verificar membresía ─────────────────────────────────────────────
    if not _require_active_membership(request):
        messages.warning(
            request,
            'Necesitas una membresía activa para obtener un certificado.'
        )
        return redirect('home:membership_plans')

    # ── 2. Obtener curso ───────────────────────────────────────────────────
    Course      = apps.get_model('course_app', 'Course')
    Certificate = apps.get_model('course_app', 'Certificate')

    course = get_object_or_404(Course, id=course_id, publicado=True)

    # ── 3. Emitir o recuperar el certificado ───────────────────────────────
    certificado, created = Certificate.objects.get_or_create(
        usuario=request.user,
        curso=course,
    )

    if created:
        messages.success(
            request,
            f'🎉 ¡Felicitaciones! Has completado "{course.titulo}". '
            'Tu certificado ha sido emitido.'
        )

    # ── 4. Datos del instructor ────────────────────────────────────────────
    instructor = getattr(course, 'profesor', None)

    context = {
        'curso'        : course,
        'certificado'  : certificado,
        'instructor'   : instructor,
    }

    return render(request, 'course_player/certificado.html', context)
