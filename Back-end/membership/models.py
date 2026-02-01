"""
Modelos del dominio Membership.

Este módulo define los modelos para gestionar:
- Planes de membresía disponibles en la plataforma
- Suscripciones de usuarios a planes específicos

RESPONSABILIDADES DEL DOMINIO:
- Definir estructura de datos de membresías
- Contener reglas de negocio de suscripciones
- Validar estados y transiciones
- Gestionar acceso a contenido premium
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


class MembershipPlan(models.Model):
    """
    Plan de membresía disponible en la plataforma.
    
    Representa un tipo de suscripción que los usuarios pueden adquirir
    para acceder al contenido premium de la plataforma.
    """
    
    PLAN_TYPE_CHOICES = [
        ('MONTHLY', 'Mensual'),
        ('ANNUAL', 'Anual'),
        ('LIFETIME', 'Vitalicio'),
    ]
    
    # Información básica del plan
    name = models.CharField(max_length=100, verbose_name="Nombre del Plan")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="Slug")
    description = models.TextField(blank=True, verbose_name="Descripción")
    
    # Tipo y duración
    plan_type = models.CharField(
        max_length=20,
        choices=PLAN_TYPE_CHOICES,
        default='MONTHLY',
        verbose_name="Tipo de Plan"
    )
    duration_days = models.IntegerField(
        default=30,
        help_text="Duración del plan en días",
        verbose_name="Duración (días)"
    )
    
    # Precios
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Precio"
    )
    original_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Precio original (para mostrar descuento)",
        verbose_name="Precio Original"
    )
    
    # Características del plan (almacenadas como JSON)
    features = models.JSONField(
        default=list,
        blank=True,
        help_text="Lista de características del plan",
        verbose_name="Características"
    )
    
    # Estado y orden
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    is_featured = models.BooleanField(
        default=False,
        help_text="Destacar como mejor opción",
        verbose_name="Destacado"
    )
    display_order = models.IntegerField(default=0, verbose_name="Orden de Visualización")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última Actualización")
    
    class Meta:
        db_table = 'membership_plan'
        verbose_name = 'Plan de Membresía'
        verbose_name_plural = 'Planes de Membresía'
        ordering = ['display_order', 'price']
    
    def __str__(self):
        return f"{self.name} - ${self.price}"
    
    @property
    def savings(self):
        """Calcula el ahorro respecto al precio original"""
        if self.original_price and self.original_price > self.price:
            return self.original_price - self.price
        return 0
    
    @property
    def savings_percentage(self):
        """Calcula el porcentaje de ahorro"""
        if self.original_price and self.original_price > 0:
            return int(((self.original_price - self.price) / self.original_price) * 100)
        return 0


class UserMembership(models.Model):
    """
    Suscripción de un usuario a un plan de membresía.
    
    Representa la relación activa entre un usuario y un plan,
    incluyendo el período de vigencia y estado de la suscripción.
    """
    
    STATUS_CHOICES = [
        ('ACTIVE', 'Activa'),
        ('EXPIRED', 'Expirada'),
        ('CANCELLED', 'Cancelada'),
        ('PENDING', 'Pendiente de Pago'),
    ]
    
    # Relaciones
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='memberships',
        verbose_name="Usuario"
    )
    plan = models.ForeignKey(
        MembershipPlan,
        on_delete=models.PROTECT,
        related_name='subscriptions',
        verbose_name="Plan"
    )
    
    # Período de vigencia
    start_date = models.DateTimeField(
        default=timezone.now,
        verbose_name="Fecha de Inicio"
    )
    end_date = models.DateTimeField(
        verbose_name="Fecha de Expiración"
    )
    
    # Estado
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING',
        verbose_name="Estado"
    )
    
    # Opciones de renovación
    auto_renew = models.BooleanField(
        default=False,
        verbose_name="Renovación Automática"
    )
    
    # Metadata de pago
    payment_reference = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Referencia de Pago"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Registro")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última Actualización")
    
    class Meta:
        db_table = 'user_membership'
        verbose_name = 'Membresía de Usuario'
        verbose_name_plural = 'Membresías de Usuarios'
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['end_date']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.plan.name} ({self.status})"
    
    def save(self, *args, **kwargs):
        """Calcula automáticamente la fecha de expiración si no está definida"""
        if not self.end_date:
            self.end_date = self.start_date + timedelta(days=self.plan.duration_days)
        super().save(*args, **kwargs)
    
    @property
    def is_active(self):
        """Verifica si la membresía está activa"""
        return (
            self.status == 'ACTIVE' and
            self.start_date <= timezone.now() <= self.end_date
        )
    
    @property
    def days_remaining(self):
        """Calcula los días restantes de la membresía"""
        if self.is_active:
            delta = self.end_date - timezone.now()
            return max(0, delta.days)
        return 0
    
    @property
    def is_expiring_soon(self):
        """Verifica si la membresía expira en los próximos 7 días"""
        return self.is_active and self.days_remaining <= 7
    
    def activate(self):
        """Activa la membresía"""
        self.status = 'ACTIVE'
        self.save(update_fields=['status', 'updated_at'])
    
    def cancel(self):
        """Cancela la membresía"""
        self.status = 'CANCELLED'
        self.auto_renew = False
        self.save(update_fields=['status', 'auto_renew', 'updated_at'])
    
    def expire(self):
        """Marca la membresía como expirada"""
        self.status = 'EXPIRED'
        self.save(update_fields=['status', 'updated_at'])
