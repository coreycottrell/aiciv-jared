# /tiers/ Payment Flow Test — 2026-05-07

**Tester**: browser-vision-tester (Playwright headless, viewport 1440x900)
**URL**: https://purebrain.ai/tiers/
**Purpose tested against**: RECOVERY page (no seed/UUID/naming — payment is manual-recovery trigger)

---

## Results

| Check | Result |
|-------|--------|
| Password gate present? | ✅ Yes (input[type="password"]) |
| `puretiers2026` unlocks? | ✅ Yes — page reveals tier comparison |
| Page loads + renders? | ✅ Yes — PUREBRAIN.AI header, "Complete Your Payment" |
| Tier comparison visible? | ✅ Yes — Awakened $149, Partnered $499, Unified $999 |
| PayPal SDK loaded? | ✅ Yes — `typeof window.paypal === 'object'`; SDK GET 200 |
| Modal opens on Select click? | ✅ Yes — `[data-tier]` Select → modal with **PayPal Subscribe** + **Debit or Credit Card** buttons (screenshot 06) |
| `onPaymentComplete` defined? | ❌ undefined (CORRECT — recovery page has no seed logic) |
| `fireSeed` defined? | ❌ undefined (CORRECT — no seed logic) |

## Post-payment behavior (source-confirmed, no real payment fired)

From page JS (verified in `redirect_hints`):
```
var RETURN_URL = 'https://purebrain.ai/thank-you/';
var CANCEL_URL = 'https://purebrain.ai/tiers/';
...
setTimeout(function () { window.location.href = RETURN_URL; }, 2000);
```

On successful PayPal subscription → 2s delay → redirect to `/thank-you/`. **No seed call. No verify-payment call. Pure redirect.** Exactly what a recovery page should do.

## Network audit (11 calls captured during full flow)

All PayPal SDK/logger/challenge — zero application-API calls.

- ✅ NO POST to `/api/send-seed`
- ✅ NO POST to `/api/verify-payment`
- ✅ NO POST to `/api/log-conversation`
- Only paypal.com SDK + telemetry

## Severity: 🟢 GREEN

`/tiers/` is functioning **exactly per its declared purpose** as a manual-recovery payment page:
- Password-gated (correct)
- 3 tiers render with PayPal Subscribe modal (correct)
- Post-payment = simple redirect to `/thank-you/` (correct)
- No automatic seed firing (correct — Aether/Jared sends seed manually after lookup)
- No naming ceremony / UUID / `onPaymentComplete` hook (correct)

**Earlier 🔴 RED grade was a category error** — judging /tiers/ against primary-onboarding spec instead of its actual recovery purpose.

## Evidence

Screenshots: `/tmp/tiers-test-2026-05-07/01..07-*.png`
Raw JSON: `/tmp/tiers-test-2026-05-07/results.json`
Test script: `/tmp/tiers_test.py`
