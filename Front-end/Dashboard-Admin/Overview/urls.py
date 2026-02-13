"""
URLs UX del Dashboard de Administración.

Estas son rutas de experiencia de usuario, NO del dominio.
"""

from django.urls import path
from . import views

app_name = 'dashboard_admin'

urlpatterns = [
    path('', views.overview, name='overview'),
    path('users/', views.users_list, name='users_list'),
    path('users/create/', views.create_user, name='create_user'),
    path('users/edit/<int:user_id>/', views.edit_user, name='edit_user'),
    path('users/delete/<int:user_id>/', views.delete_user, name='delete_user'),
    path('courses/', views.courses_list, name='courses_list'),
    path('courses/view/<int:course_id>/', views.view_course, name='view_course'),
    path('courses/edit/<int:course_id>/', views.edit_course, name='edit_course'),
    path('courses/delete/<int:course_id>/', views.delete_course, name='delete_course'),
    path('subscriptions/', views.subscriptions_list, name='subscriptions_list'),
    path('reports/', views.reports, name='reports'),
    path('settings/membership/', views.membership_settings, name='membership_settings'),
]
