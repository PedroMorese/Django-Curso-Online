# Guía de Prueba del CRUD de Cursos

## ✅ Configuración Completada

- [x] Modelo `Course` creado
- [x] Vistas CRUD implementadas
- [x] URLs configuradas
- [x] Migraciones aplicadas
- [x] App registrada en INSTALLED_APPS

---

## 🚀 Cómo Probar el CRUD

### 1. Iniciar el Servidor

```bash
python manage.py runserver
```

El servidor estará disponible en: `http://localhost:8000`

---

### 2. Crear un Usuario Profesor

Primero necesitas un usuario con rol PROFESOR para crear cursos.

#### Opción A: Desde Django Shell

```bash
python manage.py shell
```

```python
from django.contrib.auth import get_user_model

User = get_user_model()

# Crear un profesor
profesor = User.objects.create_user(
    username='profesor@example.com',
    email='profesor@example.com',
    password='test123',
    first_name='Juan',
    last_name='Pérez'
)

# Si tu modelo tiene campo 'role'
if hasattr(profesor, 'role'):
    profesor.role = 'PROFESOR'
    profesor.save()

print(f"Profesor creado: {profesor.email}")
```

#### Opción B: Desde el Endpoint de Registro

```javascript
fetch('/auth/register/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    email: 'profesor@example.com',
    password: 'test123',
    first_name: 'Juan',
    last_name: 'Pérez',
    role: 'PROFESOR'
  })
})
  .then(res => res.json())
  .then(data => console.log(data));
```

---

### 3. Iniciar Sesión

```javascript
fetch('/auth/login/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    email: 'profesor@example.com',
    password: 'test123'
  }),
  credentials: 'same-origin'
})
  .then(res => res.json())
  .then(data => console.log('Login exitoso:', data));
```

---

### 4. Crear un Curso

```javascript
fetch('/api/courses/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    titulo: 'Introducción a Python',
    descripcion: 'Aprende Python desde cero con este curso completo',
    imagen_portada: 'https://picsum.photos/800/400',
    nivel: 'PRINCIPIANTE',
    duracion_estimada: 180,
    publicado: false
  }),
  credentials: 'same-origin'
})
  .then(res => res.json())
  .then(data => {
    console.log('Curso creado:', data);
    // Guarda el ID para las siguientes pruebas
    window.cursoId = data.id;
  });
```

---

### 5. Listar Todos los Cursos

```javascript
fetch('/api/courses/')
  .then(res => res.json())
  .then(data => {
    console.log('Cursos disponibles:', data.cursos);
  });
```

#### Con Filtros

```javascript
// Solo cursos publicados
fetch('/api/courses/?publicado=true')
  .then(res => res.json())
  .then(data => console.log('Cursos publicados:', data.cursos));

// Cursos de nivel intermedio
fetch('/api/courses/?nivel=INTERMEDIO')
  .then(res => res.json())
  .then(data => console.log('Cursos intermedios:', data.cursos));

// Buscar por palabra clave
fetch('/api/courses/?search=python')
  .then(res => res.json())
  .then(data => console.log('Resultados búsqueda:', data.cursos));
```

---

### 6. Obtener Detalle de un Curso

```javascript
// Usa el ID del curso creado anteriormente
const cursoId = 1; // o window.cursoId

fetch(`/api/courses/${cursoId}/`)
  .then(res => res.json())
  .then(data => {
    console.log('Detalle del curso:', data);
  });
```

---

### 7. Actualizar un Curso

```javascript
const cursoId = 1;

fetch(`/api/courses/${cursoId}/`, {
  method: 'PUT',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    titulo: 'Introducción a Python - Actualizado',
    descripcion: 'Curso completo de Python con ejercicios prácticos',
    nivel: 'INTERMEDIO',
    duracion_estimada: 240
  }),
  credentials: 'same-origin'
})
  .then(res => res.json())
  .then(data => {
    console.log('Curso actualizado:', data);
  });
```

---

### 8. Publicar un Curso

```javascript
const cursoId = 1;

fetch(`/api/courses/${cursoId}/publish/`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    publicado: true
  }),
  credentials: 'same-origin'
})
  .then(res => res.json())
  .then(data => {
    console.log('Curso publicado:', data);
  });
```

---

### 9. Obtener Mis Cursos (Solo Profesores)

```javascript
fetch('/api/courses/my-courses/', {
  credentials: 'same-origin'
})
  .then(res => res.json())
  .then(data => {
    console.log('Mis cursos:', data.cursos);
  });
```

---

### 10. Eliminar un Curso

```javascript
const cursoId = 1;

fetch(`/api/courses/${cursoId}/`, {
  method: 'DELETE',
  credentials: 'same-origin'
})
  .then(res => res.json())
  .then(data => {
    console.log('Curso eliminado:', data);
  });
```

---

## 🧪 Pruebas desde la Consola del Navegador

Abre la consola del navegador (F12) y ejecuta estos comandos:

### Prueba Completa

```javascript
// 1. Crear curso
fetch('/api/courses/', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    titulo: 'Django para Principiantes',
    descripcion: 'Aprende Django desde cero',
    nivel: 'PRINCIPIANTE',
    duracion_estimada: 200
  }),
  credentials: 'same-origin'
})
.then(res => res.json())
.then(curso => {
  console.log('✅ Curso creado:', curso);
  
  // 2. Actualizar curso
  return fetch(`/api/courses/${curso.id}/`, {
    method: 'PUT',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      titulo: 'Django para Principiantes - Edición 2026'
    }),
    credentials: 'same-origin'
  });
})
.then(res => res.json())
.then(curso => {
  console.log('✅ Curso actualizado:', curso);
  
  // 3. Publicar curso
  return fetch(`/api/courses/${curso.id}/publish/`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({publicado: true}),
    credentials: 'same-origin'
  });
})
.then(res => res.json())
.then(data => {
  console.log('✅ Curso publicado:', data);
  
  // 4. Listar cursos
  return fetch('/api/courses/');
})
.then(res => res.json())
.then(data => {
  console.log('✅ Lista de cursos:', data.cursos);
})
.catch(err => console.error('❌ Error:', err));
```

---

## 📊 Verificar en la Base de Datos

```bash
python manage.py shell
```

```python
from Back-end.Course.models import Course
from django.contrib.auth import get_user_model

User = get_user_model()

# Ver todos los cursos
cursos = Course.objects.all()
for curso in cursos:
    print(f"ID: {curso.id} | {curso.titulo} | Publicado: {curso.publicado}")

# Ver cursos de un profesor específico
profesor = User.objects.get(email='profesor@example.com')
mis_cursos = Course.objects.filter(profesor=profesor)
print(f"\nCursos de {profesor.email}: {mis_cursos.count()}")

# Ver solo cursos publicados
publicados = Course.objects.filter(publicado=True)
print(f"\nCursos publicados: {publicados.count()}")
```

---

## 🔍 Verificar Endpoints con cURL

### Listar Cursos
```bash
curl http://localhost:8000/api/courses/
```

### Crear Curso (requiere sesión)
```bash
curl -X POST http://localhost:8000/api/courses/ \
  -H "Content-Type: application/json" \
  -d '{
    "titulo": "Curso de Prueba",
    "descripcion": "Descripción del curso",
    "nivel": "PRINCIPIANTE"
  }'
```

### Obtener Detalle
```bash
curl http://localhost:8000/api/courses/1/
```

### Actualizar Curso
```bash
curl -X PUT http://localhost:8000/api/courses/1/ \
  -H "Content-Type: application/json" \
  -d '{
    "titulo": "Curso Actualizado"
  }'
```

### Eliminar Curso
```bash
curl -X DELETE http://localhost:8000/api/courses/1/
```

---

## ✨ Próximos Pasos

1. ✅ CRUD de Cursos completado
2. ⏭️ Crear CRUD de Clases
3. ⏭️ Relacionar Cursos con Clases
4. ⏭️ Crear interfaz frontend para gestión de cursos
5. ⏭️ Implementar sistema de membresías
6. ⏭️ Agregar control de acceso basado en membresía

---

## 📝 Notas Importantes

- **Autenticación**: Asegúrate de estar autenticado antes de crear/editar cursos
- **Permisos**: Solo PROFESOR y ADMIN pueden crear cursos
- **Propiedad**: Solo el dueño del curso o ADMIN pueden editarlo/eliminarlo
- **Visibilidad**: Cursos no publicados solo son visibles para el dueño y admins

---

## 🐛 Solución de Problemas

### Error 401 (Unauthorized)
- Verifica que hayas iniciado sesión
- Usa `credentials: 'same-origin'` en fetch

### Error 403 (Forbidden)
- Verifica que tu usuario tenga rol PROFESOR o ADMIN
- Verifica que seas el dueño del curso que intentas editar

### Error 404 (Not Found)
- Verifica que el ID del curso sea correcto
- Si el curso no está publicado, solo el dueño puede verlo

### No se crean cursos
- Verifica que la app esté en INSTALLED_APPS
- Verifica que las migraciones estén aplicadas
- Revisa los logs del servidor para ver errores
