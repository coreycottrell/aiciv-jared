# Audit Page Orange Fix: wpautop Bypass via wp:html Block

**Date**: 2026-02-22
**Type**: teaching
**Topic**: WordPress wpautop injecting </p> tags inside <style> blocks, causing CSS corruption (orange theme)

---

## Root Cause

WordPress's `wpautop` filter automatically wraps text in `<p>` tags. It gets confused by content
that looks like paragraphs inside `<style>` blocks, injecting `</p>` before `</style>`.

**Symptom**: `font-size: 42px; }</p>\n</style>` — stray closing `</p>` breaks the CSS,
causing the page to fall back to orange/default WordPress theme styling.

**How to diagnose**: Compare rendered vs raw content:
- `GET /wp-json/wp/v2/pages/{id}` → `content.rendered` shows the mangled version
- `GET /wp-json/wp/v2/pages/{id}?context=edit` → `content.raw` shows what was stored

If rendered has `</p></style>` but raw does not → wpautop is the culprit.

---

## Fix: Gutenberg wp:html Block

Wrap ALL content (both `<style>` and HTML body) in a Gutenberg raw HTML block:

```
<!-- wp:html -->
<style>
  ... your CSS here ...
</style>

<div id="your-wrapper">
  ... your HTML here ...
</div>
<!-- /wp:html -->
```

**Why this works**: Gutenberg's `<!-- wp:html -->` block is excluded from wpautop processing.
The block editor treats it as verbatim HTML — no paragraph injection, no filter chain.

**Previous incorrect approach**: Storing raw `<style>...<div>` content directly. WordPress applies
wpautop to ALL stored content by default, even when deployed via REST API.

---

## Deployment

- purebrain.ai Page ID 620: https://purebrain.ai/ai-partnership-audit/
- Fixed 2026-02-22, modified timestamp: 2026-02-22T12:58:28
- After deploy: `DELETE /wp-json/elementor/v1/cache` to clear Elementor cache
- Verification: page rendered 163,553 chars, 1 clean `<style>` block, no `</p>` injection

---

## Verification Pattern

```python
# Check if wpautop broke the style block
page_content = fetch_page_html(url)
has_broken_p = "</p>\n</style>" in page_content or "</p></style>" in page_content
# If True → wrap in <!-- wp:html --><!-- /wp:html --> and redeploy
```

---

## Key Rule for Future WordPress HTML Deployments

**ALWAYS use `<!-- wp:html -->` blocks** when deploying self-contained HTML pages to WordPress
via REST API. Never store raw `<style>` blocks without the wp:html wrapper.

File reference: `/home/jared/projects/AI-CIV/aether/exports/ai-partnership-audit-interactive.html`
