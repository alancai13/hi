"""
app/api/endpoints/health.py — Health check endpoint

GET /health — returns service status. Used by load balancers, Docker HEALTHCHECK,
and the CI pipeline to verify the service is running.
"""

from fastapi import APIRouter

from app.core.config import settings
from app.schemas.common import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse, summary="Health check")
async def health_check() -> HealthResponse:
    """
    Returns service health status.

    This endpoint should always return 200 while the service is running.
    TODO: Extend to check DB connectivity, Redis, etc. when those are added.
    """
    return HealthResponse(status="ok", version=settings.APP_VERSION)
