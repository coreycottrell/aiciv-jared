# Seed Cross-Contamination Fix: Pricing Gate + Custom ID UUID

**Date**: 2026-04-06
**Type**: bugfix
**Severity**: CRITICAL (customer data cross-contamination)

## Root Cause

Two bugs combined to allow seed cross-contamination:

1. **BUG 1: Missing pricing gate on tier pages**
   - The homepage (`/index.html`) has `.pricing-section { display: none; }` CSS + `closeCelebrationAndShowPricing()` JS that only reveals pricing after the naming ceremony completes.
   - The tier-specific pages (`/insiders/`, `/awakened/`, `/partnered/`, `/unified/`, `/live/`) had the celebration button referencing `closeCelebrationAndShowPricing()` but the function AND the CSS gate were MISSING.
   - Result: customers could scroll past the chatbox and pay without naming their AI, meaning no session UUID was properly linked.

2. **BUG 2: PayPal custom_id lacked session UUID**
   - PayPal's `custom_id` was just `'PB-AWAKENED'` with no session-specific identifier.
   - This made it impossible to link a PayPal payment back to a specific chatbox session from PayPal's own records.

## Fix Applied

### Bug 1 Fix (5 tier pages)
- Added `.pricing-section { display: none; }` and `.pricing-section.active { display: block; animation: fadeInUp 0.8s ease; }` CSS to all 5 tier pages.
- Added complete `closeCelebrationAndShowPricing()` + `showPricing()` JS functions (injected before `payment-background.js` script tag).
- Functions update AI name in badge, title, description, CTA buttons, then reveal pricing section with smooth scroll.

### Bug 2 Fix (12 production pages + shared JS)
- Changed `custom_id: 'PB-' + tier.toUpperCase()` to include `payTestData.sessionUuid`.
- New format: `PB-AWAKENED-<uuid>` (e.g., `PB-AWAKENED-a1b2c3d4-e5f6-...`).
- Updated `purebrain_log_server.py` to extract UUID from custom_id as fallback when `sessionUuid` not in request body directly.

## Files Changed

### Tier pages (Bug 1 CSS + JS + Bug 2 custom_id):
- `exports/cf-pages-deploy/insiders/index.html`
- `exports/cf-pages-deploy/awakened/index.html`
- `exports/cf-pages-deploy/partnered/index.html`
- `exports/cf-pages-deploy/unified/index.html`
- `exports/cf-pages-deploy/live/index.html`

### Homepage + home-test (Bug 2 custom_id only, already had pricing gate):
- `exports/cf-pages-deploy/index.html`
- `exports/cf-pages-deploy/home-test/index.html`
- `exports/cf-pages-deploy/home-test-sandbox/index.html`
- `exports/cf-pages-deploy/home-test-live-1/index.html`
- `exports/cf-pages-deploy/insiders/awakened/index.html`
- `exports/cf-pages-deploy/insiders/pay-test-awakened/index.html`
- `exports/cf-pages-deploy/js/homepage-payment.js`

### Seed system:
- `tools/purebrain_log_server.py` — UUID extraction from custom_id fallback

## Pages Already Correct (had pricing gate before)
- `/` (homepage) - had full gate
- `/home-test/` - had full gate
- `/home-test-sandbox/` - had full gate
- `/home-test-live-1/` - had full gate
- `/insiders/awakened/` - had full gate (uses homepage template)
- `/insiders/pay-test-awakened/` - had full gate

## Deployment
- Deployed 12 files to CF Pages (purebrain-staging)
- Deployment ID: 0daeaa3e-e5ef-4f8b-92ba-e5a71645dfe9
- CF cache purged
- Log server restarted to pick up Python changes

## Brad Nordal Manual Re-seed
- Sent corrected seed via `/api/send-seed`
- Details: Bradley Nordal, bwnordal@gmail.com, Awakened, $74.50, no AI name
- Session UUID: brad-manual-reseed-43f46cfc
- AgentMail message ID confirmed

## Remaining Work
- 12 sandbox/test pages still have old custom_id format (not customer-facing)
- Consider extracting the pricing gate CSS/JS into a shared file to prevent drift
