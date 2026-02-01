"""
Management command para inicializar los planes de membresía.
"""

from django.core.management.base import BaseCommand
from Back_end.membership.models import MembershipPlan


class Command(BaseCommand):
    help = 'Inicializa los planes de membresía predeterminados'

    def handle(self, *args, **options):
        self.stdout.write('Inicializando planes de membresía...')
        
        # Plan Mensual
        monthly_plan, created = MembershipPlan.objects.get_or_create(
            slug='monthly',
            defaults={
                'name': 'Monthly',
                'plan_type': 'MONTHLY',
                'price': 29.00,
                'duration_days': 30,
                'is_active': True,
                'description': 'Flexibility to learn at your own pace.',
                'features': [
                    'Access to all courses',
                    'Monthly billing',
                    'Cancel anytime',
                    'Email support'
                ],
                'display_order': 1
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Plan Mensual creado: {monthly_plan}'))
        else:
            self.stdout.write(self.style.WARNING(f'○ Plan Mensual ya existe: {monthly_plan}'))
        
        # Plan Anual
        annual_plan, created = MembershipPlan.objects.get_or_create(
            slug='annual',
            defaults={
                'name': 'Annual',
                'plan_type': 'ANNUAL',
                'price': 249.00,
                'original_price': 348.00,
                'duration_days': 365,
                'is_active': True,
                'is_featured': True,
                'description': 'Maximum value for serious learners.',
                'features': [
                    'Access to all courses',
                    'Annual billing',
                    'Save 28%',
                    'Priority support',
                    'Exclusive content'
                ],
                'display_order': 2
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Plan Anual creado: {annual_plan}'))
        else:
            self.stdout.write(self.style.WARNING(f'○ Plan Anual ya existe: {annual_plan}'))
        
        self.stdout.write(self.style.SUCCESS('\n✓ Inicialización completada!'))
        self.stdout.write(f'\nPlanes disponibles:')
        for plan in MembershipPlan.objects.all():
            status = '✓ Activo' if plan.is_active else '✗ Inactivo'
            self.stdout.write(f'  - {plan.name}: ${plan.price} ({status})')
