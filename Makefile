build:
	docker-compose build

up:
	docker-compose up -d

start:
	docker-compose start

stop:
	docker-compose stop

migrate:
	docker-compose run backend python manage.py migrate

collectstatic:
	docker-compose run backend python manage.py collectstatic --noinput

createsuperuser:
	docker-compose run backend python manage.py createsuperuser

shell-nginx:
	docker exec -ti reborn_nginx_1 bash

shell-backend:
	docker exec -ti reborn_backend_1 bash

log-nginx:
	docker-compose logs nginx

log-backend:
	docker-compose logs backend


