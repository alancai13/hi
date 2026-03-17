"""
app/services/code_generator.py — Playwright test code generator

Orchestrates the Gemini call:
  1. Builds the multimodal prompt via prompt_builder
  2. Calls GeminiClient.generate()
  3. Cleans the response (strips markdown fences, extracts code)
  4. Produces a GeneratedArtifact with warnings
"""

import re

from app.core.config import settings
from app.core.logging import get_logger
from app.domain.models import (
    GeneratedArtifact,
    GenerationJob,
    GenerationWarning,
    OutputFormat,
    PageSnapshot,
)
from app.services.gemini_client import gemini_client
from app.services.prompt_builder import build_parts

logger = get_logger(__name__)


class CodeGenerator:
    """Generates a Playwright test script from a job + page snapshot using Gemini."""

    async def generate(
        self,
        job: GenerationJob,
        snapshot: PageSnapshot,
    ) -> GeneratedArtifact:
        """
        Call Gemini with the full multimodal context and return a GeneratedArtifact.
        Raises RuntimeError if generation fails.
        """
        if not settings.gemini_configured:
            raise RuntimeError(
                "Gemini is not configured. Set GEMINI_API_KEY (or GCP_PROJECT for Vertex) in .env"
            )

        logger.info("Building prompt for job %s", job.job_id)
        parts = build_parts(job, snapshot)

        logger.info("Calling Gemini (%s) for job %s", settings.GEMINI_MODEL, job.job_id)
        raw_response = await gemini_client.generate(parts)

        code = _extract_code(raw_response)
        warnings = _analyse_code(code, snapshot)
        summary = _build_summary(job, snapshot)

        logger.info("Code generation complete for job %s (%d chars)", job.job_id, len(code))

        return GeneratedArtifact(
            job_id=job.job_id,
            output_format=job.input.output_format if job.input else OutputFormat.playwright,
            code=code,
            scenario_summary=summary,
            warnings=warnings,
            model_used=settings.GEMINI_MODEL,
        )


# ─── Response parsing ─────────────────────────────────────────────────────────

def _extract_code(raw: str) -> str:
    """
    Strip markdown fences from the LLM response.
    Gemini sometimes wraps code in ```typescript ... ``` even when asked not to.
    """
    # Match ```typescript ... ``` or ``` ... ```
    fence_match = re.search(r"```(?:typescript|ts|javascript|js)?\s*\n(.*?)```", raw, re.DOTALL)
    if fence_match:
        return fence_match.group(1).strip()

    # If the response starts with 'import' it's already bare code
    stripped = raw.strip()
    if stripped.startswith("import "):
        return stripped

    # Last resort: return as-is (let the user see what was generated)
    return stripped


# ─── Code analysis ────────────────────────────────────────────────────────────

def _analyse_code(code: str, snapshot: PageSnapshot) -> list[GenerationWarning]:
    """
    Inspect the generated code and emit warnings for common issues.
    These are heuristic — not guaranteed to be correct.
    """
    warnings: list[GenerationWarning] = []

    if not code.strip():
        warnings.append(GenerationWarning(
            type="generation_empty",
            severity="error",
            message="Gemini returned an empty response. Check your API key and model settings.",
        ))
        return warnings

    if "waitForTimeout" in code:
        warnings.append(GenerationWarning(
            type="fragile_wait",
            severity="warning",
            message=(
                "Generated script uses waitForTimeout() — replace with waitForSelector(), "
                "waitForURL(), or expect(...).toBeVisible() for more reliable tests."
            ),
        ))

    # Detect text-based selectors where a testid would be more stable
    text_selectors = re.findall(r"getByText\(['\"]([^'\"]+)['\"]", code)
    for sel in text_selectors[:3]:  # warn on first 3 occurrences
        warnings.append(GenerationWarning(
            type="selector_fragile",
            severity="info",
            message=f"Selector by text {sel!r} may break if the copy changes. Consider adding data-testid.",
            element=f"getByText('{sel}')",
        ))

    # If no assertions found, warn
    if "expect(" not in code:
        warnings.append(GenerationWarning(
            type="no_assertions",
            severity="warning",
            message="No expect() assertions found in the generated script. Consider adding assertions.",
        ))

    # If page has elements with data-testid but code doesn't use getByTestId
    has_testids = any(el.data_testid for el in snapshot.elements)
    if has_testids and "getByTestId" not in code and "data-testid" not in code:
        warnings.append(GenerationWarning(
            type="missed_testid",
            severity="info",
            message=(
                "The page has elements with data-testid attributes. "
                "Consider using page.getByTestId() for more stable selectors."
            ),
        ))

    return warnings


def _build_summary(job: GenerationJob, snapshot: PageSnapshot) -> str:
    """Generate a human-readable summary of what the test covers."""
    url = job.input.target_url if job.input else snapshot.url
    req = job.input.requirements.strip() if job.input and job.input.requirements.strip() else None
    title = snapshot.title or url

    if req:
        # First sentence of requirements as summary
        first_sentence = req.split("\n")[0].strip().rstrip(".")
        return f"{title} — {first_sentence}"

    n_elements = len(snapshot.elements)
    return (
        f"Auto-generated tests for {title} "
        f"({n_elements} interactive element{'s' if n_elements != 1 else ''} analysed)"
    )
