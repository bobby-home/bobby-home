user := $(shell id -u)
group := $(shell id -g)
dc := USER_ID=$(user) GROUP_ID=$(group) docker-compose
de := docker-compose exec

dc-prod := $(dc) -f docker-compose.yml -f docker-compose.prod.yml
drtest := $(dc) -f docker-compose.yml -f docker-compose.test.yml run --rm
dr := $(dc) run --rm

web_image=web
db_image=database

manage := $(dr) $(web_image) python manage.py

.PHONY: create-folders
create-folders:
	mkdir -p mosquitto-data && sudo chown -R 1883:1883 mosquitto-data
	mkdir -p psql-data

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

.PHONY: workers
workers:
	$(dc-prod) up -d rabbit_worker

.PHONY: web-services
web-services:
	$(dc-prod) up -d web

.PHONY: telegram_bot
telegram_bot:
	$(dc-prod) up -d telegram_bot

.PHONY: mqtt-services
mqtt-services:
	$(dc-prod) up -d python_process_mqtt

.PHONY: build-docker
build-docker:
	$(dc) build

.PHONY: docker-build-release
docker-build-release:
	docker buildx build --build-arg USER_ID=$(user) --build-arg GROUP_ID=$(group) --push --platform linux/arm/v7,linux/amd64 --tag mxmaxime/core ./app

.PHONY: test
test:
	$(drtest) web python -Wa manage.py test

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

.PHONY: messages
messages:
	$(dr) $(web_image) django-admin makemessages -l fr

.PHONY: compile-messages
compile-messages:
	$(dr) $(web_image) django-admin compilemessages
