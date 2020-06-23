user := $(shell id -u)
group := $(shell id -g)
dc := USER_ID=$(user) GROUP_ID=$(group) docker-compose
de := docker-compose exec

web_image=web
db_image=database

manage := $(de) $(web_image) pipenv run python manage.py


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

.PHONY: db-login
db-login:
	$(de) $(db_image) psql -U hello_django -d hello_django_dev
