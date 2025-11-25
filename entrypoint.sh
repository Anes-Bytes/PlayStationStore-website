#!/bin/bash

echo "Applying Django migrations..."
python app/manage.py migrate

echo "Collecting static files..."
python app/manage.py collectstatic --noinput

echo "Starting Gunicorn..."
gunicorn app.wsgi:application --bind 0.0.0.0:8000 --workers 4
