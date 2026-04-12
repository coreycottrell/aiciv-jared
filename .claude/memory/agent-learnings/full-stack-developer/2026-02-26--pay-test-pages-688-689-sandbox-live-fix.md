# Memory: Pay Test Pages 688/689 — Sandbox/Live Fix

**Date**: 2026-02-26
**Type**: operational + teaching
**Topic**: Fixed pay-test-sandbox-2 (688) with sandbox client ID + banner; fixed pay-test-2 (689) with live plan IDs

---

## What Was Done

### Page 688 (pay-test-sandbox-2) — SANDBOX
- Changed `PAYPAL_CLIENT_ID` from LIVE to SANDBOX: `AYTFob05DoSn0ZeVtLJ05duKwFHOdAckHgkZ2UJhAXvfJlUXEYM_PFib3HbIuVgauxV_6clZ5FdPRYq_`
- Added orange sandbox banner (`id="sandbox-banner"`) after second `<body>` tag
- Banner text: "⚠️ SANDBOX MODE — No real charges will occur. Use PayPal sandbox test accounts only."
- PLAN_IDS left as empty strings (sandbox plan IDs not available — see note below)
- WITNESS_WEBHOOK_HOST left as `https://89.167.19.20:8443` (unchanged)

### Page 689 (pay-test-2) — LIVE
- Kept `PAYPAL_CLIENT_ID` as LIVE: `AWgWNlBQAy5BMXKB5xbaMwSk01WkatC08b5rTj_JKu4Jm2JugXvjAwMRyNe1FmabNS9v846Rma5ptxhI`
- Filled in LIVE plan IDs:
  - Awakened: `P-1AG936074F0953120NGLTFKY` ($79/mo)
  - Bonded: `P-2SA65600MT088594TNGLTFKY` ($149/mo)
  - Partnered: `P-3VH43554A66001716NGLTFKY` ($499/mo)
  - Unified: `P-43A28944XN5237411NGLTFLA` ($999/mo)
- No sandbox banner added

---

## Sandbox Plan IDs — Known Issue

The PayPal sandbox credentials in `.env` (`PAYPAL_SANDBOX_CLIENT_ID` / `PAYPAL_SANDBOX_SECRET`) are returning `invalid_client` (401) when used against `api-m.sandbox.paypal.com`.

**Diagnosis**: These credentials may be expired or from a buyer sandbox test account rather than a developer/merchant sandbox app. Sandbox credentials need to be regenerated at developer.paypal.com → My Apps & Credentials → Sandbox.

**Impact on page 688**: With empty PLAN_IDS, the PayPal SDK falls back to one-time payment flow instead of subscription. The sandbox client ID still ensures no real charges. For full subscription testing in sandbox, Jared needs to:
1. Go to developer.paypal.com
2. Log in with the business PayPal account
3. Go to My Apps → Sandbox credentials
4. Create a sandbox billing product + 4 plans
5. Update page 688 PLAN_IDS with the new sandbox plan IDs

---

## Verification Results

Page 688 live checks:
- Sandbox client ID in rendered HTML: CONFIRMED
- Sandbox banner present: CONFIRMED
- Live client ID count: 0 (correct)

Page 689 live checks:
- Live client ID: CONFIRMED
- All 4 plan IDs present: CONFIRMED
- No sandbox banner: CONFIRMED (count 0)

Both pages HTTP 200 via slug URLs.

---

## Key Technical Notes

- Pages use `<!-- wp:html -->` wrapper — content updated via WP REST API `content` field
- Page has TWO `<body>` tags: outer WP body (line ~1886) and inner app body (line ~4456)
- Sandbox banner was injected after the SECOND `<body>` (the app body), not the WP theme body
- PayPal SDK auto-detects sandbox vs live from the `client-id` query param — no SDK URL change needed
- Live plans confirmed ACTIVE via PayPal API enumeration (182 total plans, 4 PureBrain plans found)

---

## File Modifications (temp files, not committed)

- `/tmp/page688_modified.html` — used for deployment
- `/tmp/page689_modified.html` — used for deployment

