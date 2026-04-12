# Memory: Comparison/Exodus Pages Orange Fix (IDs 752-760)

**Date**: 2026-02-23
**Type**: operational
**Agent**: full-stack-developer
**Topic**: Fix all-orange styling on 9 competitor comparison pages - same root cause as calculator page 777

---

## Root Cause

All 9 comparison/exodus pages (752-760) were deployed as complete HTML documents
(`<!DOCTYPE html><html><head>...<body>`) inside `<!-- wp:html -->` blocks.

This creates nested `<html>` tags in the browser. WordPress theme's body/background CSS
wins over our dark theme CSS because theme rules load earlier in DOM order.

**Symptom**: Pages appear "all orange" - WP theme's orange accent colors survive,
our dark background (#080a12) is overridden.

---

## Pages Fixed

| ID | Slug | Status |
|----|------|--------|
| 752 | /compare/ | Fixed HTTP 200 |
| 753 | /purebrain-vs-chatgpt/ | Fixed HTTP 200 |
| 754 | /purebrain-vs-claude/ | Fixed HTTP 200 |
| 755 | /purebrain-vs-copilot/ | Fixed HTTP 200 |
| 756 | /purebrain-vs-custom-gpts/ | Fixed HTTP 200 |
| 757 | /purebrain-vs-deepseek/ | Fixed HTTP 200 |
| 758 | /purebrain-vs-gemini/ | Fixed HTTP 200 |
| 759 | /purebrain-vs-jasper/ | Fixed HTTP 200 |
| 760 | /purebrain-vs-perplexity/ | Fixed HTTP 200 |

---

## Fix Applied

For each page:
1. GET content via REST API with `context=edit`
2. Strip `<!-- wp:html -->` wrappers
3. Extract all `<style>` blocks and body content (between `<body>` and `</body>`)
4. Inject WordPress override at TOP of first style block:

```css
/* WordPress Dark Theme Override */
html, body, body.page {
  background: #080a12 !important;
  background-color: #080a12 !important;
  color: #e8edf3 !important;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, sans-serif !important;
}
```

5. Re-wrap in `<!-- wp:html -->` with NO DOCTYPE/html/head/body tags
6. POST back via REST API
7. Cleared Elementor cache after all 9 pages

---

## Verification

Checked pages 752, 753, 760 via REST API:
- DOCTYPE present: False (correct)
- `<html>` tag count: 0 (correct)
- body.page override: True (correct)
- wp:html wrapped: True (correct)
- Full CSS preserved: Yes (17,725 chars on page 753 alone)

---

## Key Technical Notes

- Pages use `--pb-blue`, `--pb-orange`, `--pb-dark` CSS vars (not `--exo-*` as originally thought)
- User-Agent header required: `Mozilla/5.0 (compatible; Aether-AI/1.0)` to bypass Cloudflare 403
- Script location: `/tmp/fix_comparison_pages.py` (reusable pattern)
- Always clear Elementor cache after batch: `DELETE /wp-json/elementor/v1/cache`

---

## Pattern: When to Apply This Fix

Any page deployed as a complete HTML document inside wp:html will show this bug.
Fix pattern documented in: `2026-02-23--calculator-page-nested-html-fix.md`

**Prevention**: When deploying HTML files to WordPress, ALWAYS strip DOCTYPE/html/head
before wrapping in wp:html block.
