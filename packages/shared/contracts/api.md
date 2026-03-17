# API Contract — TestGen

Base URL: `http://localhost:8000/api/v1`

## Endpoints

### Health check

```
GET /health
```

Response `200`:
```json
{ "status": "ok", "version": "0.1.0" }
```

---

### Create a generation job

```
POST /api/v1/generate
Content-Type: application/json
```

Request body:
```json
{
  "target_url": "https://example.com/login",
  "requirements": "User can log in with a valid email and password and is redirected to the dashboard",
  "output_format": "playwright"
}
```

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `target_url` | string (URL) | yes | Must be a valid http/https URL |
| `requirements` | string | yes | Plain-English acceptance criteria, 1–2000 chars |
| `output_format` | enum | no | `"playwright"` (default) · `"robot"` (future) |

Response `202 Accepted`:
```json
{
  "job_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "status": "pending",
  "created_at": "2024-01-01T00:00:00Z"
}
```

Error `422 Unprocessable Entity`:
```json
{
  "detail": [
    { "loc": ["body", "target_url"], "msg": "invalid or missing URL scheme", "type": "value_error.url.scheme" }
  ]
}
```

---

### Get job status / result

```
GET /api/v1/jobs/{job_id}
```

Response `200` (pending):
```json
{
  "job_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "status": "pending",
  "created_at": "2024-01-01T00:00:00Z",
  "completed_at": null,
  "scenario_summary": null,
  "warnings": [],
  "generated_code": null,
  "output_format": "playwright",
  "error_message": null
}
```

Response `200` (completed):
```json
{
  "job_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "status": "completed",
  "created_at": "2024-01-01T00:00:00Z",
  "completed_at": "2024-01-01T00:00:05Z",
  "scenario_summary": "Login flow: enter email and password → submit → assert dashboard is visible",
  "warnings": [
    {
      "type": "selector_fragile",
      "severity": "warning",
      "message": "Login button was matched by visible text. Consider adding a data-testid attribute.",
      "element": "button:has-text('Log in')"
    }
  ],
  "generated_code": "import { test, expect } from '@playwright/test';\n\ntest('Login flow', async ({ page }) => {\n  // ...\n});\n",
  "output_format": "playwright",
  "error_message": null
}
```

Response `200` (failed):
```json
{
  "job_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "status": "failed",
  "error_message": "Page at https://example.com/login could not be reached (timeout after 30s)",
  ...
}
```

Response `404`:
```json
{ "detail": "Job not found" }
```

---

## Job status values

| Status | Meaning |
|--------|---------|
| `pending` | Job created, not yet started |
| `running` | Pipeline is executing |
| `completed` | Script generated successfully |
| `failed` | Pipeline encountered an unrecoverable error |

## Warning severity values

| Severity | Meaning |
|----------|---------|
| `info` | Informational note, no action needed |
| `warning` | Potentially fragile — review recommended |
| `error` | Generation may be incorrect — manual fix likely needed |

## Warning type values

| Type | Meaning |
|------|---------|
| `selector_fragile` | Selector relies on visible text or position rather than stable attributes |
| `requirement_ambiguous` | Requirement could not be clearly mapped to a test step |
| `element_not_found` | Expected element was not found on the page |
| `page_unreachable` | Target URL could not be loaded |
