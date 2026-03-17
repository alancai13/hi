# Product Flow

This document describes the intended end-to-end user experience and the corresponding system interactions. Steps marked **[NOT IMPLEMENTED]** are architecture placeholders only.

## User journey

### Step 1 — Enter inputs

The user opens the TestGen web UI and fills in:

- **Target URL** — the web app they want to test (e.g. `https://example.com/login`)
- **Requirements / acceptance criteria** — plain-English description of the scenario (e.g. "User should be able to log in with valid credentials and see their dashboard")
- **Output format** — currently only "Playwright Test" is offered; Robot Framework is a future option

### Step 2 — Submit

The frontend sends a `POST /api/v1/generate` request to the backend with the validated inputs.

The backend:
1. Validates the input schema
2. Creates a `GenerationJob` with status `pending`
3. Returns the `job_id` immediately (non-blocking)

### Step 3 — Job processing [NOT IMPLEMENTED]

The backend pipeline runs (eventually asynchronously):

1. **Page Inspection** — Playwright opens the target URL, captures interactive elements, page structure, visible text
2. **Scenario Planning** — Combines the page snapshot with the user's requirements to build a structured `TestPlan` (steps, assertions, selector candidates with confidence scores)
3. **Code Generation** — Translates the `TestPlan` into a Playwright test script
4. **Validation** *(optional)* — Runs the generated script against the target URL to check it executes without errors

### Step 4 — Display results

The frontend polls `GET /api/v1/jobs/{job_id}` (or receives a webhook/SSE event in future) and displays:

| Section | Content |
|---------|---------|
| Job status | `pending` → `running` → `completed` / `failed` |
| Scenario summary | Human-readable interpretation of what the test covers |
| Selector confidence | Warnings about fragile or ambiguous selectors |
| Generated script | Syntax-highlighted code preview |
| Actions | Copy to clipboard / Download as `.spec.ts` file |

## API contract summary

### `POST /api/v1/generate`

**Request:**
```json
{
  "target_url": "https://example.com/login",
  "requirements": "User can log in with valid email and password",
  "output_format": "playwright"
}
```

**Response:**
```json
{
  "job_id": "abc-123",
  "status": "pending",
  "created_at": "2024-01-01T00:00:00Z"
}
```

### `GET /api/v1/jobs/{job_id}`

**Response (completed):**
```json
{
  "job_id": "abc-123",
  "status": "completed",
  "scenario_summary": "Login flow: enter credentials → submit → assert dashboard",
  "warnings": [
    { "type": "selector_fragile", "message": "Login button matched by text, consider adding data-testid" }
  ],
  "generated_code": "import { test, expect } from '@playwright/test';\n\ntest('Login flow', ...",
  "output_format": "playwright",
  "created_at": "2024-01-01T00:00:00Z",
  "completed_at": "2024-01-01T00:00:05Z"
}
```

## Error cases

| Scenario | Behavior |
|----------|----------|
| Invalid URL | Validation error returned immediately (422) |
| Page unreachable | Job fails with `error_message` explaining cause |
| Ambiguous requirements | Job completes with warnings, lower confidence |
| Script validation fails | Warnings included, script still returned |

## Future flow additions

- File upload: user can attach a `.pdf` or `.docx` requirement spec instead of typing
- Saved history: previous generation jobs are persisted and browsable
- Re-run: user can tweak requirements and regenerate without re-entering the URL
- Team sharing: shareable links to generated scripts
