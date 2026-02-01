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
        clase = Class.objects.get(id=class_id)
    except Class.DoesNotExist:
        return JsonResponse({'error': 'Clase no encontrada'}, status=404)
    
    data = {
        'id': clase.id,
        'titulo': clase.titulo,
        'descripcion': clase.descripcion,
        'orden': clase.orden,
        'duracion_estimada': clase.duracion_estimada,
        'video_url': clase.video_url,
        'curso_id': clase.curso_id,
    }
    
    return JsonResponse(data)
