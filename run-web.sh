python manage.py collectstatic

python manage.py migrate

gunicorn socialalerts.wsgi:application
