"""
app/services/agents/repair_agent.py — Stage 6: Repair

When ValidationAgent finds errors, RepairAgent asks the LLM to fix the
TestPlan (not the code). CodegenAgent then re-renders the corrected plan.

The prompt includes:
  - The original TestPlan as JSON
  - Every validation issue (errors + warnings)
  - The same selector and navigation rules as PlanningAgent
"""

import json

from app.core.logging import get_logger
from app.domain.models import TestPlan, ValidationResult
from app.services.agents.planning_agent import _parse_test_plan, _plan_to_json
from app.services.gemini_client import GeminiPart, gemini_client

logger = get_logger(__name__)

_SYSTEM_PROMPT = """\
You are a Playwright test plan repair agent.

You will receive:
1. A TestPlan JSON that generated TypeScript code with validation errors
2. A list of validation issues that must be fixed

Your job is to return a corrected TestPlan JSON with the SAME schema as the input.
Fix every issue listed. Do not change anything that is already correct.

SELECTOR RULES — follow these exactly:
1. Use [data-test="x"] if a data-test attribute appears in the page elements
2. Use [data-testid="x"] if a data-testid attribute appears in the page elements
3. Use #id for elements with a unique id attribute
4. Use getByRole('role', { name: 'text' }) for buttons/links with accessible names
5. Use getByLabel('label text') for inputs with associated labels
6. ONLY use selectors visible in the provided page elements — never invent one
7. If multiple elements match, add :first-of-type or use a more specific path

NAVIGATION RULES — follow these exactly:
- Only use URLs that appear in the Navigation Links of the original page snapshot
- NEVER invent a URL that was not in the navigation links
- If a URL is unknown, click the element instead of using goto

ASYNC RULES — follow these exactly:
- After every click that triggers a page change, add wait_for_networkidle immediately after
- Never use wait_for_url unless you have seen that URL in the navigation links
- Use wait_for_visible when waiting for a specific element to appear

ASSERTION RULES:
- Always use url_contains (which maps to expect(page).toHaveURL()) for URL checks
- NEVER use a synchronous string comparison on page.url()
- Every test must have at least one assertion

Return ONLY the corrected JSON object. No markdown, no explanation, no code fences.
"""


class RepairAgent:
    """Stage 6 — repairs a TestPlan when validation finds errors."""

    async def run(self, plan: TestPlan, validation: ValidationResult) -> TestPlan:
        issue_lines = "\n".join(
            f"[{i.severity.upper()}] {i.issue_type}: {i.message}"
            + (f"\n  → {i.line_hint}" if i.line_hint else "")
            for i in validation.issues
        )

        prompt = (
            f"## Current TestPlan\n\n```json\n{_plan_to_json(plan)}\n```\n\n"
            f"## Validation Issues to Fix\n\n{issue_lines}"
        )

        parts: list[GeminiPart] = [
            GeminiPart(text=_SYSTEM_PROMPT),
            GeminiPart(text=prompt),
        ]

        raw = await gemini_client.generate(parts, json_mode=True)
        data = json.loads(raw)
        repaired = _parse_test_plan(data)

        logger.info(
            "RepairAgent: repaired plan — steps=%d assertions=%d",
            len(repaired.steps),
            len(repaired.assertions),
        )
        return repaired
