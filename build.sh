#!/usr/bin/env bash
# Exit on error
set -o errexit

# Instalar dependencias
pip install -r requirements.txt

# Crear directorio staticfiles si no existe
mkdir -p staticfiles

# Convertir archivos estáticos
python manage.py collectstatic --no-input

# Aplicar migraciones pendientes
python manage.py migrate