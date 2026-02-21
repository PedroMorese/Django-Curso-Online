"""
URLs UX del módulo Home.

Estas son las rutas públicas de la plataforma.
Incluye todas las rutas frontend.
"""

from django.urls import path, include
from . import views
from .Membership import views as membership_views

app_name = 'home'

urlpatterns = [
    # Landing / Home
    path('', views.home, name='index'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    
    # Course Catalog
    path('courses/', views.course_catalog, name='course_catalog'),
    path('courses/<int:course_id>/', views.course_preview, name='course_preview'),
    
    # Membership UX (checkout and payment pages)
    path('membership/', membership_views.membership_plans, name='membership_plans'),
    path('membership/checkout/<slug:plan_slug>/', membership_views.checkout, name='membership_checkout'),
    path('membership/payment/success/', membership_views.payment_success, name='membership_payment_success'),
    path('membership/subscribe/<slug:plan_slug>/', membership_views.subscribe, name='membership_subscribe'),
    
    # Course Player (requires auth)
    path('learn/<int:course_id>/', views.course_player_redirect, name='course_player'),
    path('learn/<int:course_id>/class/<int:class_id>/', views.course_player_class_redirect, name='course_player_class'),
    path('learn/<int:course_id>/certificado/', views.course_certificate_redirect, name='course_certificate'),
    # Galería de certificados del usuario
    path('certificados/', views.my_certificates, name='my_certificates'),
]
