# ---------------------------
# Environment Control
# ---------------------------

ENV_FILE := .env

.PHONY: help setup-dev setup-prod up down restart logs

help:
	@echo "Usage:"
	@echo "  make setup-dev   -> Copy .env.dev to .env"
	@echo "  make setup-prod  -> Copy .env.prod to .env"
	@echo "  make build       -> docker-compose build"
	@echo "  make up          -> docker-compose up"
	@echo "  make down        -> docker-compose down"
	@echo "  make restart     -> Restart all containers"
	@echo "  make rebuild     -> Rebuild image, remove old containers, and run fresh"
	@echo "  make prune       -> Remove everything: images, volumes, stopped containers, cache"
	@echo "  make logs        -> Show logs"

# ---------------------------
# Setup Environment
# ---------------------------

setup-dev:
	cp .env.dev $(ENV_FILE)
	@echo "Switched to DEV environment."

setup-prod:
	cp .env.prod $(ENV_FILE)
	@echo "Switched to PROD environment."

# ---------------------------
# Docker Compose Commands
# ---------------------------

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

restart:
	docker-compose down
	docker-compose up -d

rebuild:
	-
	docker-compose down --volumes --remove-orphans
	docker-compose build --no-cache
	docker-compose up

prune:
	docker system prune -af --volumes

nuke:
	@echo "This will DELETE all Docker Desktop data. Proceed with caution."
	@powershell -Command "Start-Process 'cmd.exe' -ArgumentList '/k %windir%\\Sysnative\\wsl.exe --shutdown && %windir%\\Sysnative\\wsl.exe --unregister docker-desktop && %windir%\\Sysnative\\wsl.exe --unregister docker-desktop-data && pause' -Verb RunAs"

logs:
	docker-compose logs --follow
