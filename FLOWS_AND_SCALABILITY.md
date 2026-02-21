# Escalabilidad y Flujos del Sistema

## Estado Actual vs. Escalabilidad Futura

### Arquitectura Actual

```
┌─────────────────────────────────────────────────────┐
│                  Cliente (Browser)                  │
└─────────────────────────┬───────────────────────────┘
                          │ HTTP + Django Session Auth
┌─────────────────────────▼───────────────────────────┐
│            Django (MVT Monolítico)                  │
│  ┌─────────────────────────────────────────────┐    │
│  │  djangocrud/urls.py → Router principal      │    │
│  │  Back-end/ apps → Models + APIs             │    │
│  │  Front-end/ apps → Views + Templates        │    │
│  │  Analytics/ → Services (cross-domain)       │    │
│  └─────────────────────────────────────────────┘    │
│                          │                          │
│              ┌───────────▼────────────┐             │
│              │      SQLite3 DB        │             │
│              └────────────────────────┘             │
└─────────────────────────────────────────────────────┘
```

---

## Estrategias de Escalabilidad

### 1. Base de Datos: SQLite → PostgreSQL

**Cambio requerido** (solo en settings):
```python
# Actual (desarrollo):
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Producción:
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}
```

**Sin cambios requeridos**: los modelos, ORM queries y migraciones son compatibles.

---

### 2. Authentication: Session → JWT (API-first)

**Actual**: Django session-based auth (cookies).

**Migración**:
```
pip install djangorestframework djangorestframework-simplejwt

# settings.py
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
}
```

Los modelos no cambian; solo se añaden serializers y cambian las vistas.

---

### 3. APIs: Vistas Django → Django REST Framework

**Actual**: Vistas Django estándar que retornan JSON o HTML.

**Migración gradual** (por módulo):
```
Back-end/Course/views.py  →  Back-end/Course/serializers.py + APIView
Back-end/Class/views.py   →  Back-end/Class/serializers.py + APIView
...
```

Los modelos existentes son 100% compatibles con DRF Serializers.

---

### 4. Archivos: Local → Cloud Storage

**Actual**: `media/` folder local.

**Migración**:
```python
pip install django-storages boto3

# settings.py
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_BUCKET')
AWS_ACCESS_KEY_ID = os.environ.get('AWS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET')
```

---

### 5. Pagos: Demo → Pasarela Real

**Actual**: Modo simulado (registra intención de pago, admin aprueba manualmente).

**Migración con Stripe**:
```python
pip install stripe

# En la vista checkout:
import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

payment_intent = stripe.PaymentIntent.create(
    amount=int(plan.price * 100),
    currency='usd',
    metadata={'user_id': user.id, 'plan_id': plan.id}
)
# → webhook para activar membresía automáticamente
```

---

### 6. Deploy: `runserver` → Producción

```
Desarrollo:  python manage.py runserver
Producción:  gunicorn djangocrud.wsgi:application --bind 0.0.0.0:8000
             + Nginx como reverse proxy
             + Supervisor/systemd para process management
```

**Variables de entorno** (producción):
```bash
SECRET_KEY=<clave-larga-aleatoria>
DEBUG=False
ALLOWED_HOSTS=tu-dominio.com
DATABASE_URL=postgres://...
```

---

## Módulos Actuales: Estado de Implementación

| Módulo            | Modelos                          | API Backend        | Dashboard Frontend    | Estado        |
| ----------------- | -------------------------------- | ------------------ | --------------------- | ------------- |
| Auth / Usuarios   | ✅ Persona                        | ✅ Login/Logout     | ✅ Admin CRUD completo | **Completo**  |
| Cursos            | ✅ Course                         | ✅ CRUD API         | ✅ Profesor + Admin    | **Completo**  |
| Certificados      | ✅ Certificate                    | ✅ get_or_create    | ✅ Player + galería    | **Completo**  |
| Clases            | ✅ Class                          | ✅ CRUD API         | ✅ Profesor inline     | **Completo**  |
| Membresías        | ✅ MembershipPlan, UserMembership | ✅ API              | ✅ Admin CRUD          | **Completo**  |
| Pagos             | ✅ Payment                        | ✅ API demo         | ✅ Admin lista         | **Demo**      |
| Analytics         | — (servicio)                     | ✅ AnalyticsService | ✅ Reportes + PDF      | **Completo**  |
| Perfil            | —                                | —                  | ✅ Vista perfil        | **Básico**    |
| Notificaciones    | ❌                                | ❌                  | ❌                     | **Pendiente** |
| Búsqueda global   | ❌                                | ❌                  | —                     | **Pendiente** |
| Progreso de curso | ❌                                | ❌                  | —                     | **Pendiente** |

---

## Flujos de Datos Críticos

### Flujo de Acceso a Clase (crítico para negocio)

```
Request: GET /learn/<course_id>/class/<class_id>/
    │
    ├─ @login_required
    │   └─ NO autenticado → redirect /auth/login/
    │
    ├─ _require_active_membership(request)
    │   └─ SELECT user_membership WHERE user=X AND status='ACTIVE'
    │       AND start_date<=NOW AND end_date>=NOW
    │   └─ FALSE → messages.warning → redirect /membership/
    │
    ├─ Course.objects.get_or_404(id=course_id, publicado=True)
    │
    ├─ Class.objects.filter(curso=course).order_by('orden')
    │
    ├─ current_class = Class.objects.get(id=class_id, curso=course)
    │
    ├─ Calcular prev_class, next_class, progress%, is_last_class
    │
    └─ render 'course_player/player.html' con contexto completo
```

### Flujo de Activación de Membresía (Admin)

```
Admin: POST /dashboard/admin/subscriptions/edit/<id>/
    │
    ├─ Obtener UserMembership
    ├─ Si new_plan != actual → membership.plan = new_plan
    ├─ Si new_status != actual:
    │   ├─ membership.status = new_status
    │   └─ Sincronizar Payment:
    │       ├─ PENDING → ACTIVE: Payment.status = 'COMPLETED'
    │       └─ ACTIVE → PENDING: Payment.status = 'PENDING'
    │       # ACTIVE/PENDING → EXPIRED: no se toca el Payment
    ├─ membership.save()
    └─ messages.success + redirect subscriptions_list
```

### Flujo de Reporte (Admin)

```
Admin: GET /dashboard/admin/reports/?period=quarterly
    │
    ├─ Determinar rango de fechas (relativedelta)
    │   ├─ monthly:   inicio del mes actual
    │   ├─ quarterly: inicio del trimestre actual
    │   └─ yearly:    1 de enero del año actual
    │
    ├─ Payment.objects.filter(status='COMPLETED', created_at__range=...)
    │   .aggregate(total=Sum('amount'))
    │
    ├─ UserMembership stats para el período
    ├─ User stats (nuevos usuarios, total)
    ├─ Course stats (publicados, borradores)
    │
    └─ render 'dashboard_admin/reports.html' con métricas calculadas
```

---

## Preparación Futura: Features Pendientes

### Progreso de Clase
```python
# Modelo a crear:
class ClassProgress(models.Model):
    user = ForeignKey(Persona)
    clase = ForeignKey(Class)
    completado = BooleanField(default=False)
    fecha_completado = DateTimeField(null=True)
    
    class Meta:
        unique_together = ('user', 'clase')
```

### Notificaciones
```python
# Posible implementación con Django Channels (WebSocket)
# o polling desde el frontend con fetch() a un endpoint JSON
```

### Búsqueda Global
```python
# Con django.contrib.postgres.search (requiere PostgreSQL)
# o con filtros Q() actuales en SQLite:
Course.objects.filter(
    Q(titulo__icontains=query) | Q(descripcion__icontains=query)
)
```

---

**Última actualización**: Febrero 2026
