"""
URLs del dominio Class (Backend).
"""

from django.urls import path
from . import views

app_name = 'class_api'

urlpatterns = [
    path('', views.class_list, name='class-list'),
    path('<int:class_id>/', views.class_detail, name='class-detail'),
    path('<int:class_id>/update/', views.class_update, name='class-update'),
]
