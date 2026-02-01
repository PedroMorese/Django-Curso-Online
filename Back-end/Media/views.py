import os
import uuid
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings

@csrf_exempt
def upload_file(request):
    """
    Endpoint para subir archivos.
    Recibe un archivo en el campo 'file' del POST.
    Retorna la URL absoluta para acceder al archivo.
    """
    if request.method == 'POST' and request.FILES.get('file'):
        file_obj = request.FILES['file']
        
        # Generar un nombre único para evitar colisiones
        ext = os.path.splitext(file_obj.name)[1]
        filename = f"{uuid.uuid4().hex}{ext}"
        
        # Guardar el archivo en la carpeta media/uploads/
        path = default_storage.save(f'uploads/{filename}', ContentFile(file_obj.read()))
        
        # Generar la URL completa (absoluta si es posible para el frontend)
        file_url = f"{settings.MEDIA_URL}{path}"
        
        # Opcional: Si necesitas la URL absoluta con dominio
        # full_url = request.build_absolute_uri(file_url)
        
        return JsonResponse({
            'status': 'success',
            'url': file_url,
            'name': file_obj.name
        })
        
    return JsonResponse({
        'status': 'error',
        'message': 'No file was provided or method not allowed.'
    }, status=400)
