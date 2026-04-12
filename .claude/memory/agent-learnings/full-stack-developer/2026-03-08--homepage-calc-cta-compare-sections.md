# Homepage: FREE TOOL + COMPARE PUREBRAIN Sections

**Date**: 2026-03-08
**Type**: operational
**Agent**: full-stack-developer

## Task
Add FREE TOOL calculator CTA section and COMPARE PUREBRAIN section to homepage (page-id-11), matching what exists on pay-test-sandbox-3.

## Key Finding: Homepage Already Had Compare PureBrain

Before starting, the homepage (page-id-11) already had:
- The "Compare PureBrain" pills section (vs ChatGPT, vs Claude, vs Copilot, etc.) — in Elementor HTML widget
- The CSS hover rules for the calculator button (in pb-button-styling plugin)
- The "See All Comparisons" button to `/compare/`

What was MISSING:
- The "FREE TOOL — How Much Are You Wasting on AI Tool Sprawl?" CTA section

## Solution: Updated pb-calculator-cta Plugin

**Plugin path**: `tools/security/pb-calculator-cta/pb-calculator-cta.php`

Changed v1.0.0 → v2.0.0:
- Added `is_front_page()` check to `pb_calc_cta_is_target()`
- Added page ID `11` to `PB_CALC_CTA_PAGES` array
- Improved JS injection: searches `p, span, h2, h3, h4, div` (added `div`) for "Compare PureBrain" text
- Added 2000ms retry for Elementor async rendering
- Added `id="pb-calc-cta-injector"` to script tag for easier verification

## Injection Logic on Homepage
The JS injection Strategy 1 finds "Compare PureBrain" text in the Elementor HTML widget, walks up the DOM to find the `elementor-top-section`, and inserts the calc CTA section immediately before it.

## Deploy Script
`tools/security/deploy_calculator_cta_v200.py` — Playwright-based, same pattern as other plugin deploys.

## Verification
```bash
curl -s "https://purebrain.ai/?nocache=$(date +%s)" | grep "pb-calc-cta-injector"
```
Confirmed: `<script id="pb-calc-cta-injector">` found in page source.

## Page ID Reference
- Homepage: page-id-11 (is_front_page = true)
- pay-test-2: page-id-689
- pay-test-sandbox-3: page-id-1232 (NOT 688 — 688 is the old sandbox-2 video bg page)

## Important: Deploy Approach
REST API is blocked on purebrain.ai for plugin edits. Must use Playwright → WP Plugin Editor.
Login URL: `https://purebrain.ai/wp-login.php?wpaas-standard-login=1`
Editor URL pattern: `https://purebrain.ai/wp-admin/plugin-editor.php?file={slug}/{file}.php&plugin={slug}/{file}.php`
