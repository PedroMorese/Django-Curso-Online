from django.apps import AppConfig


class AuthConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Back-end.Auth'
    label = 'auth_backend'
    verbose_name = 'Autenticación'
