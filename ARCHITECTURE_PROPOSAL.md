# Arquitectura de Software y Especificaciones UI/UX
## Proyecto: Plataforma de Educación Online con Membresía

Este documento define la base técnica y visual para la construcción de una plataforma de cursos online escalable, utilizando **Django** como núcleo, con una separación clara de responsabilidades y un enfoque moderno en la experiencia del usuario.

---

## 1. Arquitectura del Sistema (Estructura de Carpetas)
Se propone una estructura que desacopla la lógica de negocio de la presentación, facilitando el mantenimiento y la escalabilidad futura.

```text
mi_proyecto/
├── manage.py
├── mi_proyecto/            # Configuración global (Settings, WSGI, ASGI)
├── backend/                # LÓGICA DE NEGOCIO Y DATOS
│   ├── models/             # Definiciones de modelos (Persona, Curso, etc.)
│   ├── views/              # Controladores y Endpoints (API/Views)
│   ├── services/           # Lógica compleja (Pagos, Membresías, Inscripciones)
│   ├── migrations/         # Historial de base de datos
│   └── urls.py             # Enrutamiento interno de la lógica
├── frontend/               # CAPA DE PRESENTACIÓN (TEMPLATES)
│   ├── static/             # Activos estáticos
│   │   ├── css/            # Estilos (Independientes por módulo)
│   │   ├── js/             # Lógica de cliente (Interacciones, Validaciones)
│   │   └── img/            # Assets visuales
│   ├── templates/          # Estructura de vistas por ROL
│   │   ├── client/         # Dashboard Estudiante y Reproductor
│   │   ├── professor/      # Dashboard y CRUD de Cursos
│   │   ├── admin/          # Gestión de Usuarios y Pagos
│   │   └── base/           # Layouts base compartidos
│   └── components/         # Fragmentos de UI reutilizables (Partials)
├── db.sqlite3              # Persistencia de datos (SQLite3)
└── requirements.txt        # Dependencias
```

---

## 2. Modelo de Datos (Esquema de Base de Datos)
La base de datos se basa en una estructura de usuarios con roles y un sistema de suscripción centralizado.

### Tablas Principales:
*   **Persona**: Extensión de `AbstractUser`. Campos: `rol` (Cliente, Profesor, Admin), `avatar`, `bio`.
*   **Membresia**: Catálogo de planes. Campos: `nombre` (Mensual/Anual), `precio`, `duracion_dias`.
*   **Pago**: Registro histórico de transacciones. Campos: `monto`, `fecha`, `metodo`, `estado`.
*   **Persona_membresia_pago**: Vinculación de usuario con membresía activa y su último pago.
*   **Curso**: Cabecera del curso. Campos: `titulo`, `descripcion`, `imagen`, `profesor_id`.
*   **Clases**: Unidades de video/contenido. Campos: `titulo`, `orden`, `video_url`, `pdf_recursos`.
*   **Cursos_clases**: Tabla relacional (o Relación directa) que define la estructura del curso.

---

## 3. Especificaciones de UI/UX (Design System)
Inspirado en plataformas líderes como Coursera y Platzi, buscando profesionalismo y claridad.

### Paleta de Colores y Tipografía
*   **Primario (Brand)**: `#2563EB` (Indigo Moderno) para CTAs y navegación.
*   **Fondo**: `#F9FAFB` (Gris Ultra-Light) para descanso visual.
*   **Texto**: `#111827` (Gris casi negro) para máxima legibilidad.
*   **Tipografía**: **Inter** o **Roboto** (Google Fonts).

### Componentes UI Reutilizables
*   **LoginForm**: Limpio con validación en tiempo real.
*   **MembershipStatusCard**: Muestra vigencia de suscripción en el dashboard del cliente.
*   **CourseCard**: Grid de cursos con título, miniatura y autor.
*   **VideoPlayer**: Reproductor minimalista con índice lateral.
*   **AdminStatsCards**: Indicadores clave (Ingresos, Usuarios activos).

---

## 4. Flujo de Navegación por Rol

### A. Cliente (Estudiante)
`Home` → `Login` → `Dashboard (Ver Estado Membresía)` → `Catálogo de Cursos` → `Detalle/Reproductor de Clase`.
*   *Nota*: Si la membresía está inactiva, el reproductor debe estar bloqueado por un guard de acceso.

### B. Profesor
`Login` → `Dashboard (Mis Cursos)` → `Crear Nuevo Curso` → `Editor de Clases` → `Subida de Recursos`.
*   *Nota*: El profesor tiene prohibido ver métricas de pago o acceso a datos de otros profesores.

### C. Administrador
`Login` → `Panel de Administración` → `Gestión de Usuarios (Roles)` → `Auditoría de Pagos` → `Mantenimiento de Cursos`.

---

## 5. Reglas de Negocio y Seguridad
1.  **Membresía Obligatoria**: Middleware personalizado que intercepta peticiones a `/cursos/` y verifica vigencia en `Persona_membresia_pago`.
2.  **Exclusividad de Rol**: Un `Usuario` pertenece a un solo grupo de Django que mapea a su `rol`.
3.  **Integridad de Pagos**: Los pagos solo pueden ser creados por procesos de sistema de pago, no editables manualmente por el usuario.
4.  **Aislamiento de Profesor**: Solo puede realizar CRUD sobre cursos donde su `ID` coincida con `profesor_id`.
