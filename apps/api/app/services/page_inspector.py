"""
app/services/page_inspector.py — Page inspection service

Responsible for opening a URL with Playwright, capturing page structure,
and returning a PageSnapshot with candidate interactive elements.

STATUS: Stub — not implemented.

TODO (Phase 1):
  - Install playwright: `pip install playwright && playwright install chromium`
  - Implement inspect_page() using async Playwright API
  - Extract: title, forms, buttons, links, inputs, ARIA roles, data-testid attributes
  - Rank SelectorCandidates by stability (data-testid > aria-role > text > css)
  - Handle: SPAs (wait for network idle), auth-gated pages, timeouts
"""

from app.core.logging import get_logger
from app.domain.models import PageSnapshot, SelectorCandidate, SelectorStrategy

logger = get_logger(__name__)


class PageInspector:
    """
    Inspects a target URL and returns a structured snapshot of its UI.

    Future implementation will use Playwright to:
    1. Navigate to the URL
    2. Wait for the page to be interactive
    3. Extract all relevant interactive elements
    4. Propose stable selectors for each element
    """

    async def inspect_page(self, url: str) -> PageSnapshot:
        """
        Open the given URL with a headless browser and capture page metadata.

        Args:
            url: The fully-qualified URL to inspect.

        Returns:
            PageSnapshot with title, interactive elements, and selector candidates.

        TODO: Implement using Playwright async API.
        """
        logger.info("inspect_page() called for %s — not yet implemented, returning stub", url)

        # ── Stub response ─────────────────────────────────────────────────────
        # Returns a placeholder snapshot so the pipeline can be wired up
        # without a real browser. Replace with real Playwright logic.
        return PageSnapshot(
            url=url,
            title="[Stub] Page title not yet fetched",
            interactive_elements=[
                SelectorCandidate(
                    element_type="input",
                    visible_text=None,
                    selector='[name="email"]',
                    strategy=SelectorStrategy.css_id,
                    confidence=0.8,
                    attributes={"type": "email", "name": "email"},
                ),
                SelectorCandidate(
                    element_type="input",
                    visible_text=None,
                    selector='[name="password"]',
                    strategy=SelectorStrategy.css_id,
                    confidence=0.8,
                    attributes={"type": "password", "name": "password"},
                ),
                SelectorCandidate(
                    element_type="button",
                    visible_text="Log in",
                    selector="button:has-text('Log in')",
                    strategy=SelectorStrategy.text,
                    confidence=0.5,
                    attributes={"type": "submit"},
                ),
            ],
        )

    # TODO: Add helper methods:
    # async def _get_forms(self, page) -> list[dict]: ...
    # async def _get_buttons(self, page) -> list[SelectorCandidate]: ...
    # async def _get_inputs(self, page) -> list[SelectorCandidate]: ...
    # def _rank_selector(self, element) -> SelectorStrategy: ...
