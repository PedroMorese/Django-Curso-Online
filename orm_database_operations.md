# Documentación de Operaciones ORM - Base de Datos del Proyecto

**Proyecto:** Sistema de Gestión de Cursos Online  
**Fecha:** 2026-02-05  
**Objetivo:** Documentar todas las operaciones de base de datos realizadas mediante el ORM de Django

---

## Tabla de Contenidos

1. [Módulo Auth (Autenticación)](#módulo-auth)
2. [Módulo Course (Cursos)](#módulo-course)
3. [Módulo Class (Clases)](#módulo-class)
4. [Módulo Membership (Membresías)](#módulo-membership)
5. [Resumen de Operaciones](#resumen-de-operaciones)

---

## Módulo Auth

### Modelos Definidos

#### Modelo `Persona`
Extiende `AbstractUser` de Django para agregar roles y campos personalizados.

```python
class Persona(AbstractUser):
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='CLIENTE')
    phone = models.CharField(max_length=20, blank=True, null=True)
```

**Tabla en BD:** `auth_persona`

---

### Operaciones del ORM - Auth

| Archivo                                                                            | Función ORM                                                | Descripción                                                          | SQL Equivalente                                                                                                                                       |
| ---------------------------------------------------------------------------------- | ---------------------------------------------------------- | -------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| [views.py](file:///c:/Users/Pedro/Desktop/Proyecto_db/Back-end/Auth/views.py#L49)  | `get_user_model()`                                         | Obtiene el modelo de usuario activo (Persona)                        | N/A - Función de Django                                                                                                                               |
| [views.py](file:///c:/Users/Pedro/Desktop/Proyecto_db/Back-end/Auth/views.py#L67)  | `User.objects.create_user(**kwargs, password=password)`    | Crea un nuevo usuario con password hasheado usando PBKDF2            | `INSERT INTO auth_persona (username, email, password, first_name, last_name, role, phone, is_active, date_joined) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)` |
| [views.py](file:///c:/Users/Pedro/Desktop/Proyecto_db/Back-end/Auth/views.py#L78)  | `user.save()`                                              | Guarda cambios en el usuario existente                               | `UPDATE auth_persona SET first_name=?, last_name=?, role=? WHERE id=?`                                                                                |
| [views.py](file:///c:/Users/Pedro/Desktop/Proyecto_db/Back-end/Auth/views.py#L123) | `authenticate(request, username=email, password=password)` | Verifica credenciales del usuario comparando password con hash en BD | `SELECT * FROM auth_persona WHERE username=? LIMIT 1` + verificación de hash                                                                          |
| [views.py](file:///c:/Users/Pedro/Desktop/Proyecto_db/Back-end/Auth/views.py#L130) | `User.objects.filter(email__iexact=email).first()`         | Busca usuario por email (case-insensitive) y retorna el primero      | `SELECT * FROM auth_persona WHERE LOWER(email) = LOWER(?) LIMIT 1`                                                                                    |
| [views.py](file:///c:/Users/Pedro/Desktop/Proyecto_db/Back-end/Auth/views.py#L143) | `login(request, user)`                                     | Crea sesión de usuario y envía cookie `sessionid`                    | `INSERT INTO django_session (session_key, session_data, expire_date) VALUES (?, ?, ?)`                                                                |
| [views.py](file:///c:/Users/Pedro/Desktop/Proyecto_db/Back-end/Auth/views.py#L154) | `logout(request)`                                          | Destruye la sesión del usuario                                       | `DELETE FROM django_session WHERE session_key=?`                                                                                                      |

---

## Módulo Course

### Modelos Definidos

#### Modelo `Course`
Representa un curso creado por un profesor.

```python
class Course(models.Model):
    titulo = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True, null=True)
    imagen_portada = models.URLField(max_length=500, blank=True, null=True)
    profesor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cursos_creados')
    fecha_creacion = models.DateTimeField(default=timezone.now)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    publicado = models.BooleanField(default=False)
    nivel = models.CharField(max_length=20, choices=NIVEL_CHOICES, default='PRINCIPIANTE')
    duracion_estimada = models.IntegerField(blank=True, null=True)
```

**Tabla en BD:** `curso`

---

### Operaciones del ORM - Course

| Archivo                                                                                   | Función ORM                                                                      | Descripción                                                  | SQL Equivalente                                                                                                                                             |
| ----------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------- | ------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [views.py](file:///c:/Users/Pedro/Desktop/Proyecto_db/Back-end/Course/views.py#L54)       | `Course.objects.all()`                                                           | Obtiene todos los cursos                                     | `SELECT * FROM curso`                                                                                                                                       |
| [views.py](file:///c:/Users/Pedro/Desktop/Proyecto_db/Back-end/Course/views.py#L64)       | `cursos.filter(Q(profesor=user) \| Q(publicado=True))`                           | Filtra cursos del profesor o publicados (OR lógico)          | `SELECT * FROM curso WHERE (profesor_id=? OR publicado=1)`                                                                                                  |
| [views.py](file:///c:/Users/Pedro/Desktop/Proyecto_db/Back-end/Course/views.py#L67)       | `cursos.filter(publicado=True)`                                                  | Filtra solo cursos publicados                                | `SELECT * FROM curso WHERE publicado=1`                                                                                                                     |
| [views.py](file:///c:/Users/Pedro/Desktop/Proyecto_db/Back-end/Course/views.py#L73)       | `cursos.filter(publicado=publicado_bool)`                                        | Filtra por estado de publicación                             | `SELECT * FROM curso WHERE publicado=?`                                                                                                                     |
| [views.py](file:///c:/Users/Pedro/Desktop/Proyecto_db/Back-end/Course/views.py#L77)       | `cursos.filter(nivel=nivel.upper())`                                             | Filtra cursos por nivel de dificultad                        | `SELECT * FROM curso WHERE nivel=?`                                                                                                                         |
| [views.py](file:///c:/Users/Pedro/Desktop/Proyecto_db/Back-end/Course/views.py#L81-L83)   | `cursos.filter(Q(titulo__icontains=search) \| Q(descripcion__icontains=search))` | Búsqueda de texto en título o descripción (case-insensitive) | `SELECT * FROM curso WHERE (titulo LIKE '%?%' OR descripcion LIKE '%?%')`                                                                                   |
| [views.py](file:///c:/Users/Pedro/Desktop/Proyecto_db/Back-end/Course/views.py#L87)       | `cursos.filter(profesor_id=profesor_id)`                                         | Filtra cursos por ID del profesor                            | `SELECT * FROM curso WHERE profesor_id=?`                                                                                                                   |
| [views.py](file:///c:/Users/Pedro/Desktop/Proyecto_db/Back-end/Course/views.py#L91)       | `cursos.select_related('profesor')`                                              | Optimiza query con JOIN para evitar N+1 queries              | `SELECT * FROM curso INNER JOIN auth_persona ON curso.profesor_id = auth_persona.id`                                                                        |
| [views.py](file:///c:/Users/Pedro/Desktop/Proyecto_db/Back-end/Course/views.py#L142-L150) | `Course.objects.create(titulo=..., profesor=user, ...)`                          | Crea un nuevo curso                                          | `INSERT INTO curso (titulo, descripcion, imagen_portada, profesor_id, nivel, duracion_estimada, publicado, fecha_creacion) VALUES (?, ?, ?, ?, ?, ?, ?, ?)` |
| [views.py](file:///c:/Users/Pedro/Desktop/Proyecto_db/Back-end/Course/views.py#L179)      | `Course.objects.select_related('profesor').get(id=course_id)`                    | Obtiene un curso por ID con JOIN al profesor                 | `SELECT * FROM curso INNER JOIN auth_persona ON curso.profesor_id = auth_persona.id WHERE curso.id=? LIMIT 1`                                               |
| [views.py](file:///c:/Users/Pedro/Desktop/Proyecto_db/Back-end/Course/views.py#L244)      | `curso.save()`                                                                   | Actualiza campos del curso                                   | `UPDATE curso SET titulo=?, descripcion=?, imagen_portada=?, nivel=?, duracion_estimada=?, publicado=?, fecha_actualizacion=? WHERE id=?`                   |
| [views.py](file:///c:/Users/Pedro/Desktop/Proyecto_db/Back-end/Course/views.py#L271)      | `curso.delete()`                                                                 | Elimina un curso (CASCADE elimina clases relacionadas)       | `DELETE FROM curso WHERE id=?` + `DELETE FROM clase WHERE curso_id=?`                                                                                       |
| [views.py](file:///c:/Users/Pedro/Desktop/Proyecto_db/Back-end/Course/views.py#L312)      | `curso.save(update_fields=['publicado'])`                                        | Actualiza solo el campo especificado (optimización)          | `UPDATE curso SET publicado=?, fecha_actualizacion=? WHERE id=?`                                                                                            |
| [views.py](file:///c:/Users/Pedro/Desktop/Proyecto_db/Back-end/Course/views.py#L338)      | `Course.objects.filter(profesor=user).order_by('-fecha_creacion')`               | Filtra cursos del profesor ordenados por fecha descendente   | `SELECT * FROM curso WHERE profesor_id=? ORDER BY fecha_creacion DESC`                                                                                      |
| [models.py](file:///c:/Users/Pedro/Desktop/Proyecto_db/Back-end/Course/models.py#L70)     | `self.clases.count()`                                                            | Cuenta clases relacionadas (propiedad `total_clases`)        | `SELECT COUNT(*) FROM clase WHERE curso_id=?`                                                                                                               |

---

## Módulo Class

### Modelos Definidos

#### Modelo `Class`
Representa una clase/lección dentro de un curso.

```python
class Class(models.Model):
    curso = models.ForeignKey('course_app.Course', on_delete=models.CASCADE, related_name='clases')
    titulo = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True, null=True)
    orden = models.PositiveIntegerField(default=0)
    video_url = models.URLField(max_length=500, blank=True, null=True)
    imagen_portada = models.URLField(max_length=500, blank=True, null=True)
    duracion_estimada = models.IntegerField(default=0)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
```

**Tabla en BD:** `clase`

---

### Operaciones del ORM - Class

| Archivo                                                                             | Función ORM                                              | Descripción                                | SQL Equivalente                                                                                                    |
| ----------------------------------------------------------------------------------- | -------------------------------------------------------- | ------------------------------------------ | ------------------------------------------------------------------------------------------------------------------ |
| [views.py](file:///c:/Users/Pedro/Desktop/Proyecto_db/Back-end/Class/views.py#L29)  | `Class.objects.all()`                                    | Obtiene todas las clases                   | `SELECT * FROM clase`                                                                                              |
| [views.py](file:///c:/Users/Pedro/Desktop/Proyecto_db/Back-end/Class/views.py#L32)  | `classes.filter(curso_id=curso_id)`                      | Filtra clases por ID del curso             | `SELECT * FROM clase WHERE curso_id=?`                                                                             |
| [views.py](file:///c:/Users/Pedro/Desktop/Proyecto_db/Back-end/Class/views.py#L34)  | `classes.order_by('orden')`                              | Ordena clases por campo `orden` ascendente | `SELECT * FROM clase ORDER BY orden ASC`                                                                           |
| [views.py](file:///c:/Users/Pedro/Desktop/Proyecto_db/Back-end/Class/views.py#L57)  | `Class.objects.select_related('curso').get(id=class_id)` | Obtiene clase por ID con JOIN al curso     | `SELECT * FROM clase INNER JOIN curso ON clase.curso_id = curso.id WHERE clase.id=? LIMIT 1`                       |
| [views.py](file:///c:/Users/Pedro/Desktop/Proyecto_db/Back-end/Class/views.py#L111) | `clase.save()`                                           | Actualiza campos de la clase               | `UPDATE clase SET titulo=?, descripcion=?, orden=?, duracion_estimada=?, video_url=?, imagen_portada=? WHERE id=?` |

---

## Módulo Membership

### Modelos Definidos

#### Modelo `MembershipPlan`
Define los planes de membresía disponibles.

```python
class MembershipPlan(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    plan_type = models.CharField(max_length=20, choices=PLAN_TYPE_CHOICES, default='MONTHLY')
    duration_days = models.IntegerField(default=30)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    original_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    features = models.JSONField(default=list, blank=True)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    display_order = models.IntegerField(default=0)
```

**Tabla en BD:** `membership_plan`

#### Modelo `UserMembership`
Representa la suscripción de un usuario a un plan.

```python
class UserMembership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='memberships')
    plan = models.ForeignKey(MembershipPlan, on_delete=models.PROTECT, related_name='subscriptions')
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    auto_renew = models.BooleanField(default=False)
    payment_reference = models.CharField(max_length=255, blank=True, null=True)
```

**Tabla en BD:** `user_membership`

---

### Operaciones del ORM - Membership

| Archivo                                                                                  | Función ORM                                                                                | Descripción                                           | SQL Equivalente                                                                                                                                        |
| ---------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------ | ----------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| views.py (via services)                                                                  | `MembershipPlan.objects.filter(is_active=True).order_by('display_order', 'price')`         | Obtiene planes activos ordenados                      | `SELECT * FROM membership_plan WHERE is_active=1 ORDER BY display_order ASC, price ASC`                                                                |
| views.py (via services)                                                                  | `MembershipPlan.objects.filter(slug=slug, is_active=True).first()`                         | Busca plan por slug                                   | `SELECT * FROM membership_plan WHERE slug=? AND is_active=1 LIMIT 1`                                                                                   |
| views.py (via services)                                                                  | `UserMembership.objects.filter(user=user, status='ACTIVE').select_related('plan').first()` | Obtiene membresía activa del usuario con JOIN al plan | `SELECT * FROM user_membership INNER JOIN membership_plan ON user_membership.plan_id = membership_plan.id WHERE user_id=? AND status='ACTIVE' LIMIT 1` |
| [views.py](file:///c:/Users/Pedro/Desktop/Proyecto_db/Back-end/membership/views.py#L174) | `MembershipPlan.objects.get(slug=slug)`                                                    | Obtiene plan por slug (lanza excepción si no existe)  | `SELECT * FROM membership_plan WHERE slug=? LIMIT 1`                                                                                                   |
| [views.py](file:///c:/Users/Pedro/Desktop/Proyecto_db/Back-end/membership/views.py#L178) | `plan.save()`                                                                              | Actualiza precio y configuración del plan             | `UPDATE membership_plan SET price=?, original_price=?, is_active=?, updated_at=? WHERE id=?`                                                           |
| models.py                                                                                | `membership.activate()`                                                                    | Cambia status a ACTIVE                                | `UPDATE user_membership SET status='ACTIVE', updated_at=? WHERE id=?`                                                                                  |
| models.py                                                                                | `membership.cancel()`                                                                      | Cancela membresía y desactiva auto-renovación         | `UPDATE user_membership SET status='CANCELLED', auto_renew=0, updated_at=? WHERE id=?`                                                                 |
| models.py                                                                                | `membership.expire()`                                                                      | Marca membresía como expirada                         | `UPDATE user_membership SET status='EXPIRED', updated_at=? WHERE id=?`                                                                                 |

---

## Resumen de Operaciones

### Operaciones por Tipo

| Tipo de Operación | Función ORM                                          | Cantidad de Usos |
| ----------------- | ---------------------------------------------------- | ---------------- |
| **CREATE**        | `objects.create()`, `create_user()`                  | 3                |
| **READ**          | `objects.all()`, `objects.get()`, `objects.filter()` | 20+              |
| **UPDATE**        | `save()`, `save(update_fields=[])`                   | 10+              |
| **DELETE**        | `delete()`                                           | 2                |

### Optimizaciones Implementadas

| Optimización             | Descripción                       | Beneficio                                         |
| ------------------------ | --------------------------------- | ------------------------------------------------- |
| `select_related()`       | JOIN en queries de ForeignKey     | Reduce queries de N+1 a 1                         |
| `save(update_fields=[])` | Actualiza solo campos específicos | Reduce tamaño de query UPDATE                     |
| `filter().first()`       | Usa LIMIT 1 en búsquedas          | Más eficiente que `get()` cuando puede no existir |
| Índices en BD            | `indexes = [...]` en Meta         | Acelera búsquedas frecuentes                      |

### Queries Complejos

#### 1. Búsqueda con OR lógico
```python
cursos.filter(Q(titulo__icontains=search) | Q(descripcion__icontains=search))
```
**SQL:** `WHERE (titulo LIKE '%?%' OR descripcion LIKE '%?%')`

#### 2. Filtros combinados con permisos
```python
cursos.filter(Q(profesor=user) | Q(publicado=True))
```
**SQL:** `WHERE (profesor_id=? OR publicado=1)`

#### 3. JOIN optimizado
```python
Course.objects.select_related('profesor').get(id=course_id)
```
**SQL:** `SELECT * FROM curso INNER JOIN auth_persona ON curso.profesor_id = auth_persona.id WHERE curso.id=?`

---

## Estadísticas del Proyecto

| Métrica                            | Valor                                                      |
| ---------------------------------- | ---------------------------------------------------------- |
| **Total de Modelos**               | 5 (Persona, Course, Class, MembershipPlan, UserMembership) |
| **Total de Tablas en BD**          | 5 + tablas de Django (session, migrations, etc.)           |
| **Operaciones CRUD Implementadas** | 35+                                                        |
| **Endpoints API**                  | 15+                                                        |
| **Relaciones ForeignKey**          | 4                                                          |
| **Campos con Índices**             | 6                                                          |

---

## Notas Técnicas

### Seguridad
- ✅ Passwords hasheados con PBKDF2
- ✅ Autenticación basada en sesiones
- ✅ Validación de permisos por rol (ADMIN, PROFESOR, CLIENTE)
- ⚠️ CSRF deshabilitado en algunos endpoints (requiere revisión para producción)

### Rendimiento
- ✅ Uso de `select_related()` para evitar N+1 queries
- ✅ Índices en campos frecuentemente consultados
- ✅ `update_fields` para actualizaciones parciales
- ✅ Ordenamiento en nivel de BD con `order_by()`

### Escalabilidad
- ✅ Separación por módulos (Auth, Course, Class, Membership)
- ✅ Uso de `related_name` para queries inversas
- ✅ Campos JSON para datos flexibles (features en MembershipPlan)
- ✅ Soft deletes mediante status (en UserMembership)

