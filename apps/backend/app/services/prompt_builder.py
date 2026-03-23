"""
app/services/prompt_builder.py — Builds the Gemini generation prompt

Assembles all available context into a structured prompt:
  - Page metadata (title, URL, meta description)
  - Interactive elements extracted by Playwright
  - Plain-text page excerpt
  - User requirements / acceptance criteria
  - Content from uploaded requirement documents
  - Visual references (page screenshot + user-uploaded screenshots)

Returns a list of GeminiPart objects ready to send to GeminiClient.
"""

from app.core.logging import get_logger
from app.domain.models import GenerationJob, PageSnapshot
from app.services.gemini_client import GeminiPart

logger = get_logger(__name__)

# Selector strategy guide injected into every prompt
_SELECTOR_GUIDE = """\
Selector priority (most stable → least stable):
  1. page.locator('[data-test="value"]')   ← data-test attribute (common in Angular/Vue apps)
  2. page.getByTestId('value')             ← data-testid attribute
  3. page.getByRole('role', {name})        ← ARIA role + accessible name
  4. page.getByLabel('label')              ← associated <label> text
  5. page.getByPlaceholder('text')         ← placeholder attribute
  6. page.getByText('text')                ← visible text (buttons, links)
  7. page.locator('#id')                   ← unique id attribute
  8. page.locator('[name="x"]')            ← name attribute (forms)
  9. page.locator('css-selector')          ← CSS (last resort)\
"""


def build_parts(job: GenerationJob, snapshot: PageSnapshot) -> list[GeminiPart]:
    """
    Assemble the full multimodal prompt for Playwright test generation.

    Returns a list of GeminiPart(text=...) and GeminiPart(data=...) items.
    Text parts are structured as a readable prompt; image parts follow inline.
    """
    parts: list[GeminiPart] = []

    # ── System instruction ────────────────────────────────────────────────────
    parts.append(GeminiPart(text=_SYSTEM_INSTRUCTION))

    # ── Target page context ───────────────────────────────────────────────────
    parts.append(GeminiPart(text=_format_page_context(snapshot, label="Page 1 (Entry URL)")))

    # ── Additional pages (cart, product, login) ───────────────────────────────
    for i, extra in enumerate(snapshot.additional_pages, start=2):
        parts.append(GeminiPart(text=_format_page_context(extra, label=f"Page {i}")))
        if extra.screenshot_bytes:
            parts.append(GeminiPart(text=f"[Screenshot of Page {i}: {extra.url}]"))
            parts.append(GeminiPart(data=extra.screenshot_bytes, mime_type="image/png"))

    # ── Page screenshot ───────────────────────────────────────────────────────
    if snapshot.screenshot_bytes:
        parts.append(
            GeminiPart(
                text="[Page screenshot — use this to understand the layout and identify elements]"
            )
        )
        parts.append(GeminiPart(data=snapshot.screenshot_bytes, mime_type="image/png"))
    else:
        parts.append(GeminiPart(text="[No page screenshot available]"))

    # ── Test requirements ─────────────────────────────────────────────────────
    if job.input and job.input.requirements.strip():
        parts.append(GeminiPart(text=f"## Test Requirements\n\n{job.input.requirements.strip()}"))
    else:
        parts.append(
            GeminiPart(
                text=(
                    "## Test Requirements\n\n"
                    "No explicit requirements were provided. "
                    "Analyse the page and generate comprehensive tests covering:\n"
                    "- Core user flows visible on the page\n"
                    "- Form validation (if forms exist)\n"
                    "- Navigation and link behaviour\n"
                    "- Key assertions for visible content"
                )
            )
        )

    # ── Uploaded requirement documents ────────────────────────────────────────
    doc_parts = _format_requirement_docs(job)
    if doc_parts:
        parts.append(GeminiPart(text=f"## Uploaded Requirement Documents\n\n{doc_parts}"))

    # ── User-uploaded screenshots ─────────────────────────────────────────────
    if job.screenshots:
        parts.append(
            GeminiPart(
                text=f"## User-Provided Screenshots ({len(job.screenshots)} image(s))\n"
                "These are reference screenshots provided by the tester:"
            )
        )
        for shot in job.screenshots:
            if shot.is_image:
                parts.append(GeminiPart(text=f"[Screenshot: {shot.filename}]"))
                parts.append(GeminiPart(data=shot.data, mime_type=shot.content_type))

    # ── Generation instructions ───────────────────────────────────────────────
    parts.append(GeminiPart(text=_generation_instructions(job)))

    return parts


# ─── Formatters ───────────────────────────────────────────────────────────────


def _format_page_context(snapshot: PageSnapshot, label: str = "Target Page") -> str:
    lines = [f"## {label}\n"]
    lines.append(f"**URL:** {snapshot.url}")
    lines.append(f"**Title:** {snapshot.title}")

    if snapshot.meta_description:
        lines.append(f"**Description:** {snapshot.meta_description}")

    if snapshot.headings:
        lines.append("\n### Page Structure (headings)")
        for h in snapshot.headings:
            indent = "  " * (int(h["level"].replace("H", "")) - 1)
            lines.append(f"{indent}{h['level']}: {h['text']}")

    if snapshot.elements:
        lines.append("\n### Interactive Elements Found by Playwright")
        lines.append("(Use these to write accurate selectors)\n")
        for el in snapshot.elements:
            lines.append(_format_element(el))

    if snapshot.nav_links:
        lines.append("\n### Navigation Links (from nav/header — use these for routing)")
        lines.append("These are the ACTUAL hrefs in the page nav. Use them for goto() calls.")
        for link in snapshot.nav_links:
            text = link.get("text") or "(no text)"
            href = link.get("href", "")
            lines.append(f"  {text}  →  {href}")

    if snapshot.page_text_excerpt:
        lines.append("\n### Visible Page Text (excerpt)")
        lines.append(snapshot.page_text_excerpt[:1500])

    return "\n".join(lines)


def _format_element(el) -> str:  # el: PageElement
    parts = [f"<{el.tag}>"]
    if el.element_type:
        parts.append(f"type={el.element_type!r}")
    if el.data_testid:
        parts.append(f"data-testid={el.data_testid!r}  ← prefer this selector")
    if el.element_id:
        parts.append(f"id={el.element_id!r}")
    if el.name:
        parts.append(f"name={el.name!r}")
    if el.aria_label:
        parts.append(f"aria-label={el.aria_label!r}")
    if el.placeholder:
        parts.append(f"placeholder={el.placeholder!r}")
    if el.text:
        parts.append(f"text={el.text!r}")
    if el.required:
        parts.append("required")
    if el.href:
        parts.append(f"href={el.href!r}")
    return "  " + "  ".join(parts)


def _format_requirement_docs(job: GenerationJob) -> str:
    sections = []
    for f in job.requirement_files:
        text = f.text_content
        if text:
            sections.append(f"### {f.filename}\n{text[:3000]}")
        else:
            sections.append(
                f"### {f.filename}\n"
                f"[Binary file — {f.content_type}. "
                "Text extraction for PDF/DOCX is not yet implemented; "
                "use the visual context and requirements text above.]"
            )
    return "\n\n".join(sections)


def _generation_instructions(job: GenerationJob) -> str:
    fmt = job.input.output_format.value if job.input else "playwright"
    return f"""## Generation Instructions

Generate a complete, production-ready **{fmt}** test file.

{_SELECTOR_GUIDE}

Rules:
- Import only from `@playwright/test`
- Use `test.describe()` to group related tests
- Use `test.beforeEach()` for navigation that applies to all tests
- Every `test()` block must have a clear, human-readable name
- Every assertion must use `expect()`
- Add a short comment above any non-obvious step
- If multiple user flows exist, create one `test()` per flow
- Do NOT hardcode credentials — use placeholder values like `'testuser@example.com'`
- Do NOT use `page.waitForTimeout()` for timing — use proper `waitFor` methods
- ALWAYS use `await expect(page).toHaveURL(...)` for URL assertions — NEVER use the synchronous
  `expect(page.url()).toContain(...)` which runs once and does not retry

Selector strictness rules (CRITICAL — Playwright throws if a locator matches multiple elements):
- NEVER use a locator that could match more than one element without calling `.first()`, `.nth(n)`,
  or narrowing with `.filter()`
- When selecting from a list of results (search results, product cards, table rows), ALWAYS scope
  to a specific card element first: e.g. `page.locator('.card').first()` not `page.getByText('...')`
- Only use `page.getByTestId()` or `data-testid` selectors if `data-testid` attributes are present
  in the page elements provided above — do NOT assume they exist
- Only use `page.locator('[data-test="x"]')` if `data-test` attributes are present in the elements
- When using getByRole('link', {{ name: '...' }}), the name must EXACTLY match the link's
  accessible text including capitalisation — check the elements list above for the exact text

Navigation and async rules (CRITICAL — these cause flaky tests if ignored):
- After ANY mutating action (add to cart, submit form, delete, etc.) ALWAYS await
  `page.waitForLoadState('networkidle')` or `expect(element).toBeVisible()` before navigating away
- NEVER rely on transient UI elements (toasts, snackbars, notification popups) for navigation —
  they disappear too fast; instead navigate directly with `page.goto('/path')` or click a
  persistent link
- NEVER invent a URL. Only use hrefs that appear in the Navigation Links section above.
  If no cart/checkout href is listed there, click the cart icon element instead of guessing a path.
  Do NOT write page.goto('/cart') or any path you have not seen in the navigation links.
- If you genuinely cannot determine a URL or selector, omit that step and leave a clear
  `// MANUAL: could not determine URL for checkout — add href from Navigation Links above` comment.
  Do NOT substitute an unrelated page (e.g. /auth/login) as a workaround.
- After clicking "Add to cart" or similar async actions, wait for confirmation before proceeding:
  e.g. `await expect(page.locator('[data-test="cart-quantity"]')).not.toHaveText('0')`

Output format:
- Return ONLY valid TypeScript code
- Start the file with `import {{ test, expect }} from '@playwright/test';`
- Do NOT wrap in markdown code fences
- Do NOT add any explanation text before or after the code
"""


_SYSTEM_INSTRUCTION = """\
You are a world-class test automation engineer specialising in Playwright with TypeScript.

Your task: generate a complete, production-ready Playwright test file that faithfully tests
the requirements described below, using the page analysis and visual context provided.

You have access to:
1. The live page structure extracted by Playwright (elements, selectors, headings)
2. A screenshot of the page's current state
3. The user's test requirements and uploaded reference materials

Non-negotiable quality rules:
- Every locator must be STRICT — it must match exactly one element. If a selector could match
  multiple elements, narrow it with .first(), .nth(), or .filter() before interacting.
- Never depend on toasts or transient popups for navigation — navigate directly.
- Always wait for async side-effects (cart updates, form submissions) to settle before
  moving to the next step. Use waitForLoadState('networkidle') or targeted expect() assertions.
- Only reference URLs you have evidence for from the page snapshot. Do not invent routes.
- If a required URL or element is not in the snapshot, follow a visible link/button to get there
  rather than guessing. If truly unknown, leave a `// TODO: verify this URL` comment — NEVER
  substitute an unrelated page (e.g. navigating to /auth/login when you meant /checkout).

Write tests that a professional QA engineer would be proud to commit.
"""
