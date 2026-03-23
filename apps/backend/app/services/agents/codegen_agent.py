"""
app/services/agents/codegen_agent.py — Stage 4: Code Generation

Pure template rendering — NO LLM call. Converts a structured TestPlan into
valid Playwright TypeScript. Because the output is deterministic and derived
entirely from the plan, bugs in the generated code always trace back to the
plan — which the RepairAgent can fix.
"""

import re

from app.core.logging import get_logger
from app.domain.models import TestAssertion, TestPlan, TestStep

logger = get_logger(__name__)


class CodegenAgent:
    """Stage 4 — renders a TestPlan into Playwright TypeScript. Synchronous, no LLM."""

    def run(self, plan: TestPlan) -> str:
        step_lines = "\n".join(_render_step(s) for s in plan.steps)
        assertion_lines = "\n".join(_render_assertion(a) for a in plan.assertions)

        if not assertion_lines:
            assertion_lines = "    // TODO: add assertions for this test"

        code = _FILE_TEMPLATE.format(
            test_name=plan.test_name,
            description=plan.description,
            before_each_url=plan.before_each_url,
            step_lines=step_lines,
            assertion_lines=assertion_lines,
        )

        # Append plan warnings as comments
        if plan.plan_warnings:
            warning_block = "\n".join(f"// PLAN WARNING: {w}" for w in plan.plan_warnings)
            code = code + "\n" + warning_block + "\n"

        logger.info(
            "CodegenAgent: rendered %d steps + %d assertions (%d chars)",
            len(plan.steps),
            len(plan.assertions),
            len(code),
        )
        return code


# ─── Step renderers ───────────────────────────────────────────────────────────


def _render_step(step: TestStep) -> str:
    comment = f"  // {step.description}" if step.description else ""
    renderer = _STEP_RENDERERS.get(step.action)
    if renderer is None:
        return f"  // UNKNOWN ACTION: {step.action} — skipped"
    line = renderer(step)
    return f"{line}{comment}" if comment and not line.endswith(comment) else line


def _goto(step: TestStep) -> str:
    return f"    await page.goto({_q(step.value or '')});"


def _fill(step: TestStep) -> str:
    return f"    await {_loc(step.selector)}.fill({_q(step.value or '')});"


def _click(step: TestStep) -> str:
    return f"    await {_loc(step.selector)}.click();"


def _wait_for_url(step: TestStep) -> str:
    pattern = _url_regex(step.value or "")
    return f"    await expect(page).toHaveURL({pattern});"


def _wait_for_networkidle(_: TestStep) -> str:
    return "    await page.waitForLoadState('networkidle');"


def _wait_for_visible(step: TestStep) -> str:
    return f"    await expect({_loc(step.selector)}).toBeVisible();"


def _select_option(step: TestStep) -> str:
    return f"    await {_loc(step.selector)}.selectOption({_q(step.value or '')});"


_STEP_RENDERERS = {
    "goto": _goto,
    "fill": _fill,
    "click": _click,
    "wait_for_url": _wait_for_url,
    "wait_for_networkidle": _wait_for_networkidle,
    "wait_for_visible": _wait_for_visible,
    "select_option": _select_option,
}


# ─── Assertion renderers ──────────────────────────────────────────────────────


def _render_assertion(assertion: TestAssertion) -> str:
    comment = f"  // {assertion.description}" if assertion.description else ""
    t = assertion.assertion_type

    if t == "url_contains":
        pattern = _url_regex(assertion.expected_value)
        line = f"    await expect(page).toHaveURL({pattern});"
    elif t == "element_visible":
        line = f"    await expect({_loc(assertion.selector)}).toBeVisible();"
    elif t == "not_visible":
        line = f"    await expect({_loc(assertion.selector)}).not.toBeVisible();"
    elif t == "element_text":
        line = (
            f"    await expect({_loc(assertion.selector)})"
            f".toContainText({_q(assertion.expected_value)});"
        )
    elif t == "element_count":
        line = (
            f"    await expect({_loc(assertion.selector)})"
            f".toHaveCount({assertion.expected_value});"
        )
    else:
        line = f"    // UNRECOGNISED assertion type: {t}"

    return f"{line}{comment}" if comment else line


# ─── Helpers ──────────────────────────────────────────────────────────────────


def _q(value: str) -> str:
    """Single-quote a string value, escaping inner single quotes."""
    escaped = value.replace("'", "\\'")
    return f"'{escaped}'"


def _loc(selector: str | None) -> str:
    """Wrap a selector in the appropriate Playwright locator call."""
    if not selector:
        return "page.locator('MISSING_SELECTOR')"
    # Already a Playwright helper call — use page.xxx directly
    if selector.startswith("getBy"):
        return f"page.{selector}"
    return f"page.locator({_q(selector)})"


def _url_regex(value: str) -> str:
    """Convert a URL or path fragment into a JS regex literal for toHaveURL."""
    # If it's a full URL, extract just the path portion for a flexible match
    path = re.sub(r"^https?://[^/]+", "", value).strip("/")
    if path:
        escaped = re.escape(path)
        return f"/{escaped}/"
    return f"/{re.escape(value)}/"


# ─── File template ────────────────────────────────────────────────────────────

_FILE_TEMPLATE = """\
import {{ test, expect }} from '@playwright/test';

test.describe('{test_name}', () => {{
  // {description}

  test.beforeEach(async ({{ page }}) => {{
    await page.goto('{before_each_url}');
  }});

  test('{test_name}', async ({{ page }}) => {{
{step_lines}

    // ── Assertions ──────────────────────────────────────────────────────────
{assertion_lines}
  }});
}});
"""
