# AI Partnership Audit WordPress Page Deployment
**Date**: 2026-02-21
**Type**: operational
**Topic**: Converting self-contained HTML lead magnet to WordPress pages on two sites

## What Was Done
- Deployed `exports/ai-partnership-audit-lead-magnet.html` as a live WordPress page
- purebrain.ai: Page ID 620, template = elementor_canvas
  - Live URL: https://purebrain.ai/ai-partnership-audit/
- jareddsanborn.com: Page ID 1116, template = page-template-blank.php
  - Live URL: https://jareddsanborn.com/ai-partnership-audit/

## Conversion Pattern (HTML file → WordPress page)
1. Extract `<style>` block from `<head>` section
2. Extract content between `<body>` and `</body>`
3. Combine as: `<style>{css}</style>\n{body_content}`
4. Add a body override: `body.page { background-color: #080a12 !important; }` (prevents theme from overriding dark bg)
5. POST to `/wp-json/wp/v2/pages` with `content`, `title`, `slug`, `status: publish`, `template`

## Template Names Per Site
- purebrain.ai: `elementor_canvas` (full-width, no header/footer)
- jareddsanborn.com: `page-template-blank.php` (blank canvas, no header/footer)
  - Note: `elementor_canvas` returns 400 on jareddsanborn.com - use blank template instead
  - Can set template in a separate PATCH/POST after initial creation

## Post-Deploy Steps
1. Clear Elementor cache on purebrain.ai: `DELETE /wp-json/elementor/v1/cache`
2. Verify page loads at expected URL (HTTP 200)
3. Verify CTA link points to `https://purebrain.ai/#awakening` (not test pages)

## Key Rules Applied
- CTA button: `https://purebrain.ai/#awakening` (CTA LINK RULE)
- Brand colors: #2a93c1 blue, #f1420b orange
- Logo wordmark: PUREBR (blue) + AI (orange) + N (blue)
- Dual publish: created on both purebrain.ai AND jareddsanborn.com

## File Reference
- Source: `/home/jared/projects/AI-CIV/aether/exports/ai-partnership-audit-lead-magnet.html`
- Prior art: 2026-02-20--ai-adoption-assessment-deployment.md (same pattern)
