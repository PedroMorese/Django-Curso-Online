# 📚 Documentación del Proyecto - Plataforma de Educación Online

Bienvenido a la documentación técnica de la plataforma de cursos online con sistema de membresía.

## 🗂️ Índice de Documentación

### 📐 Arquitectura y Diseño

1. **[Propuesta de Arquitectura](ARCHITECTURE_PROPOSAL.md)**
   - Estructura de carpetas completa
   - Modelo de datos y esquema de base de datos
   - Especificaciones UI/UX y Design System
   - Flujos de navegación por rol

2. **[Arquitectura Original](ARCHITECTURE.md)**
   - Visión general del sistema MVT
   - Entidades principales y relaciones
   - Lineamientos de diseño UI/UX
   - Reglas de negocio críticas

3. **[Especificaciones Técnicas](TECHNICAL_SPECS.md)**
   - Detalles técnicos de implementación
   - Configuraciones del proyecto

4. **[Blueprint Técnico](TECHNICAL_BLUEPRINT.md)**
   - Definición de modelos Django
   - Implementación de servicios
   - Guía de estructura frontend

### 🔄 Flujos y Funcionalidades

5. **[Mapeo Frontend-Backend](FE_BE_MAPPING.md)**
   - Relación entre funcionalidades, tablas DB y componentes UI
   - Especificación de componentes reutilizables
   - Responsabilidades de cada capa

6. **[Flujos de Usuario](USER_FLOWS.md)**
   - Mapa de navegación por rol (Cliente, Profesor, Admin)
   - Flujo de activación de membresía
   - Jerarquía visual de componentes

7. **[Escalabilidad](FLOWS_AND_SCALABILITY.md)**
   - Flujos de navegación detallados
   - Estrategias de escalabilidad backend y frontend
   - Preparación para migración de base de datos

### 🔧 Backend - Módulos Específicos

8. **[Course API - Documentación](Back-end/Course/API_DOCUMENTATION.md)**
   - Endpoints disponibles
   - Ejemplos de uso
   - Códigos de respuesta

9. **[Course - README](Back-end/Course/README.md)**
   - Descripción del módulo de cursos
   - Estructura de archivos
   - Modelos y vistas

10. **[Course - Guía de Testing](Back-end/Course/TESTING_GUIDE.md)**
    - Casos de prueba
    - Comandos para ejecutar tests
    - Validaciones de seguridad

### 👥 Usuarios de Prueba

11. **[Usuarios de Prueba](TEST_USERS.md)**
    - Credenciales para testing
    - Usuarios por rol (Cliente, Profesor, Admin)
    - Instrucciones de uso

---

## 🚀 Inicio Rápido

### Requisitos Previos
- Python 3.8+
- Django 4.x
- SQLite3 (incluido con Python)

### Instalación

```bash
# 1. Clonar el repositorio
git clone <repository-url>
cd Proyecto_db

# 2. Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Ejecutar migraciones
python manage.py migrate

# 5. Crear usuarios de prueba (opcional)
python create_test_users.py

# 6. Iniciar servidor de desarrollo
python manage.py runserver
```

### Acceso a la Plataforma

- **Home/Landing**: http://localhost:8000/
- **Catálogo de Cursos**: http://localhost:8000/courses/
- **Planes de Membresía**: http://localhost:8000/membership/plans/
- **Dashboard Profesor**: http://localhost:8000/dashboard/profesor/
- **Dashboard Admin**: http://localhost:8000/dashboard/admin/
- **Documentación**: http://localhost:8000/documentation/

---

## 🏗️ Estructura del Proyecto

```
Proyecto_db/
├── manage.py
├── djangocrud/              # Configuración global Django
├── Back-end/                # Lógica de negocio
│   ├── Auth/                # Autenticación y usuarios
│   ├── Course/              # Gestión de cursos
│   ├── Class/               # Gestión de clases
│   ├── Media/               # Subida de archivos
│   └── Membership/          # Sistema de membresías
├── Front-end/               # Capa de presentación
│   ├── home/                # Landing y catálogo público
│   ├── Dashboard-Profesor/  # Panel de profesor
│   ├── Dashboard-Admin/     # Panel de administrador
│   └── Profile/             # Gestión de perfil
├── Resources/               # Recursos estáticos
├── db.sqlite3               # Base de datos
└── requirements.txt         # Dependencias
```

---

## 👤 Roles y Permisos

### Cliente (Estudiante)
- ✅ Ver catálogo de cursos
- ✅ Acceder a cursos (con membresía activa)
- ✅ Gestionar perfil personal
- ❌ No ve información de pagos ni progreso

### Profesor
- ✅ Crear, editar y eliminar cursos propios
- ✅ Gestionar clases de sus cursos
- ✅ Publicar/despublicar cursos
- ❌ No ve información de alumnos ni pagos

### Administrador
- ✅ Acceso total al sistema
- ✅ Gestión de usuarios y roles
- ✅ Visualización de pagos y membresías
- ✅ Moderación de contenido
- ✅ Reportes y estadísticas

---

## 🎨 Tecnologías Utilizadas

### Backend
- **Django 4.x**: Framework web principal
- **SQLite3**: Base de datos (migrable a PostgreSQL)
- **Python 3.8+**: Lenguaje de programación

### Frontend
- **HTML5**: Estructura
- **Vanilla CSS + Tailwind CSS**: Estilos
- **JavaScript (Vanilla)**: Interactividad
- **Django Templates**: Motor de plantillas

### Diseño
- **Google Fonts (Inter/Roboto)**: Tipografía
- **Material Symbols**: Iconografía
- **Paleta de colores**: Modo oscuro refinado con acentos en azul índigo

---

## 📝 Reglas de Negocio

1. **Membresía Obligatoria**: Solo usuarios con membresía activa pueden acceder a cursos
2. **Rol Único**: Un usuario solo puede tener un rol (Cliente, Profesor o Admin)
3. **Membresía Única**: No se permiten múltiples membresías activas simultáneas
4. **Separación de Datos**: Los profesores no tienen acceso a información de pagos

---

## 🤝 Contribución

Para contribuir al proyecto:

1. Lee la documentación de arquitectura
2. Revisa las guías de testing
3. Sigue las convenciones de código establecidas
4. Documenta cualquier cambio significativo

---

## 📞 Soporte

Para preguntas o problemas:
- Revisa la documentación técnica
- Consulta los archivos README específicos de cada módulo
- Verifica los usuarios de prueba disponibles

---

**Última actualización**: Febrero 2026
**Versión**: 1.0.0
