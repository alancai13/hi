"""
app/schemas/generation.py — Pydantic schemas for the generation API

These are the HTTP-layer contracts: request validation and response serialization.
They intentionally mirror the shared TypeScript types in packages/shared/types/index.ts.

Domain models (richer, more complex) live in app/domain/models.py.
"""

from datetime import datetime
from enum import Enum
from typing import Literal

from pydantic import AnyHttpUrl, BaseModel, Field

# ─── Enums ────────────────────────────────────────────────────────────────────


class OutputFormat(str, Enum):
    playwright = "playwright"
    robot = "robot"  # future


class JobStatus(str, Enum):
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"


class WarningSeverity(str, Enum):
    info = "info"
    warning = "warning"
    error = "error"


class WarningType(str, Enum):
    selector_fragile = "selector_fragile"
    requirement_ambiguous = "requirement_ambiguous"
    element_not_found = "element_not_found"
    page_unreachable = "page_unreachable"


# ─── Request ──────────────────────────────────────────────────────────────────


class GenerationRequest(BaseModel):
    """Incoming request to generate an E2E test script."""

    target_url: AnyHttpUrl = Field(
        ...,
        description="The URL of the web application to test.",
        examples=["https://example.com/login"],
    )
    requirements: str = Field(
        ...,
        min_length=5,
        max_length=2000,
        description="Plain-English acceptance criteria describing the test scenario.",
        examples=["User can log in with valid credentials and is redirected to the dashboard."],
    )
    output_format: OutputFormat = Field(
        default=OutputFormat.playwright,
        description="The format of the generated test script.",
    )


# ─── Sub-models ───────────────────────────────────────────────────────────────


class GenerationWarning(BaseModel):
    """A warning about a potential issue in the generated test."""

    type: WarningType
    severity: WarningSeverity
    message: str
    element: str | None = Field(
        default=None,
        description="The selector or element reference that triggered this warning.",
    )


# ─── Responses ────────────────────────────────────────────────────────────────


class CreateJobResponse(BaseModel):
    """Returned immediately after a job is created."""

    job_id: str
    status: Literal[JobStatus.pending] = JobStatus.pending
    created_at: datetime


class JobResult(BaseModel):
    """Full job state — returned by GET /api/v1/jobs/{job_id}."""

    job_id: str
    status: JobStatus
    created_at: datetime
    completed_at: datetime | None = None

    scenario_summary: str | None = Field(
        default=None,
        description="Human-readable summary of the inferred test scenario.",
    )
    warnings: list[GenerationWarning] = Field(default_factory=list)
    generated_code: str | None = Field(
        default=None,
        description="The generated test script source code.",
    )
    output_format: OutputFormat
    error_message: str | None = None
