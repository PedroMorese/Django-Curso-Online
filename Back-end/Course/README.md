# ✅ Módulo Course — Implementación Completa

## 📋 Resumen

Módulo de **Cursos y Certificados** de la plataforma de educación online. Contiene los modelos `Course` y `Certificate`, las APIs CRUD y toda la lógica relacionada con el contenido de cursos.

---

## 🎯 Archivos Creados/Modificados

### ✨ Nuevos Archivos Creados

1. **`Back-end/Course/models.py`**
   - Modelo `Course` con todos los campos necesarios
   - Relación con el modelo de Usuario (profesor)
   - Métodos helper: `publicar()`, `despublicar()`, `total_clases`
   - Índices para optimización de consultas

2. **`Back-end/Course/views.py`**
   - `course_list()` - GET (listar) y POST (crear)
   - `course_detail()` - GET (detalle), PUT (actualizar), DELETE (eliminar)
   - `course_publish()` - POST (publicar/despublicar)
   - `my_courses()` - GET (cursos del profesor autenticado)
   - Control de acceso basado en roles (RBAC)

3. **`Back-end/Course/urls.py`**
   - Rutas para todos los endpoints del CRUD
   - Prefijo: `/api/courses/`

4. **`Back-end/Course/apps.py`**
   - Configuración de la aplicación Django

5. **`Back-end/Course/__init__.py`**
   - Paquete Python

6. **`Back-end/Course/API_DOCUMENTATION.md`**
   - Documentación completa de la API
   - Ejemplos de request/response
   - Códigos de error
   - Ejemplos con JavaScript fetch

7. **`Back-end/Course/TESTING_GUIDE.md`**
   - Guía paso a paso para probar el CRUD
   - Ejemplos con consola del navegador
   - Comandos cURL
   - Verificación en base de datos

8. **`Back-end/__init__.py`**
   - Paquete Python para Back-end

### 🔧 Archivos Modificados

1. **`djangocrud/settings.py`**
   - Agregado `'Back-end.Course'` a `INSTALLED_APPS`

2. **`djangocrud/urls.py`**
   - Agregado `path('api/courses/', include('Back-end.Course.urls'))`

3. **`Front-end/home/Membership/urls.py`**
   - Corregido import de `.view` a `.views`

### 📦 Migraciones

- ✅ Migración `0001_initial.py` creada
- ✅ Migración aplicada a la base de datos
- ✅ Tabla `curso` creada en SQLite3

---

## 🗄️ Modelos

### `Course`
```python
class Course(models.Model):  # db_table='curso', app_label='course_app'
    # Campos principales
    titulo                  # CharField(255)
    descripcion             # TextField (opcional)
    imagen_portada          # URLField (opcional)
    pdf_adjuntos            # TextField — JSON con lista de URLs de PDFs
    
    # Relaciones
    profesor                # ForeignKey → Persona (cursos_creados)
    
    # Metadata
    fecha_creacion          # DateTimeField (default: timezone.now)
    fecha_actualizacion     # DateTimeField (auto_now=True)
    publicado               # BooleanField (default: False)
    nivel                   # CharField: PRINCIPIANTE | INTERMEDIO | AVANZADO
    duracion_estimada       # IntegerField (minutos, opcional)
    
    # Propiedades: total_clases, esta_publicado
    # Métodos: publicar(), despublicar()
```

### `Certificate` _(añadido)_
```python
class Certificate(models.Model):  # db_table='certificado', app_label='course_app'
    usuario                 # ForeignKey → Persona (certificados)
    curso                   # ForeignKey → Course (certificados)
    fecha_emision           # DateTimeField (default: timezone.now)
    codigo_verificacion     # UUIDField (unique, auto-generado, inmutable)
    
    # unique_together = ('usuario', 'curso')  → 1 certificado por (usuario, curso)
    # Propiedad: codigo_display (UUID en mayúsculas)
```

---

## 🌐 Endpoints Disponibles

| Método | Endpoint                     | Descripción          | Autenticación | Roles           |
| ------ | ---------------------------- | -------------------- | ------------- | --------------- |
| GET    | `/api/courses/`              | Listar cursos        | ❌             | Todos           |
| POST   | `/api/courses/`              | Crear curso          | ✅             | PROFESOR, ADMIN |
| GET    | `/api/courses/{id}/`         | Detalle de curso     | ❌             | Todos*          |
| PUT    | `/api/courses/{id}/`         | Actualizar curso     | ✅             | Dueño, ADMIN    |
| DELETE | `/api/courses/{id}/`         | Eliminar curso       | ✅             | Dueño, ADMIN    |
| POST   | `/api/courses/{id}/publish/` | Publicar/despublicar | ✅             | Dueño, ADMIN    |
| GET    | `/api/courses/my-courses/`   | Mis cursos           | ✅             | PROFESOR, ADMIN |

\* Cursos no publicados solo visibles para dueño y ADMIN

---

## 🔐 Control de Acceso Implementado

### Por Rol

- **CLIENTE**: Solo ve cursos publicados
- **PROFESOR**: Ve sus cursos + cursos publicados
- **ADMIN**: Ve todos los cursos

### Por Propiedad

- Solo el **dueño** del curso o **ADMIN** pueden:
  - Editar el curso
  - Eliminar el curso
  - Publicar/despublicar el curso

---

## 🎨 Características Implementadas

### ✅ Funcionalidades CRUD de Cursos

- [x] **Create** — Crear nuevos cursos (solo PROFESOR/ADMIN)
- [x] **Read** — Listar y ver detalles de cursos
- [x] **Update** — Actualizar información de cursos
- [x] **Delete** — Eliminar cursos

### ✅ Funcionalidades Adicionales

- [x] Filtrado por estado de publicación
- [x] Filtrado por nivel (PRINCIPIANTE/INTERMEDIO/AVANZADO)
- [x] Búsqueda por título y descripción
- [x] Filtrado por profesor
- [x] Endpoint para obtener cursos del profesor autenticado
- [x] Endpoint para publicar/despublicar cursos
- [x] Control de acceso basado en roles (RBAC)
- [x] Validación de permisos por propiedad
- [x] Manejo de errores completo
- [x] Campo `pdf_adjuntos` — PDFs adjuntos al curso en JSON

### ✅ Sistema de Certificados

- [x] Modelo `Certificate` con UUID único por (usuario, curso)
- [x] Certificado emitido al completar la última clase (`is_last_class=True`)
- [x] Idempotente: `get_or_create()` evita duplicados
- [x] Vista frontend: `course_certificate()` + template `certificado.html`
- [x] Galería: `my_certificates()` + template `mis_certificados.html`
- [x] Requiere membresía activa para generar certificado

### ✅ Optimizaciones

- [x] Índices en base de datos para consultas rápidas
- [x] `select_related()` para optimizar queries con relaciones
- [x] Ordenamiento por fecha de creación

---

## 📚 Ejemplo de Uso Rápido

### 1. Crear un Curso

```javascript
fetch('/api/courses/', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    titulo: 'Python para Principiantes',
    descripcion: 'Aprende Python desde cero',
    nivel: 'PRINCIPIANTE',
    duracion_estimada: 180
  }),
  credentials: 'same-origin'
})
.then(res => res.json())
.then(data => console.log('Curso creado:', data));
```

### 2. Listar Cursos Publicados

```javascript
fetch('/api/courses/?publicado=true')
  .then(res => res.json())
  .then(data => console.log('Cursos:', data.cursos));
```

### 3. Actualizar un Curso

```javascript
fetch('/api/courses/1/', {
  method: 'PUT',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    titulo: 'Python para Principiantes - Edición 2026',
    publicado: true
  }),
  credentials: 'same-origin'
})
.then(res => res.json())
.then(data => console.log('Curso actualizado:', data));
```

### 4. Eliminar un Curso

```javascript
fetch('/api/courses/1/', {
  method: 'DELETE',
  credentials: 'same-origin'
})
.then(res => res.json())
.then(data => console.log(data.detail));
```

---

## 🧪 Cómo Probar

### Opción 1: Consola del Navegador

1. Abre `http://localhost:8000` en tu navegador
2. Abre la consola (F12)
3. Ejecuta los ejemplos de JavaScript anteriores

### Opción 2: Django Shell

```bash
python manage.py shell
```

```python
from Back-end.Course.models import Course
from django.contrib.auth import get_user_model

User = get_user_model()

# Crear un profesor
profesor = User.objects.first()  # o crear uno nuevo

# Crear un curso
curso = Course.objects.create(
    titulo='Mi Primer Curso',
    descripcion='Descripción del curso',
    profesor=profesor,
    nivel='PRINCIPIANTE',
    publicado=True
)

print(f"Curso creado: {curso.titulo}")

# Listar todos los cursos
cursos = Course.objects.all()
for c in cursos:
    print(f"- {c.titulo} (Publicado: {c.publicado})")
```

### Opción 3: cURL

```bash
# Listar cursos
curl http://localhost:8000/api/courses/

# Ver detalle
curl http://localhost:8000/api/courses/1/
```

---

## 📖 Documentación Completa

- **API Documentation**: `Back-end/Course/API_DOCUMENTATION.md`
- **Testing Guide**: `Back-end/Course/TESTING_GUIDE.md`

---

## ✅ Integración con Otros Módulos

| Módulo                         | Integración                                        |
| ------------------------------ | -------------------------------------------------- |
| `class_app.Class`              | FK → Course.clases (related_name)                  |
| `course_app.Certificate`       | FK → Course.certificados (related_name)            |
| `membership.UserMembership`    | Verificado en el Course Player antes de dar acceso |
| `Auth.Persona`                 | profesor=FK para ownership control                 |
| `Dashboard-Admin.Overview`     | CRUD de cursos desde el panel admin                |
| `Dashboard-Profesor.MyCourses` | CRUD de cursos y clases desde el panel profesor    |

---

## ✨ Características Destacadas

### 🎯 Separación de Responsabilidades

- **Models**: Lógica de datos y relaciones
- **Views**: Lógica de negocio y control de acceso
- **URLs**: Enrutamiento limpio y RESTful

### 🔒 Seguridad

- Validación de permisos en cada endpoint
- Control de acceso basado en roles
- Verificación de propiedad de recursos
- Manejo seguro de errores

### 📊 Escalabilidad

- Índices en base de datos
- Queries optimizadas
- Estructura modular
- Fácil de extender

### 📝 Documentación

- Código bien comentado
- Docstrings en funciones
- Documentación de API completa
- Guía de pruebas detallada

---

## 🎉 Estado del Módulo

```
✅ CRUD de Cursos (API + Dashboard Profesor + Dashboard Admin)
✅ Modelo Certificate con UUID y unique_together
✅ Campo pdf_adjuntos (JSON de URLs)
✅ Frontend: Course Player con navegación entre clases
✅ Frontend: Certificado individual + galería de certificados
✅ Control de acceso: membresía activa requerida
✅ Migraciones aplicadas
✅ Documentación actualizada
```

---

**Última actualización**: Febrero 2026
