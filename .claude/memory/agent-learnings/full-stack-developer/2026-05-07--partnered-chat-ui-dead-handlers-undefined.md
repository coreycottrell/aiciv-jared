# Production Payment Pages Have Dead Chat UI — Silent Capture Failure

**Date**: 2026-05-07
**Type**: gotcha
**Severity**: CRITICAL (systemic; affects every customer paying via 4 production pages)
**Files**: `exports/cf-pages-deploy/{partnered,awakened,unified,insiders/awakened}/index.html`

## What Happened

Sheila (`sheila@couplify.com`) paid $499 Partnered tier. PayPal payer was `Jay Whitehurst` (her partner/agent). She received magic-link to `torque-jay.app.purebrain.ai` — Jay Hutton's container. Token leak.

Prior trace assumed Sheila skipped the chat. Jared then said: "She went through https://purebrain.ai/partnered/. She did the full awakening and then paid. How are we not tracking conversations on these pages?"

**The truth**: She *couldn't* have done the awakening on `/partnered/`, because the chat UI on that page is wired to undefined JS handlers.

## Diagnostic Receipts

`exports/cf-pages-deploy/partnered/index.html` (and live `https://purebrain.ai/partnered/`):
- Line 1550: `<button onclick="startConversation()">` — `startConversation` is referenced but never defined on this page (`grep -c "function startConversation\|window.startConversation\s*=" = 0`)
- Line 1557: `<form onsubmit="handleSubmit(event)">` — `handleSubmit` never defined (`grep -c = 0`)
- Lines 5740, 7889, 8227, 8246 read `window._pbPrePurchaseSession`, but nothing assigns it (`grep -c "_pbPrePurchaseSession\s*=" = 0`)

Cross-check across 10 payment pages:
- BROKEN (production customer pages): `partnered`, `awakened`, `unified`, `insiders/awakened`
- WORKING (sandboxes): `pay-test`, `pay-test-awakened`, `pay-test-partnered`, `pay-test-unified`, `insiders/pay-test-awakened`
- DIFFERENT path (Claude proxy chat): `index.html` (homepage)

## Pipeline Failure Chain

1. Customer clicks "Begin Awakening" -> `startConversation()` undefined -> nothing happens.
2. Customer scrolls past "broken" chat, clicks PayPal subscribe.
3. `createSubscription` (line 5132) does NOT pass `custom_id` (only one-time orders at line 5163 do). UUID never threads to PayPal.
4. `verifyPaymentServerSide` POSTs `{orderId, tier, payerInfo, sessionUuid:""}`.
5. `handlePaymentSuccess` runs but `window.onPaymentComplete` is never defined on partnered/, so `initPayTestFlow` never starts. Post-payment questionnaire never collects email. `fireSeed()`/`/api/send-seed` never fires.
6. `/api/verify-payment` fires seed dispatcher with empty UUID. S1-S4 all 0. S5-payerName fuzzy-matches "Jay" -> 26 of Jay Hutton's messages -> Sheila bound to Torque container.

## Why This Wasn't Caught

- Chat UI markup looks normal. Header, "online" indicator, input field, "Begin Awakening" button all render.
- No JS console error visible to user (handler just silently does nothing).
- No telemetry that the chat *should* fire but didn't.
- Production deploys came from a template fork that stripped chat handlers but kept markup.

## The Fix Class

1. **Restore handlers** on all 4 production payment pages OR **remove the chat markup entirely** (decision: do customers awaken on payment pages or only on `/`?).
2. **Disable S5-payerName** in `tools/purebrain_log_server.py:1029-1062` OR gate behind email-domain match.
3. **Hard-block** `/api/verify-payment` from firing seed when S2-uuid=0 AND S3-email=0. Queue for human review + Telegram alert.
4. **Thread sessionUuid** into PayPal subscription flow (plan metadata or post-approve link).
5. **Pre-deploy guard**: grep-fail any page with `onclick="startConversation()"` whose script bundle does not export `window.startConversation`.

## Pattern (constitutional)

Whenever a payment page has chat UI markup, the deploy pipeline MUST verify the handlers are defined. Whenever a seed dispatcher has fuzzy-match strategies, they MUST be off-by-default and require explicit enable. Treat any seed dispatch with `S2-uuid=0` AND `S3-email=0` as a hard failure.

## Files Referenced

- `exports/cf-pages-deploy/partnered/index.html:1550, 1557, 5132, 5163, 5705, 6794, 7878, 8210`
- `tools/purebrain_log_server.py:441, 553, 1029-1062`
- `logs/purebrain_log_server.log` (smoking-gun line at 11:54:36.430)
- `.magic-links.json` key `email:Sheila@couplify.com` (corrupted record)
- `exports/portal-files/partnered-conversation-capture-trace-2026-05-07.md` (deliverable)
- `exports/portal-files/sheila-keeper-seed-trace-2026-05-07.md` (prior trace)
