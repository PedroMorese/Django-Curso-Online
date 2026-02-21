# Instrucciones de Visualización y Acceso

Guía rápida para navegar y probar la plataforma en desarrollo local.

---

## 🚀 Iniciar el Servidor

```bash
# Desde la carpeta del proyecto
cd Proyecto_db

# Activar entorno virtual
venv\Scripts\activate   # Windows
source venv/bin/activate  # Linux/Mac

# Iniciar servidor
python manage.py runserver
```

El servidor estará disponible en: **http://localhost:8000/**

---

## 🌐 Accesos por Rol

### Área Pública (sin login)
| Sección             | URL                                                | Descripción                |
| ------------------- | -------------------------------------------------- | -------------------------- |
| Landing Page        | http://localhost:8000/                             | Home con cursos destacados |
| Catálogo            | http://localhost:8000/courses/                     | Cursos publicados          |
| Preview Curso       | http://localhost:8000/courses/1/                   | Detalle de un curso        |
| Planes de Membresía | http://localhost:8000/membership/                  | Opciones de suscripción    |
| Checkout            | http://localhost:8000/membership/checkout/monthly/ | Proceso de pago            |

### Cliente (Estudiante) — requiere login + membresía ACTIVE
| Sección          | URL                                        | Descripción               |
| ---------------- | ------------------------------------------ | ------------------------- |
| Reproductor      | http://localhost:8000/learn/1/             | Primera clase del curso 1 |
| Clase específica | http://localhost:8000/learn/1/class/1/     | Clase 1 del curso 1       |
| Vista general    | http://localhost:8000/learn/1/overview/    | Lista de clases del curso |
| Certificado      | http://localhost:8000/learn/1/certificado/ | Emitir/ver certificado    |
| Mis Certificados | http://localhost:8000/certificados/        | Galería de certificados   |

### Dashboard Profesor — requiere login con role=PROFESOR
| Sección       | URL                                                | Descripción               |
| ------------- | -------------------------------------------------- | ------------------------- |
| Mis Cursos    | http://localhost:8000/dashboard/profesor/          | Listado de cursos propios |
| Crear Curso   | http://localhost:8000/dashboard/profesor/create/   | Formulario nuevo curso    |
| Detalle Curso | http://localhost:8000/dashboard/profesor/course/1/ | Gestión de curso y clases |
| Perfil        | http://localhost:8000/dashboard/profesor/profile/  | Perfil del profesor       |

### Dashboard Admin — requiere login con role=ADMIN (o is_staff)
| Sección          | URL                                                        | Descripción                   |
| ---------------- | ---------------------------------------------------------- | ----------------------------- |
| Overview         | http://localhost:8000/dashboard/admin/                     | Métricas en tiempo real       |
| Usuarios         | http://localhost:8000/dashboard/admin/users/               | Gestión de usuarios           |
| Crear Usuario    | http://localhost:8000/dashboard/admin/users/create/        | Nuevo usuario                 |
| Cursos           | http://localhost:8000/dashboard/admin/courses/             | Catálogo admin                |
| Suscripciones    | http://localhost:8000/dashboard/admin/subscriptions/       | Membresías activas/pendientes |
| Reportes         | http://localhost:8000/dashboard/admin/reports/             | Ingresos y métricas           |
| Config Membresía | http://localhost:8000/dashboard/admin/settings/membership/ | Planes de membresía           |

### Otros
| Sección               | URL                                  |
| --------------------- | ------------------------------------ |
| Django Admin          | http://localhost:8000/admin/         |
| Documentación interna | http://localhost:8000/documentation/ |

---

## 👤 Usuarios de Prueba

Ver [TEST_USERS.md](TEST_USERS.md) para las credenciales actuales.

### Credenciales rápidas (si se corrió `create_test_users.py`):

| Rol      | Email             | Contraseña |
| -------- | ----------------- | ---------- |
| Admin    | admin@test.com    | admin123   |
| Profesor | profesor@test.com | prof123    |
| Cliente  | cliente@test.com  | cliente123 |

---

## 🧪 Verificar el Sistema

### 1. Verificar control de acceso (membresía)
```
1. Iniciar sesión como cliente SIN membresía activa
2. Ir a http://localhost:8000/learn/1/
3. Debe redirigir a /membership/ con mensaje de advertencia ✅
```

### 2. Verificar activación de membresía (Admin)
```
1. Iniciar sesión como cliente → seleccionar un plan → completar checkout
2. Iniciar sesión como Admin → ir a /dashboard/admin/subscriptions/
3. Editar la suscripción PENDING → cambiar status a ACTIVE
4. El cliente ahora puede acceder al reproductor ✅
```

### 3. Verificar certificados
```
1. Como cliente con membresía activa, ir al reproductor de un curso
2. Navegar hasta la última clase
3. Aparece el botón "Complete Course"
4. Hacer clic → ir a /learn/<id>/certificado/
5. Se emite el certificado con UUID único ✅
6. Ir a /certificados/ para ver la galería ✅
```

### 4. Verificar reportes (Admin)
```
1. Ir a /dashboard/admin/reports/
2. Probar filtros: Monthly, Quarterly, Yearly
3. Los datos del gráfico cambian según el período ✅
4. Botón "Export PDF" genera descarga ✅
```

---

## 🔧 Comandos Útiles de Desarrollo

```bash
# Crear migraciones después de cambiar modelos
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Shell interactivo de Django
python manage.py shell

# Ver SQL de una migración
python manage.py sqlmigrate course_app 0001

# Crear superusuario
python manage.py createsuperuser

# Crear usuarios de prueba
python create_test_users.py
```

---

## 🐞 Problemas Comunes

| Problema                     | Solución                                                                        |
| ---------------------------- | ------------------------------------------------------------------------------- |
| "Table not found"            | Ejecutar `python manage.py migrate`                                             |
| "No module named..."         | Activar el entorno virtual                                                      |
| Error 500 en el player       | Verificar que exista un curso con `publicado=True` y clases asociadas           |
| "No tienes membresía activa" | El Admin debe activar la membresía en `/dashboard/admin/subscriptions/`         |
| CSS no carga                 | Ejecutar `python manage.py collectstatic` (producción) o verificar `DEBUG=True` |

---

**Última actualización**: Febrero 2026
