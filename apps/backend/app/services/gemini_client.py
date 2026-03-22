"""
app/services/gemini_client.py — Gemini API client

Wraps google-generativeai to support both:
  - API key auth  (GEMINI_BACKEND=gemini_api)  — Google AI Studio key
  - Vertex AI     (GEMINI_BACKEND=vertex)       — service account / ADC

The generate() method is async-safe: it wraps the synchronous SDK call in a
thread-pool executor so it doesn't block the FastAPI event loop.
"""

import asyncio
import functools
from dataclasses import dataclass

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class GeminiPart:
    """A single content part — either text or raw bytes (image)."""

    text: str | None = None
    data: bytes | None = None
    mime_type: str | None = None  # required when data is set


class GeminiClient:
    """
    Thin async wrapper around the Gemini generative model.

    Usage:
        client = GeminiClient()
        response = await client.generate([
            GeminiPart(text="Write a Playwright test for..."),
            GeminiPart(data=png_bytes, mime_type="image/png"),
        ])
    """

    def __init__(self) -> None:
        self._model = None  # lazy init on first call

    def _get_model(self):
        """Initialise the model once (lazy, thread-safe enough for single-process dev)."""
        if self._model is not None:
            return self._model

        backend = settings.GEMINI_BACKEND

        if backend == "gemini_api":
            import google.generativeai as genai  # type: ignore[import-untyped]

            if not settings.GEMINI_API_KEY:
                raise RuntimeError("GEMINI_API_KEY is not set. Add it to apps/backend/.env")
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self._model = genai.GenerativeModel(settings.GEMINI_MODEL)
            logger.info("Gemini client initialised (API key, model=%s)", settings.GEMINI_MODEL)

        elif backend == "vertex":
            import vertexai  # type: ignore[import-untyped]
            from vertexai.generative_models import GenerativeModel  # type: ignore[import-untyped]

            if not settings.GCP_PROJECT:
                raise RuntimeError("GCP_PROJECT is not set. Add it to apps/backend/.env")
            vertexai.init(project=settings.GCP_PROJECT, location=settings.GCP_LOCATION)
            self._model = GenerativeModel(settings.GEMINI_MODEL)
            logger.info(
                "Gemini client initialised (Vertex AI, project=%s, model=%s)",
                settings.GCP_PROJECT,
                settings.GEMINI_MODEL,
            )

        else:
            raise RuntimeError(
                f"Unknown GEMINI_BACKEND: {backend!r}. Use 'gemini_api' or 'vertex'."
            )

        return self._model

    def _build_sdk_parts(self, parts: list[GeminiPart]) -> list:
        """Convert GeminiPart list into whatever the SDK expects."""
        if settings.GEMINI_BACKEND == "vertex":
            from vertexai.generative_models import Part  # type: ignore[import-untyped]

            sdk_parts = []
            for p in parts:
                if p.text is not None:
                    sdk_parts.append(Part.from_text(p.text))
                elif p.data is not None and p.mime_type is not None:
                    sdk_parts.append(Part.from_data(data=p.data, mime_type=p.mime_type))
            return sdk_parts

        # gemini_api backend: accepts plain strings and dicts
        sdk_parts = []
        for p in parts:
            if p.text is not None:
                sdk_parts.append(p.text)
            elif p.data is not None and p.mime_type is not None:
                sdk_parts.append({"mime_type": p.mime_type, "data": p.data})
        return sdk_parts

    def _call_sync(self, parts: list[GeminiPart]) -> str:
        """Synchronous generation call — called from a thread pool."""
        model = self._get_model()
        sdk_parts = self._build_sdk_parts(parts)
        response = model.generate_content(sdk_parts)

        # Vertex AI: response.text raises if candidates are empty or blocked
        try:
            text = response.text
        except ValueError as exc:
            # Surface finish_reason and safety ratings in the error
            candidates = getattr(response, "candidates", [])
            if candidates:
                reason = getattr(candidates[0], "finish_reason", "unknown")
                raise RuntimeError(
                    f"Gemini returned no text (finish_reason={reason}). "
                    "The request may have been blocked by safety filters."
                ) from exc
            raise RuntimeError(f"Gemini returned an empty response: {exc}") from exc

        return text

    async def generate(self, parts: list[GeminiPart]) -> str:
        """
        Generate content from a mixed list of text and image parts.
        Non-blocking — runs the synchronous SDK call in a thread pool.
        """
        loop = asyncio.get_running_loop()
        fn = functools.partial(self._call_sync, parts)
        text = await loop.run_in_executor(None, fn)
        logger.info("Gemini generation complete (%d chars)", len(text))
        return text


# Module-level singleton
gemini_client = GeminiClient()
