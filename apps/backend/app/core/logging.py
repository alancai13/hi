"""
app/core/logging.py — Logging configuration

Centralised logging setup. Import `get_logger` in any module that needs logging.

TODO: Add structured JSON logging for production (e.g. structlog or python-json-logger).
"""

import logging

from app.core.config import settings


def configure_logging() -> None:
    """Configure root logger. Call once at startup."""
    level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )


def get_logger(name: str) -> logging.Logger:
    """Get a named logger for a module."""
    return logging.getLogger(name)
