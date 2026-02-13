"""
URLs para el módulo de pagos.
"""

from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('process/', views.process_payment, name='process_payment'),
]
