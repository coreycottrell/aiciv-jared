# CTO: Video Background Transparent Override Pattern

**Date**: 2026-03-05
**Type**: teaching, operational
**Topic**: tt-magic-cursor body background blocks fixed-position video elements

## Root Cause

The PureBrain Security Plugin's `pb-magic-cursor-body-override` CSS block applies:
```css
body.tt-magic-cursor {
    background-color: #0a0e1a !important;
}
```

This fires on **every page** that has the tt-magic-cursor class on body. It creates a solid body background, which covers `.video-background { position: fixed; z-index: -1 }` elements — they exist but are visually blocked.

## The Fix Pattern

Any page that has a fixed-position video background element (z-index: -1) needs a transparent override in the `pb-magic-cursor-body-override` style block:

```css
body.page-id-XXX.tt-magic-cursor {
    background: transparent !important;
    background-color: transparent !important;
}
```

Pages that needed this (as of v6.2.2):
- `body.home.tt-magic-cursor` (homepage, page ID 11)
- `body.page-id-689.tt-magic-cursor` (pay-test-2)
- `body.page-id-688.tt-magic-cursor` (pay-test-sandbox-2)
- `body.page-id-1232.tt-magic-cursor` (pay-test-sandbox-3)
- `body.page-id-319.tt-magic-cursor` (blog/)
- `body.single-post.tt-magic-cursor` (all blog posts)
- `body.blog.tt-magic-cursor` (blog listing)

## Rule Going Forward

**Any new page added with a brain background video needs to be added to this list.**

Ask: What is the body class on that page? Does it have tt-magic-cursor? Does it have a .video-background div? If yes → add transparent override.

## Plugin Deployment Pattern

When Playwright form submit fails:
1. Try cookie-based HTTP: login → fetch editor page → extract nonce → POST form directly
2. If that fails → Playwright with `cm.save()` before submit + direct textarea set as backup
3. Key: `cm.save()` is critical — syncs CodeMirror to hidden `#newcontent` textarea

Deploy script: `/home/jared/projects/AI-CIV/aether/tools/security/deploy_plugin_v622_final.py`

## Verification

After deploy, check pages for the CSS marker in HTML source:
- `body.page-id-689.tt-magic-cursor` should appear in page source
- Cloudflare may cache for 1-2 min — check both source and visual render

## Button Hover CSS Location

Button hover fixes deployed in v4.8.4 via `wp_head` CSS:
- "Try Free Calculator" = blue bg + white text on hover
- "See All Comparisons" = orange bg + white text on hover
These are in the `wp_head` block, not the `wp_footer` block — they are independent of the body override.
