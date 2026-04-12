# Memory: pay-test-sandbox-2 PayPal Modal - JS Scope Bug

**Date**: 2026-03-01
**Type**: teaching + operational
**Topic**: openWaitlistModal JS scoping bug - window property vs local scope

---

## Critical Finding

After the PayPal SDK integration was deployed to pay-test-sandbox-2:
- The PayPal SDK script correctly overwrites `window.openWaitlistModal` to call the new PayPal modal
- BUT: Pricing card buttons use bare `openWaitlistModal(tier)` in onclick attributes
- The bare call resolves to the LOCAL scope function (old waitlist form), not `window.openWaitlistModal`
- Result: Users still see the old waitlist signup form, not a PayPal checkout modal

---

## What IS Working

- Sandbox banner: orange "SANDBOX MODE" bar at top of page, visible and correct
- Chatbox: Begin button, AI awakening flow, bypass code all work
- Pricing section: All 5 tiers render correctly after bypass
- PayPal SDK script: Deployed, overwrites window.openWaitlistModal, builds modal DOM
- openPayPalModal alias: Set correctly at window scope
- openPayPalCheckout alias: Set correctly at window scope
- Fallback form POST: Exists, creates PayPal.com/cgi-bin/webscr form when SDK fails
- Page 689 (pay-test-2): Loads fine, no unexpected errors

---

## The Fix

Change 4 pricing card buttons from:
```
onclick="openWaitlistModal('Awakened')"
```
To either:
```
onclick="window.openWaitlistModal('Awakened')"
```
Or (preferred - explicit alias):
```
onclick="openPayPalModal('Awakened')"
```

The Unified tier already correctly uses `openPayPalModal('Unified')`.

---

## PayPal SDK Behavior

- SDK URL: `https://www.sandbox.paypal.com/sdk/js?client-id=AWgWNlBQ...`
- Returns HTTP 400 (sandbox client ID may be invalid or expired)
- Falls back gracefully to form POST approach
- `window.__pbUseSDK = false` is set after failure
- Fallback form POST button renders in modal with PayPal logo
- To get SDK buttons: Need valid sandbox client ID from PayPal developer portal

---

## Side Finding

pay-test-2 (page 689 - production) appears to have the sandbox banner deployed too.
May be unintentional. Should be flagged to dev team.

---

## Test Infrastructure

- Script: `tools/sandbox2_playwright_qa.py`
- Strategy: WP REST API fetch (WAF-safe), serve locally, domcontentloaded (not networkidle)
- Screenshots: `exports/screenshots/sandbox2-qa-20260301/` (10 files)
- Report: `exports/screenshots/sandbox2-qa-20260301/QA-REPORT.md`

## Tags

purebrain, sandbox-2, paypal, openWaitlistModal, window-scope, js-scoping, qa-2026-03-01, pricing-buttons, fallback-form-post
