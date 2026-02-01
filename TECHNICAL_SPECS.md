# Especificaciones Técnicas Detalladas - EduPlatform

## 1. Stack Tecnológico Seleccionado
- **Framework**: Django 5.x+
- **Base de Datos**: SQLite3 (Desarrollo), PostgreSQL (Producción)
- **Frontend**: Django Templates + Tailwind CSS (vía CDN o compilado)
- **Gestión de Sesiones**: Autenticación basada en sesiones de Django (SessionAuthentication)
- **Control de Acceso**: Custom Middleware + Mixins de Django

## 2. Definición de Modelos (Schema)

### 2.1 Dominio de Suscripción (membership/models.py)
```python
class MembershipPlan(models.Model):
    name = models.CharField(max_length=50) # 'Mensual', 'Anual'
    slug = models.SlugField(unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_days = models.IntegerField() # 30, 365

class UserMembership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plan = models.ForeignKey(MembershipPlan, on_delete=models.PROTECT)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
```

### 2.2 Dominio de Contenido (course/models.py)
```python
class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    thumbnail = models.ImageField(upload_to='courses/')
    professor = models.ForeignKey(User, limit_choices_to={'role': 'PROFESOR'})

class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    video_url = models.URLField()
    resources = models.FileField(upload_to='resources/', blank=True)
```

## 3. Capa de Servicios (Business Logic)
Para evitar "Fat Views", la lógica compleja se moverá a `services.py`:

- `membership_services.py`:
    - `activate_membership(user, plan_id)`: Procesa el pago y establece fechas de expiración.
    - `check_access(user)`: Middleware utiliza esto para bloquear contenido.

- `course_services.py`:
    - `reorder_lessons(course_id, lesson_order_list)`: Lógica para que el profesor organice su curso.

## 4. Control de Acceso por Rol (RBAC)
Se implementará un decorator personalizado `@role_required`:

```python
def role_required(allowed_roles):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if request.user.role in allowed_roles:
                return view_func(request, *args, **kwargs)
            return redirect('no_access')
        return _wrapped_view
    return decorator
```

## 5. Requerimientos de UI para "Premium Feel"
- **Micro-interacciones**: Transiciones suaves al abrir cursos (use CSS `transition` o Framer Motion si es SPA).
- **Video Player Re-utilizable**: Componente `VideoPlayer` que soporte bookmarks y guardado de progreso (vía AJAX).
- **Empty States**: Diseñar vistas específicas para cuando el alumno no tiene membresía activa, incitando al upgrade con copys persuasivos.

## 6. Configuración de Entorno (requirements.txt sugerido)
```text
Django>=5.0.0
Pillow>=10.0.0  # Para manejo de imágenes
django-environ  # Variables de entorno
python-dotenv
```
