"""
app/schemas/common.py — Shared Pydantic response models

These are not domain-specific — they are used across multiple endpoints.
"""

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    version: str

    model_config = {"json_schema_extra": {"example": {"status": "ok", "version": "0.1.0"}}}


class ErrorResponse(BaseModel):
    """Generic error response wrapper."""

    detail: str
