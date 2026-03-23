"""
app/services/page_inspector.py — Playwright page inspection

Launches a headless Chromium browser, navigates to the target URL, and captures:
  - Page title and meta description
  - A viewport screenshot (PNG bytes)
  - All interactive elements (inputs, buttons, links, selects)
  - Heading structure (h1–h3)
  - A plain-text excerpt of visible body content
  - Navigation links from the header/nav
  - Additional key pages (cart/checkout, first product, login) for richer context
"""

import re
from urllib.parse import urljoin, urlparse

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
            testId: el.getAttribute('data-testid') || el.getAttribute('data-test') || null,
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
            testId: el.getAttribute('data-testid') || el.getAttribute('data-test') || null,
            text: text || null,
            href: null,
            required: false,
        });
    });

    // Links — include icon-only nav links (cart, account) even without visible text
    document.querySelectorAll('a[href]').forEach(el => {
        const text = (el.innerText || '').trim().substring(0, 80);
        const ariaLabel = el.getAttribute('aria-label') || null;
        const testId = el.getAttribute('data-testid') || el.getAttribute('data-test') || null;
        const href = el.href || '';
        const isNavLink = /cart|checkout|basket|account|login|auth/i.test(href);
        if (!text && !ariaLabel && !testId && !isNavLink) return;
        els.push({
            tag: 'a',
            type: null,
            name: null,
            id: el.id || null,
            placeholder: null,
            ariaLabel: ariaLabel,
            testId: testId,
            text: text || null,
            href: href,
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

_EXTRACT_NAV_LINKS_JS = """
() => {
    const seen = new Set();
    const links = [];
    const selectors = ['nav a[href]', 'header a[href]', '[class*="nav"] a[href]',
                       '[class*="menu"] a[href]', '[class*="header"] a[href]'];
    selectors.forEach(sel => {
        document.querySelectorAll(sel).forEach(el => {
            const href = el.getAttribute('href') || '';
            if (!href || href === '#' || seen.has(href)) return;
            seen.add(href);
            const text = (el.innerText || el.getAttribute('aria-label') || '').trim()
                           .substring(0, 60);
            links.push({ text: text || null, href });
        });
    });
    return links.slice(0, 40);
}
"""

_EXTRACT_BODY_TEXT_JS = """
() => {
    const body = document.body;
    if (!body) return '';
    const clone = body.cloneNode(true);
    clone.querySelectorAll('script, style, noscript').forEach(n => n.remove());
    return (clone.innerText || '').replace(/\\s+/g, ' ').trim().substring(0, 2000);
}
"""

# Patterns that identify key pages worth following
_CART_PATTERN = re.compile(r"cart|checkout|basket|bag", re.I)
_PRODUCT_PATTERN = re.compile(r"/product/|/item/|/p/|/shop/", re.I)
_AUTH_PATTERN = re.compile(r"login|signin|sign-in|auth", re.I)


class PageInspector:
    """Inspects a URL with Playwright and returns a structured PageSnapshot."""

    async def inspect_page(self, url: str) -> PageSnapshot:
        """
        Open the URL in a headless browser, capture the main page, then follow
        up to 3 key linked pages (cart/checkout, first product, login) to give
        the model a richer view of the app's routing and element structure.
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
                user_agent=("Mozilla/5.0 (compatible; TestGen/1.0; +https://github.com/testgen)"),
            )
            page = await context.new_page()

            try:
                main_snapshot = await self._capture(page, url)
                additional = await self._follow_key_pages(page, url, main_snapshot.nav_links)
            except Exception as exc:
                await browser.close()
                raise RuntimeError(f"Failed to load {url}: {exc}") from exc

            await browser.close()

        main_snapshot.additional_pages = additional
        logger.info(
            "Inspection complete: title=%r elements=%d additional_pages=%d",
            main_snapshot.title,
            len(main_snapshot.elements),
            len(additional),
        )
        return main_snapshot

    # ── Private helpers ────────────────────────────────────────────────────────

    async def _capture(self, page, url: str) -> PageSnapshot:
        """Navigate to url and capture a full PageSnapshot."""
        await page.goto(url, wait_until="domcontentloaded", timeout=settings.PLAYWRIGHT_TIMEOUT_MS)
        await page.wait_for_timeout(1500)

        title = await page.title()
        screenshot_bytes = await page.screenshot(type="png", full_page=False)
        meta_description = await page.evaluate(_EXTRACT_META_JS)
        raw_elements = await page.evaluate(_EXTRACT_ELEMENTS_JS)
        headings = await page.evaluate(_EXTRACT_HEADINGS_JS)
        page_text = await page.evaluate(_EXTRACT_BODY_TEXT_JS)
        nav_links = await page.evaluate(_EXTRACT_NAV_LINKS_JS)

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

        return PageSnapshot(
            url=url,
            title=title,
            meta_description=meta_description,
            screenshot_bytes=screenshot_bytes,
            headings=headings,
            elements=elements,
            page_text_excerpt=page_text,
            nav_links=nav_links,
        )

    async def _follow_key_pages(
        self, page, base_url: str, nav_links: list[dict]
    ) -> list[PageSnapshot]:
        """
        Identify and visit up to 3 key pages linked from the main page:
          1. Cart / checkout page (highest priority — needed for purchase flows)
          2. First product page  (needed for add-to-cart flows)
          3. Login / auth page   (needed for authentication flows)
        """
        base_origin = urlparse(base_url).scheme + "://" + urlparse(base_url).netloc
        visited: set[str] = {base_url}
        queue: list[tuple[int, str]] = []  # (priority, url) — lower = higher priority

        # Score nav links by category
        for link in nav_links:
            href = link.get("href", "")
            if not href or href.startswith("mailto:") or href.startswith("tel:"):
                continue
            full = urljoin(base_origin, href)
            if urlparse(full).netloc != urlparse(base_origin).netloc:
                continue  # skip external links
            if _CART_PATTERN.search(full):
                queue.append((1, full))
            elif _AUTH_PATTERN.search(full):
                queue.append((3, full))

        # Also look for the first product link in the DOM
        first_product_href = await page.evaluate(
            """
            () => {
                const patterns = ['/product/', '/item/', '/p/', '/shop/'];
                for (const p of patterns) {
                    const a = document.querySelector(`a[href*="${p}"]`);
                    if (a) return a.href;
                }
                return null;
            }
        """
        )
        if first_product_href:
            queue.append((2, first_product_href))

        # Visit up to 3 unique pages in priority order
        queue.sort(key=lambda x: x[0])
        snapshots: list[PageSnapshot] = []
        for _, url in queue:
            if url in visited or len(snapshots) >= 3:
                break
            visited.add(url)
            try:
                logger.info("Following key page: %s", url)
                snap = await self._capture(page, url)
                snapshots.append(snap)
            except Exception as exc:
                logger.warning("Could not capture %s: %s", url, exc)

        return snapshots
