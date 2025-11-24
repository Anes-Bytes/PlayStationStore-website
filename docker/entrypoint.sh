#!/bin/sh

python manage.py migrate
python manage.py collectstatic --noinput

# Start Django + Gunicorn
gunicorn config.wsgi:application --bind 0.0.0.0:8000 &
gunicorn_pid=$!

# Start Telegram Bot
python manage.py runbot &

wait $gunicorn_pid
