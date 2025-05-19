# Default docker-compose files
COMPOSE_DEV=docker-compose-development.yml
COMPOSE_PROD=docker-compose-production.yml

# --- Development ---

dev:
	@echo "[DEV] Starting development environment..."
	docker compose -f $(COMPOSE_DEV) up --build

dev-down:
	@echo "[DEV] Stopping development environment..."
	docker compose -f $(COMPOSE_DEV) down --remove-orphans

dev-test:
	@echo "[DEV] Running test suite..."
	docker compose -f $(COMPOSE_DEV) run --rm tests

dev-clean:
	@echo "[DEV] Cleaning up development environment..."
	docker compose -f $(COMPOSE_DEV) down -v --remove-orphans

# --- Production ---

prod:
	@echo "[PROD] Starting production environment..."
	docker compose -f $(COMPOSE_PROD) up -d --build

prod-down:
	@echo "[PROD] Stopping production environment..."
	docker compose -f $(COMPOSE_PROD) down

prod-restart:
	@echo "[PROD] Restarting production environment..."
	docker compose -f $(COMPOSE_PROD) down && docker compose -f $(COMPOSE_PROD) up -d --build

# --- Utilities ---

logs:
	docker compose -f $(COMPOSE_DEV) logs -f

ps:
	docker compose -f $(COMPOSE_DEV) ps

# --- Shortcuts ---

test: dev-test
up: dev
down: dev-down
clean: dev-clean
