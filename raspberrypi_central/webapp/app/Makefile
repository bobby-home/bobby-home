user := $(shell id -u)
group := $(shell id -g)
dc := USER_ID=$(user) GROUP_ID=$(group) docker-compose
de := docker-compose exec

web_image=web
db_image=database

manage := $(de) $(web_image) python manage.py

.PHONY: rabbit-services
rabbit-services:
	$(dc) up rabbit rabbit_worker

.PHONY: web-services
web-services:
	$(dc) up celery_beat web database mqtt python_process_mqtt


.PHONY: migrations
migrations:
	$(manage) makemigrations

.PHONY: migrate
migrate: ## Migrate database /!\ docker-compose up should run.
	$(manage) migrate

.PHONY: tests
tests:
	$(manage) test


.PHONY: manage
manage:
	$(manage) $(command)

.PHONY: createapp
createapp:
	$(manage) startapp $(name)
	sudo chown -R ${USER}:${USER} $(name)

.PHONY: db-login
db-login:
	$(de) $(db_image) psql -U hello_django -d hello_django_dev

.PHONY: register_devices
register_devices:
	$(de) $(web_image) pipenv run python register_devices.py
