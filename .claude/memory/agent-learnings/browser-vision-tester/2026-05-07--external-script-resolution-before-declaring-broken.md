# External Script Resolution Before Declaring a Page Broken

**Date**: 2026-05-07
**Type**: gotcha
**Confidence**: high
**Tags**: verification, source-inspection, false-positives, payment-pages

---

## Context

Verifying 5 LIVE awakening pages (`/`, `/awakened/`, `/partnered/`, `/unified/`, `/insiders/`) against `NEW-ONBOARDING-FLOW-SPEC-2026-04-01.md`. Spec §6 requires `window.onPaymentComplete` to fire seed + redirect to `/thank-you/`. Source grep of served HTML showed:

- Homepage: defines `window.onPaymentComplete = function` inline (line 16081) ✅
- `/home-test-sandbox/`: defines inline (line 16013) ✅
- `/awakened/`, `/partnered/`, `/unified/`, `/insiders/`: **0 inline definitions** — looks broken

Almost dispatched a fix sprint based on this finding.

## What I Did Right

Before writing the deliverable, I grepped for `<script src=` on the 4 "broken" pages and noticed they include `<script src="/js/payment-glue.js">` while the homepage does NOT. The homepage and sandbox define `onPaymentComplete` inline because they're full deploy variants; the 4 single-tier pages share a common glue file.

Curl'd `https://purebrain.ai/js/payment-glue.js` (HTTP 200, 173 lines) and found `window.onPaymentComplete = function(tier, orderId, payerInfo) { ... /thank-you/?aiName=...&name=...&email=...&tier=... }` defined identically with 300ms delay.

## The Gotcha

**Modern static-deploy patterns split critical JavaScript across multiple files.** A page can be 100% spec-compliant with ZERO inline definitions of a function — the function lives in an external file loaded via `<script src=>`. Source-of-truth verification MUST follow external script references before declaring a page broken.

## Verification Workflow That Catches This

1. Download served HTML
2. Grep for behavior markers (function definitions, redirects, etc.)
3. **If markers absent**: grep for `<script src=` and resolve every external JS file
4. Repeat behavior-marker grep on resolved external files
5. Only then write verdict

## When to Apply

- Any payment page verification
- Any behavior-vs-spec audit on static deploys
- Any "is X function defined?" check
- Especially when spec compliance matters legally/financially

## Customer Impact of Almost Getting This Wrong

Would have triggered an unnecessary fix sprint on 4 production payment pages that ARE working correctly. False-positive cost: dev time + risk of introducing bugs while "fixing" non-broken code.

## Path Reference

Deliverable: `exports/portal-files/5-page-definitive-verification-2026-05-07.md`
Spec: `exports/portal-files/NEW-ONBOARDING-FLOW-SPEC-2026-04-01.md` §6, §16
External glue: `https://purebrain.ai/js/payment-glue.js`
