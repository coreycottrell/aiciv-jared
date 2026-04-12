# Site-Wide Dark Background — Plugin v4.6.6

**Date**: 2026-02-27
**Type**: deployment + pattern
**Agent**: dept-systems-technology (ST#)

## What Changed (v4.6.5 → v4.6.6)

**v4.6.5**: Dark bg (#080a12) was scoped to `body.page-id-777` only (calculator page).
**v4.6.6**: Dark bg is now SITE-WIDE — all pages, no page-id scoping.

Jared's rule (locked in 2026-02-27):
> "NO page on purebrain.ai should ever show an orange background."

## Implementation

Layer 1 (wp_head priority 1) — fires before ALL CSS:
```css
html, body {
    background: #080a12 !important;
    background-color: #080a12 !important;
}
```

Layer 2 (wp_head priority 999) — fires after ALL CSS:
```css
html body,
html body.elementor-default,
... (full selector list for maximum specificity) ...
{
    background: #080a12 !important;
}
/* Blog posts keep their own dark bg (#0a0a0f) — don't override */
html body.single-post { background: unset !important; }
```

Layer 3 — JS at DOMContentLoaded + load + 500ms/1500ms delays:
```javascript
b.style.setProperty('background', '#080a12', 'important');
```

Blog posts (body.single-post) explicitly excluded — they use Additional CSS dark bg system.

## Deployment Pattern

- Script: `/home/jared/projects/AI-CIV/aether/tools/security/deploy_plugin_v466_sitewide_dark_bg.py`
- Method: Playwright → WP Plugin Editor (CodeMirror) → Save
- Cache: Elementor cache clear attempted (HTTP 403 = fine, WP already invalidated)
- Version verified via WP REST API: `GET /wp-json/wp/v2/plugins` → check `version`

## Verification Results

All checks passed:
- Homepage (purebrain.ai): Layer1/2/3 present, #080a12 in HEAD
- Calculator (/ai-tool-stack-calculator/): all layers present
- Blog listing (/blog/): layers present
- Blog post spot-check: dark bg still present, not broken by global rule
- REST API version confirmed: 4.6.6

## Future Reference

When expanding the dark bg scope:
1. Remove `is_page(777)` or similar guards from existing scoped rules
2. Change `body.page-id-XXX` selectors to `html, body` for global application
3. Always add explicit EXCLUSION for body.single-post if they have their own bg system
4. Verify every major page type after deployment (homepage, calculator, blog listing, blog post)
5. REST API version check = fastest way to confirm deployment landed
