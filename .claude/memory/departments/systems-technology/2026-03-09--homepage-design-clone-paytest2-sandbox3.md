# Homepage Design Clone: pay-test-2 + sandbox-3

**Date**: 2026-03-09
**Type**: deployment, pattern
**Pages**: pay-test-2 (ID 689), sandbox-3 (ID 1232)

---

## Task Summary

Cloned purebrain.ai homepage design onto pay-test-2 and sandbox-3 while preserving each page's unique chatbox code, PayPal links, and post-payment flow.

---

## Key Findings (What Differed)

### pay-test-2 vs homepage
- Missing: `pb-demo-section` (video demo), `pb-calc-cta` (calculator CTA)
- Had OLD pricing cards ($79 Awakened, no MOST POPULAR badge, different taglines)
- Had 15:00 session timer (homepage has 30:00)
- Had older main chatbox script (missing exit popup functions: canShowExitPopup, showExitPopup, exitZoom)
- Had outdated CSS

### sandbox-3 vs homepage
- Missing: PayPal SDK entirely (buttons called `openPayPalModal` but function not defined)
- Missing: post-payment chat flow
- Missing: integration glue script
- Had different pricing display ($197/month*, $579/month*, $1,089/month*)
- Had emoji encoding differences in HTML

---

## Solution Applied

For BOTH pages:
1. Replaced ALL HTML sections (hero through compare) with homepage versions
2. Added `pb-demo-section` and `pb-calc-cta` from homepage
3. Replaced CSS with homepage CSS (16 unique blocks, ~177k)
4. Replaced main chatbox script with homepage version (has exit popup + 30min timer)
5. Kept post-compare content from each page (their own timeline + footer sections)

### pay-test-2 KEPT (page-specific):
- PayPal client ID: `AWgWNlBQ...` (LIVE key)
- Plan IDs: P-1AG936074 (Awakened $79/mo LIVE), P-2SA65600 (Bonded $149/mo), etc.
- Post-payment chat flow v4.7 (88k script)
- Integration glue (3.8k)
- PayPal alias fix

### sandbox-3 USED (from homepage):
- PayPal client ID: `AYTFob05...` (homepage production key)
- Plan IDs: Awakened P-2SA65600, Partnered P-3VH43554, Unified P-43A28944
- Post-payment chat flow v4.7 (89k script from homepage)
- Integration glue (6.9k from homepage)

---

## Architecture Note: Why Elementor sections NOT cloned

Homepage sections `why_pb_688`, `a18b125d`, `1839607` are Elementor-rendered with Elementor-specific classes. They require Elementor CSS/JS to render. Since pay-test-2 and sandbox-3 are pure HTML pages (Elementor disabled), adding these Elementor sections would render broken. Only `pb-demo-section` and `pb-calc-cta` (pure HTML) were added.

---

## Verification Results

Both pages pass all 10 checks:
- Dark background, all sections rendered, PayPal SDK, post-payment flow, canvas, video bg, no orange bg

---

## Deployment Details

- pay-test-2: deployed 2026-03-09T20:36:55, 540993 chars
- sandbox-3: deployed 2026-03-09T20:37:26, 547974 chars
- Template: elementor_canvas (unchanged)
- Elementor cache cleared after deployment

---

## Pattern: Homepage Design Clone Process

1. Fetch homepage rendered HTML (GET purebrain.ai/)
2. Fetch target pages via WP API (GET /wp-json/wp/v2/pages/{id}?context=edit)
3. Extract CSS from homepage (deduplicate, ~16 blocks, ~177k)
4. Extract main chatbox script from homepage (70k DOMContentLoaded script)
5. Extract page-specific PayPal + post-payment scripts from each target page
6. Extract HTML sections from homepage (hero, about, pb-demo-section, value-pyramid, capabilities, awakening, value, pricing, compare)
7. Extract body structure from target page (pre-canvas modals, canvas elements)
8. Build new page: head_meta + combined_css + body_structure + hp_sections + post_compare + scripts
9. Deploy via WP API POST with JSON payload file (--data-binary "@file.json")
10. Clear Elementor cache: DELETE /elementor/v1/cache
11. Verify rendered pages with password cookie + curl
