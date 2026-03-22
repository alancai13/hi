# apps/api — TestGen FastAPI Backend

## Quick start

```bash
cd apps/api
cp .env.example .env
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health: http://localhost:8000/health

## Project structure

```
app/
├── main.py              # FastAPI app factory and startup
├── core/
│   ├── config.py        # Settings (reads from .env)
│   └── logging.py       # Logging configuration
├── api/
│   ├── router.py        # Assembles all routers
│   └── endpoints/
│       ├── health.py    # GET /health
│       └── generation.py  # POST /api/v1/generate, GET /api/v1/jobs/{id}
├── schemas/
│   ├── common.py        # Shared response schemas (HealthResponse, ErrorResponse)
│   └── generation.py    # API request/response schemas for generation
├── domain/
│   └── models.py        # Core domain dataclasses (GenerationJob, TestPlan, etc.)
├── services/
│   ├── generation_service.py   # Orchestrates the pipeline (currently mocked)
│   ├── page_inspector.py       # [STUB] Playwright page inspection
│   ├── scenario_planner.py     # [STUB] Requirement → TestPlan
│   ├── code_generator.py       # [STUB] TestPlan → script code
│   ├── script_validator.py     # [STUB] Optional dry-run validation
│   └── artifact_exporter.py    # Export/filename helpers
├── repositories/
│   └── job_store.py     # In-memory job store (replace with DB in Phase 4)
├── models/              # Future ORM models (empty until DB is added)
└── utils/
    └── helpers.py       # Pure utility functions
```

## Running with linting

```bash
ruff check app/       # lint
ruff format app/      # format
```

## Environment variables

See `.env.example` for all available settings.
