from django.urls import path
from . import views

urlpatterns = [
    # Lista y creación de cursos
    path('', views.course_list, name='course-list'),
    
    # Mis cursos (solo para profesores)
    path('my-courses/', views.my_courses, name='my-courses'),
    
    # Detalle, actualización y eliminación de curso
    path('<int:course_id>/', views.course_detail, name='course-detail'),
    
    # Publicar/despublicar curso
    path('<int:course_id>/publish/', views.course_publish, name='course-publish'),
]
