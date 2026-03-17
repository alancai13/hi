.PHONY: dev dev-web dev-api install install-web install-api lint lint-web lint-api format clean help

# ─── Dev servers ──────────────────────────────────────────────────────────────

dev-web:
	cd apps/web && npm run dev

dev-api:
	cd apps/api && source .venv/bin/activate && uvicorn app.main:app --reload --port 8000

# Note: run dev-web and dev-api in separate terminals, or use a process manager.
dev:
	@echo "Run 'make dev-web' and 'make dev-api' in separate terminals."

# ─── Install ──────────────────────────────────────────────────────────────────

install: install-web install-api

install-web:
	cd apps/web && npm install

install-api:
	cd apps/api && python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt

# ─── Lint / Format ────────────────────────────────────────────────────────────

lint: lint-web lint-api

lint-web:
	cd apps/web && npm run lint

lint-api:
	cd apps/api && source .venv/bin/activate && ruff check app/

format-api:
	cd apps/api && source .venv/bin/activate && ruff format app/

format-web:
	cd apps/web && npm run format

format: format-web format-api

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
	@echo "  make dev-web       Start Next.js frontend (port 3000)"
	@echo "  make dev-api       Start FastAPI backend (port 8000)"
	@echo "  make install       Install all dependencies"
	@echo "  make lint          Lint frontend + backend"
	@echo "  make format        Format frontend + backend"
	@echo "  make docker-up     Build and start Docker services"
	@echo "  make docker-down   Stop Docker services"
	@echo "  make clean         Remove build artifacts and caches"
	@echo ""
