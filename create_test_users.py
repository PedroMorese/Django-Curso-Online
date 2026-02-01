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
        'role': 'ADMIN',
        'is_staff': True,
        'is_superuser': True,
    },
    {
        'email': 'profesor@eduplatform.com',
        'password': 'profesor123',
        'first_name': 'Carlos',
        'last_name': 'Martinez',
        'role': 'PROFESOR',
        'is_staff': False,
        'is_superuser': False,
    },
    {
        'email': 'alumno@eduplatform.com',
        'password': 'alumno123',
        'first_name': 'Maria',
        'last_name': 'Garcia',
        'role': 'CLIENTE',
        'is_staff': False,
        'is_superuser': False,
    },
]

print("=" * 60)
print("CREANDO USUARIOS DE PRUEBA")
print("=" * 60)

for user_data in test_users:
    email = user_data['email']
    username = email.split('@')[0]
    
    # Verificar si el usuario ya existe
    if User.objects.filter(email=email).exists():
        print(f"Usuario {email} ya existe. Eliminando...")
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
    user.role = user_data['role']
    user.is_staff = user_data['is_staff']
    user.is_superuser = user_data['is_superuser']
    user.save()
    
    print(f"Usuario creado: {email} (Rol: {user.role})")

print("=" * 60)
print("USUARIOS CREADOS EXITOSAMENTE")
print("=" * 60)
