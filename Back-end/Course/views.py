import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db.models import Q
from .models import Course

User = get_user_model()


def _get_user_from_request(request):
    """
    Helper para obtener el usuario autenticado.
    En producción, usar request.user directamente si hay autenticación por sesión.
    """
    if request.user.is_authenticated:
        return request.user
    return None


def _is_profesor_or_admin(user):
    """Verifica si el usuario es profesor o admin"""
    if not user:
        return False
    role = getattr(user, 'role', '').upper()
    return role in ['PROFESOR', 'ADMIN']


def _is_course_owner(user, course):
    """Verifica si el usuario es el dueño del curso o es admin"""
    if not user:
        return False
    role = getattr(user, 'role', '').upper()
    return course.profesor == user or role == 'ADMIN'


@csrf_exempt
def course_list(request):
    """
    GET: Lista todos los cursos (filtrados según el usuario)
    POST: Crea un nuevo curso (solo PROFESOR o ADMIN)
    
    Query params para GET:
    - publicado: true/false (filtrar por estado de publicación)
    - nivel: PRINCIPIANTE/INTERMEDIO/AVANZADO
    - search: buscar en título y descripción
    - profesor_id: filtrar por profesor
    """
    if request.method == 'GET':
        user = _get_user_from_request(request)
        
        # Iniciar con todos los cursos
        cursos = Course.objects.all()
        
        # Filtrar según el rol del usuario
        role = getattr(user, 'role', '').upper() if user else None
        
        if role == 'ADMIN':
            # Admin ve todos los cursos
            pass
        elif role == 'PROFESOR':
            # Profesor ve sus cursos y los publicados
            cursos = cursos.filter(Q(profesor=user) | Q(publicado=True))
        else:
            # Cliente o no autenticado solo ve cursos publicados
            cursos = cursos.filter(publicado=True)
        
        # Aplicar filtros adicionales
        publicado = request.GET.get('publicado')
        if publicado is not None:
            publicado_bool = publicado.lower() == 'true'
            cursos = cursos.filter(publicado=publicado_bool)
        
        nivel = request.GET.get('nivel')
        if nivel:
            cursos = cursos.filter(nivel=nivel.upper())
        
        search = request.GET.get('search')
        if search:
            cursos = cursos.filter(
                Q(titulo__icontains=search) | Q(descripcion__icontains=search)
            )
        
        profesor_id = request.GET.get('profesor_id')
        if profesor_id:
            cursos = cursos.filter(profesor_id=profesor_id)
        
        # Serializar cursos
        cursos_data = []
        for curso in cursos.select_related('profesor'):
            cursos_data.append({
                'id': curso.id,
                'titulo': curso.titulo,
                'descripcion': curso.descripcion,
                'imagen_portada': curso.imagen_portada,
                'profesor': {
                    'id': curso.profesor.id,
                    'email': getattr(curso.profesor, 'email', None),
                    'nombre': f"{getattr(curso.profesor, 'first_name', '')} {getattr(curso.profesor, 'last_name', '')}".strip()
                },
                'fecha_creacion': curso.fecha_creacion.isoformat(),
                'fecha_actualizacion': curso.fecha_actualizacion.isoformat(),
                'publicado': curso.publicado,
                'nivel': curso.nivel,
                'duracion_estimada': curso.duracion_estimada,
                'total_clases': curso.total_clases,
            })
        
        return JsonResponse({'cursos': cursos_data}, status=200)
    
    elif request.method == 'POST':
        user = _get_user_from_request(request)
        
        if not user or not user.is_authenticated:
            return JsonResponse({'detail': 'Authentication required'}, status=401)
        
        if not _is_profesor_or_admin(user):
            return JsonResponse({'detail': 'Only professors and admins can create courses'}, status=403)
        
        try:
            payload = json.loads(request.body or b'{}')
        except Exception:
            return JsonResponse({'detail': 'Invalid JSON'}, status=400)
        
        titulo = payload.get('titulo')
        descripcion = payload.get('descripcion', '')
        imagen_portada = payload.get('imagen_portada', '')
        nivel = (payload.get('nivel') or 'PRINCIPIANTE').upper()
        duracion_estimada = payload.get('duracion_estimada')
        publicado = payload.get('publicado', False)
        
        if not titulo:
            return JsonResponse({'detail': 'Title is required'}, status=400)
        
        if nivel not in ['PRINCIPIANTE', 'INTERMEDIO', 'AVANZADO']:
            return JsonResponse({'detail': 'Invalid level. Must be PRINCIPIANTE, INTERMEDIO, or AVANZADO'}, status=400)
        
        try:
            curso = Course.objects.create(
                titulo=titulo,
                descripcion=descripcion,
                imagen_portada=imagen_portada,
                profesor=user,
                nivel=nivel,
                duracion_estimada=duracion_estimada,
                publicado=publicado
            )
            
            return JsonResponse({
                'id': curso.id,
                'titulo': curso.titulo,
                'descripcion': curso.descripcion,
                'imagen_portada': curso.imagen_portada,
                'profesor_id': curso.profesor.id,
                'fecha_creacion': curso.fecha_creacion.isoformat(),
                'publicado': curso.publicado,
                'nivel': curso.nivel,
                'duracion_estimada': curso.duracion_estimada,
            }, status=201)
        
        except Exception as e:
            return JsonResponse({'detail': f'Error creating course: {str(e)}'}, status=500)
    
    else:
        return JsonResponse({'detail': 'Method not allowed'}, status=405)


@csrf_exempt
def course_detail(request, course_id):
    """
    GET: Obtiene detalles de un curso específico
    PUT: Actualiza un curso (solo dueño o admin)
    DELETE: Elimina un curso (solo dueño o admin)
    """
    try:
        curso = Course.objects.select_related('profesor').get(id=course_id)
    except Course.DoesNotExist:
        return JsonResponse({'detail': 'Course not found'}, status=404)
    
    user = _get_user_from_request(request)
    
    if request.method == 'GET':
        # Verificar permisos de visualización
        role = getattr(user, 'role', '').upper() if user else None
        
        if not curso.publicado:
            # Solo el dueño o admin pueden ver cursos no publicados
            if not user or not _is_course_owner(user, curso):
                return JsonResponse({'detail': 'Course not found'}, status=404)
        
        curso_data = {
            'id': curso.id,
            'titulo': curso.titulo,
            'descripcion': curso.descripcion,
            'imagen_portada': curso.imagen_portada,
            'profesor': {
                'id': curso.profesor.id,
                'email': getattr(curso.profesor, 'email', None),
                'nombre': f"{getattr(curso.profesor, 'first_name', '')} {getattr(curso.profesor, 'last_name', '')}".strip()
            },
            'fecha_creacion': curso.fecha_creacion.isoformat(),
            'fecha_actualizacion': curso.fecha_actualizacion.isoformat(),
            'publicado': curso.publicado,
            'nivel': curso.nivel,
            'duracion_estimada': curso.duracion_estimada,
            'total_clases': curso.total_clases,
        }
        
        return JsonResponse(curso_data, status=200)
    
    elif request.method == 'PUT':
        if not user or not user.is_authenticated:
            return JsonResponse({'detail': 'Authentication required'}, status=401)
        
        if not _is_course_owner(user, curso):
            return JsonResponse({'detail': 'You do not have permission to edit this course'}, status=403)
        
        try:
            payload = json.loads(request.body or b'{}')
        except Exception:
            return JsonResponse({'detail': 'Invalid JSON'}, status=400)
        
        # Actualizar campos
        if 'titulo' in payload:
            curso.titulo = payload['titulo']
        if 'descripcion' in payload:
            curso.descripcion = payload['descripcion']
        if 'imagen_portada' in payload:
            curso.imagen_portada = payload['imagen_portada']
        if 'nivel' in payload:
            nivel = payload['nivel'].upper()
            if nivel not in ['PRINCIPIANTE', 'INTERMEDIO', 'AVANZADO']:
                return JsonResponse({'detail': 'Invalid level'}, status=400)
            curso.nivel = nivel
        if 'duracion_estimada' in payload:
            curso.duracion_estimada = payload['duracion_estimada']
        if 'publicado' in payload:
            curso.publicado = payload['publicado']
        
        try:
            curso.save()
            
            return JsonResponse({
                'id': curso.id,
                'titulo': curso.titulo,
                'descripcion': curso.descripcion,
                'imagen_portada': curso.imagen_portada,
                'profesor_id': curso.profesor.id,
                'fecha_creacion': curso.fecha_creacion.isoformat(),
                'fecha_actualizacion': curso.fecha_actualizacion.isoformat(),
                'publicado': curso.publicado,
                'nivel': curso.nivel,
                'duracion_estimada': curso.duracion_estimada,
            }, status=200)
        
        except Exception as e:
            return JsonResponse({'detail': f'Error updating course: {str(e)}'}, status=500)
    
    elif request.method == 'DELETE':
        if not user or not user.is_authenticated:
            return JsonResponse({'detail': 'Authentication required'}, status=401)
        
        if not _is_course_owner(user, curso):
            return JsonResponse({'detail': 'You do not have permission to delete this course'}, status=403)
        
        try:
            curso_id = curso.id
            curso.delete()
            return JsonResponse({'detail': 'Course deleted successfully', 'id': curso_id}, status=200)
        except Exception as e:
            return JsonResponse({'detail': f'Error deleting course: {str(e)}'}, status=500)
    
    else:
        return JsonResponse({'detail': 'Method not allowed'}, status=405)


@csrf_exempt
def course_publish(request, course_id):
    """
    POST: Publica o despublica un curso
    Body: {"publicado": true/false}
    """
    if request.method != 'POST':
        return JsonResponse({'detail': 'Method not allowed'}, status=405)
    
    try:
        curso = Course.objects.get(id=course_id)
    except Course.DoesNotExist:
        return JsonResponse({'detail': 'Course not found'}, status=404)
    
    user = _get_user_from_request(request)
    
    if not user or not user.is_authenticated:
        return JsonResponse({'detail': 'Authentication required'}, status=401)
    
    if not _is_course_owner(user, curso):
        return JsonResponse({'detail': 'You do not have permission to publish this course'}, status=403)
    
    try:
        payload = json.loads(request.body or b'{}')
    except Exception:
        return JsonResponse({'detail': 'Invalid JSON'}, status=400)
    
    publicado = payload.get('publicado')
    if publicado is None:
        return JsonResponse({'detail': 'Field "publicado" is required'}, status=400)
    
    curso.publicado = publicado
    curso.save(update_fields=['publicado'])
    
    return JsonResponse({
        'id': curso.id,
        'titulo': curso.titulo,
        'publicado': curso.publicado,
        'detail': f'Course {"published" if publicado else "unpublished"} successfully'
    }, status=200)


@csrf_exempt
def my_courses(request):
    """
    GET: Obtiene todos los cursos del profesor autenticado
    """
    if request.method != 'GET':
        return JsonResponse({'detail': 'Method not allowed'}, status=405)
    
    user = _get_user_from_request(request)
    
    if not user or not user.is_authenticated:
        return JsonResponse({'detail': 'Authentication required'}, status=401)
    
    if not _is_profesor_or_admin(user):
        return JsonResponse({'detail': 'Only professors can access this endpoint'}, status=403)
    
    cursos = Course.objects.filter(profesor=user).order_by('-fecha_creacion')
    
    cursos_data = []
    for curso in cursos:
        cursos_data.append({
            'id': curso.id,
            'titulo': curso.titulo,
            'descripcion': curso.descripcion,
            'imagen_portada': curso.imagen_portada,
            'fecha_creacion': curso.fecha_creacion.isoformat(),
            'fecha_actualizacion': curso.fecha_actualizacion.isoformat(),
            'publicado': curso.publicado,
            'nivel': curso.nivel,
            'duracion_estimada': curso.duracion_estimada,
            'total_clases': curso.total_clases,
        })
    
    return JsonResponse({'cursos': cursos_data}, status=200)
