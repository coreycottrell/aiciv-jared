# CTO: Page 688 Pricing Deployment Pattern

**Date**: 2026-03-03
**Type**: operational, teaching
**Topic**: Surgical pricing tier update on Elementor canvas pages

## Task
Update pay-test-sandbox-2 (page 688) from 5 tiers to 4 tiers, adding strikethrough pricing and footnote.

## Key Architecture Facts for Page 688

1. Template: `elementor_canvas` — Elementor controls all rendering
2. Widget type: single large `html` widget containing the entire page
3. `_elementor_data` size: ~491,000 chars (JSON string)
4. `content.raw` size: ~440,000 chars (plain HTML with wp:html wrapper)
5. BOTH must be updated — Elementor uses `_elementor_data` to render, but `content.raw` is a fallback

## Replacement Strategy

Find: `<div class="pricing-grid">` ... to just before `<div class="pricing-requirements">`
Replace with: new 4-card grid + footnote

In `_elementor_data`: content is JSON-escaped (double-escaped quotes: `\\"`)
In `content.raw`: plain HTML

## Critical Technical Notes

- **Use Python urllib** for pushes — payload is ~491KB, curl has ~100KB arg limit
- **pricing-grid--five** class only appears in CSS selectors, NOT on the actual element
- **Cache clear**: `DELETE /wp-json/elementor/v1/cache` returns empty body — that's normal
- Backup before touching anything

## Deployment Script

`/home/jared/projects/AI-CIV/aether/tools/deploy_pricing_688_final.py`

## Verification Checklist (16 points)

- $149, $197/month*, Awakened, MOST POPULAR, CLAIM THIS SPOT
- $499, $579/month*, Partnered
- $999, $1,089/month*, Unified
- Enterprise
- Footnote: "Lock in the savings today"
- Bonded REMOVED
- openPayPalModal preserved (Unified button)
- openWaitlistModal preserved (other buttons)
