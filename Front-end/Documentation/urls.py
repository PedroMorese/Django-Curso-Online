"""
URLs para el módulo de Documentación.
"""

from django.urls import path
from . import views

app_name = 'documentation'

urlpatterns = [
    path('', views.documentation_index, name='index'),
    path('<slug:doc_slug>/', views.documentation_view, name='view'),
]
