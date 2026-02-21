# Flujos de Usuario por Rol

Este documento describe los flujos de navegación reales e implementados para cada rol de la plataforma.

---

## 🎓 Rol: Cliente (Estudiante)

### Acceso Sin Membresía
```
/ (Landing)
├── Ver cursos destacados y recientes (solo visual)
├── /courses/         → Catálogo de cursos publicados
│   └── /courses/<id>/  → Preview del curso
│       ├── Ver título, descripción, lista de clases (solo títulos)
│       └── Botón "Start Learning" → redirige a /membership/
│
└── /membership/      → Planes disponibles
    └── /membership/checkout/<slug>/  → Formulario de pago
        └── /membership/payment/success/  → Confirmación (PENDING)
```

### Acceso Con Membresía ACTIVE
```
/ (Landing)
├── /courses/                           → Catálogo completo
│   └── /courses/<id>/                  → Preview del curso
│       └── Botón "Start Learning" → /learn/<id>/
│
└── /learn/<course_id>/                 → Reproductor (primera clase)
    ├── /learn/<id>/class/<class_id>/   → Clase específica
    │   ├── Video embebido (video_url)
    │   ├── Descripción de la clase
    │   ├── Sidebar: lista de todas las clases del curso
    │   ├── Botones: ← Anterior | Siguiente →
    │   └── [Última clase] → Botón "Complete Course"
    │
    └── /learn/<id>/certificado/        → Certificado de participación
        ├── Se emite 1 vez por (usuario, curso)
        ├── Código de verificación UUID único
        └── Diseño imprimible

/certificados/                          → Galería de certificados obtenidos
```

---

## 👨‍🏫 Rol: Profesor

```
Login → /dashboard/profesor/            → Mis Cursos
│
├── Lista de cursos propios
│   ├── Badge "Published" / "Draft"
│   ├── Número de clases por curso
│   └── Acciones: Ver Detalle | Toggle Publicar
│
├── /dashboard/profesor/create/         → Crear Curso
│   ├── Formulario: título, descripción, imagen, nivel
│   └── Se crea en estado "Draft" (publicado=False)
│
├── /dashboard/profesor/course/<id>/    → Detalle del Curso
│   ├── Ver/editar metadata del curso
│   ├── Lista de clases con orden
│   ├── Formulario inline: añadir nueva clase
│   │   └── Campos: título, descripción, video_url, imagen, duración, orden
│   ├── Editar clase existente (inline o modal)
│   └── Eliminar clase → Modal de confirmación JS
│       └── POST /course/<id>/class/<cid>/delete/
│
└── /dashboard/profesor/course/<id>/toggle-publish/
    └── Alterna publicado=True/False
```

### Lo que el Profesor NO puede ver:
- ❌ Información de pagos de alumnos
- ❌ Lista de alumnos inscritos
- ❌ Estadísticas de visualizaciones
- ❌ Planes de membresía ni precios

---

## 🛡️ Rol: Administrador

```
Login → /dashboard/admin/               → Overview (métricas en tiempo real)
│   ├── Total Revenue (pagos COMPLETED, all-time)
│   ├── Active Members (UserMembership ACTIVE con fechas vigentes)
│   ├── Expired Subs (EXPIRED + CANCELLED)
│   └── Recent Transactions (últimos 5 pagos)
│
├── /dashboard/admin/users/             → Gestión de Usuarios
│   ├── Búsqueda por nombre/email/ID
│   ├── Filtros: por rol (ADMIN/PROFESOR/CLIENTE), por estado (activo/inactivo)
│   ├── Paginación: 10 usuarios por página
│   └── Acciones por usuario:
│       ├── /users/create/         → Crear usuario (con rol y contraseña)
│       ├── /users/edit/<id>/      → Editar nombre, email, rol, estado
│       └── /users/delete/<id>/    → Eliminar usuario
│
├── /dashboard/admin/courses/           → Catálogo de Cursos
│   ├── Búsqueda por título, profesor, ID
│   ├── Filtros: por nivel (PRINCIPIANTE/INTERMEDIO/AVANZADO), por estado (published/draft)
│   ├── Paginación: 9 cursos por página
│   └── Acciones:
│       ├── /courses/view/<id>/    → Ver detalles
│       ├── /courses/edit/<id>/    → Editar título, descripción, nivel, estado
│       └── /courses/delete/<id>/ → Eliminar curso
│
├── /dashboard/admin/subscriptions/     → Gestión de Suscripciones
│   ├── Búsqueda por nombre, email, referencia de pago
│   ├── Filtros: por plan (MONTHLY/ANNUAL/LIFETIME), por estado (ACTIVE/PENDING/EXPIRED)
│   ├── Paginación: 10 membresías por página
│   └── Acciones:
│       ├── /subscriptions/edit/<id>/    → Cambiar plan y/o estado
│       │   └── PENDING→ACTIVE también marca el Payment como COMPLETED
│       ├── /subscriptions/cancel/<id>/  → Cambiar estado a EXPIRED
│       └── /subscriptions/delete/<id>/ → Eliminar registro
│
├── /dashboard/admin/reports/           → Reportes de Ingresos
│   ├── Filtros de período: Monthly | Quarterly | Yearly
│   ├── Métricas dinámicas:
│   │   ├── Revenue total del período
│   │   ├── Market Share
│   │   ├── Estadísticas de usuarios y cursos
│   │   ├── Transacción promedio
│   │   ├── Tasa de retención
│   │   └── Proyección (forecast)
│   ├── Gráfico de barras con datos reales de la BD
│   └── /reports/export-pdf/  → Exportar reporte en PDF
│
└── /dashboard/admin/settings/membership/  → Configuración de Planes
    ├── Ver planes existentes (MembershipPlan)
    └── Crear/editar planes con precio, tipo y características
```

---

## 🔐 Flujo de Activación de Membresía

```
1. CLIENTE selecciona plan en /membership/
       │
       ▼
2. Checkout: llena datos de pago (tarjeta o transferencia bancaria)
       │
       ▼
3. Se registra Payment(status='PENDING') + UserMembership(status='PENDING')
       │
       ▼
4. ADMIN ve en /subscriptions/ → membresía en estado PENDING
       │
       ▼
5. ADMIN edita suscripción: cambia status → ACTIVE
       │
       ▼
6. Sistema sincroniza: Payment.status → COMPLETED
       │
       ▼
7. CLIENTE ahora tiene acceso completo al reproductor de clases
```

---

## 🌐 Mapa de URLs Completo

### Rutas Públicas
| URL                             | Vista                  | Descripción                                    |
| ------------------------------- | ---------------------- | ---------------------------------------------- |
| `/`                             | `home()`               | Landing page con cursos recientes/recomendados |
| `/register/`                    | `register()`           | Abre modal de registro                         |
| `/login/`                       | `login()`              | Abre modal de login                            |
| `/courses/`                     | `course_catalog()`     | Catálogo de cursos publicados                  |
| `/courses/<id>/`                | `course_preview()`     | Preview de curso específico                    |
| `/membership/`                  | `membership_plans()`   | Planes de membresía                            |
| `/membership/checkout/<slug>/`  | `checkout()`           | Checkout de plan                               |
| `/membership/payment/success/`  | `payment_success()`    | Confirmación de pago                           |
| `/membership/subscribe/<slug>/` | `subscribe()`          | Suscripción directa (demo)                     |
| `/learn/<id>/`                  | `course_player()`      | Reproductor (primera clase)                    |
| `/learn/<id>/class/<cid>/`      | `course_player()`      | Reproductor (clase específica)                 |
| `/learn/<id>/overview/`         | `course_overview()`    | Lista de clases del curso                      |
| `/learn/<id>/certificado/`      | `course_certificate()` | Emisión/visualización certificado              |
| `/certificados/`                | `my_certificates()`    | Galería de certificados                        |

### Dashboard Admin
| URL                                           | Vista                   | Descripción             |
| --------------------------------------------- | ----------------------- | ----------------------- |
| `/dashboard/admin/`                           | `overview()`            | Métricas en tiempo real |
| `/dashboard/admin/users/`                     | `users_list()`          | Lista de usuarios       |
| `/dashboard/admin/users/create/`              | `create_user()`         | Crear usuario           |
| `/dashboard/admin/users/edit/<id>/`           | `edit_user()`           | Editar usuario          |
| `/dashboard/admin/users/delete/<id>/`         | `delete_user()`         | Eliminar usuario        |
| `/dashboard/admin/courses/`                   | `courses_list()`        | Catálogo admin          |
| `/dashboard/admin/courses/view/<id>/`         | `view_course()`         | Detalle de curso        |
| `/dashboard/admin/courses/edit/<id>/`         | `edit_course()`         | Editar curso            |
| `/dashboard/admin/courses/delete/<id>/`       | `delete_course()`       | Eliminar curso          |
| `/dashboard/admin/subscriptions/`             | `subscriptions_list()`  | Suscripciones           |
| `/dashboard/admin/subscriptions/edit/<id>/`   | `edit_subscription()`   | Editar suscripción      |
| `/dashboard/admin/subscriptions/cancel/<id>/` | `cancel_subscription()` | Cancelar                |
| `/dashboard/admin/subscriptions/delete/<id>/` | `delete_subscription()` | Eliminar                |
| `/dashboard/admin/reports/`                   | `reports()`             | Reportes de ingresos    |
| `/dashboard/admin/reports/export-pdf/`        | `export_report_pdf()`   | Exportar PDF            |
| `/dashboard/admin/settings/membership/`       | `membership_settings()` | Config planes           |

### Dashboard Profesor
| URL                                                   | Vista              | Descripción          |
| ----------------------------------------------------- | ------------------ | -------------------- |
| `/dashboard/profesor/`                                | `my_courses()`     | Mis cursos           |
| `/dashboard/profesor/create/`                         | `create_course()`  | Crear curso          |
| `/dashboard/profesor/course/<id>/`                    | `course_detail()`  | Detalle + clases     |
| `/dashboard/profesor/course/<id>/class/<cid>/delete/` | `delete_class()`   | Eliminar clase       |
| `/dashboard/profesor/course/<id>/toggle-publish/`     | `toggle_publish()` | Publicar/Despublicar |
| `/dashboard/profesor/profile/`                        | `profile()`        | Perfil del profesor  |

---

**Última actualización**: Febrero 2026
