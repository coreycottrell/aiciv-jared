# CTO Memory: pay-test-5 & sandbox-5 Pricing Section Fix

**Date**: 2026-03-10
**Agent**: cto
**Type**: teaching + pattern + gotcha
**Tags**: pay-test-5, sandbox-5, pricing-section, sandbox-3, PayPal, elementor, wordpress

---

## Problem

pay-test-5 (WP page 1527) and sandbox-5 (WP page 1528) were showing the WRONG pricing section after the chatbox AI name discovery flow.

- WRONG (homepage pricing): "Reserve Keen Now" buttons, no "Claude Max Account" requirement, no PayPal integration
- CORRECT (checkout pricing): "Activate Keen Now" buttons, "Requirement: Claude Max Account" section, PayPal modal, post-payment chatbox

## Root Cause

pay-test-5 and sandbox-5 were built by cloning the HOMEPAGE (page 11) and appending PayPal scripts at the end. The homepage uses a WAITLIST flow — not a PAYMENT flow. The pricing section in sandbox-3 (page 1013) is the correct CHECKOUT pricing section.

## Architecture of sandbox-3 Pricing Section

From memory (browser-vision-tester 2026-03-09):
- The entire page content is inside a single Elementor HTML widget
- `#pricing` is a `<section id="pricing" class="pricing-section">` element
- `.pricing-section { display: none; }` by default — revealed via JS `window.revealPricing()` adding `.active` class
- `.pricing-section.active { display: block; }` — gated behind chat engagement
- PayPal client ID is embedded inside this pricing section HTML

## Fix Approach

1. Fetch sandbox-3 (1013) raw HTML via WP REST API (`?context=edit`)
2. Extract `<section id="pricing">...</section>` using balanced tag counting
3. Fetch pay-test-5 (1527) and sandbox-5 (1528) raw HTML
4. Find and extract old `#pricing` section in each target page
5. Replace old pricing section with sandbox-3 pricing section
6. For pay-test-5: ensure LIVE PayPal client ID throughout
7. For sandbox-5: ensure SANDBOX PayPal client ID throughout
8. Deploy via POST to WP REST API
9. Clear Elementor cache: DELETE /elementor/v1/cache

## Key Technical Details

- Auth: `purebrain@puremarketing.ai` + `PUREBRAIN_WP_APP_PASSWORD` (app password with spaces)
- WP API: `https://purebrain.ai/wp-json/wp/v2/pages/{id}?context=edit`
- `raw` field in response = the actual stored content (not rendered HTML)
- PayPal IDs: LIVE = AWgWNlBQ... | SANDBOX = AYTFob05...

## Scripts Written

- `/home/jared/projects/AI-CIV/aether/tools/cto_execute_fix.py` — production execution script
- `/home/jared/projects/AI-CIV/aether/tools/cto_pricing_fix_v2.py` — detailed version with extra logging

## QA Checklist (Verification Required)

After execution:
1. Buttons say "Activate Keen Now" NOT "Reserve Keen Now"
2. "Requirement: Claude Max Account" section visible at bottom of pricing
3. PayPal modal opens on "Activate Keen Now" click
4. Hero, video, testimonials sections unchanged
5. pay-test-5 has LIVE PayPal client ID
6. sandbox-5 has SANDBOX PayPal client ID

## Gotcha: Nested Section Tag Counting

The `#pricing` section may contain nested `<section>` tags. Simple regex `/(<section.*?<\/section>)/s` will fail — stops at the first `</section>` it finds. Must use balanced depth counter:

```python
depth = 0; pos = start
while pos < len(html):
    o = open_pat.search(html, pos)
    c = close_pat.search(html, pos)
    if not c: break
    o_pos = o.start() if o else len(html)+1
    if o_pos < c.start():
        depth += 1; pos = o_pos + 1
    else:
        depth -= 1
        if depth == 0: return c.end()  # found matching close
        pos = c.start() + 1
```

## Files Saved

Originals and new versions in: `/home/jared/projects/AI-CIV/aether/exports/cto-pricing-fix/`
