"""
URLs del dominio Membership (Backend).

Estas rutas son para operaciones del dominio, NO para UX.
Las rutas UX deben estar en Front-end/.
"""

from django.urls import path
from . import views

app_name = 'membership_api'

urlpatterns = [
    # API endpoints del dominio
    path('plans/', views.list_plans, name='list_plans'),
    path('plans/<slug:slug>/', views.plan_detail, name='plan_detail'),
    path('my-membership/', views.user_membership, name='user_membership'),
]
