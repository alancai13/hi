# Future Roadmap

This document tracks what is intentionally not built yet and what comes next.

## Current state (skeleton)

The project has:
- Clean monorepo structure
- Typed interfaces and schemas
- Stubbed backend pipeline modules
- Placeholder frontend UI
- Runnable locally (frontend loads, backend starts, health endpoint works)
- Mock generation endpoint returns placeholder data

## Phase 1 — Core pipeline (next priority)

Goals: make the generation pipeline actually work end-to-end with a simple case.

| Task | Module | Notes |
|------|--------|-------|
| Implement `PageInspector.inspect_page()` | `services/page_inspector.py` | Use Playwright to capture page title, interactive elements, forms, buttons |
| Implement `ScenarioPlanner.build_test_plan()` | `services/scenario_planner.py` | Rule-based first: map requirements keywords to test steps |
| Implement `CodeGenerator.generate_playwright_script()` | `services/code_generator.py` | Template-based Playwright code generation from a `TestPlan` |
| Wire up orchestration in `GenerationService` | `services/generation_service.py` | Replace mock with real pipeline call |
| Replace in-memory job store with async task | `repositories/job_store.py` | Use `asyncio` background task or Celery |

## Phase 2 — Quality and reliability

| Task | Notes |
|------|-------|
| Selector confidence scoring | Rank selectors: `data-testid` > ARIA role > CSS class > text |
| Warning generation | Flag fragile selectors, missing ARIA labels, dynamic content |
| LLM integration | Use Claude/GPT to reason about requirements and improve test plan quality |
| Script dry-run validation | Run generated script against target URL, capture pass/fail |
| Robust error handling | Handle page load timeouts, auth walls, SPAs, redirects |

## Phase 3 — Multi-format output

| Task | Notes |
|------|-------|
| Robot Framework output | Add `RobotFrameworkGenerator` implementing the same interface as `PlaywrightGenerator` |
| Output format plugin system | Abstract `BaseCodeGenerator` so new formats are easy to add |
| Allure annotations | Add Allure metadata to generated Playwright scripts |

## Phase 4 — Persistence and async jobs

| Task | Notes |
|------|-------|
| PostgreSQL persistence | Replace in-memory job store with SQLAlchemy + Postgres |
| Redis job queue | Use Celery or ARQ for async background generation |
| SSE / WebSocket updates | Push job status to frontend instead of polling |
| User accounts (optional) | Save history, share scripts, API keys |

## Phase 5 — Developer experience and production

| Task | Notes |
|------|-------|
| File upload for requirements | Accept `.pdf`, `.docx`, `.md` requirement files |
| GitHub Actions — full CI | Add real test runs, Docker build, deployment |
| Docker production build | Multi-stage Dockerfiles, non-root users, proper healthchecks |
| Allure reporting integration | Store test results and display historical reports |
| Rate limiting and auth | API key authentication, per-user job limits |

## Known design decisions to revisit

- **In-memory job store**: Fine for prototype, must be replaced before any concurrent usage
- **Synchronous generation**: Currently blocking — needs async execution before production
- **No LLM yet**: The scenario planner is rule-based. LLM integration will improve quality significantly but adds cost and latency considerations
- **Single output format**: The code generator interface is designed for multiple formats but only Playwright is implemented

## Open questions

- Should page inspection run at job creation time or lazily?
- Should generated scripts be stored as files or as database blobs?
- What is the right confidence threshold for showing warnings?
- How should auth-protected pages be handled? (Cookie passing, token injection)
