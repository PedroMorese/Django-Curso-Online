"""
Vistas para el módulo de Documentación.

Renderiza archivos Markdown como HTML navegable.
"""

import os
import markdown
from django.shortcuts import render, redirect
from django.http import Http404
from django.conf import settings


# ── Lista central de documentos disponibles ───────────────────────────────────
DOCS = [
    {'name': 'README Principal',          'slug': 'readme',               'file': 'README.md'},
    {'name': 'Arquitectura',              'slug': 'architecture',         'file': 'ARCHITECTURE.md'},
    {'name': 'Propuesta Arquitectura',    'slug': 'architecture-proposal','file': 'ARCHITECTURE_PROPOSAL.md'},
    {'name': 'Especificaciones Técnicas', 'slug': 'technical-specs',      'file': 'TECHNICAL_SPECS.md'},
    {'name': 'Blueprint Técnico',         'slug': 'technical-blueprint',  'file': 'TECHNICAL_BLUEPRINT.md'},
    {'name': 'Mapeo Frontend-Backend',    'slug': 'fe-be-mapping',        'file': 'FE_BE_MAPPING.md'},
    {'name': 'Flujos de Usuario',         'slug': 'user-flows',           'file': 'USER_FLOWS.md'},
    {'name': 'Escalabilidad y Flujos',    'slug': 'scalability',          'file': 'FLOWS_AND_SCALABILITY.md'},
    {'name': 'Instrucciones de Acceso',   'slug': 'instrucciones',        'file': 'INSTRUCCIONES_VISUALIZACION.md'},
    {'name': 'ORM — Consultas DB',        'slug': 'orm-docs',             'file': 'orm_database_operations.md'},
    {'name': 'Usuarios de Prueba',        'slug': 'test-users',           'file': 'TEST_USERS.md'},
    # Backend — Course
    {'name': 'Course API',                'slug': 'course-api',           'file': 'Back-end/Course/API_DOCUMENTATION.md'},
    {'name': 'Course README',             'slug': 'course-readme',        'file': 'Back-end/Course/README.md'},
    {'name': 'Course Testing',            'slug': 'course-testing',       'file': 'Back-end/Course/TESTING_GUIDE.md'},
    # Backend — Membership
    {'name': 'Membership API Settings',   'slug': 'membership-api',       'file': 'Back-end/membership/API_MEMBERSHIP_SETTINGS.md'},
]

# ── Índices de búsqueda rápida ─────────────────────────────────────────────────
SLUG_TO_FILE = {d['slug']: d['file'] for d in DOCS}
FILE_TO_SLUG = {d['file']: d['slug'] for d in DOCS}
# Normaliza separadores en las claves (backslash → forward slash)
FILE_TO_SLUG_NORM = {k.replace('\\', '/'): v for k, v in FILE_TO_SLUG.items()}
# Por nombre de archivo solo (sin ruta)
FILENAME_TO_SLUG = {}
for d in DOCS:
    fname = os.path.basename(d['file'])
    # Si hay conflicto de nombre, el primero gana
    if fname not in FILENAME_TO_SLUG:
        FILENAME_TO_SLUG[fname] = d['slug']


def _normalize_doc_slug(raw_slug):
    """
    Normaliza el slug recibido tolerando múltiples formatos:

      'readme'                                      → 'readme'
      'ARCHITECTURE.md'                             → 'architecture'
      'readme/ARCHITECTURE.md'                      → 'architecture'
      'Back-end/membership/API_MEMBERSHIP_SETTINGS.md' → 'membership-api'
      'readme/Back-end/membership/API_...'          → 'membership-api'

    Retorna el slug limpio o None si no hay coincidencia.
    """
    # 1. Coincidencia directa (slug limpio como 'readme')
    if raw_slug in SLUG_TO_FILE:
        return raw_slug

    # 2. Normalizar separadores
    normalized = raw_slug.replace('\\', '/')

    # 3. Si contiene .md, intentar varias estrategias
    if '.md' in normalized:
        # 3a. Ruta completa (ej: 'Back-end/membership/API_MEMBERSHIP_SETTINGS.md')
        if normalized in FILE_TO_SLUG_NORM:
            return FILE_TO_SLUG_NORM[normalized]

        # 3b. Puede venir prefijado con el slug de la página anterior
        #     ej: 'readme/Back-end/membership/API_MEMBERSHIP_SETTINGS.md'
        #     Buscamos desde la derecha el primer segmento que exista como ruta
        parts = normalized.split('/')
        for start in range(len(parts)):
            candidate = '/'.join(parts[start:])
            if candidate in FILE_TO_SLUG_NORM:
                return FILE_TO_SLUG_NORM[candidate]

        # 3c. Solo por nombre de archivo (última parte)
        filename = parts[-1]
        if filename in FILENAME_TO_SLUG:
            return FILENAME_TO_SLUG[filename]

    return None


def _render_markdown(content):
    """Convierte Markdown a HTML con extensiones."""
    return markdown.markdown(
        content,
        extensions=[
            'markdown.extensions.fenced_code',
            'markdown.extensions.tables',
            'markdown.extensions.toc',
            'markdown.extensions.nl2br',
            'markdown.extensions.sane_lists',
            'markdown.extensions.codehilite',
        ],
        extension_configs={
            'markdown.extensions.codehilite': {
                'css_class': 'highlight',
                'linenums': False,
            }
        }
    )


def _make_context(content_html, current_slug, page_title):
    return {
        'content': content_html,
        'docs': DOCS,
        'current_doc': current_slug,
        'page_title': page_title,
    }


def documentation_index(request):
    """Vista principal: muestra el README.md."""
    readme_path = os.path.join(settings.BASE_DIR, 'README.md')
    try:
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        content = "# Documentación\n\nEl archivo README.md no se encuentra."

    context = _make_context(_render_markdown(content), 'readme', 'README Principal')
    return render(request, 'documentation/index.html', context)


def documentation_view(request, doc_slug):
    """
    Vista para documentos específicos.
    Acepta slugs limpios, nombres de archivo y rutas relativas
    (gracias a <path:doc_slug> en urls.py que captura barras).
    """
    clean_slug = _normalize_doc_slug(doc_slug)

    if clean_slug is None:
        raise Http404(
            f"Documento '{doc_slug}' no encontrado en el sistema de documentación."
        )

    # Si el slug llegó "sucio", redirigir a la URL canónica limpia
    if clean_slug != doc_slug:
        from django.urls import reverse
        return redirect(reverse('documentation:view', kwargs={'doc_slug': clean_slug}))

    file_relative = SLUG_TO_FILE[clean_slug]
    file_path = os.path.join(settings.BASE_DIR, file_relative)

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        raise Http404(f"Archivo '{file_relative}' no encontrado en el servidor.")

    doc_name = next((d['name'] for d in DOCS if d['slug'] == clean_slug), 'Documento')
    context = _make_context(_render_markdown(content), clean_slug, doc_name)
    return render(request, 'documentation/index.html', context)
