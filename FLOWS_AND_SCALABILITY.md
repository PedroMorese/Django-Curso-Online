# Flujos de Usuario y Escalabilidad Técnica

## 1. Flujos de Navegación por Rol

### Flujo Estudiante (Consumidor)
1.  **Entrada**: Landing page con catálogo visible pero "cerrado" (preview).
2.  **Checkout**: El usuario selecciona membresía y paga.
3.  **Activación**: Se crea registro en `Persona_membresia_pago`.
4.  **Consumo**: Acceso a `dashboard/` -> `course/ID/` -> `class/ID/`.
5.  **Restricción**: Si intenta acceder a una clase sin membresía, se redirige a `/pricing/`.

### Flujo Profesor (Creador)
1.  **Entrada**: Login -> `/professor/dashboard/`.
2.  **Gestión**: Lista de sus cursos con indicadores básicos.
3.  **CRUD**: Botón "Nuevo Curso" -> Formulario Meta -> Botón "Agregar Clase" -> Formulario de Contenido.
4.  **Validación**: El backend asegura que el profesor solo edite sus propios registros.

### Flujo Administrador (Control)
1.  **Entrada**: Login -> `/admin-custom/dashboard/`.
2.  **Finanzas**: Vista de `Pagos` recientes.
3.  **Usuarios**: Búsqueda y gestión de `Persona`. Cambio de roles si es necesario.
4.  **Calidad**: Revisión de cursos creados.

---

## 2. Estrategia de Escalabilidad

### Backend (Django)
*   **Patrón de Servicios (Services.py)**: Toda la lógica de validación de membresía y procesamiento de pagos vivirá en `services/`, no en las `views`. Esto permite que futuros cambios (ej. añadir Stripe) no afecten las vistas.
*   **Asincronía**: Procesamiento de videos y subida de archivos pesados mediante tareas en segundo plano (Recomendado: Celery - en el futuro).
*   **Roles y Permisos**: Uso del sistema de Grupos y Permisos nativo de Django, extendido con Mixins personalizados (`MembershipRequiredMixin`).

### Frontend (Arquitectura Clean)
*   **Template Tags Personalizados**: Crear tags para verificar membresía en el template sin lógica compleja (`{% if user.has_active_membership %}`).
*   **Vanilla JS Components**: Encapsular lógica de componentes (modales, reproductores) en clases JS para evitar "jQuery spaghetti".
*   **CSS Modular**: Dividir archivos CSS por rol (`client.css`, `professor.css`, `admin.css`) para evitar carga de estilos innecesarios.

---

## 3. Preparación para SQLite3 y Migración
*   **SQLite3**: Ideal para desarrollo y MVP. Se garantiza la integridad mediante Foreign Keys estrictas.
*   **PostgreSQL Ready**: La arquitectura evita el uso de funciones específicas de SQLite, permitiendo migrar a Postgres mediante configuración en `settings.py` sin reescribir modelos.
