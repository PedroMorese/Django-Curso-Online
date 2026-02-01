from django.apps import AppConfig


class CourseConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Back-end.Course'
    label = 'course_app'
    verbose_name = 'Cursos'
