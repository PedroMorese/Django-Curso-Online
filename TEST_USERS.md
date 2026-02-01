# 🔐 Credenciales de Usuarios de Prueba

## Usuarios Creados

### 👨‍💼 ADMINISTRADOR
- **Email:** `admin@eduplatform.com`
- **Password:** `admin123`
- **Rol:** ADMIN
- **Permisos:** 
  - Acceso completo al Dashboard de Administrador
  - Acceso al Django Admin Panel
  - Ver estadísticas globales
  - Gestionar usuarios y cursos

---

### 👨‍🏫 PROFESOR
- **Email:** `profesor@eduplatform.com`
- **Password:** `profesor123`
- **Rol:** PROFESOR
- **Permisos:**
  - Acceso al Dashboard de Profesor
  - Crear y gestionar cursos propios
  - Publicar/despublicar cursos
  - Ver estadísticas de sus cursos

---

### 👨‍🎓 ALUMNO
- **Email:** `alumno@eduplatform.com`
- **Password:** `alumno123`
- **Rol:** CLIENTE
- **Permisos:**
  - Ver catálogo de cursos
  - Suscribirse a membresías
  - Acceder a cursos (con membresía activa)
  - Ver su progreso

---

## Cómo Usar

1. Ve a http://127.0.0.1:8000/
2. Haz click en "Login" en el navbar
3. Usa cualquiera de las credenciales de arriba
4. Serás redirigido según tu rol:
   - **Admin** → `/dashboard/admin/`
   - **Profesor** → `/dashboard/profesor/`
   - **Alumno** → Catálogo de cursos

---

## Recrear Usuarios

Si necesitas recrear los usuarios, ejecuta:

```bash
python create_test_users.py
```

Este script eliminará los usuarios existentes y los creará de nuevo con las mismas credenciales.
