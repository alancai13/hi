# packages/shared

Shared contracts, type definitions, and example payloads for the TestGen system.

This package is the **source of truth for the API contract** between the frontend and backend.
It is intentionally language-agnostic — it contains JSON examples, documentation, and
TypeScript type definitions that the frontend consumes directly.

The backend's Pydantic schemas in `apps/api/app/schemas/` should always match these definitions.

## Contents

```
packages/shared/
├── contracts/
│   └── api.md          # Human-readable API contract documentation
├── examples/
│   ├── generation_request.json   # Example POST /api/v1/generate body
│   └── generation_response.json  # Example job status response (completed)
└── types/
    └── index.ts         # TypeScript types mirroring backend Pydantic schemas
```

## Usage

The frontend imports from `packages/shared/types/` for type safety across the API boundary.

```typescript
import type { GenerationRequest, JobStatus } from "../../packages/shared/types";
```

> In the future, consider publishing this as an internal npm package or generating
> types automatically from the OpenAPI spec at `http://localhost:8000/openapi.json`.
