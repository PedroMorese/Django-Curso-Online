# Blueprint Técnico — Guía de Implementación

Este documento sirve como referencia técnica detallada de los módulos implementados, sus responsabilidades y cómo interactúan entre sí.

---

## 1. Backend: Módulos y Servicios

### 1.1 Módulo `Auth` — Gestión de Usuarios

**Modelo**: `Persona` (extiende `AbstractUser`)

| Campo       | Tipo      | Descripción                                                                |
| ----------- | --------- | -------------------------------------------------------------------------- |
| `role`      | CharField | `ADMIN` \| `PROFESOR` \| `CLIENTE` (default: CLIENTE)                      |
| `phone`     | CharField | Teléfono opcional                                                          |
| (heredados) |           | `username`, `email`, `first_name`, `last_name`, `is_active`, `date_joined` |

**Decorador de acceso admin**:
```python
# Front-end/Dashboard-Admin/Overview/views.py
def admin_required(view_func):
    """Requiere role='ADMIN' OR is_staff OR is_superuser"""
```

**Validaciones al crear usuario (Admin Panel)**:
- Email requerido y único
- Password mínimo 6 caracteres
- Rol válido: `ADMIN`, `PROFESOR` o `CLIENTE`

---

### 1.2 Módulo `Course` — Cursos y Certificados

**Modelos**: `Course`, `Certificate`

#### `Course`
- `db_table = 'curso'`, `app_label = 'course_app'`
- `pdf_adjuntos`: campo `TextField` que almacena JSON con lista de URLs de PDFs
- Índices: `profesor`, `publicado`, `-fecha_creacion`
- Propiedades: `total_clases` (count de FK inversa), `esta_publicado`
- Métodos: `publicar()`, `despublicar()` (update solo campo `publicado`)

#### `Certificate`
- `db_table = 'certificado'`, `app_label = 'course_app'`
- `unique_together = ('usuario', 'curso')` → un certificado por (usuario, curso)
- `codigo_verificacion`: UUID auto-generado, inmutable
- Usado con `get_or_create()` para idempotencia

---

### 1.3 Módulo `Class` — Clases/Lecciones

**Modelo**: `Class`
- `db_table = 'clase'`, `app_label = 'class_app'`
- `ordering = ['orden']` por defecto
- FK a `course_app.Course` (string para evitar ciclos de importación)
- El profesor gestiona el orden manualmente mediante el campo `orden`

---

### 1.4 Módulo `membership` — Sistema de Membresías

**Modelos**: `MembershipPlan`, `UserMembership`

#### `MembershipPlan`
- `features`: `JSONField` con lista de strings (características del plan)
- `is_featured`: marca el plan como "mejor opción" (máximo uno por convención)
- `savings` y `savings_percentage`: propiedades calculadas del precio de descuento

#### `UserMembership`
- `save()` sobrescrito: calcula `end_date` automáticamente si no se proporciona
  ```python
  end_date = start_date + timedelta(days=plan.duration_days)
  ```
- Propiedades: `is_active`, `days_remaining`, `is_expiring_soon` (≤7 días)
- Métodos de estado: `activate()`, `cancel()`, `expire()`
- Las nuevas suscripciones se crean en `status='PENDING'`

---

### 1.5 Módulo `payments` — Sistema de Pagos

**Modelo**: `Payment`
- Almacena solo los últimos 4 dígitos de la tarjeta (`card_last_four`)
- `bank_reference`: validado con regex `^\d{6,12}$` (para transferencias bancarias)
- `transaction_id`: único en toda la tabla
- **Modo Demo**: no se realizan cargos reales
- Sincronización con `UserMembership` al activar suscripción desde el panel admin:
  ```
  UserMembership.status PENDING → ACTIVE
      └── Payment.status PENDING → COMPLETED (si existe el Payment vinculado)
  ```

---

### 1.6 Módulo `Analytics` — Servicio de Analíticas

**Clase**: `AnalyticsService` (`Back-end/Analytics/services.py`)

Métodos disponibles:

| Método                           | Parámetros                           | Retorna                                      |
| -------------------------------- | ------------------------------------ | -------------------------------------------- |
| `get_global_metrics()`           | —                                    | Dict: active/expired memberships, uptime     |
| `get_revenue_metrics(period)`    | `'month'` \| `'quarter'` \| `'year'` | Dict: revenue, goal, progress%               |
| `get_recent_transactions(limit)` | `int` (default 10)                   | List de dicts con user, plan, amount, status |
| `get_top_courses(limit)`         | `int` (default 5)                    | List de dicts con id, title, professor       |
| `get_user_statistics()`          | —                                    | Dict: total_users, new_users_this_month      |
| `get_course_statistics()`        | —                                    | Dict: total, published, draft, by_level      |

> **Nota**: El módulo `reports()` en `Dashboard-Admin/Overview/views.py` implementa directamente la lógica de reportes con `python-dateutil.relativedelta` para periodos precisos (mensual, trimestral, anual).

---

## 2. Frontend: Módulos y Templates

### 2.1 Módulo `home` — Área Pública

**Namespace de URLs**: `home`

| Vista                            | URL                        | Template                              |
| -------------------------------- | -------------------------- | ------------------------------------- |
| `home()`                         | `/`                        | `Home.html`                           |
| `course_catalog()`               | `/courses/`                | `catalog/course_list.html`            |
| `course_preview()`               | `/courses/<id>/`           | `catalog/course_preview.html`         |
| `membership_plans_redirect()`    | `/membership/`             | (redirect a `Membership/views.py`)    |
| `course_player_redirect()`       | `/learn/<id>/`             | `course_player/player.html`           |
| `course_player_class_redirect()` | `/learn/<id>/class/<cid>/` | `course_player/player.html`           |
| `course_certificate_redirect()`  | `/learn/<id>/certificado/` | `course_player/certificado.html`      |
| `my_certificates()`              | `/certificados/`           | `course_player/mis_certificados.html` |

#### Sub-módulo: `Course-Player`
**Namespace**: `course_player`

Contiene las vistas canónicas del reproductor:
- `course_player(request, course_id, class_id=None)` → carga clase actual + sidebar
- `course_overview(request, course_id)` → lista de clases del curso
- `course_certificate(request, course_id)` → emite/recupera certificado

**Verificación de membresía** (`_require_active_membership`):
```python
def _require_active_membership(request) -> bool:
    UserMembership = apps.get_model('membership', 'UserMembership')
    return UserMembership.objects.filter(
        user=request.user,
        status='ACTIVE',
        start_date__lte=timezone.now(),
        end_date__gte=timezone.now(),
    ).exists()
    # ⚠️ NO captura excepciones: errores en el ORM son explícitos
```

#### Sub-módulo: `Membership`
- `membership_plans()` → lista planes activos ordenados por precio
- `checkout(plan_slug)` → formulario de pago (tarjeta o transferencia)
- `payment_success()` → confirmación post-pago
- `subscribe(plan_slug)` → suscripción directa en modo demo (crea membresía PENDING)

---

### 2.2 Dashboard Admin — `Overview`

**Namespace**: `dashboard_admin`

Vistas implementadas y sus funciones:

| Vista                   | Funcionalidad                                                            |
| ----------------------- | ------------------------------------------------------------------------ |
| `overview()`            | Métricas en tiempo real desde BD                                         |
| `users_list()`          | Lista con búsqueda, filtros por rol/estado, paginación (10/pág)          |
| `create_user()`         | Formulario de creación con validaciones                                  |
| `edit_user()`           | Edición de nombre, email, rol, estado activo                             |
| `delete_user()`         | Eliminación con manejo de errores                                        |
| `courses_list()`        | Lista con búsqueda, filtros por nivel/publicado, paginación (9/pág)      |
| `view_course()`         | Ver detalle del curso                                                    |
| `edit_course()`         | Editar título, descripción, nivel, imagen, publicado                     |
| `delete_course()`       | Eliminación con manejo de errores                                        |
| `subscriptions_list()`  | Membresías con búsqueda, filtros por plan/estado, paginación (10/pág)    |
| `edit_subscription()`   | Cambiar plan y/o estado (sincroniza Payment)                             |
| `cancel_subscription()` | Cambiar status → EXPIRED                                                 |
| `delete_subscription()` | Eliminar registro de BD                                                  |
| `reports()`             | Reportes con filtro de período (monthly/quarterly/yearly), gráficos, PDF |
| `export_report_pdf()`   | Generar PDF del reporte                                                  |
| `membership_settings()` | Configurar planes de membresía                                           |

---

### 2.3 Dashboard Profesor — `MyCourses`

**Namespace**: `dashboard_profesor`

| Vista              | Funcionalidad                                  |
| ------------------ | ---------------------------------------------- |
| `my_courses()`     | Lista los cursos donde `profesor=request.user` |
| `create_course()`  | Formulario de creación de curso                |
| `course_detail()`  | CRUD de clases del curso (inline)              |
| `delete_class()`   | Eliminar clase con confirmación modal JS       |
| `toggle_publish()` | Alternar `Course.publicado` True/False         |
| `profile()`        | Perfil del profesor autenticado                |

**Modal de confirmación de eliminación de clase**:
```javascript
// Implementado en JavaScript del template
function confirmDeleteClass(classId, courseId) {
    // Muestra modal → POST /course/<id>/class/<cid>/delete/
}
```

---

## 3. Convenciones de Código

### Imports de modelos entre apps
```python
# ✅ Usar apps.get_model() en vistas para evitar problemas de importación
from django.apps import apps
Course = apps.get_model('course_app', 'Course')
UserMembership = apps.get_model('membership', 'UserMembership')
```

### Manejo de errores en vistas admin
```python
try:
    # operación de BD
except ModelClass.DoesNotExist:
    messages.error(request, 'Registro no encontrado.')
except Exception as e:
    messages.error(request, f'Error: {str(e)}')
return redirect('dashboard_admin:vista_lista')
```

### Templates: extensión de base
```html
{% extends "base/base.html" %}
{% block content %}
  <!-- contenido específico sin duplicar header/nav -->
{% endblock %}
```
> ⚠️ **Regla**: Los templates específicos (como `certificado.html`) NO deben incluir su propio header/nav si ya extienden un base template que los provee.

---

## 4. Flujo de Desarrollo: Añadir Nueva Feature

1. **Definir modelo** en `Back-end/<Módulo>/models.py`
2. **Crear migración**: `python manage.py makemigrations`
3. **Aplicar migración**: `python manage.py migrate`
4. **Crear/editar vista backend** en `Back-end/<Módulo>/views.py`
5. **Registrar URL backend** en `Back-end/<Módulo>/urls.py`
6. **Crear vista frontend** en `Front-end/<Dashboard>/views.py`
7. **Registrar URL frontend** en `Front-end/<Dashboard>/urls.py`
8. **Crear/editar template** en el directorio `templates/` correspondiente
9. **Actualizar documentación** en los archivos `.md` correspondientes

---

**Última actualización**: Febrero 2026
