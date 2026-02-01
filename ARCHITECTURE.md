# Documentación de Arquitectura y Diseño UI/UX - Plataforma de Educación Online

## 1. Introducción
Este documento detalla la arquitectura de software, especificaciones técnicas y propuesta de diseño para la plataforma de cursos online con modelo de membresía. El sistema está diseñado para ser escalable, seguro y con una separación clara entre la lógica de negocio (Backend) y la presentación (Frontend).

## 2. Arquitectura de Sistema

### 2.1 Visión General
Se utiliza el framework **Django** siguiendo el patrón de arquitectura **MVT (Model-View-Template)**, pero con una organización de carpetas personalizada que separa claramente los componentes de Backend y Frontend para facilitar el mantenimiento.

### 2.2 Estructura de Carpetas Propuesta
```
mi_proyecto/
├── manage.py
├── djangocrud/             # Configuración global de Django (Settings, WSGI, URLs raíz)
├── backend/                # Lógica de negocio y base de datos
│   ├── auth/               # Gestión de usuarios, roles y permisos
│   ├── membership/         # Planes de membresía y lógica de suscripción
│   ├── course/             # Gestión de cursos y categorías
│   ├── class/              # Gestión de clases y recursos
│   ├── payments/           # Integración de pagos y pasarelas
│   └── services/           # Procesos de negocio (lógica desacoplada de vistas)
├── frontend/               # Presentación y templates
│   ├── templates/          # HTML organizado por rol
│   │   ├── base/           # Layouts base compartidos
│   │   ├── client/         # Vistas para el estudiante
│   │   ├── professor/      # Dashboard y gestión de cursos
│   │   └── admin/          # Panel de administración total
│   ├── static/             # Activos estáticos
│   │   ├── css/            # Estilos (Vanilla CSS / Tailwind)
│   │   ├── js/             # Lógica de cliente y validaciones
│   │   └── images/         # Recursos visuales
│   └── components/         # Fragmentos HTML reutilizables (partial templates)
├── db.sqlite3              # Base de datos SQLite3
└── requirements.txt        # Dependencias del proyecto
```

## 3. Modelo de Datos (Base de Datos)

### 3.1 Entidades Principales
- **Persona (Custom User)**: Extensión de `AbstractUser` para incluir el campo `rol` (Cliente, Profesor, Admin).
- **Membresia**: Define los planes (Mensual, Anual) con su precio y duración.
- **Pago**: Registro de transacciones individuales.
- **Persona_Membresia_Pago**: Tabla relacional que vincula al usuario con su membresía actual y el historial de pagos.
- **Curso**: Contenedor principal de contenido.
- **Clases**: Unidades de contenido dentro de un curso.
- **Cursos_Clases**: Relación many-to-many o foreign key para organizar el contenido.

### 3.2 Diagrama de Relaciones (Efectivo)
- Un **Usuario** tiene una **Membresía Activa** (Control de acceso).
- Un **Profesor** es dueño de N **Cursos**.
- Un **Curso** contiene N **Clases**.
- Un **Pago** activa o renueva la **Membresía**.

## 4. Flujo de Navegación por Rol

### 4.1 Cliente (Estudiante)
1. **Landing Page**: Visualización de catálogo (bloqueado para no-miembros).
2. **Registro/Login**: Creación de cuenta y selección de membresía.
3. **Dashboard Cliente**: Acceso a cursos inscritos (si tiene membresía activa).
4. **Reproductor de Clase**: Consumo de video y descarga de recursos.

### 4.2 Profesor
1. **Dashboard Profesor**: Estadísticas de sus cursos.
2. **Editor de Cursos**: Crear/Editar/Eliminar cursos.
3. **Gestor de Contenido**: Añadir videos y archivos a las clases.

### 4.3 Administrador
1. **Panel General**: Métricas de ingresos y usuarios activos.
2. **Gestión de Membresías**: Configurar precios y planes.
3. **Moderación**: Control total sobre usuarios y cursos subidos.

## 5. Especificaciones de UI/UX

### 5.1 Lineamientos de Diseño
- **Estética Moderno-Minimalista**: Inspirado en Platzi (limpieza) y Coursera (seriedad académica).
- **Esquema de Colores**:
    - Primario: Azul Profundo o Índigo (Confianza).
    - Acento: Violeta o Verde Esmeralda (Energía/Progreso).
    - Fondo: Modo Dark refinado o Blanco Off-white para evitar fatiga visual.
- **Tipografía**: Fuentes Sans-serif modernas (Inter o Roboto).

### 5.2 Componentes UI Mapeados
| Feature          | Tabla DB               | Componente UI                  |
| :--------------- | :--------------------- | :----------------------------- |
| Login/Registro   | Persona                | `LoginForm`, `RoleGuard`       |
| Estado Membresía | Persona_Membresia_Pago | `MembershipStatusCard`         |
| Catálogo         | Curso                  | `CourseGrid`, `CourseCard`     |
| Clase            | Clases                 | `VideoPlayer`, `ResourceList`  |
| Gestión Profesor | Cursos/Clases          | `CourseEditor`, `ClassForm`    |
| Admin Panel      | Todos                  | `AdminStatsCards`, `UserTable` |

## 6. Reglas de Negocio Críticas
1. **Acceso Restringido**: Middleware que verifica `user.is_authenticated` y `membership.is_active` para acceder a cualquier clase.
2. **Rol Único**: Un usuario no puede cambiar su rol una vez registrado (salvo intervención de admin).
3. **Membresía Única**: No se permiten suscripciones concurrentes; la nueva reemplaza o extiende la actual.
4. **Separación de Datos**: Los profesores no tienen acceso a la tabla `Pago`.

## 7. Propuesta de Escalabilidad
- **Backend**: Implementar **Services Pattern** para que la lógica de pagos y membresías no resida en las views, permitiendo en el futuro cambiar a APIs con Django Rest Framework fácilmente.
- **Frontend**: Uso de **Django Components** (fragmentos reutilizables) para evitar duplicación de código en dashboards.
- **Infraestructura**: Preparado para migrar de SQLite a **PostgreSQL** mediante variables de entorno.
