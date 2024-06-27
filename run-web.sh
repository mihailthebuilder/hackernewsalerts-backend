#!/bin/sh
 
python manage.py collectstatic --no-input
python manage.py migrate
gunicorn socialalerts.wsgi:application --bind=0.0.0.0:8000