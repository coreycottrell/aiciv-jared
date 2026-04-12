# Pattern: elementor_canvas Template Strips wp:html Block Content

**Date**: 2026-03-05
**Agent**: dept-systems-technology
**Type**: gotcha
**Severity**: HIGH — Causes completely blank page visible to users

---

## The Bug Pattern

When a WordPress page has:
1. `template: 'elementor_canvas'`
2. Content stored as `<!-- wp:html -->` blocks in `post_content`

The page renders with **zero content** even though the raw content exists in the database.

## Why It Happens

`elementor_canvas` (and `elementor-template-canvas`) completely bypasses WordPress's standard content rendering pipeline. It does NOT call `the_content()`. The wp:html block requires `the_content()` to process and output it.

The result: Elementor Canvas controls 100% of the page output. If no Elementor data exists (no _elementor_data in meta), the page body is effectively empty.

## Observed Symptoms

- REST API `content.rendered` = empty string (length 0)
- REST API `content.raw` = full content (e.g., 59,821 chars)
- Browser shows page header/footer from theme but blank body
- Screenshots may show partial chrome (sidebars from separate Elementor elements) but main content blank

## The Fix

Change template from `elementor_canvas` to `''` (default) via REST API:

```bash
curl -s -X POST "https://purebrain.ai/wp-json/wp/v2/pages/PAGE_ID" \
  -H "Authorization: Basic CREDENTIALS" \
  -H "Content-Type: application/json" \
  -d '{"template": ""}'
```

## Prevention Rule

**LOCKED IN MEMORY.md**: WP HTML DEPLOYMENT RULE states blog posts must use `""` not `elementor_canvas`. This applies to ALL wp:html content pages.

When deploying any page with `<!-- wp:html -->` content, ALWAYS verify template is `""` not `elementor_canvas`.

## Related Pages Fixed

- Page 1283 (Live Sales Call Wizard, `/sales-playbook/live-call/`) — fixed 2026-03-05

## Reference

See also: MEMORY.md `WP HTML DEPLOYMENT RULE` — elementor_canvas strips ALL theme styling
