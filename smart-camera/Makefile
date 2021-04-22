user := $(shell id -u)
group := $(shell id -g)
dc := USER_ID=$(user) GROUP_ID=$(group) docker-compose
de := docker-compose exec

# -f docker-compose.test.yml
drtest := $(dc) run --rm
dc-prod := $(dc) -f docker-compose.yml -f docker-compose.prod.yml

.PHONY: prod-up
prod-up:
	$(dc) -f ./docker-compose.yml -f ./docker-compose.prod.yml up -d

.PHONY: dev-up
dev-up:
	$(dc) up

.PHONY: build-docker
build-docker:
	$(dc) build

.PHONY: test
test:
	$(drtest) camera python -m unittest test/test_run_listen_frame.py #

.PHONY: docker-build-release
docker-build-release:
	docker buildx build --build-arg USER_ID=$(user) --build-arg GROUP_ID=$(group) --push --platform linux/arm/v7,linux/amd64 --tag bobbyhome/camera:$(version) ./app
