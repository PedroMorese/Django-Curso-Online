"""
URLs UX del módulo Home.

Estas son las rutas públicas de la plataforma.
Incluye todas las rutas frontend.
"""

from django.urls import path
from . import views

app_name = 'home'

urlpatterns = [
    # Landing / Home
    path('', views.home, name='index'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    
    # Course Catalog
    path('courses/', views.course_catalog, name='course_catalog'),
    path('courses/<int:course_id>/', views.course_preview, name='course_preview'),
    
    # Membership (direct routes)
    path('membership/plans/', views.membership_plans_redirect, name='membership_plans'),
    path('membership/subscribe/<slug:plan_slug>/', views.membership_subscribe_redirect, name='membership_subscribe'),
    
    # Course Player (requires auth)
    path('learn/<int:course_id>/', views.course_player_redirect, name='course_player'),
    path('learn/<int:course_id>/class/<int:class_id>/', views.course_player_class_redirect, name='course_player_class'),
]
