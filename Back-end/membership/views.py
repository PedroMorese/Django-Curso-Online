"""
Vistas del dominio Membership (Backend).

Estas vistas son endpoints del dominio para obtener datos.
NO renderizan HTML de UX - solo retornan datos o respuestas JSON.
"""

from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.contrib.auth.decorators import login_required


@require_GET
def list_plans(request):
    """
    Obtiene todos los planes de membresía activos.
    Endpoint: GET /api/membership/plans/
    """
    from .services import MembershipService
    
    plans = MembershipService.get_available_plans()
    
    data = [{
        'id': plan.id,
        'name': plan.name,
        'slug': plan.slug,
        'description': plan.description,
        'plan_type': plan.plan_type,
        'duration_days': plan.duration_days,
        'price': str(plan.price),
        'original_price': str(plan.original_price) if plan.original_price else None,
        'features': plan.features,
        'is_featured': plan.is_featured,
        'savings': str(plan.savings),
        'savings_percentage': plan.savings_percentage,
    } for plan in plans]
    
    return JsonResponse({'plans': data})


@require_GET
def plan_detail(request, slug):
    """
    Obtiene detalles de un plan específico.
    Endpoint: GET /api/membership/plans/<slug>/
    """
    from .services import MembershipService
    
    plan = MembershipService.get_plan_by_slug(slug)
    
    if not plan:
        return JsonResponse({'error': 'Plan no encontrado'}, status=404)
    
    data = {
        'id': plan.id,
        'name': plan.name,
        'slug': plan.slug,
        'description': plan.description,
        'plan_type': plan.plan_type,
        'duration_days': plan.duration_days,
        'price': str(plan.price),
        'original_price': str(plan.original_price) if plan.original_price else None,
        'features': plan.features,
        'is_featured': plan.is_featured,
        'savings': str(plan.savings),
        'savings_percentage': plan.savings_percentage,
    }
    
    return JsonResponse(data)


@login_required
@require_GET
def user_membership(request):
    """
    Obtiene la membresía activa del usuario autenticado.
    Endpoint: GET /api/membership/my-membership/
    """
    from .services import MembershipService
    
    membership = MembershipService.get_user_active_membership(request.user)
    
    if not membership:
        return JsonResponse({
            'has_membership': False,
            'membership': None
        })
    
    data = {
        'has_membership': True,
        'membership': {
            'id': membership.id,
            'plan_name': membership.plan.name,
            'plan_type': membership.plan.plan_type,
            'status': membership.status,
            'start_date': membership.start_date.isoformat(),
            'end_date': membership.end_date.isoformat(),
            'days_remaining': membership.days_remaining,
            'is_expiring_soon': membership.is_expiring_soon,
            'auto_renew': membership.auto_renew,
        }
    }
    
    return JsonResponse(data)


@login_required
def update_plan_settings(request):
    """
    Actualiza la configuración de un plan de membresía.
    Endpoint: POST /api/membership/plans/update/
    
    Requiere permisos de administrador.
    
    Body JSON:
    {
        "slug": "monthly" | "annual",
        "price": 29.00,
        "original_price": 35.00 (opcional),
        "is_active": true
    }
    """
    import json
    from django.views.decorators.csrf import csrf_exempt
    
    # Verificar que el usuario sea admin
    if not (request.user.is_staff or request.user.is_superuser or 
            (hasattr(request.user, 'role') and request.user.role == 'ADMIN')):
        return JsonResponse({'error': 'No tienes permisos para realizar esta acción'}, status=403)
    
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON inválido'}, status=400)
    
    # Validar campos requeridos
    slug = data.get('slug')
    if not slug or slug not in ['monthly', 'annual']:
        return JsonResponse({'error': 'Slug inválido. Debe ser "monthly" o "annual"'}, status=400)
    
    price = data.get('price')
    if price is None:
        return JsonResponse({'error': 'El campo "price" es requerido'}, status=400)
    
    try:
        price = float(price)
        if price < 0:
            raise ValueError("El precio no puede ser negativo")
    except (ValueError, TypeError):
        return JsonResponse({'error': 'Precio inválido'}, status=400)
    
    # Obtener precio original (opcional)
    original_price = data.get('original_price')
    if original_price:
        try:
            original_price = float(original_price)
            if original_price < 0:
                raise ValueError("El precio original no puede ser negativo")
        except (ValueError, TypeError):
            return JsonResponse({'error': 'Precio original inválido'}, status=400)
    else:
        original_price = None
    
    # Obtener estado activo
    is_active = data.get('is_active', True)
    
    # Actualizar el plan
    from .models import MembershipPlan
    
    try:
        plan = MembershipPlan.objects.get(slug=slug)
        plan.price = price
        plan.original_price = original_price
        plan.is_active = is_active
        plan.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Plan {plan.name} actualizado correctamente',
            'plan': {
                'id': plan.id,
                'name': plan.name,
                'slug': plan.slug,
                'price': str(plan.price),
                'original_price': str(plan.original_price) if plan.original_price else None,
                'is_active': plan.is_active,
                'savings': str(plan.savings) if plan.savings else None,
            }
        })
    except MembershipPlan.DoesNotExist:
        return JsonResponse({'error': f'Plan con slug "{slug}" no encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'error': f'Error al actualizar el plan: {str(e)}'}, status=500)
