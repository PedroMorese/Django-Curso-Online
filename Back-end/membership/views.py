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
