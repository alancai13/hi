# Architecture Overview

## System summary

TestGen is a monorepo web application that accepts a target URL and plain-English test requirements, then generates runnable Playwright test scripts. It is designed as a modular pipeline where each stage — page inspection, scenario planning, code generation, and validation — is a separate, swappable service.

## High-level component map

```
┌──────────────────────────────────────────────────────────────────┐
│                          Browser (User)                          │
│                        Next.js Frontend                          │
│   [ Form: URL + Requirements ] → [ Result: Script + Summary ]    │
└─────────────────────────────┬────────────────────────────────────┘
                              │ HTTP (REST)
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│                       FastAPI Backend                            │
│                                                                  │
│  ┌─────────────┐   ┌──────────────┐   ┌────────────────────┐   │
│  │  API Layer  │──▶│ Generation   │──▶│  Pipeline Services │   │
│  │  (routers,  │   │  Service     │   │                    │   │
│  │   schemas)  │   │  (orchestr.) │   │  1. PageInspector  │   │
│  └─────────────┘   └──────────────┘   │  2. ScenarioPlanner│   │
│                                        │  3. CodeGenerator  │   │
│  ┌─────────────┐                       │  4. ScriptValidator│   │
│  │  Job Store  │                       │  5. ArtifactExport │   │
│  │  (in-memory │                       └────────────────────┘   │
│  │   → future  │                                                 │
│  │   DB/Redis) │                                                 │
│  └─────────────┘                                                 │
└──────────────────────────────────────────────────────────────────┘
                              │
                    (future) Playwright
                    Browser automation
```

## Layers and responsibilities

### Frontend (`apps/web`)

- Collects user input: target URL, requirements, output format
- Sends generation requests to the backend via a typed API client
- Polls or receives job status updates
- Displays: scenario summary, warnings, generated script, copy/download

### Backend (`apps/api`)

| Layer | Path | Responsibility |
|-------|------|----------------|
| API | `app/api/` | HTTP routing, request validation, response serialization |
| Schemas | `app/schemas/` | Pydantic request/response models (the API contract) |
| Services | `app/services/` | Business logic, pipeline orchestration |
| Domain | `app/domain/` | Core domain models (pure Python dataclasses/types) |
| Repositories | `app/repositories/` | Data access — job store, future DB layer |
| Utils | `app/utils/` | Shared helpers, formatting, logging utilities |
| Core | `app/core/` | App configuration, settings, startup |

### Shared (`packages/shared`)

- API contract documentation
- Example request/response payloads (JSON)
- Shared type definitions (for documentation and cross-team alignment)

## Key domain concepts

| Concept | Description |
|---------|-------------|
| `GenerationJob` | Tracks the lifecycle of a single generation request |
| `TestScenarioInput` | The user's URL + requirements, normalized |
| `PageSnapshot` | Metadata captured by Playwright about the target page |
| `TestPlan` | Intermediate structured representation of test steps/assertions |
| `SelectorCandidate` | A UI element with a proposed selector + confidence score |
| `GenerationWarning` | A warning about fragile selectors, ambiguous requirements, etc. |
| `GeneratedArtifact` | The final output: test code + metadata |

## Data flow (future implementation)

```
User Input
    │
    ▼
TestScenarioInput (validated)
    │
    ▼
PageInspector.inspect_page(url)
    │ → PageSnapshot (title, interactive elements, structure)
    ▼
ScenarioPlanner.build_test_plan(input, snapshot)
    │ → TestPlan (ordered steps, assertions, selector candidates)
    ▼
CodeGenerator.generate_playwright_script(plan)
    │ → GeneratedArtifact (code string, metadata)
    ▼
ScriptValidator.validate_script(artifact, url) [optional]
    │ → warnings, confidence, execution results
    ▼
ArtifactExporter.export(artifact, format)
    │ → downloadable file or inline code string
```

## Not implemented yet

- Page inspection via Playwright
- LLM-based or rule-based scenario reasoning
- Code generation logic
- Script validation / dry-run
- Persistent job storage (database, Redis)
- Async job execution (Celery, ARQ, or similar)
- Multi-format output (Robot Framework)
- File upload for requirement documents

See [future-roadmap.md](future-roadmap.md) for planned milestones.
