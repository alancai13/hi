"""
app/api/router.py — Top-level API router

Assembles all endpoint groups under the /api/v1 prefix.
Add new endpoint modules here as the project grows.
"""

from fastapi import APIRouter

from app.api.endpoints import generation, health

api_router = APIRouter()

# ─── Health ───────────────────────────────────────────────────────────────────
api_router.include_router(
    health.router,
    prefix="",
    tags=["health"],
)

# ─── Generation ───────────────────────────────────────────────────────────────
api_router.include_router(
    generation.router,
    prefix="/api/v1",
    tags=["generation"],
)

# TODO: Add additional routers as the API grows
# api_router.include_router(history.router, prefix="/api/v1", tags=["history"])
# api_router.include_router(export.router, prefix="/api/v1", tags=["export"])
