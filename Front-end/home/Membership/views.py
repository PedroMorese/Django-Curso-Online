"""
Vistas UX de Membresías para clientes.

Este módulo contiene las vistas UX para:
- Listado de planes de membresía
- Proceso de suscripción

RESPONSABILIDADES:
- Mostrar planes disponibles
- Validar estado del usuario
- NO contener lógica de negocio
"""

from django.shortcuts import render, redirect
from django.contrib import messages
from django.apps import apps


def membership_plans(request):
    """
    Vista de planes de membresía disponibles.
    
    Muestra todos los planes activos con sus características
    y precios para que el usuario pueda seleccionar.
    """
    # Obtener planes del backend
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
        
        # Verificar si el usuario ya tiene membresía
        user_membership = None
        if request.user.is_authenticated:
            user_membership = UserMembership.objects.filter(
                user=request.user,
                status='ACTIVE',
                start_date__lte=timezone.now(),
                end_date__gte=timezone.now()
            ).first()
            
    except Exception:
        # Fallback con datos de ejemplo si los servicios no están disponibles
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
        'selected_period': 'monthly'
    }
    
    return render(request, 'membership/plans.html', context)


def subscribe(request, plan_slug):
    """
    Inicia el proceso de suscripción a un plan.
    """
    if not request.user.is_authenticated:
        messages.info(request, 'Inicia sesión para suscribirte.')
        return redirect('Auth:login')
    
    try:
        MembershipPlan = apps.get_model('membership', 'MembershipPlan')
        UserMembership = apps.get_model('membership', 'UserMembership')
        from django.utils import timezone
        from dateutil.relativedelta import relativedelta
        
        plan = MembershipPlan.objects.filter(slug=plan_slug, is_active=True).first()
        if not plan:
            messages.error(request, 'Plan no encontrado.')
            return redirect('membership_ux:plans')
        
        # Verificar si ya tiene membresía activa
        existing = UserMembership.objects.filter(
            user=request.user,
            status='ACTIVE',
            start_date__lte=timezone.now(),
            end_date__gte=timezone.now()
        ).first()
        
        if existing:
            messages.info(request, 'Ya tienes una membresía activa.')
            return redirect('membership_ux:plans')
        
        # Calcular fechas
        start_date = timezone.now()
        if plan.plan_type == 'MONTHLY':
            end_date = start_date + relativedelta(months=1)
        elif plan.plan_type == 'ANNUAL':
            end_date = start_date + relativedelta(years=1)
        else:
            end_date = start_date + relativedelta(months=1)
        
        # Crear membresía (en producción iría a pasarela de pago)
        membership = UserMembership.objects.create(
            user=request.user,
            plan=plan,
            start_date=start_date,
            end_date=end_date,
            status='ACTIVE',
            payment_reference='DEMO-' + str(request.user.id)
        )
        
        messages.success(request, f'¡Suscripción a {plan.name} activada exitosamente!')
        return redirect('home:index')
        
    except Exception as e:
        messages.error(request, 'Servicio no disponible temporalmente.')
        return redirect('membership_ux:plans')
