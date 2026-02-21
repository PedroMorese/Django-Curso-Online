# 📚 Plataforma de Educación Online — Documentación del Proyecto

Plataforma de cursos online con sistema de membresía obligatoria, construida con Django y SQLite3. Soporta tres roles de usuario (Cliente, Profesor, Administrador) con vistas y permisos totalmente separados.

---

## 🗂️ Índice de Documentación

### 📐 Arquitectura y Diseño

| #   | Documento                                            | Contenido                                                               |
| --- | ---------------------------------------------------- | ----------------------------------------------------------------------- |
| 1   | [ARCHITECTURE.md](ARCHITECTURE.md)                   | Arquitectura MVT, entidades de datos, flujos por rol, reglas de negocio |
| 2   | [ARCHITECTURE_PROPOSAL.md](ARCHITECTURE_PROPOSAL.md) | Propuesta inicial de estructura, Design System, componentes UI          |
| 3   | [TECHNICAL_SPECS.md](TECHNICAL_SPECS.md)             | Configuración Django, apps instaladas, settings                         |
| 4   | [TECHNICAL_BLUEPRINT.md](TECHNICAL_BLUEPRINT.md)     | Definición de modelos, servicios, guía de estructura frontend           |
| 5   | [FE_BE_MAPPING.md](FE_BE_MAPPING.md)                 | Mapeo Feature → Tabla DB → Componente UI                                |
| 6   | [USER_FLOWS.md](USER_FLOWS.md)                       | Flujos de navegación por rol                                            |
| 7   | [FLOWS_AND_SCALABILITY.md](FLOWS_AND_SCALABILITY.md) | Estrategias de escalabilidad y migración de BD                          |

### 🔧 Backend — Módulos

| #   | Documento                                                                                        | Contenido                                   |
| --- | ------------------------------------------------------------------------------------------------ | ------------------------------------------- |
| 8   | [Back-end/Course/API_DOCUMENTATION.md](Back-end/Course/API_DOCUMENTATION.md)                     | Endpoints del módulo Curso                  |
| 9   | [Back-end/Course/README.md](Back-end/Course/README.md)                                           | Descripción del módulo Course               |
| 10  | [Back-end/Course/TESTING_GUIDE.md](Back-end/Course/TESTING_GUIDE.md)                             | Casos de prueba y validaciones              |
| 11  | [Back-end/membership/API_MEMBERSHIP_SETTINGS.md](Back-end/membership/API_MEMBERSHIP_SETTINGS.md) | API de membresías y configuración de planes |

### 🗃️ Base de Datos y ORM

| #   | Documento                                                | Contenido                                             |
| --- | -------------------------------------------------------- | ----------------------------------------------------- |
| 12  | [orm_database_operations.md](orm_database_operations.md) | Operaciones ORM documentadas, consultas SQL generadas |

### 👥 Testing y Usuarios

| #   | Documento                      | Contenido                      |
| --- | ------------------------------ | ------------------------------ |
| 13  | [TEST_USERS.md](TEST_USERS.md) | Credenciales de prueba por rol |

---

## 🚀 Inicio Rápido

### Requisitos
- Python 3.8+
- Django 4.x
- SQLite3 (incluido con Python)
- `python-dateutil` (para cálculo de períodos en reportes)

### Instalación

```bash
# 1. Activar entorno virtual
venv\Scripts\activate   # Windows

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Aplicar migraciones
python manage.py migrate

# 4. Crear usuarios de prueba (opcional)
python create_test_users.py

# 5. Iniciar servidor
python manage.py runserver
```

### URLs de acceso

| Sección                 | URL                                              |
| ----------------------- | ------------------------------------------------ |
| Landing / Home          | `http://localhost:8000/`                         |
| Catálogo de Cursos      | `http://localhost:8000/courses/`                 |
| Planes de Membresía     | `http://localhost:8000/membership/`              |
| Course Player           | `http://localhost:8000/learn/<course_id>/`       |
| Galería de Certificados | `http://localhost:8000/certificados/`            |
| Dashboard Profesor      | `http://localhost:8000/dashboard/profesor/`      |
| Dashboard Admin         | `http://localhost:8000/dashboard/admin/`         |
| Reportes Admin          | `http://localhost:8000/dashboard/admin/reports/` |
| Documentación interna   | `http://localhost:8000/documentation/`           |
| Django Admin            | `http://localhost:8000/admin/`                   |

---

## 🏗️ Estructura Real del Proyecto

```
Proyecto_db/
├── manage.py
├── djangocrud/                     # Configuración global Django (settings, urls raíz)
│
├── Back-end/                       # Lógica de negocio y modelos de datos
│   ├── Auth/                       # Modelo Persona (CustomUser con roles)
│   │   ├── models.py               # Persona extiende AbstractUser + campo role
│   │   ├── views.py                # Login, logout, registro
│   │   └── urls.py
│   ├── Course/                     # Módulo de cursos y certificados
│   │   ├── models.py               # Course, Certificate
│   │   ├── views.py                # API CRUD de cursos
│   │   └── urls.py
│   ├── Class/                      # Módulo de clases/lecciones
│   │   ├── models.py               # Class (orden, video_url, imagen_portada)
│   │   ├── views.py                # API CRUD de clases
│   │   └── urls.py
│   ├── membership/                 # Sistema de membresías
│   │   ├── models.py               # MembershipPlan, UserMembership
│   │   ├── views.py                # API planes y suscripciones
│   │   └── urls.py
│   ├── payments/                   # Sistema de pagos
│   │   ├── models.py               # Payment (tarjeta, transferencia)
│   │   ├── views.py                # API de pagos
│   │   └── urls.py
│   ├── Analytics/                  # Servicio de analíticas
│   │   └── services.py             # AnalyticsService (métricas globales, reportes)
│   └── Media/                      # Gestión de archivos subidos
│       └── views.py
│
├── Front-end/                      # Capa de presentación
│   ├── home/                       # Módulo público (landing, catálogo, membresía, player)
│   │   ├── views.py                # home, course_catalog, course_preview, player, certificados
│   │   ├── urls.py                 # Rutas públicas
│   │   ├── Membership/             # Sub-módulo: checkout, pago, suscripción
│   │   ├── Course-Player/          # Sub-módulo: reproductor de clases, certificados
│   │   └── Template/               # Templates de la home (base, catálogo, membership, player)
│   ├── Dashboard-Admin/
│   │   └── Overview/               # Dashboard completo del administrador
│   │       ├── views.py            # overview, users, courses, subscriptions, reports, settings
│   │       └── urls.py
│   ├── Dashboard-Profesor/
│   │   └── MyCourses/              # Panel del profesor (cursos y clases)
│   │       ├── views.py            # my_courses, create_course, course_detail, delete_class
│   │       └── urls.py
│   ├── Profile/                    # Gestión de perfil de usuario
│   └── Documentation/              # Documentación visual interna
│
├── Resources/                      # Recursos estáticos adicionales
├── media/                          # Archivos subidos por usuarios
├── db.sqlite3                      # Base de datos SQLite3
└── requirements.txt
```

---

## 👤 Roles y Permisos

### 🎓 Cliente (Estudiante)
| Acción                                      | Permitido |
| ------------------------------------------- | --------- |
| Ver catálogo de cursos                      | ✅         |
| Acceder a cursos (con membresía activa)     | ✅         |
| Reproducir clases y navegar entre lecciones | ✅         |
| Descargar recursos (PDFs)                   | ✅         |
| Obtener certificados de participación       | ✅         |
| Ver galería personal de certificados        | ✅         |
| Gestionar perfil personal                   | ✅         |
| Ver pagos o estadísticas                    | ❌         |

### 👨‍🏫 Profesor
| Acción                                 | Permitido |
| -------------------------------------- | --------- |
| Crear y editar cursos propios          | ✅         |
| Gestionar clases de sus cursos         | ✅         |
| Publicar / despublicar cursos          | ✅         |
| Eliminar clases con confirmación modal | ✅         |
| Ver estadísticas de alumnos o pagos    | ❌         |

### 🛡️ Administrador
| Acción                                                   | Permitido |
| -------------------------------------------------------- | --------- |
| Dashboard con métricas en tiempo real                    | ✅         |
| CRUD completo de usuarios (con paginación y filtros)     | ✅         |
| CRUD completo de cursos                                  | ✅         |
| Gestión de suscripciones (editar plan, estado, cancelar) | ✅         |
| Reportes de ingresos (mensual, trimestral, anual)        | ✅         |
| Exportar reportes en PDF                                 | ✅         |
| Configurar planes de membresía                           | ✅         |

---

## 🗄️ Modelos de Base de Datos

### `Persona` (CustomUser) — app `Auth`
```python
# Extiende AbstractUser de Django
role: CharField  # ADMIN | PROFESOR | CLIENTE  (default: CLIENTE)
phone: CharField  # opcional
# Hereda: username, email, first_name, last_name, is_active, date_joined
```

### `Course` — app `course_app`
```python
titulo: CharField
descripcion: TextField
imagen_portada: URLField
profesor: ForeignKey(Persona)
nivel: CharField  # PRINCIPIANTE | INTERMEDIO | AVANZADO
publicado: BooleanField
duracion_estimada: IntegerField  # minutos
pdf_adjuntos: TextField  # JSON con lista de URLs de PDFs
fecha_creacion: DateTimeField
fecha_actualizacion: DateTimeField
```

### `Certificate` — app `course_app`
```python
usuario: ForeignKey(Persona)
curso: ForeignKey(Course)
fecha_emision: DateTimeField
codigo_verificacion: UUIDField  # único, auto-generado
# Constraint: unique_together = (usuario, curso)
```

### `Class` — app `class_app`
```python
curso: ForeignKey(Course)
titulo: CharField
descripcion: TextField
orden: PositiveIntegerField
video_url: URLField
imagen_portada: URLField  # miniatura
duracion_estimada: IntegerField  # minutos
fecha_creacion: DateTimeField
```

### `MembershipPlan` — app `membership`
```python
name: CharField
slug: SlugField  # único
description: TextField
plan_type: CharField  # MONTHLY | ANNUAL | LIFETIME
duration_days: IntegerField
price: DecimalField
original_price: DecimalField  # para mostrar descuento
features: JSONField  # lista de características
is_active: BooleanField
is_featured: BooleanField  # destacado como mejor opción
display_order: IntegerField
```

### `UserMembership` — app `membership`
```python
user: ForeignKey(Persona)
plan: ForeignKey(MembershipPlan)
start_date: DateTimeField
end_date: DateTimeField  # calculado automáticamente si no se provee
status: CharField  # ACTIVE | EXPIRED | CANCELLED | PENDING
auto_renew: BooleanField
payment_reference: CharField
```

### `Payment` — app `payments`
```python
user: ForeignKey(Persona)
membership_plan: ForeignKey(MembershipPlan)
amount: DecimalField
currency: CharField  # default: USD
payment_method: CharField  # CREDIT_CARD | DEBIT_CARD | PAYPAL | BANK_TRANSFER
card_last_four: CharField  # últimos 4 dígitos
card_brand: CharField  # VISA | MASTERCARD | AMEX | DISCOVER | OTHER
cardholder_name: CharField
status: CharField  # PENDING | COMPLETED | FAILED | REFUNDED
transaction_id: CharField  # único
bank_reference: CharField  # 6–12 dígitos, para transferencias
payment_date: DateTimeField
```

---

## 🌐 Mapa de URLs

### Rutas Públicas (home)
```
/                               → Landing page
/register/                      → Abrir modal de registro
/login/                         → Abrir modal de login
/courses/                       → Catálogo de cursos
/courses/<id>/                  → Preview de curso
/membership/                    → Planes de membresía
/membership/checkout/<slug>/    → Checkout de plan
/membership/payment/success/    → Confirmación de pago
/membership/subscribe/<slug>/   → Suscripción directa (demo)
/learn/<course_id>/             → Reproductor (primera clase)
/learn/<course_id>/class/<id>/  → Reproductor (clase específica)
/learn/<course_id>/certificado/ → Emisión/visualización de certificado
/certificados/                  → Galería personal de certificados
```

### Dashboard Admin (`/dashboard/admin/`)
```
/                               → Overview con métricas
/users/                         → Lista de usuarios (búsqueda, filtros, paginación)
/users/create/                  → Crear usuario
/users/edit/<id>/               → Editar usuario
/users/delete/<id>/             → Eliminar usuario
/courses/                       → Catálogo de cursos (admin)
/courses/view/<id>/             → Detalle de curso
/courses/edit/<id>/             → Editar curso
/courses/delete/<id>/           → Eliminar curso
/subscriptions/                 → Lista de suscripciones
/subscriptions/edit/<id>/       → Editar suscripción
/subscriptions/cancel/<id>/     → Cancelar suscripción
/subscriptions/delete/<id>/     → Eliminar suscripción
/reports/                       → Reportes de ingresos (filtro: mensual/trimestral/anual)
/reports/export-pdf/            → Exportar reporte PDF
/settings/membership/           → Configurar planes de membresía
```

### Dashboard Profesor (`/dashboard/profesor/`)
```
/                               → Mis cursos
/create/                        → Crear curso
/course/<id>/                   → Detalle del curso + gestión de clases
/course/<id>/class/<cid>/delete/→ Eliminar clase (con confirmación modal)
/course/<id>/toggle-publish/    → Publicar/Despublicar curso
/profile/                       → Perfil del profesor
```

### APIs Backend
```
/auth/...                       → Login, logout, registro
/api/courses/...                → CRUD de cursos
/api/classes/...                → CRUD de clases
/api/membership/...             → Planes y suscripciones
/api/payments/...               → Procesamiento de pagos
/api/media/...                  → Subida de archivos
```

---

## 📦 Servicios Principales

### `AnalyticsService` (`Back-end/Analytics/services.py`)
Agrega datos de múltiples dominios para el panel de administración:
- `get_global_metrics()` → membresías activas/expiradas
- `get_revenue_metrics(period)` → ingresos por mes/trimestre/año
- `get_recent_transactions(limit)` → últimas transacciones
- `get_top_courses(limit)` → cursos más recientes publicados
- `get_user_statistics()` → totales y nuevos usuarios
- `get_course_statistics()` → cursos por estado y nivel

### Control de Acceso por Membresía
La función `_require_active_membership(request)` en `Course-Player/views.py` verifica:
```python
UserMembership.objects.filter(
    user=request.user,
    status='ACTIVE',
    start_date__lte=now,
    end_date__gte=now,
).exists()
```
> ⚠️ **No silencia errores**: si el modelo de membresía falla, lanza la excepción para evitar acceso indebido.

---

## 📝 Reglas de Negocio

1. **Membresía Obligatoria**: Solo usuarios con membresía ACTIVE cuya `end_date >= now` pueden acceder al reproductor de clases y obtener certificados.
2. **Rol Único**: Un usuario tiene un solo rol; no puede cambiarlo sin intervención del Admin.
3. **Membresía Única**: No se permiten múltiples membresías ACTIVE simultáneas por usuario.
4. **Suscripción en PENDING**: Las nuevas suscripciones se crean en estado PENDING; el Admin las activa desde el panel.
5. **Sincronización Payment↔Membership**: Al cambiar el estado de una suscripción en el panel admin, el pago asociado se sincroniza (PENDING→ACTIVE marca el pago como COMPLETED).
6. **Certificados**: Se emiten una sola vez por (usuario, curso). Si el usuario ya tiene uno, se recupera el existente.
7. **Separación de Datos**: Los profesores no tienen acceso a tablas de Pago ni estadísticas de alumnos.

---

## 🎨 Stack Tecnológico

| Capa              | Tecnología                                             |
| ----------------- | ------------------------------------------------------ |
| Framework         | Django 4.x (MVT)                                       |
| Base de datos     | SQLite3 (migrable a PostgreSQL)                        |
| Lenguaje          | Python 3.8+                                            |
| Templates         | Django Template Language (DTL)                         |
| Frontend          | HTML5, Vanilla CSS, JavaScript                         |
| Tipografía        | Google Fonts (Inter)                                   |
| Iconos            | Material Symbols                                       |
| PDF Export        | `reportlab` / alternativa de plantilla HTML imprimible |
| Períodos de fecha | `python-dateutil` (`relativedelta`)                    |

---

## 🤝 Contribución

1. Leer la documentación de arquitectura antes de modificar modelos.
2. Respetar la separación Backend / Frontend en la estructura de carpetas.
3. Toda lógica de negocio va en servicios o modelos, **no en las vistas**.
4. Documentar cambios en los archivos `.md` correspondientes.
5. Verificar que el control de acceso por membresía funcione después de cambios en el reproductor.

---

**Última actualización**: Febrero 2026  
**Versión**: 2.0.0
