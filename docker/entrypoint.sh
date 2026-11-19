#!/bin/sh

set -eu

echo "Application des migrations..."
python manage.py migrate --noinput

echo "Demarrage de Gunicorn..."

exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers "${GUNICORN_WORKERS:-2}" \
    --timeout 60 \
    --access-logfile - \
    --error-logfile - \
    --capture-output
