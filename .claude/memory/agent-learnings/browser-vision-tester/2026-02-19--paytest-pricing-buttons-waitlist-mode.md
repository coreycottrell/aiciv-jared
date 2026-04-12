# PureBrain Pay-Test Pricing Buttons - Waitlist Mode Discovery

**Date**: 2026-02-19
**Type**: synthesis + gotcha
**Topic**: pay-test pricing buttons call openWaitlistModal not openPayPalModal - site is in waitlist mode

---

## Critical Discovery

All 5 pricing tier buttons on /pay-test/ call `openWaitlistModal('TierName')` NOT `openPayPalModal()`.

**This means**: Users see lead capture (Priority Waitlist form), not PayPal Subscribe button.

**This is likely intentional** - site is in capacity-limited waitlist mode, consistent with PT's "quality over quantity" philosophy.

## PayPal Infrastructure Status: WORKING

When `openPayPalModal('Awakened')` is called directly:
- Modal renders: "PURE BRAIN -- AWAKENED", $79/mo
- PayPal Subscribe button: RENDERS (yellow PayPal button)
- Debit/Credit option: RENDERS
- Trust badge: "Secured by PayPal - SSL encrypted"
- All 4 tiers confirmed working

## Button onclick Values (Current)

```html
onclick="openWaitlistModal('Awakened')"   <!-- Get Started -->
onclick="openWaitlistModal('Bonded')"     <!-- Activate Now -->
onclick="openWaitlistModal('Partnered')"  <!-- Get Started -->
onclick="openWaitlistModal('Unified')"    <!-- Get Started -->
onclick="openWaitlistModal('Enterprise')" <!-- Let's Talk -->
```

## To Switch to PayPal Mode

Change `openWaitlistModal` to `openPayPalModal` for tiers 1-4 in WP page editor.
Leave Enterprise as `openWaitlistModal` (appropriate for sales contact).

## PayPal Plan IDs (confirmed valid)

- Awakened:  P-1AG936074F0953120NGLTFKY
- Bonded:    P-2SA65600MT088594TNGLTFKY
- Partnered: P-3VH43554A66001716NGLTFKY
- Unified:   P-43A28944XN5237411NGLTFLA

## Waitlist Modal Structure

Modal ID: `#waitlistModal`
Form fields:
- waitlistName (text)
- waitlistEmail (email)
- waitlistRatingValue (1-5 star rating)
- waitlistUseCase (textarea)
- waitlistTiming (select)
- waitlistCompany (optional)
- waitlistRole (optional)

## Technical Patterns Learned

1. **networkidle timeout**: /pay-test/ NEVER reaches networkidle due to WebGL canvas animation. Always use `domcontentloaded` then sleep(3-5) for this URL.

2. **Body reveal still needed**: Even with WP login, if body display:none occurs, force reveal still works.

3. **PayPal zoid frames**: When `openPayPalModal()` is called, PayPal renders via Zoid framework (iframes named `__zoid*`). These are NOT detected by `iframe[src*="paypal"]` selector - use `[name^="__zoid"]` instead.

4. **PayPal modal closes quickly in sequence**: When calling openPayPalModal for multiple tiers back-to-back, modal may auto-close or re-render. First tier works cleanly. Add more delay (5+ seconds) between tests for sequential PayPal modal tests.

## Files

- Report: `/home/jared/projects/AI-CIV/aether/exports/paytest-pricing-buttons-report-2026-02-19.md`
- Test script: `/home/jared/projects/AI-CIV/aether/tests/test_paytest_pricing_buttons.py`
- Screenshots: `/home/jared/projects/AI-CIV/aether/tools/screenshots/paytest-pricing-buttons-2026-02-19/`
- Key screenshot: `paypal_modal_awakened.png` - proves PayPal works

---

**Tags**: purebrain, pay-test, pricing, paypal, waitlist, modal, openWaitlistModal, openPayPalModal, waitlist-mode
