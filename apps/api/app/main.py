"""
app/main.py — TestGen API entrypoint

Initializes the FastAPI application, registers middleware, and mounts routers.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import settings

app = FastAPI(
    title="TestGen API",
    description=(
        "E2E Test Script Generator — generates Playwright test scripts "
        "from plain-English requirements."
    ),
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ─── CORS ─────────────────────────────────────────────────────────────────────
# Allow the Next.js frontend to call the API in development.
# Tighten this in production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Routers ──────────────────────────────────────────────────────────────────
app.include_router(api_router)


# ─── Startup / shutdown events ────────────────────────────────────────────────
@app.on_event("startup")
async def on_startup() -> None:
    """
    Run once when the server starts.
    TODO: Initialize DB connection pool, Redis client, Playwright browser pool, etc.
    """
    pass  # placeholder


@app.on_event("shutdown")
async def on_shutdown() -> None:
    """
    Run once when the server shuts down.
    TODO: Close DB connections, flush queues, close Playwright browsers.
    """
    pass  # placeholder
