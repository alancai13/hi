"""
app/services/agents/planning_agent.py — Stage 3: Planning

Converts the structured IntakeResult + live PageSnapshot into a TestPlan.
This is the core LLM reasoning step: the model decides WHAT to do (actions,
selectors, assertions) based on the actual page elements — not HOW to write code.

The plan is structured JSON so CodegenAgent can render it deterministically.
"""

import dataclasses
import json

from app.core.logging import get_logger
from app.domain.models import IntakeResult, PageSnapshot, TestAssertion, TestPlan, TestStep
from app.services.gemini_client import GeminiPart, gemini_client
from app.services.prompt_builder import _format_page_context

logger = get_logger(__name__)

_SYSTEM_PROMPT = """\
You are a senior Playwright test architect. Your job is to convert a test requirement
and a live page inspection into a structured TEST PLAN as JSON.

You will receive:
1. A structured intake (flow type, goal, entities, constraints)
2. One or more page snapshots (URL, title, interactive elements, navigation links, screenshot)

Your output must be a single JSON object with EXACTLY this schema:

{
  "test_name": "snake_case_descriptive_name",
  "description": "One sentence describing what this test verifies",
  "before_each_url": "https://full-url-to-navigate-to-before-each-test",
  "steps": [
    {
      "action": "goto|fill|click|wait_for_url|wait_for_networkidle|wait_for_visible|select_option",
      "selector": "CSS selector or Playwright locator string, or null",
      "value": "URL for goto, text for fill, option text for select_option, or null",
      "description": "Short comment for this step"
    }
  ],
  "assertions": [
    {
      "assertion_type": "url_contains|element_visible|element_text|not_visible",
      "selector": "CSS selector, or null for url_contains",
      "expected_value": "value to assert against",
      "description": "What this assertion verifies"
    }
  ],
  "plan_warnings": ["any assumptions or limitations to note"]
}

SELECTOR RULES — follow these exactly:
1. Use [data-test="x"] if a data-test attribute appears in the page elements
2. Use [data-testid="x"] if a data-testid attribute appears in the page elements
3. Use #id for elements with a unique id attribute
4. Use getByRole('role', {{ name: 'text' }}) for buttons/links with accessible names
5. Use getByLabel('label text') for inputs with associated labels
6. ONLY use selectors visible in the provided page elements — never invent one
7. If multiple elements match, add :first-of-type or use a more specific path

NAVIGATION RULES — follow these exactly:
- Only use URLs that appear in the Navigation Links section of the page snapshot
- NEVER invent a URL (e.g. /cart) that is not listed in the navigation links
- If you need to navigate after an action, find the href from the navigation links
- If the cart/checkout URL is not in the nav links, click the cart element instead of goto

ASYNC RULES — follow these exactly:
- After every click that triggers a page change or network request, add a
  wait_for_networkidle step immediately after
- NEVER use wait_for_url unless you have seen that URL in the navigation links
- Use wait_for_visible when waiting for a specific element to appear

Return ONLY the JSON object. No markdown, no explanation, no code fences.
"""


class PlanningAgent:
    """Stage 3 — produces a structured TestPlan from intake + page snapshot."""

    async def run(self, intake: IntakeResult, snapshot: PageSnapshot) -> TestPlan:
        parts: list[GeminiPart] = [GeminiPart(text=_SYSTEM_PROMPT)]

        # Page 1 context
        parts.append(GeminiPart(text=_format_page_context(snapshot, label="Page 1 (Entry URL)")))
        if snapshot.screenshot_bytes:
            parts.append(GeminiPart(text="[Screenshot of Page 1]"))
            parts.append(GeminiPart(data=snapshot.screenshot_bytes, mime_type="image/png"))

        # Additional pages (cart, product, login)
        for i, extra in enumerate(snapshot.additional_pages, start=2):
            parts.append(GeminiPart(text=_format_page_context(extra, label=f"Page {i}")))
            if extra.screenshot_bytes:
                parts.append(GeminiPart(text=f"[Screenshot of Page {i}: {extra.url}]"))
                parts.append(GeminiPart(data=extra.screenshot_bytes, mime_type="image/png"))

        # Intake
        parts.append(GeminiPart(text=_format_intake(intake)))

        raw = await gemini_client.generate(parts, json_mode=True)
        data = json.loads(raw)
        plan = _parse_test_plan(data)
        logger.info(
            "PlanningAgent: test_name=%r steps=%d assertions=%d warnings=%d",
            plan.test_name,
            len(plan.steps),
            len(plan.assertions),
            len(plan.plan_warnings),
        )
        return plan


# ─── Shared helpers (also used by RepairAgent) ────────────────────────────────


def _parse_test_plan(data: dict) -> TestPlan:
    """Convert a raw JSON dict into a typed TestPlan. Tolerant of missing fields."""
    steps = []
    for s in data.get("steps", []):
        action = s.get("action", "")
        if action not in {
            "goto",
            "fill",
            "click",
            "wait_for_url",
            "wait_for_networkidle",
            "wait_for_visible",
            "select_option",
        }:
            continue  # skip unknown actions silently
        steps.append(
            TestStep(
                action=action,
                selector=s.get("selector"),
                value=s.get("value"),
                description=s.get("description", ""),
            )
        )

    assertions = []
    for a in data.get("assertions", []):
        assertions.append(
            TestAssertion(
                assertion_type=a.get("assertion_type", "element_visible"),
                selector=a.get("selector"),
                expected_value=str(a.get("expected_value", "")),
                description=a.get("description", ""),
            )
        )

    return TestPlan(
        test_name=data.get("test_name", "generated_test"),
        description=data.get("description", ""),
        before_each_url=data.get("before_each_url", ""),
        steps=steps,
        assertions=assertions,
        plan_warnings=data.get("plan_warnings", []),
    )


def _plan_to_json(plan: TestPlan) -> str:
    """Serialise a TestPlan to JSON for the RepairAgent prompt."""
    return json.dumps(dataclasses.asdict(plan), indent=2)


def _format_intake(intake: IntakeResult) -> str:
    lines = [
        "## Test Requirement (Intake)\n",
        f"**Flow type:** {intake.flow_type}",
        f"**Goal:** {intake.goal}",
    ]
    if intake.entities:
        lines.append(f"**Key entities:** {', '.join(intake.entities)}")
    if intake.constraints:
        lines.append(f"**Constraints:** {', '.join(intake.constraints)}")
    if intake.requires_auth:
        lines.append("**Requires auth:** yes — use placeholder credentials")
    if intake.multi_page:
        lines.append("**Multi-page flow:** yes — the test spans more than one URL")
    return "\n".join(lines)
