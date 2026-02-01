"""
URLs UX del Dashboard de Profesor.

Estas son rutas de experiencia de usuario para profesores.
"""

from django.urls import path
from . import views

app_name = 'dashboard_profesor'

urlpatterns = [
    path('', views.my_courses, name='my_courses'),
    path('create/', views.create_course, name='create_course'),
    path('course/<int:course_id>/', views.course_detail, name='course_detail'),
    path('course/<int:course_id>/toggle-publish/', views.toggle_publish, name='toggle_publish'),
    path('profile/', views.profile, name='profile'),
]
