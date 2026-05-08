# Payment Pages Comprehensive Audit — 2026-05-07

**Type**: operational + teaching
**Task**: Full audit of 12 payment pages against constitutional onboarding spec (NEW-ONBOARDING-FLOW-SPEC-2026-04-01.md)

## Key Findings

### Systemic (all 12 pages RED)
- MED-003 security commit removed `window.payTestData` but left all PayPal script blocks reading `typeof payTestData !== 'undefined'` — cross-`<script>` `const` scope means UUID is always null. Fix: `window.pbSessionUuid = payTestData.sessionUuid;` after generation.
- No `createSubscription` call on any page carries `custom_id` with session UUID. Subscriptions are the primary product. S1 strategy always misses on subscription payments.
- S5-payerName fuzzy fallback in `tools/purebrain_log_server.py:1060-1062` caused Sheila → Jay container collision. Must be disabled immediately.

### Post-Payment Flow Split (8 pages wrong)
- Spec Section 6 mandates: `onPaymentComplete` → `fireSeed()` → 300ms → redirect to `/thank-you/`
- Only 4 of 12 pages implement this: `/` (homepage), `/home-test/`, `/home-test-live-1/`, `/home-test-sandbox/`
- 8 pages still use the old in-chat `runThankYouMessage` flow (explicitly REMOVED per Spec Section 16 Rule 5): `/live/`, `/awakened/`, `/partnered/`, `/unified/`, `/insiders/`, `/insiders/awakened/`, `/pay-test-sandbox-3/`, `/pay-test-sandbox-5/`
- LIVE subscription pages `/awakened/`, `/partnered/`, `/unified/` never register `window.onPaymentComplete` — the PayPal callback fires but nothing redirects.

### Per-Message Logging Split
- Pages using `payment-background.js` (awakened, partnered, unified, insiders, insiders/awakened): only log ONCE post-payment via `logPayTestData`. Pre-payment chat is never captured in JSONL.
- Homepage has full `logConversationToBackend('message_exchange')` per-message. That function needs extracting to shared JS.

### Thank-You Page Issues
- Exists at `exports/cf-pages-deploy/thank-you/index.html`
- Polls by email key (`email:${email}`) not by UUID — email fallback path only
- Does NOT parse `tier` URL param despite spec including it
- Shows correct "Enter [AI Name]'s Brain Stream" button text

## Architecture Pattern
- Two distinct architectures: external `payment-background.js` (5 pages) vs inline (7 pages)
- Consent gate is the ONE section with perfect compliance across all 12 pages
- Fix strategy: shared `window.pbSessionUuid`, shared `onPaymentComplete` redirect handler, per-message logging in `payment-background.js`

## Fix Sequence (constitutional)
1. TODAY: Disable S5 dispatcher (emergency)
2. Day 1-2: UUID thread fix + custom_id to createSubscription
3. Day 2-4: Migrate 8 pages to /thank-you/ redirect
4. Day 3-5: Per-message logging in payment-background.js
5. Day 4-5: Thank-you page UUID polling + monitoring canaries
6. Day 5: Gitignore state files

Total: 9 engineer-days

## Deliverable
`exports/portal-files/payment-pages-fix-plan-2026-05-07.md`
