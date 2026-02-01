# API de Cursos - Documentación

## Endpoints Disponibles

### Base URL: `/api/courses/`

---

## 1. Listar Cursos

**GET** `/api/courses/`

Lista todos los cursos según el rol del usuario:
- **ADMIN**: Ve todos los cursos
- **PROFESOR**: Ve sus cursos + cursos publicados
- **CLIENTE/No autenticado**: Solo cursos publicados

### Query Parameters (opcionales)

| Parámetro     | Tipo    | Descripción                                                  |
| ------------- | ------- | ------------------------------------------------------------ |
| `publicado`   | boolean | Filtrar por estado de publicación (`true`/`false`)           |
| `nivel`       | string  | Filtrar por nivel (`PRINCIPIANTE`, `INTERMEDIO`, `AVANZADO`) |
| `search`      | string  | Buscar en título y descripción                               |
| `profesor_id` | integer | Filtrar por ID del profesor                                  |

### Ejemplo Request

```bash
# Listar todos los cursos publicados
GET /api/courses/?publicado=true

# Buscar cursos de nivel intermedio
GET /api/courses/?nivel=INTERMEDIO

# Buscar cursos por palabra clave
GET /api/courses/?search=python

# Cursos de un profesor específico
GET /api/courses/?profesor_id=5
```

### Ejemplo Response (200 OK)

```json
{
  "cursos": [
    {
      "id": 1,
      "titulo": "Introducción a Python",
      "descripcion": "Aprende Python desde cero",
      "imagen_portada": "https://example.com/python.jpg",
      "profesor": {
        "id": 2,
        "email": "profesor@example.com",
        "nombre": "Juan Pérez"
      },
      "fecha_creacion": "2026-01-15T10:30:00Z",
      "fecha_actualizacion": "2026-01-20T14:20:00Z",
      "publicado": true,
      "nivel": "PRINCIPIANTE",
      "duracion_estimada": 180,
      "total_clases": 12
    }
  ]
}
```

---

## 2. Crear Curso

**POST** `/api/courses/`

Crea un nuevo curso. **Requiere autenticación** y rol **PROFESOR** o **ADMIN**.

### Request Body

```json
{
  "titulo": "Curso de Django Avanzado",
  "descripcion": "Aprende Django a nivel profesional",
  "imagen_portada": "https://example.com/django.jpg",
  "nivel": "AVANZADO",
  "duracion_estimada": 300,
  "publicado": false
}
```

### Campos

| Campo               | Tipo         | Requerido | Descripción                                                               |
| ------------------- | ------------ | --------- | ------------------------------------------------------------------------- |
| `titulo`            | string       | ✅ Sí      | Título del curso                                                          |
| `descripcion`       | string       | ❌ No      | Descripción del curso                                                     |
| `imagen_portada`    | string (URL) | ❌ No      | URL de la imagen de portada                                               |
| `nivel`             | string       | ❌ No      | Nivel: `PRINCIPIANTE`, `INTERMEDIO`, `AVANZADO` (default: `PRINCIPIANTE`) |
| `duracion_estimada` | integer      | ❌ No      | Duración en minutos                                                       |
| `publicado`         | boolean      | ❌ No      | Estado de publicación (default: `false`)                                  |

### Ejemplo Response (201 Created)

```json
{
  "id": 5,
  "titulo": "Curso de Django Avanzado",
  "descripcion": "Aprende Django a nivel profesional",
  "imagen_portada": "https://example.com/django.jpg",
  "profesor_id": 2,
  "fecha_creacion": "2026-02-01T00:30:00Z",
  "publicado": false,
  "nivel": "AVANZADO",
  "duracion_estimada": 300
}
```

### Errores Posibles

- **401 Unauthorized**: No autenticado
- **403 Forbidden**: Usuario no es profesor ni admin
- **400 Bad Request**: Datos inválidos

---

## 3. Obtener Detalle de Curso

**GET** `/api/courses/{course_id}/`

Obtiene los detalles de un curso específico.

### Ejemplo Request

```bash
GET /api/courses/5/
```

### Ejemplo Response (200 OK)

```json
{
  "id": 5,
  "titulo": "Curso de Django Avanzado",
  "descripcion": "Aprende Django a nivel profesional",
  "imagen_portada": "https://example.com/django.jpg",
  "profesor": {
    "id": 2,
    "email": "profesor@example.com",
    "nombre": "Juan Pérez"
  },
  "fecha_creacion": "2026-02-01T00:30:00Z",
  "fecha_actualizacion": "2026-02-01T00:30:00Z",
  "publicado": false,
  "nivel": "AVANZADO",
  "duracion_estimada": 300,
  "total_clases": 0
}
```

### Errores Posibles

- **404 Not Found**: Curso no existe o no está publicado (y no eres el dueño)

---

## 4. Actualizar Curso

**PUT** `/api/courses/{course_id}/`

Actualiza un curso existente. **Requiere autenticación** y ser el **dueño del curso** o **ADMIN**.

### Request Body (todos los campos son opcionales)

```json
{
  "titulo": "Curso de Django Avanzado - Actualizado",
  "descripcion": "Nueva descripción",
  "imagen_portada": "https://example.com/new-image.jpg",
  "nivel": "INTERMEDIO",
  "duracion_estimada": 350,
  "publicado": true
}
```

### Ejemplo Response (200 OK)

```json
{
  "id": 5,
  "titulo": "Curso de Django Avanzado - Actualizado",
  "descripcion": "Nueva descripción",
  "imagen_portada": "https://example.com/new-image.jpg",
  "profesor_id": 2,
  "fecha_creacion": "2026-02-01T00:30:00Z",
  "fecha_actualizacion": "2026-02-01T01:15:00Z",
  "publicado": true,
  "nivel": "INTERMEDIO",
  "duracion_estimada": 350
}
```

### Errores Posibles

- **401 Unauthorized**: No autenticado
- **403 Forbidden**: No eres el dueño del curso
- **404 Not Found**: Curso no existe

---

## 5. Eliminar Curso

**DELETE** `/api/courses/{course_id}/`

Elimina un curso. **Requiere autenticación** y ser el **dueño del curso** o **ADMIN**.

### Ejemplo Request

```bash
DELETE /api/courses/5/
```

### Ejemplo Response (200 OK)

```json
{
  "detail": "Course deleted successfully",
  "id": 5
}
```

### Errores Posibles

- **401 Unauthorized**: No autenticado
- **403 Forbidden**: No eres el dueño del curso
- **404 Not Found**: Curso no existe

---

## 6. Publicar/Despublicar Curso

**POST** `/api/courses/{course_id}/publish/`

Cambia el estado de publicación de un curso. **Requiere autenticación** y ser el **dueño del curso** o **ADMIN**.

### Request Body

```json
{
  "publicado": true
}
```

### Ejemplo Response (200 OK)

```json
{
  "id": 5,
  "titulo": "Curso de Django Avanzado",
  "publicado": true,
  "detail": "Course published successfully"
}
```

### Errores Posibles

- **401 Unauthorized**: No autenticado
- **403 Forbidden**: No eres el dueño del curso
- **404 Not Found**: Curso no existe
- **400 Bad Request**: Campo "publicado" no proporcionado

---

## 7. Mis Cursos (Solo Profesores)

**GET** `/api/courses/my-courses/`

Obtiene todos los cursos del profesor autenticado. **Requiere autenticación** y rol **PROFESOR** o **ADMIN**.

### Ejemplo Request

```bash
GET /api/courses/my-courses/
```

### Ejemplo Response (200 OK)

```json
{
  "cursos": [
    {
      "id": 5,
      "titulo": "Curso de Django Avanzado",
      "descripcion": "Aprende Django a nivel profesional",
      "imagen_portada": "https://example.com/django.jpg",
      "fecha_creacion": "2026-02-01T00:30:00Z",
      "fecha_actualizacion": "2026-02-01T01:15:00Z",
      "publicado": true,
      "nivel": "AVANZADO",
      "duracion_estimada": 300,
      "total_clases": 8
    },
    {
      "id": 3,
      "titulo": "Python para Data Science",
      "descripcion": "Análisis de datos con Python",
      "imagen_portada": "https://example.com/datascience.jpg",
      "fecha_creacion": "2026-01-20T10:00:00Z",
      "fecha_actualizacion": "2026-01-25T14:30:00Z",
      "publicado": false,
      "nivel": "INTERMEDIO",
      "duracion_estimada": 240,
      "total_clases": 15
    }
  ]
}
```

### Errores Posibles

- **401 Unauthorized**: No autenticado
- **403 Forbidden**: Usuario no es profesor ni admin

---

## Ejemplos de Uso con JavaScript (Fetch)

### Listar Cursos Publicados

```javascript
fetch('/api/courses/?publicado=true')
  .then(response => response.json())
  .then(data => {
    console.log('Cursos:', data.cursos);
  });
```

### Crear un Curso

```javascript
fetch('/api/courses/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    titulo: 'Mi Nuevo Curso',
    descripcion: 'Descripción del curso',
    nivel: 'PRINCIPIANTE',
    publicado: false
  }),
  credentials: 'same-origin'
})
  .then(response => response.json())
  .then(data => {
    if (data.id) {
      console.log('Curso creado:', data);
    } else {
      console.error('Error:', data.detail);
    }
  });
```

### Actualizar un Curso

```javascript
fetch('/api/courses/5/', {
  method: 'PUT',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    titulo: 'Título Actualizado',
    publicado: true
  }),
  credentials: 'same-origin'
})
  .then(response => response.json())
  .then(data => console.log('Curso actualizado:', data));
```

### Eliminar un Curso

```javascript
fetch('/api/courses/5/', {
  method: 'DELETE',
  credentials: 'same-origin'
})
  .then(response => response.json())
  .then(data => console.log(data.detail));
```

### Publicar un Curso

```javascript
fetch('/api/courses/5/publish/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    publicado: true
  }),
  credentials: 'same-origin'
})
  .then(response => response.json())
  .then(data => console.log(data.detail));
```

### Obtener Mis Cursos

```javascript
fetch('/api/courses/my-courses/', {
  credentials: 'same-origin'
})
  .then(response => response.json())
  .then(data => {
    console.log('Mis cursos:', data.cursos);
  });
```

---

## Control de Acceso por Rol

| Endpoint                          | CLIENTE           | PROFESOR             | ADMIN   |
| --------------------------------- | ----------------- | -------------------- | ------- |
| GET `/api/courses/`               | ✅ Solo publicados | ✅ Suyos + publicados | ✅ Todos |
| POST `/api/courses/`              | ❌                 | ✅                    | ✅       |
| GET `/api/courses/{id}/`          | ✅ Solo publicados | ✅ Suyos + publicados | ✅ Todos |
| PUT `/api/courses/{id}/`          | ❌                 | ✅ Solo suyos         | ✅ Todos |
| DELETE `/api/courses/{id}/`       | ❌                 | ✅ Solo suyos         | ✅ Todos |
| POST `/api/courses/{id}/publish/` | ❌                 | ✅ Solo suyos         | ✅ Todos |
| GET `/api/courses/my-courses/`    | ❌                 | ✅                    | ✅       |

---

## Notas Importantes

1. **Autenticación**: Los endpoints que requieren autenticación verifican `request.user.is_authenticated`
2. **CSRF**: Actualmente los endpoints tienen `@csrf_exempt` para desarrollo. En producción, implementar CSRF tokens.
3. **Permisos**: Los profesores solo pueden editar/eliminar sus propios cursos. Los admins pueden editar/eliminar cualquier curso.
4. **Cursos no publicados**: Solo son visibles para el dueño y admins.
5. **Formato de fechas**: Todas las fechas están en formato ISO 8601 (UTC).

---

## Próximos Pasos

1. Crear migraciones: `python manage.py makemigrations`
2. Aplicar migraciones: `python manage.py migrate`
3. Crear un superusuario: `python manage.py createsuperuser`
4. Probar los endpoints con Postman o desde el frontend
