"""
app/services/agents/intake_agent.py — Stage 1: Intake

Normalises the raw URL + requirements string into a structured IntakeResult
so every downstream stage works with typed, predictable inputs rather than
free-form text.

Falls back to sensible defaults if the LLM call fails so the pipeline
can always continue.
"""

import json

from app.core.logging import get_logger
from app.domain.models import IntakeResult
from app.services.gemini_client import GeminiPart, gemini_client

logger = get_logger(__name__)

_SYSTEM_PROMPT = """\
You are an intake classifier for an automated Playwright test generation system.

Given a target URL and plain-English test requirements, return a single JSON object
with exactly these fields:

{
  "flow_type": "<auth|ecommerce|form_submission|navigation|data_display|other>",
  "goal": "<one sentence — what must be true for the test to pass>",
  "entities": ["<key UI noun>", ...],
  "constraints": ["<any constraint or rule>", ...],
  "requires_auth": <true|false>,
  "multi_page": <true|false>
}

Rules:
- flow_type must be exactly one of the listed values
- goal must be one clear, testable sentence
- entities are the UI elements that matter (e.g. "search box", "Add to cart button")
- constraints come directly from the requirements (e.g. "use valid credentials")
- requires_auth is true if the flow needs a logged-in user
- multi_page is true if the flow spans more than one URL

Return ONLY the JSON object. No markdown, no explanation.
"""


class IntakeAgent:
    """Stage 1 — normalises the test request into structured intent."""

    async def run(self, target_url: str, requirements: str) -> IntakeResult:
        prompt = (
            f"Target URL: {target_url}\n\n"
            f"Requirements:\n{requirements.strip() or '(none provided — analyse the page)'}"
        )
        try:
            raw = await gemini_client.generate(
                [GeminiPart(text=_SYSTEM_PROMPT), GeminiPart(text=prompt)],
                json_mode=True,
            )
            data = json.loads(raw)
            result = IntakeResult(
                flow_type=data.get("flow_type", "other"),
                goal=data.get("goal", requirements[:120] or "Verify the page works correctly"),
                entities=data.get("entities", []),
                constraints=data.get("constraints", []),
                requires_auth=bool(data.get("requires_auth", False)),
                multi_page=bool(data.get("multi_page", False)),
            )
            logger.info(
                "IntakeAgent: flow_type=%s requires_auth=%s multi_page=%s",
                result.flow_type,
                result.requires_auth,
                result.multi_page,
            )
            return result

        except Exception as exc:
            logger.warning("IntakeAgent failed (%s) — using defaults", exc)
            return IntakeResult(
                flow_type="other",
                goal=requirements[:120] or "Verify the page works correctly",
                entities=[],
                constraints=[],
            )
