user := $(shell id -u)
group := $(shell id -g)
dc := USER_ID=$(user) GROUP_ID=$(group) docker-compose
de := docker-compose exec

dc-prod := $(dc) -f docker-compose.yml -f docker-compose.prod.yml
drtest := $(dc) -f docker-compose.yml -f docker-compose.test.yml run --rm

web_image=web
db_image=database

manage := $(de) $(web_image) python manage.py

.PHONY: stop-all
stop-all:
	docker stop $(docker ps -aq)

.PHONY: prod-up
prod-up:
	$(dc) -f ../docker-compose.yml -f ../docker-compose.prod.yml -d up

.PHONY: dev-up
dev-up:
	$(dc) up

.PHONY: monitoring
monitoring:
	$(dc-prod) up -d loki promtail grafana

.PHONY: rabbit-services
rabbit-services:
	$(dc-prod) up -d rabbit rabbit_worker

.PHONY: web-services
web-services:
	$(dc-prod) up -d database celery_beat web telegram_bot

.PHONY: mqtt-services
mqtt-services:
	$(dc-prod) up -d mqtt python_process_mqtt

.PHONY: build-docker
build-docker:
	$(dc) build

.PHONY: test
test:
	$(drtest) web python manage.py test

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

.PHONY: db-login
db-login:
	$(de) $(db_image) psql -U hello_django -d hello_django_dev

.PHONY: makemessages
makemessages:
	$(de) $(web_image) django-admin makemessages -l fr

.PHONY: compilemessages
compilemessages:
	$(de) $(web_image) django-admin compilemessages
