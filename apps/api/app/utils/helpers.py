"""
app/utils/helpers.py — Shared utility functions

Small, pure helper functions used across multiple modules.
Keep this file lean — don't accumulate unrelated utilities here.
"""

import re
from urllib.parse import urlparse


def sanitise_slug(text: str, max_length: int = 50) -> str:
    """
    Convert a string to a URL/filename-safe slug.

    Example:
        >>> sanitise_slug("Login flow: enter credentials")
        "login_flow_enter_credentials"
    """
    slug = text.lower()
    slug = re.sub(r"[^a-z0-9\s_-]", "", slug)
    slug = re.sub(r"[\s-]+", "_", slug.strip())
    return slug[:max_length]


def is_valid_http_url(url: str) -> bool:
    """
    Return True if the given string is a valid http or https URL.

    Note: Pydantic's AnyHttpUrl already validates this at the schema layer.
    This helper is for cases where we need to check programmatically at runtime.
    """
    try:
        parsed = urlparse(url)
        return parsed.scheme in ("http", "https") and bool(parsed.netloc)
    except Exception:
        return False


def truncate(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate text to max_length characters, appending suffix if truncated."""
    if len(text) <= max_length:
        return text
    return text[: max_length - len(suffix)] + suffix
