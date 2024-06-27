run-web:
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
	
run-prod-web:
	SECRET_KEY=test python manage.py runserver

docker-build-web:
	docker build -f ./Dockerfile-web -t social-alerts .

docker-run-web:
	docker run -d -p 8000:8000 --env-file ./.env social-alerts