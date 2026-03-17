"""
app/services/page_inspector.py — Playwright page inspection

Launches a headless Chromium browser, navigates to the target URL, and captures:
  - Page title and meta description
  - A viewport screenshot (PNG bytes)
  - All interactive elements (inputs, buttons, links, selects)
  - Heading structure (h1–h3)
  - A plain-text excerpt of visible body content
"""

from app.core.config import settings
from app.core.logging import get_logger
from app.domain.models import PageElement, PageSnapshot

logger = get_logger(__name__)

# JS that extracts interactive elements from the live DOM
_EXTRACT_ELEMENTS_JS = """
() => {
    const els = [];

    // Inputs, textareas, selects
    document.querySelectorAll('input:not([type="hidden"]), textarea, select').forEach(el => {
        els.push({
            tag: el.tagName.toLowerCase(),
            type: el.getAttribute('type') || null,
            name: el.getAttribute('name') || null,
            id: el.id || null,
            placeholder: el.getAttribute('placeholder') || null,
            ariaLabel: el.getAttribute('aria-label') || null,
            testId: el.getAttribute('data-testid') || null,
            text: null,
            href: null,
            required: el.required || false,
        });
    });

    // Buttons and submit inputs
    const btnSelector = 'button, [role="button"], input[type="submit"], input[type="button"]';
    document.querySelectorAll(btnSelector).forEach(el => {
        const text = (el.innerText || el.value || '').trim().substring(0, 80);
        els.push({
            tag: 'button',
            type: el.getAttribute('type') || null,
            name: el.getAttribute('name') || null,
            id: el.id || null,
            placeholder: null,
            ariaLabel: el.getAttribute('aria-label') || null,
            testId: el.getAttribute('data-testid') || null,
            text: text || null,
            href: null,
            required: false,
        });
    });

    // Links with visible text
    document.querySelectorAll('a[href]').forEach(el => {
        const text = (el.innerText || '').trim().substring(0, 80);
        if (!text) return;
        els.push({
            tag: 'a',
            type: null,
            name: null,
            id: el.id || null,
            placeholder: null,
            ariaLabel: el.getAttribute('aria-label') || null,
            testId: el.getAttribute('data-testid') || null,
            text: text,
            href: el.href,
            required: false,
        });
    });

    return els.slice(0, 100);
}
"""

_EXTRACT_HEADINGS_JS = """
() => Array.from(document.querySelectorAll('h1, h2, h3')).map(h => ({
    level: h.tagName,
    text: (h.innerText || '').trim().substring(0, 120),
})).slice(0, 20)
"""

_EXTRACT_META_JS = """
() => {
    const m = document.querySelector('meta[name="description"]')
           || document.querySelector('meta[property="og:description"]');
    return m ? m.getAttribute('content') : null;
}
"""

_EXTRACT_BODY_TEXT_JS = """
() => {
    const body = document.body;
    if (!body) return '';
    // Remove script/style nodes for cleaner text
    const clone = body.cloneNode(true);
    clone.querySelectorAll('script, style, noscript').forEach(n => n.remove());
    return (clone.innerText || '').replace(/\\s+/g, ' ').trim().substring(0, 2000);
}
"""


class PageInspector:
    """Inspects a URL with Playwright and returns a structured PageSnapshot."""

    async def inspect_page(self, url: str) -> PageSnapshot:
        """
        Open the URL in a headless browser and extract page metadata.
        Raises RuntimeError if the page cannot be loaded.
        """
        try:
            from playwright.async_api import async_playwright  # lazy import
        except ImportError as exc:
            raise RuntimeError(
                "Playwright is not installed. "
                "Run: pip install playwright && playwright install chromium"
            ) from exc

        logger.info("Inspecting page: %s", url)

        async with async_playwright() as pw:
            browser = await pw.chromium.launch(headless=settings.PLAYWRIGHT_HEADLESS)
            context = await browser.new_context(
                viewport={"width": 1280, "height": 800},
                user_agent="Mozilla/5.0 (compatible; TestGen/1.0; +https://github.com/testgen)",
            )
            page = await context.new_page()

            try:
                await page.goto(
                    url,
                    wait_until="domcontentloaded",
                    timeout=settings.PLAYWRIGHT_TIMEOUT_MS,
                )
                # Brief pause to let JS frameworks render initial content
                await page.wait_for_timeout(1500)

                title = await page.title()
                screenshot_bytes = await page.screenshot(type="png", full_page=False)
                meta_description = await page.evaluate(_EXTRACT_META_JS)
                raw_elements = await page.evaluate(_EXTRACT_ELEMENTS_JS)
                headings = await page.evaluate(_EXTRACT_HEADINGS_JS)
                page_text = await page.evaluate(_EXTRACT_BODY_TEXT_JS)

            except Exception as exc:
                await browser.close()
                raise RuntimeError(f"Failed to load {url}: {exc}") from exc

            await browser.close()

        elements = [
            PageElement(
                tag=e.get("tag", ""),
                element_type=e.get("type"),
                text=e.get("text"),
                name=e.get("name"),
                element_id=e.get("id"),
                placeholder=e.get("placeholder"),
                aria_label=e.get("ariaLabel"),
                data_testid=e.get("testId"),
                href=e.get("href"),
                required=bool(e.get("required", False)),
            )
            for e in raw_elements
        ]

        logger.info("Page inspection complete: title=%r, elements=%d", title, len(elements))

        return PageSnapshot(
            url=url,
            title=title,
            meta_description=meta_description,
            screenshot_bytes=screenshot_bytes,
            headings=headings,
            elements=elements,
            page_text_excerpt=page_text,
        )
