# Guía de Referencia para el Desarrollo (Django Blueprint)

Este documento sirve como plano técnico para la implementación inmediata de los modelos y servicios.

## 1. Definición de Modelos (Back-end)

### Persona (Custom User)
```python
class Persona(AbstractUser):
    ROLES = (
        ('CLIENTE', 'Cliente'),
        ('PROFESOR', 'Profesor'),
        ('ADMIN', 'Administrador'),
    )
    rol = models.CharField(max_length=15, choices=ROLES)
    # Solo un rol por usuario
```

### Gestión de Membresía y Pagos
```python
class Membresia(models.Model):
    plan = models.CharField(max_length=50) # Mensual, Anual
    precio = models.DecimalField(max_digits=10, decimal_places=2)

class Pago(models.Model):
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateTimeField(auto_now_add=True)
    persona = models.ForeignKey(Persona, on_delete=models.CASCADE)

class Persona_Membresia_Pago(models.Model):
    persona = models.ForeignKey(Persona, on_delete=models.CASCADE)
    membresia = models.ForeignKey(Membresia, on_delete=models.CASCADE)
    pago = models.OneToOneField(Pago, on_delete=models.CASCADE)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    activo = models.BooleanField(default=True)
```

### Gestión de Contenido
```python
class Curso(models.Model):
    titulo = models.CharField(max_length=200)
    profesor = models.ForeignKey(Persona, limit_choices_to={'rol': 'PROFESOR'}, on_delete=models.CASCADE)

class Clases(models.Model):
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, related_name='clases')
    titulo = models.CharField(max_length=200)
    video_url = models.URLField()
    recursos = models.FileField(upload_to='resources/', null=True, blank=True)
```

## 2. Implementación de Servicios (Services)
Se recomienda crear archivos en `backend/services/` para desacoplar la lógica:
- `membership_service.py`: Funciones `check_access(user)`, `activate_membership(user, plan)`.
- `payment_service.py`: Funciones `process_payment(user, data)`, `generate_invoice(pago)`.
- `course_service.py`: Lógica para validar que un profesor solo edite sus cursos.

## 3. Guía de Front-end (Templates)
Organización por carpetas según rol para evitar colisiones de rutas y estilos:

- `frontend/templates/cliente/`: `dashboard.html`, `course_list.html`, `video_player.html`.
- `frontend/templates/profesor/`: `course_editor.html`, `class_manager.html`.
- `frontend/templates/admin/`: `user_list.html`, `revenue_report.html`.

### Componentes HTML Reutilizables:
Uso de `{% include "components/name.html" with context %}` para:
- `navbar.html`
- `sidebar_role.html`
- `footer.html`
- `course_card.html`
- `status_badge.html`
