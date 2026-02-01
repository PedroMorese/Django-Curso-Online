from django.contrib.auth.models import AbstractUser
from django.db import models

class Persona(AbstractUser):
    ROLE_CHOICES = (
        ('ADMIN', 'Administrador'),
        ('PROFESOR', 'Profesor'),
        ('CLIENTE', 'Cliente'),
    )
    
    role = models.CharField(
        max_length=20, 
        choices=ROLE_CHOICES, 
        default='CLIENTE'
    )
    phone = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.email} - {self.role}"
