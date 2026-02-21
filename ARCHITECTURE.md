# Arquitectura del Sistema — Plataforma de Educación Online

## 1. Visión General

La plataforma sigue el patrón **MVT (Model-View-Template)** de Django con una separación explícita entre Backend y Frontend en la estructura de carpetas. No se usa Django REST Framework para las vistas principales; las APIs son vistas Django estándar que devuelven JSON o renderizan templates.

```
┌─────────────────────────────────────────────────────────┐
│                     USUARIO (Browser)                   │
└────────────────────────┬────────────────────────────────┘
                         │ HTTP
┌────────────────────────▼────────────────────────────────┐
│              Django URL Router (djangocrud/urls.py)     │
│  ┌──────────────────────────────────────────────────┐   │
│  │  /auth/          → Back-end.Auth                 │   │
│  │  /api/courses/   → Back-end.Course               │   │
│  │  /api/classes/   → Back-end.Class                │   │
│  │  /api/membership/→ Back-end.membership           │   │
│  │  /api/payments/  → Back-end.payments             │   │
│  │  /api/media/     → Back-end.Media                │   │
│  │  /dashboard/admin/   → Dashboard-Admin.Overview  │   │
│  │  /dashboard/profesor/→ Dashboard-Profesor.MyCourses│  │
│  │  /profile/       → Front-end.Profile             │   │
│  │  /documentation/ → Front-end.Documentation       │   │
│  │  /               → Front-end.home                │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         ▼               ▼               ▼
   ┌──────────┐   ┌──────────────┐  ┌─────────┐
   │ Backend  │   │   Services   │  │Frontend │
   │ (Models) │◄──│ (Analytics)  │  │(Views + │
   │          │   │              │  │Templates│
   └──────────┘   └──────────────┘  └─────────┘
         │
   ┌──────────┐
   │ SQLite3  │
   │   DB     │
   └──────────┘
```

---

## 2. Estructura Real de Carpetas

```
Proyecto_db/
├── manage.py
├── djangocrud/                         # Config global Django
│   ├── settings.py
│   ├── urls.py                         # Router raíz
│   └── wsgi.py
│
├── Back-end/                           # Lógica de negocio
│   ├── __init__.py
│   ├── Auth/                           # app_label: 'Auth'
│   │   ├── models.py                   # Persona (CustomUser)
│   │   ├── views.py                    # Login, logout, registro
│   │   └── urls.py
│   ├── Course/                         # app_label: 'course_app'
│   │   ├── models.py                   # Course, Certificate
│   │   ├── views.py                    # API CRUD cursos
│   │   ├── urls.py
│   │   ├── API_DOCUMENTATION.md
│   │   ├── README.md
│   │   └── TESTING_GUIDE.md
│   ├── Class/                          # app_label: 'class_app'
│   │   ├── models.py                   # Class
│   │   ├── views.py
│   │   └── urls.py
│   ├── membership/                     # app_label: 'membership'
│   │   ├── models.py                   # MembershipPlan, UserMembership
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── API_MEMBERSHIP_SETTINGS.md
│   ├── payments/                       # app_label: 'payments'
│   │   ├── models.py                   # Payment
│   │   ├── views.py
│   │   └── urls.py
│   ├── Analytics/                      # Sin app_label propio (servicio)
│   │   ├── apps.py
│   │   └── services.py                 # AnalyticsService
│   └── Media/                          # app_label: 'Media'
│       └── views.py                    # Subida de archivos
│
├── Front-end/                          # Capa de presentación
│   ├── home/                           # app_label: 'home'
│   │   ├── views.py                    # Vistas públicas + player + certificados
│   │   ├── urls.py                     # Rutas públicas
│   │   ├── Membership/                 # Sub-módulo membresía
│   │   │   ├── views.py                # plans, checkout, payment_success, subscribe
│   │   │   └── templates/membership/  # plans.html, checkout.html, success.html
│   │   ├── Course-Player/             # Sub-módulo reproductor
│   │   │   ├── views.py               # course_player, course_overview, course_certificate
│   │   │   └── urls.py                # app_name: course_player
│   │   └── Template/
│   │       ├── Home.html
│   │       ├── base/
│   │       ├── catalog/               # course_list.html, course_preview.html
│   │       └── course_player/         # player.html, certificado.html, mis_certificados.html
│   ├── Dashboard-Admin/
│   │   └── Overview/                  # app_name: dashboard_admin
│   │       ├── views.py               # overview, users CRUD, courses CRUD,
│   │       │                          # subscriptions, reports, export_report_pdf,
│   │       │                          # membership_settings
│   │       ├── urls.py
│   │       └── templates/dashboard_admin/
│   │           ├── overview.html
│   │           ├── users_list.html
│   │           ├── user_edit.html
│   │           ├── user_create.html
│   │           ├── courses_list.html
│   │           ├── course_view.html
│   │           ├── course_edit.html
│   │           ├── subscriptions_list.html
│   │           └── reports.html
│   ├── Dashboard-Profesor/
│   │   └── MyCourses/                 # app_name: dashboard_profesor
│   │       ├── views.py               # my_courses, create_course, course_detail,
│   │       │                          # delete_class (con modal confirmación), toggle_publish
│   │       ├── urls.py
│   │       └── templates/
│   ├── Profile/                       # app_name: profile
│   └── Documentation/                 # Documentación visual interna
```

---

## 3. Modelos de Base de Datos

### 3.1 Diagrama de Relaciones

```
Persona (CustomUser)
  │
  ├──[1:N]──► Course (profesor=FK)
  │               │
  │               ├──[1:N]──► Class (curso=FK)
  │               └──[1:N]──► Certificate (curso=FK)
  │
  ├──[1:N]──► UserMembership (user=FK)
  │               │
  │               └──[N:1]──► MembershipPlan
  │
  ├──[1:N]──► Payment (user=FK)
  │               │
  │               └──[N:1]──► MembershipPlan
  │
  └──[1:N]──► Certificate (usuario=FK)
```

### 3.2 Tablas Reales en SQLite3

| Modelo Django    | Tabla SQLite            | App Label    |
| ---------------- | ----------------------- | ------------ |
| `Persona`        | `auth_user` (extendida) | `Auth`       |
| `Course`         | `curso`                 | `course_app` |
| `Certificate`    | `certificado`           | `course_app` |
| `Class`          | `clase`                 | `class_app`  |
| `MembershipPlan` | `membership_plan`       | `membership` |
| `UserMembership` | `user_membership`       | `membership` |
| `Payment`        | `payments_payment`      | `payments`   |

---

## 4. Flujos de Navegación por Rol

### 4.1 Cliente (Estudiante)
```
Landing (/) 
  → Registro/Login (modal)
  → Catálogo (/courses/)
    → Preview de Curso (/courses/<id>/)
      [Sin membresía] → Planes (/membership/)
        → Checkout (/membership/checkout/<slug>/)
        → Pago exitoso
      [Con membresía] → Reproductor (/learn/<id>/)
        → Clase específica (/learn/<id>/class/<cid>/)
        → Certificado (/learn/<id>/certificado/)
        → Galería de certificados (/certificados/)
```

### 4.2 Profesor
```
Login → Dashboard Profesor (/dashboard/profesor/)
  → Mis Cursos (lista con publicado/borrador)
  → Crear Curso (/dashboard/profesor/create/)
  → Detalle de Curso (/dashboard/profesor/course/<id>/)
    → Agregar Clase (formulario inline)
    → Editar Clase (formulario inline)
    → Eliminar Clase (modal de confirmación)
    → Toggle Publicar (/toggle-publish/)
  → Perfil (/dashboard/profesor/profile/)
```

### 4.3 Administrador
```
Login → Dashboard Admin (/dashboard/admin/)
  → Overview (métricas en tiempo real: revenue, membresías, transacciones)
  → Usuarios (/dashboard/admin/users/)
    → Crear / Editar / Eliminar usuario
  → Cursos (/dashboard/admin/courses/)
    → Ver / Editar / Eliminar curso
  → Suscripciones (/dashboard/admin/subscriptions/)
    → Editar plan y estado
    → Cancelar suscripción (→ EXPIRED)
    → Eliminar registro
  → Reportes (/dashboard/admin/reports/)
    → Filtrar por período (monthly / quarterly / yearly)
    → Exportar PDF (/reports/export-pdf/)
  → Configuración Membresía (/settings/membership/)
```

---

## 5. Capas y Responsabilidades

| Capa               | Ubicación                        | Responsabilidad                                           |
| ------------------ | -------------------------------- | --------------------------------------------------------- |
| **Models**         | `Back-end/*/models.py`           | Estructura de datos, validaciones, propiedades calculadas |
| **Backend Views**  | `Back-end/*/views.py`            | APIs funcionales, operaciones CRUD, respuestas JSON       |
| **Services**       | `Back-end/Analytics/services.py` | Lógica de negocio compleja, agregación de datos           |
| **Frontend Views** | `Front-end/*/views.py`           | Orquestación de datos, renderizado de templates           |
| **Templates**      | `*/templates/`                   | HTML, presentación visual                                 |
| **URLs**           | `*/urls.py`                      | Definición de rutas                                       |

---

## 6. Control de Acceso

### Decorador Admin
```python
def admin_required(view_func):
    # Verifica: is_staff OR is_superuser OR role == 'ADMIN'
    # Redirige a home:index si no cumple
```

### Verificación de Membresía
```python
def _require_active_membership(request) -> bool:
    # Consulta: status='ACTIVE' AND start_date<=now AND end_date>=now
    # NO captura excepciones → errores del ORM son visibles
```

### Aplicaciones de Control
- `@login_required` en todas las vistas del reproductor y certificados
- `@admin_required` en todas las vistas del dashboard de administración
- `@login_required` (verificación de rol `PROFESOR`) en el dashboard de profesor

---

## 7. Reglas de Negocio

1. **Acceso Restringido**: `UserMembership.status='ACTIVE'` + `end_date >= now` para ver clases y certificados.
2. **Rol Único**: Un `Persona` tiene un solo campo `role`; sin roles compuestos.
3. **Membresía Única Activa**: Las nuevas suscripciones se crean en `PENDING`; el Admin las activa.
4. **Sincronización Membresía-Pago**: Cambiar `UserMembership.status` de PENDING→ACTIVE también marca el `Payment` asociado como COMPLETED.
5. **Certificado Único**: `unique_together = (usuario, curso)` en `Certificate`; se usa `get_or_create`.
6. **Separación de Datos**: Los profesores nunca acceden a `Payment` ni estadísticas de alumnos.

---

## 8. Escalabilidad

| Área     | Estado Actual          | Migración Futura                               |
| -------- | ---------------------- | ---------------------------------------------- |
| BD       | SQLite3                | PostgreSQL (cambio de `DATABASES` en settings) |
| Auth     | Token de sesión Django | JWT con DRF                                    |
| APIs     | Vistas Django estándar | Django REST Framework                          |
| Pagos    | Modo DEMO (simulado)   | Stripe / PayPal SDK                            |
| Archivos | Local `media/`         | AWS S3 / Cloudinary                            |
| Deploy   | `runserver` local      | Gunicorn + Nginx                               |

---

**Última actualización**: Febrero 2026
