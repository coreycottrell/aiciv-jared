# Mission/Vision/Values Page Deployment — WordPress Page 929

**Date**: 2026-02-24
**Type**: operational
**Topic**: Deployed purebrain-mission-vision-values.html to WordPress as page ID 929

---

## Deployment Summary

- **Source**: `docs/from-telegram/purebrain-mission-vision-values.html` (Jared's approved version)
- **WordPress Page ID**: 929
- **Page URL**: https://purebrain.ai/mission-vision-values/
- **Template**: elementor_canvas
- **Status**: Published

---

## What Was Done

1. Read source HTML — already had `<!-- wp:html -->` / `<!-- /wp:html -->` wrapper
2. Extracted components (font links, style block, body content)
3. Added `body.tt-magic-cursor` anti-orange override (was NOT in source)
4. Deployed via WordPress REST API POST to `/wp-json/wp/v2/pages`
5. Verified 14/15 checks passed (the 1 "fail" was expected: WP strips `<!-- wp:html -->` comment markers on frontend render)

---

## Anti-Orange Override Added

Source HTML did NOT include magic-cursor override. Added before deployment:

```css
body {
  background: #0a0a0a !important;
  background-color: #0a0a0a !important;
  color: #f0f4f8 !important;
  border-color: transparent !important;
}
body.tt-magic-cursor {
  background: #0a0a0a !important;
  background-color: #0a0a0a !important;
  color: #f0f4f8 !important;
  border-color: transparent !important;
  fill: currentColor !important;
}
```

Note: page-id-929 selector NOT added at deploy time since ID wasn't known yet. Could add via plugin update.

---

## wp:html Check in Frontend

**Important**: WordPress strips `<!-- wp:html -->` comment markers when rendering frontend HTML.
This is CORRECT EXPECTED BEHAVIOR — the block is processed by Gutenberg.
To verify content stored correctly, use `?context=edit` in REST API:
```
GET /wp-json/wp/v2/pages/929?context=edit
```
Returns `content.raw` which contains the full `<!-- wp:html -->` block (33,696 chars).

---

## Page Content Sections

- Gradient strip + sticky nav (PUREBRAIN.ai logo + "Start Your Awakening" CTA)
- Hero section: "Our Mission, Vision & Values"
- Mission section with 6 phrase-cards unpacking the mission statement
- Vision section with context paragraphs
- Values section: 7 Pillars (Integrity, Accountability, Transparency, Growth, Innovation, Persistence, Love)
- Brand Promise section with 5 promise list items
- Key Differentiators section: 6 differentiator cards
- CTA section → https://purebrain.ai/#awakening
- Footer: "PureBrain makes AI personal. © 2026 Pure Technology Inc."

---

## Next Steps (Separate Tasks)

1. Footer integration — add "Mission / Vision / Values" link to site footer across all pages (needs plugin approach)
2. Homepage section — add MVV summary section BEFORE footer with "Read Full Version" button
3. Could add `body.page-id-929` override to plugin CSS for extra specificity
