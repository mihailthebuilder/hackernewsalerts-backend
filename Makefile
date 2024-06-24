run:
	python manage.py runserver

run-tasks:
	python manage.py qcluster

run-local-postgres:
	docker run --name postgres -p 5432:5432 -e POSTGRES_PASSWORD=mysecretpassword -d postgres
	
makemigrations:
	python manage.py makemigrations

migrate:
	python manage.py migrate

create-superuser:
	python manage.py createsuperuser

collect-static:
	python manage.py collectstatic
	
run-prod:
	SECRET_KEY=test python manage.py runserver

docker-build:
	docker build -t social-alerts .

docker-run:
	docker run -d -p 8000:8000 social-alerts