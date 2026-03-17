# TestGen — E2E Test Script Generator

A tool that helps test engineers generate end-to-end UI test scripts for web apps from plain-English requirements.

## What this is

TestGen takes a **target URL** and **natural-language acceptance criteria**, inspects the web app, reasons about the test scenario, and generates robust **Playwright** test scripts — ready to drop into a test suite.

## Current state

> **This is a project skeleton.** The architecture, folder structure, interfaces, and API contracts are in place. The core generation pipeline (page inspection, LLM reasoning, code generation) is intentionally not implemented yet.

See [docs/future-roadmap.md](docs/future-roadmap.md) for what comes next.

## Project structure

```
/
├── apps/
│   ├── web/          # Next.js + TypeScript frontend
│   └── api/          # Python + FastAPI backend
├── packages/
│   └── shared/       # API contracts, shared types, example payloads
├── docs/             # Architecture, product flow, roadmap
├── .github/          # CI/CD workflow placeholders
├── docker-compose.yml
└── Makefile
```

## Quick start

### Prerequisites

- Node.js 20+
- Python 3.11+
- (Optional) Docker + Docker Compose

### Frontend

```bash
cd apps/web
cp .env.example .env.local
npm install
npm run dev
# → http://localhost:3000
```

### Backend

```bash
cd apps/api
cp .env.example .env
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
# → http://localhost:8000
# → http://localhost:8000/docs  (Swagger UI)
```

### Docker (skeleton only)

```bash
docker-compose up
```

### Make shortcuts

```bash
make dev-api      # start backend
make dev-web      # start frontend
make dev          # start both (requires two terminals or tmux)
make install      # install all dependencies
```

## Tech stack

| Layer      | Technology                        |
|------------|-----------------------------------|
| Frontend   | Next.js 14 + TypeScript           |
| Backend    | Python 3.11 + FastAPI             |
| Automation | Playwright (future)               |
| Output     | Playwright Test (primary)         |
| Output     | Robot Framework (future/optional) |
| Reporting  | Allure (future)                   |
| CI/CD      | GitHub Actions (placeholder)      |
| Container  | Docker + Docker Compose           |

## Documentation

- [Architecture overview](docs/architecture.md)
- [Product flow](docs/product-flow.md)
- [Future roadmap](docs/future-roadmap.md)
