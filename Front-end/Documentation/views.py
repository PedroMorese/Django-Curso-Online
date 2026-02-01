"""
Vistas para el módulo de Documentación.

Renderiza archivos Markdown como HTML navegable.
"""

import os
import markdown
from django.shortcuts import render
from django.http import Http404
from django.conf import settings


def documentation_index(request):
    """
    Vista principal de documentación.
    Muestra el README.md principal con índice navegable.
    """
    readme_path = os.path.join(settings.BASE_DIR, 'README.md')
    
    try:
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        content = "# Documentación no disponible\n\nEl archivo README.md no se encuentra."
    
    # Convertir Markdown a HTML con extensiones mejoradas
    html_content = markdown.markdown(
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
    
    # Lista de documentos disponibles
    docs = [
        {'name': 'README Principal', 'slug': 'readme', 'file': 'README.md'},
        {'name': 'Propuesta de Arquitectura', 'slug': 'architecture-proposal', 'file': 'ARCHITECTURE_PROPOSAL.md'},
        {'name': 'Arquitectura Original', 'slug': 'architecture', 'file': 'ARCHITECTURE.md'},
        {'name': 'Especificaciones Técnicas', 'slug': 'technical-specs', 'file': 'TECHNICAL_SPECS.md'},
        {'name': 'Blueprint Técnico', 'slug': 'technical-blueprint', 'file': 'TECHNICAL_BLUEPRINT.md'},
        {'name': 'Mapeo Frontend-Backend', 'slug': 'fe-be-mapping', 'file': 'FE_BE_MAPPING.md'},
        {'name': 'Flujos de Usuario', 'slug': 'user-flows', 'file': 'USER_FLOWS.md'},
        {'name': 'Escalabilidad', 'slug': 'scalability', 'file': 'FLOWS_AND_SCALABILITY.md'},
        {'name': 'Course API', 'slug': 'course-api', 'file': 'Back-end/Course/API_DOCUMENTATION.md'},
        {'name': 'Course README', 'slug': 'course-readme', 'file': 'Back-end/Course/README.md'},
        {'name': 'Course Testing', 'slug': 'course-testing', 'file': 'Back-end/Course/TESTING_GUIDE.md'},
        {'name': 'Usuarios de Prueba', 'slug': 'test-users', 'file': 'TEST_USERS.md'},
    ]
    
    context = {
        'content': html_content,
        'docs': docs,
        'current_doc': 'readme',
        'page_title': 'Documentación del Proyecto',
    }
    
    return render(request, 'documentation/index.html', context)


def documentation_view(request, doc_slug):
    """
    Vista para documentos específicos.
    """
    # Mapeo de slugs a archivos
    doc_map = {
        'readme': 'README.md',
        'architecture-proposal': 'ARCHITECTURE_PROPOSAL.md',
        'architecture': 'ARCHITECTURE.md',
        'technical-specs': 'TECHNICAL_SPECS.md',
        'technical-blueprint': 'TECHNICAL_BLUEPRINT.md',
        'fe-be-mapping': 'FE_BE_MAPPING.md',
        'user-flows': 'USER_FLOWS.md',
        'scalability': 'FLOWS_AND_SCALABILITY.md',
        'course-api': 'Back-end/Course/API_DOCUMENTATION.md',
        'course-readme': 'Back-end/Course/README.md',
        'course-testing': 'Back-end/Course/TESTING_GUIDE.md',
        'test-users': 'TEST_USERS.md',
    }
    
    if doc_slug not in doc_map:
        raise Http404("Documento no encontrado")
    
    file_path = os.path.join(settings.BASE_DIR, doc_map[doc_slug])
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        raise Http404("Archivo de documentación no encontrado")
    
    # Convertir Markdown a HTML con extensiones mejoradas
    html_content = markdown.markdown(
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
    
    # Lista de documentos para navegación
    docs = [
        {'name': 'README Principal', 'slug': 'readme', 'file': 'README.md'},
        {'name': 'Propuesta de Arquitectura', 'slug': 'architecture-proposal', 'file': 'ARCHITECTURE_PROPOSAL.md'},
        {'name': 'Arquitectura Original', 'slug': 'architecture', 'file': 'ARCHITECTURE.md'},
        {'name': 'Especificaciones Técnicas', 'slug': 'technical-specs', 'file': 'TECHNICAL_SPECS.md'},
        {'name': 'Blueprint Técnico', 'slug': 'technical-blueprint', 'file': 'TECHNICAL_BLUEPRINT.md'},
        {'name': 'Mapeo Frontend-Backend', 'slug': 'fe-be-mapping', 'file': 'FE_BE_MAPPING.md'},
        {'name': 'Flujos de Usuario', 'slug': 'user-flows', 'file': 'USER_FLOWS.md'},
        {'name': 'Escalabilidad', 'slug': 'scalability', 'file': 'FLOWS_AND_SCALABILITY.md'},
        {'name': 'Course API', 'slug': 'course-api', 'file': 'Back-end/Course/API_DOCUMENTATION.md'},
        {'name': 'Course README', 'slug': 'course-readme', 'file': 'Back-end/Course/README.md'},
        {'name': 'Course Testing', 'slug': 'course-testing', 'file': 'Back-end/Course/TESTING_GUIDE.md'},
        {'name': 'Usuarios de Prueba', 'slug': 'test-users', 'file': 'TEST_USERS.md'},
    ]
    
    # Obtener nombre del documento actual
    doc_name = next((d['name'] for d in docs if d['slug'] == doc_slug), 'Documento')
    
    context = {
        'content': html_content,
        'docs': docs,
        'current_doc': doc_slug,
        'page_title': doc_name,
    }
    
    return render(request, 'documentation/index.html', context)
