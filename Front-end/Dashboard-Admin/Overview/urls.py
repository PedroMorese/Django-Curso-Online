"""
URLs UX del Dashboard de Administración.

Estas son rutas de experiencia de usuario, NO del dominio.
"""

from django.urls import path
from . import views

app_name = 'dashboard_admin'

urlpatterns = [
    path('', views.overview, name='overview'),
    path('users/', views.users_list, name='users'),
    path('courses/', views.courses_list, name='courses'),
    path('subscriptions/', views.subscriptions_list, name='subscriptions'),
    path('reports/', views.reports, name='reports'),
]
