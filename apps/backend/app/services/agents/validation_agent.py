"""
app/services/agents/validation_agent.py — Stage 5: Validation

Static analysis of rendered Playwright TypeScript — NO LLM call.
Catches common generation mistakes so RepairAgent can fix the plan
before the code is returned to the user.
"""

import re

from app.core.logging import get_logger
from app.domain.models import ValidationIssue, ValidationResult

logger = get_logger(__name__)

# Minimum character count for a plausible test file
_MIN_CODE_LENGTH = 100


class ValidationAgent:
    """Stage 5 — static analysis of generated TypeScript. Synchronous, no LLM."""

    def run(self, code: str) -> ValidationResult:
        issues: list[ValidationIssue] = []

        _check_length(code, issues)
        _check_no_assertions(code, issues)
        _check_sync_url_assert(code, issues)
        _check_hardcoded_sleep(code, issues)
        _check_broad_locator(code, issues)
        _check_missing_wait_after_mutation(code, issues)
        _check_missing_selector(code, issues)
        _check_unknown_action(code, issues)

        passed = not any(i.severity == "error" for i in issues)
        logger.info(
            "ValidationAgent: passed=%s issues=%d (errors=%d warnings=%d)",
            passed,
            len(issues),
            sum(1 for i in issues if i.severity == "error"),
            sum(1 for i in issues if i.severity == "warning"),
        )
        return ValidationResult(passed=passed, issues=issues)


# ─── Individual checks ────────────────────────────────────────────────────────


def _check_length(code: str, issues: list[ValidationIssue]) -> None:
    if len(code) < _MIN_CODE_LENGTH:
        issues.append(
            ValidationIssue(
                issue_type="too_short",
                severity="error",
                message=(
                    f"Generated code is suspiciously short "
                    f"({len(code)} chars < {_MIN_CODE_LENGTH})"
                ),
            )
        )


def _check_no_assertions(code: str, issues: list[ValidationIssue]) -> None:
    # Must have at least one expect() call (excluding TODO comments)
    has_expect = bool(re.search(r"\bexpect\s*\(", code))
    if not has_expect:
        issues.append(
            ValidationIssue(
                issue_type="no_assertions",
                severity="error",
                message="No expect() assertions found — the test cannot verify anything",
            )
        )


def _check_sync_url_assert(code: str, issues: list[ValidationIssue]) -> None:
    # expect(page.url()) is synchronous and always passes — must use toHaveURL
    for i, line in enumerate(code.splitlines(), start=1):
        if re.search(r"expect\s*\(\s*page\.url\s*\(\s*\)", line):
            issues.append(
                ValidationIssue(
                    issue_type="sync_url_assert",
                    severity="error",
                    message=(
                        "expect(page.url()) is a synchronous string check and "
                        "will not wait for navigation — use expect(page).toHaveURL(...) instead"
                    ),
                    line_hint=f"line {i}: {line.strip()}",
                )
            )


def _check_hardcoded_sleep(code: str, issues: list[ValidationIssue]) -> None:
    for i, line in enumerate(code.splitlines(), start=1):
        if re.search(r"page\.waitForTimeout\s*\(", line):
            issues.append(
                ValidationIssue(
                    issue_type="hardcoded_sleep",
                    severity="warning",
                    message=(
                        "page.waitForTimeout() is a time-based sleep — "
                        "replace with waitForLoadState or expect(...).toBeVisible()"
                    ),
                    line_hint=f"line {i}: {line.strip()}",
                )
            )


def _check_broad_locator(code: str, issues: list[ValidationIssue]) -> None:
    """Flag locators that match many elements and will fail in strict mode."""
    broad_patterns = [
        (r"page\.locator\s*\(\s*'a'\s*\)", "page.locator('a')"),
        (r'page\.locator\s*\(\s*"a"\s*\)', 'page.locator("a")'),
        (r"page\.locator\s*\(\s*'button'\s*\)", "page.locator('button')"),
        (r'page\.locator\s*\(\s*"button"\s*\)', 'page.locator("button")'),
        (r"page\.locator\s*\(\s*'input'\s*\)", "page.locator('input')"),
        (r'page\.locator\s*\(\s*"input"\s*\)', 'page.locator("input")'),
    ]
    for i, line in enumerate(code.splitlines(), start=1):
        for pattern, label in broad_patterns:
            if re.search(pattern, line):
                issues.append(
                    ValidationIssue(
                        issue_type="broad_locator",
                        severity="error",
                        message=(
                            f"{label} matches multiple elements and will fail in strict mode — "
                            "use a more specific selector or add .first()"
                        ),
                        line_hint=f"line {i}: {line.strip()}",
                    )
                )
                break  # one issue per line is enough


def _check_missing_wait_after_mutation(code: str, issues: list[ValidationIssue]) -> None:
    """Warn when a .click() or .fill() + .press('Enter') has no wait immediately after."""
    lines = code.splitlines()
    for i, line in enumerate(lines):
        stripped = line.strip()
        is_mutation = bool(
            re.search(r"\.click\s*\(\s*\)", stripped)
            or re.search(r"\.press\s*\(\s*'Enter'\s*\)", stripped)
        )
        if not is_mutation:
            continue
        # Look at the next non-blank line
        next_line = ""
        for j in range(i + 1, min(i + 4, len(lines))):
            candidate = lines[j].strip()
            if candidate:
                next_line = candidate
                break
        has_wait = bool(
            re.search(
                r"waitForLoadState|waitForNavigation|waitForURL|toHaveURL|toBeVisible",
                next_line,
            )
        )
        if not has_wait:
            issues.append(
                ValidationIssue(
                    issue_type="missing_wait",
                    severity="warning",
                    message=(
                        "click() / press('Enter') with no wait_for_networkidle or "
                        "expect().toBeVisible() immediately after — test may be flaky"
                    ),
                    line_hint=f"line {i + 1}: {stripped}",
                )
            )


def _check_missing_selector(code: str, issues: list[ValidationIssue]) -> None:
    for i, line in enumerate(code.splitlines(), start=1):
        if "MISSING_SELECTOR" in line:
            issues.append(
                ValidationIssue(
                    issue_type="missing_selector",
                    severity="error",
                    message=(
                        "Placeholder MISSING_SELECTOR was not resolved "
                        "— the plan is missing a selector"
                    ),
                    line_hint=f"line {i}: {line.strip()}",
                )
            )


def _check_unknown_action(code: str, issues: list[ValidationIssue]) -> None:
    for i, line in enumerate(code.splitlines(), start=1):
        if "UNKNOWN ACTION:" in line:
            issues.append(
                ValidationIssue(
                    issue_type="unknown_action",
                    severity="error",
                    message=(
                        f"Plan contained an unrecognised action that was skipped: {line.strip()}"
                    ),
                    line_hint=f"line {i}: {line.strip()}",
                )
            )
