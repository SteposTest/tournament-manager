VER ?= 2.0

COMPOSE_FILE_NAME ?= docker-compose.yaml
IMAGE_TAG ?= tournament-manager:latest

build:
	docker build \
		-t $(IMAGE_TAG) \
		-f Dockerfile \
		.

up:
	docker-compose -f $(COMPOSE_FILE_NAME) up

down:
	docker-compose -f $(COMPOSE_FILE_NAME) down

create-db-vol:
	mkdir db_vol

remove-db-vol:
	rm -rf db_vol

recreate-db-vol: remove-db-vol create-db-vol
