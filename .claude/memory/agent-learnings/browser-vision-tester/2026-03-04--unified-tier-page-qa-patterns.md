# Unified Tier Page QA Patterns
**Date**: 2026-03-04
**Agent**: browser-vision-tester
**Type**: technique

## Context
QA audit of newly created https://purebrain.ai/unified-how-this-levels-you-up/ page.
$999/month Unified tier sales page with PayPal sandbox integration.

## Key Findings

### PayPal Iframe Interaction Pattern (CRITICAL)
- PayPal smart buttons render as IFRAMES from sandbox.paypal.com
- The iframe contains NO `<button>` elements - uses `div[tabindex]` instead
- Correct selector: `frame.query_selector_all('div[tabindex]')` on the PayPal frame
- Clicking opens a POPUP WINDOW (new page), not an overlay modal on same page
- Popup URL pattern: `https://www.sandbox.paypal.com/checkoutnow?atomic-event-state=...`
- To capture: use `context.on("page", handler)` BEFORE clicking, then `context.pages[-1]`
- Wait time needed: 5+ seconds after click for popup to fully load

### Finding PayPal Frame
```python
for frame in page.frames:
    if 'sandbox.paypal.com/smart/buttons' in frame.url:
        # This is the PayPal button frame
        buttons = await frame.query_selector_all('div[tabindex]')
        await buttons[0].click()  # First = Pay with PayPal
```

### Background Color Verification
- This page uses `rgb(10, 14, 26)` = #0a0e1a (very dark navy, PASSES dark check)
- Body class includes: `page-template-elementor_canvas` - means full-screen template
- Plugin enforces dark bg - verified working

### CSP Console Errors (Expected/Non-Critical)
These 4 errors appear on every purebrain.ai page and are EXPECTED:
1. GTM script blocked by CSP (Google Tag Manager)
2. wsimg.com signals script blocked
3. wsimg.com traffic script blocked
4. blob: worker blocked

These do NOT affect page functionality. They're GoDaddy/GTM scripts being blocked
by the strict security plugin CSP. The PayPal scripts are whitelisted and work fine.

## Page QA Results
| Check | Result | Details |
|-------|--------|---------|
| Dark background | PASS | rgb(10,14,26) = #0a0e1a |
| Hero section | PASS | "UNIFIED TIER - $999/MONTH" badge + H1 correct |
| Content sections | PASS | 6 categories visible, Live + In Development badges |
| PayPal button | PASS | 3 payment options visible (PayPal, SEPA, Credit Card) |
| PayPal modal | PASS | Sandbox Login to PayPal screen opens |

## Screenshot Paths
/home/jared/projects/AI-CIV/aether/exports/screenshots/unified-qa-20260304/
- 001-page-top.png: Hero section
- 002-scroll-25pct.png: Category 02 + 03 with Live/In Development badges
- 003-scroll-50pct.png: Category 06, Community section
- 004-scroll-75pct.png: Pricing box with $999 and feature list
- 005-bottom-paypal.png: PayPal buttons (all 3 options)
- 006-full-page.png: Full page composite
- 011-paypal-modal-popup.png: PayPal sandbox Login screen
