user := $(shell id -u)
group := $(shell id -g)
dc := USER_ID=$(user) GROUP_ID=$(group) docker-compose
de := docker-compose exec

dc-prod := $(dc) -f docker-compose.yml -f docker-compose.prod.yml
drtest := $(dc) -f docker-compose.yml -f docker-compose.test.yml run --rm
dr := $(dc) -f docker-compose.yml -f docker-compose.prod.yml run --rm
dr-dev := $(dc) run --rm

web_image=web
db_image=database

manage := $(dr) $(web_image) python manage.py
manage-dev := $(dr-dev) $(web_image) python manage.py

.PHONY: shell
shell:
	$(manage-dev) shell_plus --print-sql

.PHONY: prod-up
prod-up:
	$(dc) -f ./docker-compose.yml -f ./docker-compose.prod.yml up -d

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
	DOCKER_BUILDKIT=1 $(dc) build $(services)

.PHONY: docker-build-release
docker-build-release:
	cd app && npm run build && cd - && docker buildx build --build-arg USER_ID=$(user) --build-arg GROUP_ID=$(group) --push --platform linux/arm/v7,linux/amd64 --tag bobbyhome/core:$(version) ./app

.PHONY: test
test:
	$(drtest) web python -Wa manage.py test

.PHONY: migrations
migrations:
	$(manage-dev) makemigrations

.PHONY: migrate
migrate:
	$(manage-dev) migrate

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
	$(dr-dev) $(web_image) django-admin makemessages -l fr --ignore=node_modules

.PHONY: compile-messages
compile-messages:
	$(dr-dev) $(web_image) django-admin compilemessages

.PHONY: generate-mqtt-password
generate-mqtt-password:
	docker run -it --rm -v $(PWD)/config/mosquitto:/mosquitto/config eclipse-mosquitto mosquitto_passwd -c /mosquitto/config/passwd $(user)
