user := $(shell id -u)
group := $(shell id -g)

docker-build:
	docker buildx build --build-arg USER_ID=$(user) --build-arg GROUP_ID=$(group) --push --platform linux/arm/v7,linux/amd64 --tag mxmaxime/camera .
