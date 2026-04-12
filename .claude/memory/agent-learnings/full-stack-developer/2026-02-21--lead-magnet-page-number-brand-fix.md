# Lead Magnet: Page Number Overlap Fix + Brand Color Fix

**Date**: 2026-02-21
**Type**: operational
**Topic**: Two HTML fixes to ai-partnership-audit-lead-magnet.html, redeployed to both WP sites

---

## What Was Fixed

### Fix 1: Page Number Overlap
- `.page-number` had `position: absolute; bottom: 14px; right: 40px` which overlapped page content
- Solution: Set `.page-number { display: none; }` — cleanest removal, no layout disruption
- The "1 of 2" and "2 of 2" labels in HTML were left in DOM (just hidden via CSS)

### Fix 2: Footer "purebrain.ai" Brand Colors
- Was: `<div class="footer-url">purebrain.ai</div>` with single blue color
- Fixed to: `<span class="blue">PUREBR</span><span class="orange">AI</span><span class="blue">N</span><span class="footer-url-ai">.ai</span>`
- Added CSS: `.footer-url .blue`, `.footer-url .orange` (scoped to avoid conflicts)
- Added `.footer-url-ai { color: rgba(255,255,255,0.75); }` for .ai suffix
- Added print-mode equivalents for those same selectors
- Removed stale `color: var(--blue)` from `.footer-url` block itself

## Key Pattern
- `.blue` and `.orange` classes were scoped inside `.logo-wordmark` and `.calc-formula` only
- Cannot reuse them for footer without re-scoping — added `.footer-url .blue` scoped rules
- PUREBRAIN brand rule: PUREBR=blue(#2a93c1), AI=orange(#f1420b), N=blue, .ai=white/light

## Deployment
- purebrain.ai Page 620: PUT /wp-json/wp/v2/pages/620 → HTTP 200
- jareddsanborn.com Page 1116: PUT /wp-json/wp/v2/pages/1116 → HTTP 200
- Elementor cache cleared: DELETE /wp-json/elementor/v1/cache → HTTP 200
- Both pages verified HTTP 200

## File
`/home/jared/projects/AI-CIV/aether/exports/ai-partnership-audit-lead-magnet.html`
