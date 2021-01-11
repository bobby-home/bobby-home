user := $(shell id -u)
group := $(shell id -g)
dc := USER_ID=$(user) GROUP_ID=$(group) docker-compose
de := docker-compose exec

.PHONY: prod-up
prod-up:
	$(dc) -f ../docker-compose.yml -f ../docker-compose.prod.yml -d up

.PHONY: dev-up
dev-up:
	$(dc) up

.PHONY: build-docker
build-docker:
	$(dc) build
