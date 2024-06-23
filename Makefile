run:
	python manage.py runserver

run-task:
	python manage.py qcluster
	
collect-static:
	python manage.py collectstatic
	
run-prod:
	SECRET_KEY=test python manage.py runserver

docker-build:
	docker build -t social-alerts .

docker-run:
	docker run -d -p 8000:8000 social-alerts