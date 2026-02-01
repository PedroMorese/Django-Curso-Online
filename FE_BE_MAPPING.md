# Mapeo de Funcionalidades (Backend vs Frontend)

Esta guía detalla la relación técnica entre la lógica de negocio (Backend) y los elementos visuales (Frontend).

| Feature (Funcionalidad) | Tabla DB (Backend)        | Componente UI (Frontend)            | Responsabilidad                                |
| :---------------------- | :------------------------ | :---------------------------------- | :--------------------------------------------- |
| **Autenticación**       | `Persona`                 | `LoginForm`, `RegisterForm`         | Gestión de sesiones y roles.                   |
| **Control de Acceso**   | `Persona_membresia_pago`  | `RoleGuard`, `MembershipBanner`     | Redirección basada en permisos y vigencia.     |
| **Gestión Membresía**   | `Membresia`               | `SubscriptionGrid`, `PlanCard`      | Mostrar ofertas de suscripción.                |
| **Mis Cursos**          | `Curso`, `Membresia`      | `CourseGrid`, `CourseCard`          | Listado de cursos disponibles para el miembro. |
| **Progreso de Clase**   | `Clases`                  | `VideoPlayer`, `ProgressBar`        | Visualización de contenido y tracking básico.  |
| **Recursos de Clase**   | `Clases`                  | `ResourceList`, `DownloadLink`      | Listado de links y PDFs adjuntos.              |
| **Panel Profesor**      | `Curso`                   | `ProfessorDashboard`, `CourseTable` | CRUD de cursos del autor logueado.             |
| **Editor de Clases**    | `Clases`, `Cursos_clases` | `ClassForm`, `SortableList`         | Añadir, editar y ordenar clases en un curso.   |
| **Auditoría Admin**     | `Pago`, `Persona`         | `AdminPaymentTable`, `UserTable`    | Reportes financieros y gestión de cuentas.     |
| **Estadísticas Admin**  | `Persona`, `Pago`         | `AdminStatsCards`                   | Visualización de KPIs globales.                |

## Especificación de Componentes UI Reutilizables

### 1. `MembershipStatusCard` (Dashboard Cliente)
*   **Datos**: `fecha_expiracion`, `tipo_membresia`.
*   **UX**: Color verde si está activa, naranja si expira pronto, rojo si venció.
*   **Acción**: Botón "Renovar" vinculado a pasarela.

### 2. `CourseEditor` (Dashboard Profesor)
*   **Campos**: Título (Input), Descripción (Textarea), Imagen (File), Estado (Select).
*   **Lógica**: Guardado asíncrono o vía formulario estándar Django.

### 3. `AdminUserTable` (Dashboard Admin)
*   **Columnas**: Usuario, Email, Rol, Estado Membresía, Acciones (Editar/Banear).
*   **Filtros**: Por Rol o por estado de suscripción.

### 4. `VideoPlayer` (Viewer)
*   **Integración**: Vimeo/YouTube API o local media storage.
*   **Sidebar**: Listado de todas las clases del curso actual resaltando la actual.
