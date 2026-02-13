"""
Modelos para el sistema de pagos.

Este módulo contiene el modelo Payment que registra todas las transacciones
de pago realizadas por los usuarios al suscribirse a planes de membresía.
"""

from django.db import models
from django.conf import settings


class Payment(models.Model):
    """
    Modelo para registrar transacciones de pago.
    
    Almacena información sobre pagos realizados por usuarios para
    suscripciones de membresía. En modo DEMO, no se realizan cargos reales.
    """
    
    PAYMENT_METHOD_CHOICES = [
        ('CREDIT_CARD', 'Credit Card'),
        ('DEBIT_CARD', 'Debit Card'),
        ('PAYPAL', 'PayPal'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
        ('REFUNDED', 'Refunded'),
    ]
    
    CARD_BRAND_CHOICES = [
        ('VISA', 'Visa'),
        ('MASTERCARD', 'Mastercard'),
        ('AMEX', 'American Express'),
        ('DISCOVER', 'Discover'),
        ('OTHER', 'Other'),
    ]
    
    # Relaciones
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name='Usuario'
    )
    membership_plan = models.ForeignKey(
        'membership.MembershipPlan',
        on_delete=models.PROTECT,
        related_name='payments',
        verbose_name='Plan de Membresía'
    )
    
    # Información del pago
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Monto'
    )
    currency = models.CharField(
        max_length=3,
        default='USD',
        verbose_name='Moneda'
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        verbose_name='Método de Pago'
    )
    
    # Información de la tarjeta (solo últimos 4 dígitos por seguridad)
    card_last_four = models.CharField(
        max_length=4,
        blank=True,
        verbose_name='Últimos 4 Dígitos'
    )
    card_brand = models.CharField(
        max_length=20,
        choices=CARD_BRAND_CHOICES,
        blank=True,
        verbose_name='Marca de Tarjeta'
    )
    cardholder_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Nombre del Titular'
    )
    
    # Estado y tracking
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING',
        verbose_name='Estado'
    )
    transaction_id = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='ID de Transacción'
    )
    
    # Timestamps
    payment_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Pago'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Creación'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Fecha de Actualización'
    )
    
    class Meta:
        db_table = 'payments_payment'
        verbose_name = 'Pago'
        verbose_name_plural = 'Pagos'
        ordering = ['-payment_date']
        indexes = [
            models.Index(fields=['-payment_date']),
            models.Index(fields=['user', 'status']),
            models.Index(fields=['transaction_id']),
        ]
    
    def __str__(self):
        return f"Payment {self.transaction_id} - {self.user.email} - ${self.amount}"
    
    @property
    def is_successful(self):
        """Retorna True si el pago fue completado exitosamente."""
        return self.status == 'COMPLETED'
    
    @property
    def masked_card_number(self):
        """Retorna el número de tarjeta enmascarado."""
        if self.card_last_four:
            return f"**** **** **** {self.card_last_four}"
        return "N/A"
