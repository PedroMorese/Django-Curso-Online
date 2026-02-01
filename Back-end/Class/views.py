"""
Vistas del dominio Class (Backend).

Endpoints para operaciones CRUD de clases.
"""

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
import json


def _get_class_model():
    """Get the Class model lazily to avoid circular imports."""
    from django.apps import apps
    return apps.get_model('class_app', 'Class')


@require_GET
def class_list(request):
    """
    Lista todas las clases.
    GET /api/classes/
    """
    Class = _get_class_model()
    
    curso_id = request.GET.get('curso_id')
    
    classes = Class.objects.all()
    
    if curso_id:
        classes = classes.filter(curso_id=curso_id)
    
    classes = classes.order_by('orden')
    
    data = [{
        'id': c.id,
        'titulo': c.titulo,
        'descripcion': c.descripcion,
        'orden': c.orden,
        'duracion_estimada': c.duracion_estimada,
        'curso_id': c.curso_id,
    } for c in classes]
    
    return JsonResponse({'classes': data})


@require_GET
def class_detail(request, class_id):
    """
    Obtiene detalle de una clase específica.
    GET /api/classes/<class_id>/
    """
    Class = _get_class_model()
    
    try:
        clase = Class.objects.select_related('curso').get(id=class_id)
    except Class.DoesNotExist:
        return JsonResponse({'error': 'Clase no encontrada'}, status=404)
    
    # Verificar que el profesor sea el dueño del curso
    if clase.curso.profesor != request.user and not request.user.is_staff:
        return JsonResponse({'error': 'No tienes permisos para ver esta clase'}, status=403)
    
    data = {
        'id': clase.id,
        'titulo': clase.titulo,
        'descripcion': clase.descripcion,
        'orden': clase.orden,
        'duracion_estimada': clase.duracion_estimada,
        'video_url': clase.video_url,
        'imagen_portada': clase.imagen_portada, # Añadido imagen_portada
        'curso_id': clase.curso_id,
    }
    
    return JsonResponse(data)


@csrf_exempt
@require_POST
def class_update(request, class_id):
    """
    Actualiza una clase específica.
    POST /api/classes/<class_id>/update/
    """
    Class = _get_class_model()
    
    try:
        clase = Class.objects.select_related('curso').get(id=class_id)
    except Class.DoesNotExist:
        return JsonResponse({'error': 'Clase no encontrada'}, status=404)
    
    # Verificar que el profesor sea el dueño del curso
    if clase.curso.profesor != request.user and not request.user.is_staff:
        return JsonResponse({'error': 'No tienes permisos para modificar esta clase'}, status=403)
    
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        # Si no es JSON, fallamos
        return JsonResponse({'error': 'Formato JSON inválido'}, status=400)
    
    # Actualizar campos permitidos
    clase.titulo = data.get('titulo', clase.titulo)
    clase.descripcion = data.get('descripcion', clase.descripcion)
    clase.orden = data.get('orden', clase.orden)
    clase.duracion_estimada = data.get('duracion_estimada', clase.duracion_estimada)
    clase.video_url = data.get('video_url', clase.video_url)
    clase.imagen_portada = data.get('imagen_portada', clase.imagen_portada)
    
    clase.save()
    
    return JsonResponse({
        'status': 'success',
        'message': 'Clase actualizada correctamente',
        'clase': {
            'id': clase.id,
            'titulo': clase.titulo,
            'orden': clase.orden,
        }
    })
