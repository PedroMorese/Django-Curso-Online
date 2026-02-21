# Mapeo Frontend ↔ Backend ↔ Base de Datos

Esta guía detalla la relación técnica entre funcionalidades, modelos de base de datos y componentes de UI. Refleja el estado **real e implementado** del proyecto.

---

## Tabla Principal de Mapeo

| Feature                      | Tabla(s) DB                                      | App Django                | Vista(s) Frontend                                                      | Componentes UI / Templates                 |
| ---------------------------- | ------------------------------------------------ | ------------------------- | ---------------------------------------------------------------------- | ------------------------------------------ |
| **Login / Registro**         | `Persona`                                        | `Auth`                    | `home/views.py: home()`                                                | Modal en `Home.html`                       |
| **Control de Acceso**        | `UserMembership`                                 | `membership`              | `_require_active_membership()`                                         | Redirige a `/membership/`                  |
| **Landing Page**             | `Course` (para preview)                          | `home`                    | `home()`                                                               | `Home.html`                                |
| **Catálogo de Cursos**       | `Course`                                         | `course_app`              | `course_catalog()`                                                     | `catalog/course_list.html`                 |
| **Preview de Curso**         | `Course`, `Class`                                | `course_app`, `class_app` | `course_preview()`                                                     | `catalog/course_preview.html`              |
| **Planes de Membresía**      | `MembershipPlan`, `UserMembership`               | `membership`              | `membership_plans()`                                                   | `membership/plans.html`                    |
| **Checkout de Membresía**    | `MembershipPlan`, `Payment`                      | `membership`, `payments`  | `checkout()`                                                           | `membership/checkout.html`                 |
| **Suscripción (Demo)**       | `UserMembership`                                 | `membership`              | `subscribe()`                                                          | Redirect → home                            |
| **Reproductor de Clases**    | `Course`, `Class`, `UserMembership`              | todos                     | `course_player()`                                                      | `course_player/player.html`                |
| **Vista General del Curso**  | `Course`, `Class`                                | `course_app`, `class_app` | `course_overview()`                                                    | `course_player/overview.html`              |
| **Certificados**             | `Certificate`, `Course`                          | `course_app`              | `course_certificate()`                                                 | `course_player/certificado.html`           |
| **Galería Certificados**     | `Certificate`                                    | `course_app`              | `my_certificates()`                                                    | `course_player/mis_certificados.html`      |
| **Dashboard Profesor**       | `Course`                                         | `course_app`              | `my_courses()`                                                         | `dashboard_profesor/my_courses.html`       |
| **Crear Curso**              | `Course`                                         | `course_app`              | `create_course()`                                                      | `dashboard_profesor/create_course.html`    |
| **Detalle/Editar Curso**     | `Course`, `Class`                                | `course_app`, `class_app` | `course_detail()`                                                      | `dashboard_profesor/course_detail.html`    |
| **Eliminar Clase**           | `Class`                                          | `class_app`               | `delete_class()`                                                       | Modal de confirmación JS                   |
| **Publicar/Despublicar**     | `Course.publicado`                               | `course_app`              | `toggle_publish()`                                                     | Toggle button                              |
| **Admin Overview**           | `Payment`, `UserMembership`                      | `payments`, `membership`  | `overview()`                                                           | `dashboard_admin/overview.html`            |
| **Admin - Usuarios**         | `Persona`                                        | `Auth`                    | `users_list()`, `edit_user()`, `create_user()`, `delete_user()`        | `dashboard_admin/users_list.html`          |
| **Admin - Cursos**           | `Course`                                         | `course_app`              | `courses_list()`, `view_course()`, `edit_course()`, `delete_course()`  | `dashboard_admin/courses_list.html`        |
| **Admin - Suscripciones**    | `UserMembership`, `MembershipPlan`, `Payment`    | `membership`, `payments`  | `subscriptions_list()`, `edit_subscription()`, `cancel_subscription()` | `dashboard_admin/subscriptions_list.html`  |
| **Admin - Reportes**         | `Payment`, `UserMembership`, `Course`, `Persona` | todos                     | `reports()`, `export_report_pdf()`                                     | `dashboard_admin/reports.html`             |
| **Admin - Config Membresía** | `MembershipPlan`                                 | `membership`              | `membership_settings()`                                                | `dashboard_admin/membership_settings.html` |
| **Perfil de Usuario**        | `Persona`                                        | `Auth`                    | `Profile/views.py`                                                     | `profile/profile.html`                     |

---

## Componentes UI Reutilizables (Actuales)

### 1. `player.html` — Reproductor de Clases
- **Datos**: `course`, `current_class`, `all_classes`, `prev_class`, `next_class`, `progress`, `is_last_class`
- **Sidebar**: lista todas las clases del curso, resalta la actual
- **Player**: embebe `video_url` (iframe/video tag)
- **Controles**: botones Anterior / Siguiente clase
- **Botón "Complete Course"**: visible solo en `is_last_class=True`, lleva a `/learn/<id>/certificado/`

### 2. `certificado.html` — Certificado de Participación
- **Datos**: `curso`, `certificado` (con `codigo_verificacion` UUID), `instructor`
- **Extiende**: base template
- **Sin duplicación**: no tiene header propio, usa el del base
- **Imprimible**: diseñado para captura/impresión

### 3. `mis_certificados.html` — Galería de Certificados
- **Datos**: `certificados` (lista de Certificate con related curso y profesor)
- **Ordenado**: por `fecha_emision` descendente

### 4. `overview.html` (Admin) — Dashboard Principal
- **Métricas en tiempo real**:
  - Total Revenue (suma de `Payment.status='COMPLETED'`)
  - Active Members (`UserMembership.status='ACTIVE'` con fechas vigentes)
  - Expired Subs (`UserMembership.status IN ('EXPIRED','CANCELLED')`)
  - Recent Transactions (últimos 5 pagos)

### 5. `users_list.html` (Admin) — Gestión de Usuarios
- **Filtros**: búsqueda por nombre/email/ID, filtro por rol, filtro por estado
- **Paginación**: 10 usuarios por página
- **Acciones**: editar, eliminar con confirmación

### 6. `subscriptions_list.html` (Admin) — Gestión de Suscripciones
- **Filtros**: búsqueda, filtro por plan, filtro por estado
- **Paginación**: 10 membresías por página
- **Acciones**: editar plan/estado, cancelar, eliminar
- **Sincronización**: cambio de estado PENDING→ACTIVE también actualiza el Payment

---

## Flujo de Datos: Verificación de Acceso a Cursos

```
Request /learn/<course_id>/
    │
    ▼
@login_required
    │ (no auth → /auth/login/)
    ▼
_require_active_membership(request)
    │
    ├── SELECT FROM user_membership
    │   WHERE user=request.user
    │     AND status='ACTIVE'
    │     AND start_date <= NOW()
    │     AND end_date >= NOW()
    │
    ├── [False] → messages.warning() → redirect('home:membership_plans')
    │
    └── [True] → cargar Course, Class → render player.html
```

## Flujo de Datos: Suscripción de Cliente (Demo)

```
Cliente selecciona plan → /membership/subscribe/<slug>/
    │
    ├── ¿Autenticado? → No → guardar session → redirect login
    │
    ├── ¿Existe membresía ACTIVE? → Sí → mensaje info → redirect plans
    │
    └── Crear UserMembership(status='PENDING', payment_reference='DEMO-<user_id>')
            │
            └── Admin activa desde /dashboard/admin/subscriptions/
                    │
                    └── UserMembership.status = 'ACTIVE'
                        Payment.status = 'COMPLETED'  (si existe pago)
```

## Flujo de Datos: Emisión de Certificado

```
Request /learn/<course_id>/certificado/  (GET o POST)
    │
    ▼
@login_required + _require_active_membership()
    │
    ▼
Certificate.objects.get_or_create(usuario=request.user, curso=course)
    │
    ├── [created=True]  → messages.success() con felicitación
    └── [created=False] → mostrar certificado existente
            │
            └── render certificado.html con {curso, certificado, instructor}
```

---

## Responsabilidades por Capa

| Capa                                            | SÍ hace                                                                                                                             | NO hace                                       |
| ----------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------- |
| **Models** (`Back-end/*/models.py`)             | Validar datos, propiedades calculadas (`is_active`, `days_remaining`, `total_clases`), métodos de estado (`activate()`, `expire()`) | Lógica de presentación, formateo de templates |
| **Backend Views** (`Back-end/*/views.py`)       | Responder JSON para operaciones CRUD, validar permisos de rol                                                                       | Renderizar HTML, lógica de UI                 |
| **Services** (`Back-end/Analytics/services.py`) | Agregar datos de múltiples modelos, calcular KPIs                                                                                   | Manejar HTTP request/response                 |
| **Frontend Views** (`Front-end/*/views.py`)     | Orquestar contexto para templates, verificar membresía, redirigir                                                                   | Lógica de negocio core                        |
| **Templates** (`*/templates/`)                  | Presentar datos, manejo de formularios, UX                                                                                          | Consultas de base de datos, lógica de negocio |

---

**Última actualización**: Febrero 2026
