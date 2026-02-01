"""
Script para crear usuarios de prueba para la plataforma EduPlatform.

Ejecutar con: python manage.py shell < create_test_users.py
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangocrud.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Usuarios de prueba
test_users = [
    {
        'email': 'admin@eduplatform.com',
        'password': 'admin123',
        'first_name': 'Admin',
        'last_name': 'Principal',
        'rol': 'ADMIN',
        'is_staff': True,
        'is_superuser': True,
    },
    {
        'email': 'profesor@eduplatform.com',
        'password': 'profesor123',
        'first_name': 'Carlos',
        'last_name': 'Martínez',
        'rol': 'PROFESOR',
        'is_staff': False,
        'is_superuser': False,
    },
    {
        'email': 'alumno@eduplatform.com',
        'password': 'alumno123',
        'first_name': 'María',
        'last_name': 'García',
        'rol': 'CLIENTE',
        'is_staff': False,
        'is_superuser': False,
    },
]

print("=" * 60)
print("CREANDO USUARIOS DE PRUEBA")
print("=" * 60)

for user_data in test_users:
    email = user_data['email']
    username = email.split('@')[0]  # Use email prefix as username
    
    # Verificar si el usuario ya existe
    if User.objects.filter(email=email).exists():
        print(f"❌ Usuario {email} ya existe. Eliminando...")
        User.objects.filter(email=email).delete()
    
    # Crear el usuario
    user = User.objects.create_user(
        username=username,
        email=user_data['email'],
        password=user_data['password'],
        first_name=user_data['first_name'],
        last_name=user_data['last_name'],
    )
    
    # Asignar rol y permisos
    user.rol = user_data['rol']
    user.is_staff = user_data['is_staff']
    user.is_superuser = user_data['is_superuser']
    user.save()
    
    print(f"✅ Usuario creado: {email}")
    print(f"   Username: {username}")
    print(f"   Nombre: {user.first_name} {user.last_name}")
    print(f"   Rol: {user.rol}")
    print(f"   Password: {user_data['password']}")
    print()

print("=" * 60)
print("RESUMEN DE USUARIOS DE PRUEBA")
print("=" * 60)
print()
print("🔐 ADMINISTRADOR")
print("   Email: admin@eduplatform.com")
print("   Password: admin123")
print("   Acceso: Dashboard Admin + Django Admin")
print()
print("👨‍🏫 PROFESOR")
print("   Email: profesor@eduplatform.com")
print("   Password: profesor123")
print("   Acceso: Dashboard Profesor + Crear Cursos")
print()
print("👨‍🎓 ALUMNO")
print("   Email: alumno@eduplatform.com")
print("   Password: alumno123")
print("   Acceso: Ver cursos + Suscribirse")
print()
print("=" * 60)
print("✅ USUARIOS CREADOS EXITOSAMENTE")
print("=" * 60)
