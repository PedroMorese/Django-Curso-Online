# Especificaciones Técnicas

## Configuración del Proyecto Django

### Archivo: `djangocrud/settings.py`

```python
# Aplicaciones instaladas
INSTALLED_APPS = [
    # Apps nativas de Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Backend apps (lógica de negocio)
    'Back-end.Auth',          # app_label: 'Auth'    → tabla Persona
    'Back-end.Course',        # app_label: 'course_app' → tablas: curso, certificado
    'Back-end.Class',         # app_label: 'class_app'  → tabla: clase
    'Back-end.membership',    # app_label: 'membership' → tablas: membership_plan, user_membership
    'Back-end.payments',      # app_label: 'payments'   → tabla: payments_payment
    'Back-end.Media',         # app_label: 'Media'
    'Back-end.Analytics',     # servicio sin modelos propios

    # Frontend apps (vistas y templates)
    'Front-end.home',
    'Front-end.Dashboard-Admin.Overview',    # app_name: dashboard_admin
    'Front-end.Dashboard-Profesor.MyCourses',# app_name: dashboard_profesor
    'Front-end.Profile',
    'Front-end.Documentation',
]

# Modelo de autenticación personalizado
AUTH_USER_MODEL = 'Auth.Persona'

# Base de datos
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

### URL Router (`djangocrud/urls.py`)

```
Backend Domain URLs:
  /auth/            → Back-end.Auth.urls
  /api/courses/     → Back-end.Course.urls
  /api/classes/     → Back-end.Class.urls
  /api/membership/  → Back-end.membership.urls
  /api/media/       → Back-end.Media.urls
  /api/payments/    → Back-end.payments.urls

Frontend Dashboard URLs:
  /dashboard/profesor/ → Front-end.Dashboard-Profesor.MyCourses.urls
  /dashboard/admin/    → Front-end.Dashboard-Admin.Overview.urls
  /profile/            → Front-end.Profile.urls  (namespace: profile)
  /documentation/      → Front-end.Documentation.urls

Rutas públicas (home):
  /                    → Front-end.home.urls  (namespace: home)
```

---

## Modelos: Definiciones Completas

### `Persona` (CustomUser) — `Back-end/Auth/models.py`

```python
from django.contrib.auth.models import AbstractUser

class Persona(AbstractUser):
    ROLE_CHOICES = (
        ('ADMIN', 'Administrador'),
        ('PROFESOR', 'Profesor'),
        ('CLIENTE', 'Cliente'),
    )
    role  = CharField(max_length=20, choices=ROLE_CHOICES, default='CLIENTE')
    phone = CharField(max_length=20, blank=True, null=True)
    # Hereda: username, email, first_name, last_name, password,
    #         is_active, is_staff, is_superuser, date_joined
```

### `Course` — `Back-end/Course/models.py`

```python
class Course(models.Model):
    NIVEL_CHOICES = [('PRINCIPIANTE',…), ('INTERMEDIO',…), ('AVANZADO',…)]

    titulo             = CharField(max_length=255)
    descripcion        = TextField(blank=True, null=True)
    imagen_portada     = URLField(max_length=500, blank=True, null=True)
    profesor           = ForeignKey(User, on_delete=CASCADE, related_name='cursos_creados')
    fecha_creacion     = DateTimeField(default=timezone.now)
    fecha_actualizacion= DateTimeField(auto_now=True)
    publicado          = BooleanField(default=False)
    nivel              = CharField(max_length=20, choices=NIVEL_CHOICES, default='PRINCIPIANTE')
    duracion_estimada  = IntegerField(blank=True, null=True)  # minutos
    pdf_adjuntos       = TextField(blank=True, null=True, default='[]')  # JSON

    class Meta:
        db_table = 'curso'
        app_label = 'course_app'

    # Propiedades: total_clases, esta_publicado
    # Métodos: publicar(), despublicar()
```

### `Certificate` — `Back-end/Course/models.py`

```python
class Certificate(models.Model):
    usuario           = ForeignKey(User, on_delete=CASCADE, related_name='certificados')
    curso             = ForeignKey(Course, on_delete=CASCADE, related_name='certificados')
    fecha_emision     = DateTimeField(default=timezone.now)
    codigo_verificacion = UUIDField(default=uuid.uuid4, unique=True, editable=False)

    class Meta:
        db_table = 'certificado'
        app_label = 'course_app'
        unique_together = [('usuario', 'curso')]

    # Propiedad: codigo_display (UUID en mayúsculas)
```

### `Class` — `Back-end/Class/models.py`

```python
class Class(models.Model):
    curso              = ForeignKey('course_app.Course', on_delete=CASCADE, related_name='clases')
    titulo             = CharField(max_length=255)
    descripcion        = TextField(blank=True, null=True)
    orden              = PositiveIntegerField(default=0)
    video_url          = URLField(max_length=500, blank=True, null=True)
    imagen_portada     = URLField(max_length=500, blank=True, null=True)  # miniatura
    duracion_estimada  = IntegerField(default=0)  # minutos
    fecha_creacion     = DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'clase'
        app_label = 'class_app'
        ordering = ['orden']
```

### `MembershipPlan` — `Back-end/membership/models.py`

```python
class MembershipPlan(models.Model):
    PLAN_TYPE_CHOICES = [('MONTHLY',…), ('ANNUAL',…), ('LIFETIME',…)]

    name           = CharField(max_length=100)
    slug           = SlugField(max_length=100, unique=True)
    description    = TextField(blank=True)
    plan_type      = CharField(max_length=20, choices=PLAN_TYPE_CHOICES, default='MONTHLY')
    duration_days  = IntegerField(default=30)
    price          = DecimalField(max_digits=10, decimal_places=2)
    original_price = DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    features       = JSONField(default=list, blank=True)  # lista de strings
    is_active      = BooleanField(default=True)
    is_featured    = BooleanField(default=False)
    display_order  = IntegerField(default=0)

    class Meta:
        db_table = 'membership_plan'

    # Propiedades: savings, savings_percentage
```

### `UserMembership` — `Back-end/membership/models.py`

```python
class UserMembership(models.Model):
    STATUS_CHOICES = [('ACTIVE',…), ('EXPIRED',…), ('CANCELLED',…), ('PENDING',…)]

    user               = ForeignKey(User, on_delete=CASCADE, related_name='memberships')
    plan               = ForeignKey(MembershipPlan, on_delete=PROTECT, related_name='subscriptions')
    start_date         = DateTimeField(default=timezone.now)
    end_date           = DateTimeField()  # auto-calculado en save() si no se pasa
    status             = CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    auto_renew         = BooleanField(default=False)
    payment_reference  = CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'user_membership'
        indexes = [Index(fields=['user','status']), Index(fields=['end_date'])]

    # Propiedades: is_active, days_remaining, is_expiring_soon
    # Métodos: activate(), cancel(), expire()

    def save(self, *args, **kwargs):
        # Si end_date no está definida, la calcula automáticamente
        if not self.end_date:
            self.end_date = self.start_date + timedelta(days=self.plan.duration_days)
        super().save(*args, **kwargs)
```

### `Payment` — `Back-end/payments/models.py`

```python
class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('CREDIT_CARD',…), ('DEBIT_CARD',…), ('PAYPAL',…), ('BANK_TRANSFER',…)
    ]
    STATUS_CHOICES = [('PENDING',…), ('COMPLETED',…), ('FAILED',…), ('REFUNDED',…)]
    CARD_BRAND_CHOICES = [('VISA',…), ('MASTERCARD',…), ('AMEX',…), ('DISCOVER',…), ('OTHER',…)]

    user             = ForeignKey(settings.AUTH_USER_MODEL, on_delete=CASCADE)
    membership_plan  = ForeignKey('membership.MembershipPlan', on_delete=PROTECT)
    amount           = DecimalField(max_digits=10, decimal_places=2)
    currency         = CharField(max_length=3, default='USD')
    payment_method   = CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    card_last_four   = CharField(max_length=4, blank=True)
    card_brand       = CharField(max_length=20, choices=CARD_BRAND_CHOICES, blank=True)
    cardholder_name  = CharField(max_length=100, blank=True)
    status           = CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    transaction_id   = CharField(max_length=100, unique=True)
    bank_reference   = CharField(max_length=12, blank=True, null=True)
    # validators: RegexValidator(r'^\d{6,12}$') para bank_reference

    class Meta:
        db_table = 'payments_payment'
        indexes = [
            Index(fields=['-payment_date']),
            Index(fields=['user', 'status']),
            Index(fields=['transaction_id']),
        ]

    # Propiedades: is_successful, masked_card_number
```

---

## Dependencias (`requirements.txt`)

```
Django>=4.0
python-dateutil      # relativedelta para cálculo de períodos en reportes
reportlab            # (si se usa para exportar PDF con generación programática)
```

---

## Variables de Entorno (Desarrollo)

```python
# djangocrud/settings.py
DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

MEDIA_URL  = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

STATIC_URL = '/static/'
```

---

## Convenciones del Proyecto

### App Labels
Usamos app labels explícitos para evitar conflictos con rutas de carpetas no-estándar:

| Carpeta               | `app_label` en Meta |
| --------------------- | ------------------- |
| `Back-end/Auth`       | `Auth`              |
| `Back-end/Course`     | `course_app`        |
| `Back-end/Class`      | `class_app`         |
| `Back-end/membership` | `membership`        |
| `Back-end/payments`   | `payments`          |
| `Back-end/Media`      | `Media`             |

### Referencias entre modelos
Usar strings en `ForeignKey` para evitar importaciones circulares:
```python
# ✅ Correcto
curso = ForeignKey('course_app.Course', on_delete=CASCADE)

# ❌ Evitar importaciones directas entre apps de Back-end
from Back-end.Course.models import Course
```

### Obtener modelos desde otras apps
```python
from django.apps import apps
Course = apps.get_model('course_app', 'Course')
UserMembership = apps.get_model('membership', 'UserMembership')
```

---

**Última actualización**: Febrero 2026
