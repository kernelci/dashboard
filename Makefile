DASHBOARD_DIR ?= dashboard
BACKEND_DIR   ?= backend

.DEFAULT_GOAL := help
.PHONY: help setup install check-lint fix test build ci dev dev-build clean

help: ## Show this help
	@awk 'BEGIN{FS=":.*##"} /^[a-zA-Z0-9_.-]+:.*##/ {printf "  \033[36m%-10s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

setup: ## Copy env files for Docker dev and manual backend workflows, then install dependencies
	@test -f .env || (cp .env.example .env && echo "Created .env from .env.example")
	@test -f .env.backend || (cp .env.backend.example .env.backend && echo "Created .env.backend from .env.backend.example")
	@test -f $(DASHBOARD_DIR)/.env || (cp $(DASHBOARD_DIR)/.env.example $(DASHBOARD_DIR)/.env && echo "Created dashboard/.env from dashboard/.env.example")
	$(MAKE) install

install: ## Install dependencies (pnpm + poetry)
	cd $(DASHBOARD_DIR) && pnpm install --frozen-lockfile
	cd $(BACKEND_DIR) && poetry install

check-lint: ## Run CI-equivalent lint checks (no autofix)
	cd $(DASHBOARD_DIR) && pnpm lint-staged
	cd $(BACKEND_DIR) && poetry run ruff check .
	cd $(BACKEND_DIR) && poetry run ruff format --check .

fix: ## Apply autofixes (lint, format, prettify)
	cd $(DASHBOARD_DIR) && pnpm lint
	cd $(BACKEND_DIR) && poetry run ruff check . --fix
	cd $(BACKEND_DIR) && poetry run ruff format .
	cd $(DASHBOARD_DIR) && pnpm prettify

test: ## Run fast local tests
	cd $(DASHBOARD_DIR) && pnpm test --watch=false
	cd $(BACKEND_DIR) && poetry run pytest -m unit --cov=kernelCI_app --cov=kernelCI_cache --cov-report=term-missing

build: ## Build frontend for production
	cd $(DASHBOARD_DIR) && pnpm build

ci: ## Reproduce full CI pipeline (lint + build + test + integration)
	$(MAKE) check-lint
	$(MAKE) build
	$(MAKE) test
	@trap 'docker compose -f docker-compose.test.yml down --volumes --remove-orphans' EXIT; \
	docker compose -f docker-compose.test.yml up test_db redis -d && \
	docker compose -f docker-compose.test.yml run --rm test_backend python manage.py migrate && \
	docker compose -f docker-compose.test.yml run --rm test_backend python manage.py seed_test_data --clear --yes && \
	docker compose -f docker-compose.test.yml up test_backend -d && \
	sleep 5 && \
	cd $(BACKEND_DIR) && TEST_BASE_URL=http://localhost:8001 poetry run pytest -m integration --use-local-db --run-all --cov=kernelCI_app --cov=kernelCI_cache --cov-report=term-missing

dev: ## Start development environment with docker-compose.dev.yml
	docker compose -f docker-compose.dev.yml up -d

dev-build: ## Start development environment and rebuild images
	docker compose -f docker-compose.dev.yml up --build -d

clean: ## Remove build artifacts and caches
	cd $(DASHBOARD_DIR) && rm -rf node_modules dist
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -f $(BACKEND_DIR)/.coverage*
