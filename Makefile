.PHONY: dev dev-frontend dev-backend install install-frontend install-backend lint lint-frontend lint-backend format clean help

# ─── Dev servers ──────────────────────────────────────────────────────────────

dev-frontend:
	cd apps/frontend && npm run dev

dev-backend:
	cd apps/backend && source .venv/bin/activate && uvicorn app.main:app --reload --port 8000

# Note: run dev-frontend and dev-backend in separate terminals, or use a process manager.
dev:
	@echo "Run 'make dev-frontend' and 'make dev-backend' in separate terminals."

# ─── Install ──────────────────────────────────────────────────────────────────

install: install-frontend install-backend

install-frontend:
	cd apps/frontend && npm install

install-backend:
	cd apps/backend && python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt

# ─── Lint / Format ────────────────────────────────────────────────────────────

lint: lint-frontend lint-backend

lint-frontend:
	cd apps/frontend && npm run lint

lint-backend:
	cd apps/backend && source .venv/bin/activate && ruff check app/

format-backend:
	cd apps/backend && source .venv/bin/activate && ruff format app/

format-frontend:
	cd apps/frontend && npm run format

format: format-frontend format-backend

# ─── Docker ───────────────────────────────────────────────────────────────────

docker-up:
	docker-compose up --build

docker-down:
	docker-compose down

# ─── Utilities ────────────────────────────────────────────────────────────────

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .ruff_cache -exec rm -rf {} +
	find . -type d -name node_modules -exec rm -rf {} +
	find . -type d -name .next -exec rm -rf {} +

help:
	@echo ""
	@echo "TestGen — available make commands:"
	@echo ""
	@echo "  make dev-frontend     Start Next.js frontend (port 3000)"
	@echo "  make dev-backend      Start FastAPI backend (port 8000)"
	@echo "  make install          Install all dependencies"
	@echo "  make lint             Lint frontend + backend"
	@echo "  make format           Format frontend + backend"
	@echo "  make docker-up        Build and start Docker services"
	@echo "  make docker-down      Stop Docker services"
	@echo "  make clean            Remove build artifacts and caches"
	@echo ""
