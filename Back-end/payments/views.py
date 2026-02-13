"""
Vistas y lógica de negocio para el sistema de pagos.

Este módulo contiene toda la lógica para procesar pagos de membresías.
En modo DEMO, simula el procesamiento sin realizar cargos reales.
"""

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.apps import apps
from django.utils import timezone
from dateutil.relativedelta import relativedelta
import json
import uuid
import re


def generate_transaction_id():
    """
    Genera un ID único de transacción.
    
    Returns:
        str: ID de transacción en formato TXN-XXXXXXXX
    """
    return f"TXN-{uuid.uuid4().hex[:12].upper()}"


def validate_card_number(card_number):
    """
    Valida el número de tarjeta usando el algoritmo de Luhn.
    
    Args:
        card_number (str): Número de tarjeta a validar
        
    Returns:
        bool: True si es válido, False en caso contrario
    """
    # Remover espacios y guiones
    card_number = re.sub(r'[\s-]', '', card_number)
    
    # Verificar que solo contenga dígitos
    if not card_number.isdigit():
        return False
    
    # Verificar longitud (13-19 dígitos)
    if len(card_number) < 13 or len(card_number) > 19:
        return False
    
    # Algoritmo de Luhn
    def luhn_checksum(card_num):
        def digits_of(n):
            return [int(d) for d in str(n)]
        digits = digits_of(card_num)
        odd_digits = digits[-1::-2]
        even_digits = digits[-2::-2]
        checksum = sum(odd_digits)
        for d in even_digits:
            checksum += sum(digits_of(d * 2))
        return checksum % 10
    
    return luhn_checksum(card_number) == 0


def get_card_brand(card_number):
    """
    Detecta la marca de la tarjeta basándose en el número.
    
    Args:
        card_number (str): Número de tarjeta
        
    Returns:
        str: Marca de la tarjeta (VISA, MASTERCARD, AMEX, etc.)
    """
    card_number = re.sub(r'[\s-]', '', card_number)
    
    if card_number.startswith('4'):
        return 'VISA'
    elif card_number.startswith(('51', '52', '53', '54', '55')):
        return 'MASTERCARD'
    elif card_number.startswith(('34', '37')):
        return 'AMEX'
    elif card_number.startswith('6011') or card_number.startswith('65'):
        return 'DISCOVER'
    else:
        return 'OTHER'


def validate_expiry_date(expiry):
    """
    Valida la fecha de expiración de la tarjeta.
    
    Args:
        expiry (str): Fecha en formato MM/YY
        
    Returns:
        bool: True si es válida y futura, False en caso contrario
    """
    try:
        month, year = expiry.split('/')
        month = int(month)
        year = int('20' + year)  # Asume 20XX
        
        if month < 1 or month > 12:
            return False
        
        # Verificar que sea fecha futura
        now = timezone.now()
        if year < now.year or (year == now.year and month < now.month):
            return False
        
        return True
    except:
        return False


@require_http_methods(["POST"])
@login_required
def process_payment(request):
    """
    Procesa un pago de membresía.
    
    Este endpoint recibe los datos de pago, valida la información,
    crea el registro de pago y activa la membresía del usuario.
    
    En modo DEMO, no se realizan cargos reales.
    
    Request JSON:
        {
            "plan_slug": "monthly",
            "payment_method": "CREDIT_CARD",
            "card_number": "4242424242424242",
            "card_expiry": "12/25",
            "card_cvv": "123",
            "cardholder_name": "John Doe"
        }
    
    Returns:
        JsonResponse: Resultado del procesamiento
    """
    try:
        # Parsear datos del request
        data = json.loads(request.body)
        
        plan_slug = data.get('plan_slug')
        payment_method = data.get('payment_method', 'CREDIT_CARD')
        card_number = data.get('card_number', '')
        card_expiry = data.get('card_expiry', '')
        card_cvv = data.get('card_cvv', '')
        cardholder_name = data.get('cardholder_name', '')
        
        # Obtener modelos
        MembershipPlan = apps.get_model('membership', 'MembershipPlan')
        UserMembership = apps.get_model('membership', 'UserMembership')
        Payment = apps.get_model('payments', 'Payment')
        
        # Validar que el plan existe
        plan = MembershipPlan.objects.filter(slug=plan_slug, is_active=True).first()
        if not plan:
            return JsonResponse({
                'success': False,
                'error': 'Plan no encontrado o no está activo.'
            }, status=404)
        
        # Verificar que el usuario no tenga ya una membresía activa
        existing_membership = UserMembership.objects.filter(
            user=request.user,
            status='ACTIVE',
            start_date__lte=timezone.now(),
            end_date__gte=timezone.now()
        ).first()
        
        if existing_membership:
            return JsonResponse({
                'success': False,
                'error': 'Ya tienes una membresía activa.'
            }, status=400)
        
        # Validar datos de la tarjeta
        if not cardholder_name or len(cardholder_name.strip()) == 0:
            return JsonResponse({
                'success': False,
                'error': 'El nombre del titular es requerido.'
            }, status=400)
        
        if not validate_card_number(card_number):
            return JsonResponse({
                'success': False,
                'error': 'Número de tarjeta inválido.'
            }, status=400)
        
        if not validate_expiry_date(card_expiry):
            return JsonResponse({
                'success': False,
                'error': 'Fecha de expiración inválida o vencida.'
            }, status=400)
        
        if not card_cvv or len(card_cvv) < 3 or len(card_cvv) > 4:
            return JsonResponse({
                'success': False,
                'error': 'CVV inválido.'
            }, status=400)
        
        # Detectar marca de tarjeta
        card_brand = get_card_brand(card_number)
        
        # Obtener últimos 4 dígitos
        card_last_four = card_number.replace(' ', '').replace('-', '')[-4:]
        
        # Generar ID de transacción único
        transaction_id = generate_transaction_id()
        
        # Crear registro de pago
        payment = Payment.objects.create(
            user=request.user,
            membership_plan=plan,
            amount=plan.price,
            currency='USD',
            payment_method=payment_method,
            card_last_four=card_last_four,
            card_brand=card_brand,
            cardholder_name=cardholder_name,
            status='COMPLETED',  # En DEMO siempre es exitoso
            transaction_id=transaction_id
        )
        
        # Calcular fechas de membresía
        start_date = timezone.now()
        if plan.plan_type == 'MONTHLY':
            end_date = start_date + relativedelta(months=1)
        elif plan.plan_type == 'ANNUAL':
            end_date = start_date + relativedelta(years=1)
        else:
            end_date = start_date + relativedelta(months=1)
        
        # Crear membresía
        membership = UserMembership.objects.create(
            user=request.user,
            plan=plan,
            start_date=start_date,
            end_date=end_date,
            status='ACTIVE',
            payment_reference=transaction_id
        )
        
        return JsonResponse({
            'success': True,
            'payment_id': payment.id,
            'transaction_id': transaction_id,
            'membership_id': membership.id,
            'message': f'¡Pago procesado exitosamente! Membresía {plan.name} activada.',
            'redirect_url': '/membership/payment/success/'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Datos JSON inválidos.'
        }, status=400)
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error al procesar el pago: {str(e)}'
        }, status=500)
