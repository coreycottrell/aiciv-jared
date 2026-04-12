# Insiders Page Build — /insiders/

**Date**: 2026-03-11
**Type**: build completion
**Agent**: dept-systems-technology

---

## What Was Built

Self-contained, password-protected single-tier purchase page for PureBrain insiders.

- **URL**: https://purebrain-staging.pages.dev/insiders/
- **Files**:
  - `exports/cf-pages-deploy/insiders/index.html`
  - `purebrain-site/public/insiders/index.html`
- **Commit**: d843ae38

---

## Key Config Values

- **Password**: `PureBrainInviteOnly26+` (stored in localStorage key `pb_insiders_unlocked`)
- **Tier**: Awakened — $74.50/month recurring
- **PayPal Plan ID**: `P-9KA28683EF7622051NGLUFJY` (same as sandbox-3 Awakened)
- **PayPal Client ID**: `AYTFob05DoSn0ZeVtLJ05duKwFHOdAckHgkZ2UJhAXvfJlUXEYM_PFib3HbIuVgauxV_6clZ5FdPRYq_`
- **Source identifier**: `insiders` (appears in all log payloads — tracked separately)
- **Log endpoint**: `https://api.purebrain.ai/api/log-pay-test`

---

## Architecture Decisions

1. **Clean self-contained HTML** — No WordPress cruft. No jQuery. No theme CSS/JS.
   Started from scratch using patterns from sandbox-3, not copy-pasting WP export.

2. **Password gate loads before PayPal SDK** — `loadPayPalSDK()` only called after
   unlock to prevent bot scraping of the subscription endpoint.

3. **Preloader dismiss = inline script at top of `<head>`** — Runs immediately on
   parse, not on DOMContentLoaded. Belt-and-suspenders: CSS hides it, JS polls 30x.

4. **initPayTestFlow rewritten inline** — Full birth pipeline (Witness OAuth),
   questionnaire flow, behind-the-curtain, Telegram setup, portal watcher all present.
   Source tag `insiders` threads through every log call.

5. **PayPal SDK deferred until unlock** — `<script id="paypal-sdk-placeholder">` is
   a dummy that gets replaced by the real SDK script on `loadPayPalSDK()` call.

---

## Verification

All 15 checks passed on live deployed URL:
- Password gate, correct password, PayPal plan ID, price, preloader dismiss,
  localStorage, initPayTestFlow, source identifier, Oswald font, dark bg,
  brand colors, PayPal SDK loader, Witness birth API, log endpoint, mobile responsive.

---

## What Differs from sandbox-3

- Single tier only (no Partnered/Unified/Transcendent)
- No tier selector UI — goes straight to Awakened
- No hero chatbox (awakening form is simpler name-your-AI input)
- Price: $74.50 vs $149 in sandbox-3
- Source identifier: "insiders" not "purebrain" or "purebrain-post-payment"
- Password gate layer (entirely new feature)
- No WordPress boilerplate (clean HTML from scratch)
