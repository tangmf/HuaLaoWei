# ---------------------------
# Environment Control
# ---------------------------

ENV_FILE := .env
COMPOSE_FILE := docker-compose.dev.yaml

.PHONY: help setup-dev setup-prod build up down restart logs prune rebuild nuke

help:
	@echo "Usage:"
	@echo "  make setup-dev   -> Copy .env.dev to .env"
	@echo "  make setup-prod  -> Copy .env.prod to .env"
	@echo "  make build       -> docker compose build"
	@echo "  make up          -> docker compose up"
	@echo "  make down        -> docker compose down"
	@echo "  make restart     -> Restart all containers"
	@echo "  make rebuild     -> Rebuild images and restart cleanly"
	@echo "  make prune       -> Remove all Docker volumes, images, cache"
	@echo "  make logs        -> Show logs"

prefix-vars:
	@echo "Prefixing variables in frontend_mobileapp/.env..."
	sed -i.bak -E '/^EXPO_PUBLIC_/! s/^([A-Z_][A-Z0-9_]*)=(.*)/EXPO_PUBLIC_\1=\2/' frontend_mobileapp/.env
	rm -f frontend_mobileapp/.env.bak

prefix-vars-windows:
	powershell -Command "$$envFile = 'frontend_mobileapp/.env'; $$tmpFile = 'frontend_mobileapp/.env.tmp'; Get-Content $$envFile | ForEach-Object { if ($$_ -notmatch '^EXPO_PUBLIC_') { if ($$_ -match '^([A-Z_][A-Z0-9_]*)=(.*)') { 'EXPO_PUBLIC_{0}={1}' -f $$matches[1], $$matches[2] } else { $$_ } } else { $$_ } } | Set-Content $$tmpFile; Move-Item -Force $$tmpFile $$envFile"
	@echo "Prefixing variables in frontend_mobileapp/.env (Windows)..."

# ---------------------------
# Setup Environment
# ---------------------------

setup-dev:
	cp .env.dev $(ENV_FILE)
	cp $(ENV_FILE) frontend_dashboard/.env
	cp $(ENV_FILE) frontend_mobileapp/.env
	make prefix-vars
	@echo "Switched to DEV environment."

setup-dev-windows:
	copy /Y .env.dev $(ENV_FILE)
	copy /Y $(ENV_FILE) frontend_dashboard\.env
	copy /Y $(ENV_FILE) frontend_mobileapp\.env
	make prefix-vars-windows
	@echo "Switched to DEV environment."

setup-prod:
	cp .env.dev $(ENV_FILE)
	cp $(ENV_FILE) frontend_dashboard/.env
	cp $(ENV_FILE) frontend_mobileapp/.env
	make prefix-vars
	@echo "Switched to DEV environment."

# ---------------------------
# Docker Compose Commands
# ---------------------------

build:
	docker compose -f $(COMPOSE_FILE) build

up:
# docker compose -f $(COMPOSE_FILE) up -d || true
	docker compose -f $(COMPOSE_FILE) up -d

down:
	docker compose -f $(COMPOSE_FILE) down

restart:
	docker compose -f $(COMPOSE_FILE) down
	docker compose -f $(COMPOSE_FILE) up -d

rebuild:
	docker compose -f $(COMPOSE_FILE) down --volumes --remove-orphans
	docker compose -f $(COMPOSE_FILE) build --no-cache
	docker compose -f $(COMPOSE_FILE) up -d

prune:
	docker system prune -af --volumes

nuke:
	@echo "This will DELETE all Docker Desktop data. Proceed with caution."
	@powershell -Command "Start-Process 'cmd.exe' -ArgumentList '/k wsl.exe --shutdown && wsl.exe --unregister docker-desktop && wsl.exe --unregister docker-desktop-data && pause' -Verb RunAs"

logs:
	docker compose -f $(COMPOSE_FILE) logs --follow
