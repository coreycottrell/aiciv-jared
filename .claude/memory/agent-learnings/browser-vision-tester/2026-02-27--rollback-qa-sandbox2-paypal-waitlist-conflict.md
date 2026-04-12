# Memory: pay-test-sandbox-2 Rollback QA - PayPal vs Waitlist Conflict

**Date**: 2026-02-27
**Type**: teaching + operational
**Topic**: Plugin v4.6.4 rollback broke PayPal flow — openWaitlistModal points to waitlist form, not PayPal

---

## Critical Finding

After v4.6.4 plugin rollback: ALL pricing card buttons call `openWaitlistModal(tier)` which opens the OLD waitlist signup form (Full Name, Email, Rating, etc.) instead of PayPal checkout.

**`openPayPalCheckout` IS defined on window but no pricing button calls it.**

---

## Architecture on the Page (Post-Rollback State)

Three competing inline scripts:
1. PayPal SDK Integration v2 — defines PayPal checkout logic in `openPayPalCheckout`
2. PB-FIX alias script — aliases `openPayPalModal = openWaitlistModal` (WRONG direction)
3. Old waitlist modal — defines `openWaitlistModal` as waitlist signup form

Pricing buttons call `openWaitlistModal` → gets the waitlist form. `openPayPalCheckout` is orphaned.

---

## What IS Working

- PayPal SDK: `window.paypal.Buttons` defined, SDK loads from www.paypal.com
- `#pb-paypal-buttons-container`: exists in DOM (inside `#pb-paypal-modal`)
- `openPayPalCheckout`: defined and functional
- Pre-payment chatbox: `#chatMessages`, `#userInput`, `.chat-initial__btn` all visible
- Password unlock: `input[id^="pwbox-"]` still works
- Pricing section reveal: `document.getElementById('pricing')` + add active class works

---

## Fastest Fix

Change pricing card button onclick from `openWaitlistModal('Tier')` to `openPayPalCheckout('Tier')`. All infrastructure is ready — just the wrong function name is being called.

---

## Console Warning Pattern: PB-FIX Retries

```
[PB-FIX] openPayPalCheckout not found, retrying...  (x3, then resolves)
```

This warning means a fix script is searching for `openPayPalCheckout` in a retry loop. By the time it finds it, the alias is created pointing the wrong direction. Not a blocker — just noisy.

---

## Test Script Location

- QA script: `tools/rollback_qa_sandbox2.py`
- Deep investigation: `tools/rollback_qa_deep.py`
- Report: `docs/rollback-qa/ROLLBACK-QA-REPORT.md`
- Screenshot: `docs/rollback-qa/sandbox-bonded.png`

---

## Tags

purebrain, sandbox-2, pay-test, paypal, rollback, v4.6.4, openWaitlistModal, openPayPalCheckout, conflict, qa-audit
