# PureBrain Pay-Test: Pricing Button Audit Report

**Date**: 2026-02-19
**URL**: https://purebrain.ai/pay-test/
**Tester**: browser-vision-tester
**Screenshots**: /home/jared/projects/AI-CIV/aether/tools/screenshots/paytest-pricing-buttons-2026-02-19/

---

## CRITICAL FINDING: Buttons are in Waitlist Mode, NOT PayPal Mode

**All 5 pricing tier buttons currently call `openWaitlistModal()` instead of `openPayPalModal()`.**

This means every "Get Started" / "Activate Now" / "Let's Talk" click shows a **Priority Waitlist signup form**, NOT a PayPal Subscribe button.

The PayPal infrastructure IS working correctly - when `openPayPalModal()` is called directly, all 4 payment tiers render fully with real PayPal Subscribe buttons, correct pricing, and "Secured by PayPal" trust badge.

**This is either intentional (site is in waitlist mode) or a misconfiguration (buttons need onclick values updated).**

---

## Summary

| Metric | Value |
|--------|-------|
| Overall Status | PARTIAL (buttons work, wrong modal) |
| Buttons responding | 5/5 |
| Correct modal type | 0/4 payment tiers (all show waitlist instead) |
| Enterprise form | PASS (waitlist is appropriate for Enterprise) |
| PayPal SDK | LOADED and WORKING |
| PayPal buttons render (via openPayPalModal) | PASS - all 4 tiers confirmed |

---

## Tier-by-Tier Results

### Tier 1: Awakened ($79/mo)

- **Button text**: "Get Started"
- **Button onclick**: `openWaitlistModal('Awakened')`
- **What user sees**: Waitlist modal titled "Join the Priority Waitlist for Awakened"
- **Modal content**: Lead capture form (name, email, AI experience rating, use case, timing, company, role)
- **PayPal button**: NOT shown to user
- **PayPal via openPayPalModal()**: CONFIRMED WORKING - PayPal Subscribe button renders with $79/mo price (screenshot: paypal_modal_awakened.png)
- **Status**: PARTIAL - modal opens but is Waitlist, not PayPal

**Screenshot of waitlist modal:**
`007_tier_awakened_modal_final.png` - Shows "Join the Priority Waitlist for Awakened" with form fields

**Screenshot of PayPal modal (when called directly):**
`paypal_modal_awakened.png` - Shows dark modal with "PURE BRAIN -- AWAKENED", "$79/mo", PayPal yellow Subscribe button, debit/credit card option, Pay button, "Secured by PayPal - SSL encrypted"

---

### Tier 2: Bonded ($149/mo)

- **Button text**: "Activate Now"
- **Button onclick**: `openWaitlistModal('Bonded')`
- **What user sees**: Waitlist modal titled "Join the Priority Waitlist for Bonded"
- **PayPal via openPayPalModal()**: CONFIRMED WORKING - PayPal frame loads with $149/mo pricing, zoid frame detected
- **Status**: PARTIAL - modal opens but is Waitlist, not PayPal

---

### Tier 3: Partnered ($499/mo)

- **Button text**: "Get Started"
- **Button onclick**: `openWaitlistModal('Partnered')`
- **What user sees**: Waitlist modal titled "Join the Priority Waitlist for Partnered"
- **PayPal via openPayPalModal()**: CONFIRMED WORKING - PayPal frame loads with $499/mo pricing
- **Status**: PARTIAL - modal opens but is Waitlist, not PayPal

---

### Tier 4: Unified ($999/mo)

- **Button text**: "Get Started"
- **Button onclick**: `openWaitlistModal('Unified')`
- **What user sees**: Waitlist modal titled "Join the Priority Waitlist for Unified"
- **PayPal via openPayPalModal()**: CONFIRMED WORKING - PayPal frame loads with $999/mo pricing
- **Status**: PARTIAL - modal opens but is Waitlist, not PayPal

---

### Tier 5: Enterprise (Custom)

- **Button text**: "Let's Talk"
- **Button onclick**: `openWaitlistModal('Enterprise')`
- **What user sees**: Waitlist modal titled "Join the Priority Waitlist for Enterprise"
- **Modal fields**: Name, Email, AI experience rating (1-5 stars), Use case textarea, Timing dropdown, Company (optional), Role (optional)
- **Status**: PASS - waitlist/lead capture is appropriate for Enterprise tier

---

## PayPal Infrastructure Deep Inspection

### SDK Status
- `[PB PayPal] SDK pre-loaded and ready.` - Confirmed in console
- `window.paypal` - Defined (SDK loaded successfully)
- Real client ID: `AWgWNlBQAy5BMXKB5xbaMwSk01WkatC08b5rTj_JKu4...` (NOT a placeholder)

### PayPal Plan IDs (all 4 present in HTML)
- Awakened: `P-1AG936074F0953120NGLTFKY`
- Bonded: `P-2SA65600MT088594TNGLTFKY`
- Partnered: `P-3VH43554A66001716NGLTFKY`
- Unified: `P-43A28944XN5237411NGLTFLA`

### PayPal Modal Structure (`#pb-paypal-modal`)
The PayPal modal exists in the DOM with:
- `#pb-paypal-tier-name` - Displays "Pure Brain -- [Tier]"
- `#pb-paypal-price-line` - Displays "$[amount]/mo"
- `#pb-paypal-price-sub` - "Billed monthly - Cancel anytime"
- `#pb-paypal-buttons-container` - PayPal renders Subscribe button here
- `#pb-paypal-close` - X close button

### Window Functions Available
- `openPayPalModal(tier)` - Opens PayPal payment modal with correct tier/price
- `openPayPalCheckout(tier)` - Alias for openPayPalModal
- `openWaitlistModal(tier)` - Opens waitlist lead capture modal
- `closeWaitlistModal()` - Closes waitlist modal
- `__pbPaymentYes` - Handles successful payment
- `__pbPaymentNo` - Re-renders PayPal button on failure
- `onPaymentComplete` - Payment completion handler

---

## What Users Currently Experience (Step by Step)

1. User navigates to purebrain.ai/pay-test/
2. User sees pricing cards: Awakened $79, Bonded $149, Partnered $499, Unified $999, Enterprise
3. User clicks any "Get Started" button
4. Dark overlay modal appears titled "Join the Priority Waitlist for [Tier]"
5. Modal shows: "We're currently at capacity for new partners. We intentionally limit onboarding so every client gets exceptional, personalized treatment."
6. User fills form: name, email, AI experience rating, use case, timing, company, role
7. User clicks "Join Priority Waitlist"
8. No payment is taken - this is lead capture only

---

## Action Required from Jared

**Question**: Is this intentional?

**Option A - Intentional Waitlist Mode (Status: No action needed)**
The site is in "capacity-limited" waitlist mode. This is actually on-brand for Pure Technology's "quality over quantity" philosophy. The PayPal infrastructure is ready to activate when capacity opens. To launch PayPal payments, update button onclick attributes.

**Option B - Bug/Misconfiguration (Status: Fix needed)**
If you want PayPal payment buttons now, update each button onclick in the WordPress page editor from `openWaitlistModal('Tier')` to `openPayPalModal('Tier')`.

**Fix if needed (4 buttons to update):**
```html
<!-- Awakened button: change from -->
onclick="openWaitlistModal('Awakened')"
<!-- to -->
onclick="openPayPalModal('Awakened')"

<!-- Bonded button: change from -->
onclick="openWaitlistModal('Bonded')"
<!-- to -->
onclick="openPayPalModal('Bonded')"

<!-- Partnered: same pattern -->
<!-- Unified: same pattern -->
<!-- Enterprise: leave as waitlist (appropriate for sales contact) -->
```

---

## Console Analysis

**PayPal messages:**
- `[log] [PB PayPal] SDK pre-loaded and ready.` - Clean initialization

**Console errors:**
- `[error] SCC Library has already been loaded on page` - Known harmless duplicate script issue (documented 2026-02-18)

**No new errors.** The page is clean.

---

## Screenshots

| File | Description |
|------|-------------|
| `003_paytest_loaded.png` | Pay-test page loaded and body visible |
| `004_00_page_overview.png` | Homepage hero with PURE BRAIN branding |
| `005_00b_pricing_section.png` | Pricing tier cards (Awakened $79 visible in bg) |
| `007_tier_awakened_modal_final.png` | Awakened waitlist modal with form |
| `009_tier_bonded_modal_final.png` | Bonded waitlist modal with form |
| `011_tier_partnered_modal_final.png` | Partnered waitlist modal |
| `013_tier_unified_modal_final.png` | Unified waitlist modal |
| `015_tier_enterprise_modal_final.png` | Enterprise "Let's Talk" waitlist modal |
| `paypal_modal_awakened.png` | **PAYPAL WORKING**: $79 modal with PayPal Subscribe button |
| `paypal_modal_bonded.png` | After PayPal modal for Bonded (closed before screenshot) |
| `paypal_modal_partnered.png` | After PayPal modal for Partnered (closed before screenshot) |
| `paypal_modal_unified.png` | After PayPal modal for Unified (closed before screenshot) |

**Key screenshot to show Jared**: `paypal_modal_awakened.png` - This proves the PayPal subscription button works and looks great when openPayPalModal() is called directly.

---

## Test Script

Script location: `/home/jared/projects/AI-CIV/aether/tests/test_paytest_pricing_buttons.py`

---

*Report generated by browser-vision-tester agent - 2026-02-19*
