"""
URLs UX del Reproductor de Cursos.
"""

from django.urls import path
from . import views

app_name = 'course_player'

urlpatterns = [
    path('<int:course_id>/',                        views.course_player,      name='player'),
    path('<int:course_id>/class/<int:class_id>/',   views.course_player,      name='player_class'),
    path('<int:course_id>/overview/',               views.course_overview,    name='overview'),
    path('<int:course_id>/certificado/',            views.course_certificate, name='certificate'),
]
