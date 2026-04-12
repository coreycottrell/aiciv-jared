# Memory: pay-test-2 and pay-test-sandbox-2 Are Identical — Critical Bug

**Date**: 2026-02-26
**Type**: operational + teaching
**Topic**: pay-test-2 (page 689) and pay-test-sandbox-2 (page 688) have IDENTICAL raw HTML content — critical production issue discovered during first customer onboarding verification

---

## Critical Finding

Both pages are byte-for-byte identical (MD5: 6e3e05406b14bf9c69a247344e7c82ad, 433326 bytes each).

**This means pay-test-sandbox-2 is using the LIVE PayPal client ID — sandbox customers will be charged real money.**

---

## What Both Pages Currently Have

- **PAYPAL_CLIENT_ID**: `AWgWNlBQAy5BMXKB5xbaMwSk01WkatC08b5rTj_JKu4Jm2JugXvjAwMRyNe1FmabNS9v846Rma5ptxhI` (LIVE client ID — same on both)
- **WITNESS_WEBHOOK_HOST**: `https://89.167.19.20:8443` (production proxy — same on both)
- **PLAN_IDS**: All empty strings `''` — no subscription plan IDs configured on either page
- **BUSINESS_EMAIL**: `support@puremarketing.ai`
- **No sandbox banner**: No "SANDBOX MODE - No real charges" text in the HTML
- **Script version**: Post-Payment Chat Flow v4.7

---

## What pay-test-sandbox-2 SHOULD Have (vs pay-test-2)

For proper sandbox/live separation, sandbox page should have:
1. Sandbox PayPal client ID (starts with `A`, obtained from developer.paypal.com sandbox)
2. `&enable-sandbox` or sandbox env param in PayPal SDK URL (or use sandbox client ID — SDK auto-detects)
3. "SANDBOX MODE — No real charges" banner visible to user
4. Optionally: sandbox webhook host

---

## Historical Context

- Previous audit (2026-02-25) showed sandbox had orange "SANDBOX MODE" banner — this was visual
- Previous memory noted `AYTFob05DoSn0ZeVtLJ05...` as the production client ID on sandbox page
- The current code is v4.7 which superseded the v4.3.3 that had the bypass button
- v4.5 removed hardcoded `aiciv-07` container and sandbox bypass btn
- v4.7 added server-authoritative container + portal domain flex

---

## Page IDs

- pay-test-2 = page ID 689 (LIVE/production)
- pay-test-sandbox-2 = page ID 688 (should be sandbox but currently identical to live)

---

## Action Required

Jared must be informed immediately. Fix needed before customer onboarding:
1. Get sandbox PayPal client ID from developer.paypal.com
2. Update page 688 HTML to use sandbox client ID
3. Add visible sandbox banner to page 688
4. Confirm plan IDs (both pages have empty PLAN_IDS — may need real plan IDs for subscriptions)

