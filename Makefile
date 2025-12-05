ifneq (,$(wildcard .env))
include .env
export
endif

run-web:
	python manage.py runserver

run-tasks:
	python manage.py qcluster

makemigrations:
	python manage.py makemigrations

migrate:
	python manage.py migrate

create-superuser:
	python manage.py createsuperuser

collect-static:
	python manage.py collectstatic
	
docker-build-web:
	docker build -f ./Dockerfile-web -t social-alerts .

docker-run-web:
	docker run -d -p 8000:8000 --env-file ./.env social-alerts

test:
	python manage.py test

deploy-web:
	caprover deploy -c ./captain-definition-web.json -a $(CAPROVER_APP_WEB) -n $(CAPROVER_NODE) -b $(BRANCH)

deploy-tasks:
	caprover deploy -c ./captain-definition-tasks.json -a $(CAPROVER_APP_TASKS) -n $(CAPROVER_NODE) -b $(BRANCH)