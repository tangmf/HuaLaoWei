IMAGE_NAME = municipal-chatbot
DOCKER_COMPOSE = docker-compose

.PHONY: build rebuild run stop clean prune

# Build the Docker image
build:
	$(DOCKER_COMPOSE) build

# Force rebuild the Docker image without cache
build-clean:
	$(DOCKER_COMPOSE) build --no-cache

# Rebuild image from scratch, remove old containers, and run fresh
reset:
	-
	$(DOCKER_COMPOSE) down --volumes --remove-orphans
	$(DOCKER_COMPOSE) build --no-cache
	$(DOCKER_COMPOSE) up

# Run containers
run:
	$(DOCKER_COMPOSE) up

# Stop and remove containers
stop:
	$(DOCKER_COMPOSE) down

# Stop and remove containers, volumes, and orphans
stop-clean:
	$(DOCKER_COMPOSE) down --volumes --remove-orphans

# Remove everything: images, volumes, stopped containers, cache
prune:
	docker system prune -af --volumes

nuke:
	@echo "This will DELETE all Docker Desktop data. Proceed with caution."
	@powershell -Command "Start-Process 'cmd.exe' -ArgumentList '/k %windir%\\Sysnative\\wsl.exe --shutdown && %windir%\\Sysnative\\wsl.exe --unregister docker-desktop && %windir%\\Sysnative\\wsl.exe --unregister docker-desktop-data && pause' -Verb RunAs"