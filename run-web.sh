#!/bin/sh

python manage.py collectstatic --noinput

python manage.py migrate

gunicorn socialalerts.wsgi:application --bind=0.0.0.0:8000
