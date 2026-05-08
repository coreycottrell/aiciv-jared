# /insiders/ Page — Chat-Tracking & Payment-Threading Spot-Check

**Date**: 2026-05-07
**Auditor**: WTT (Witness Tech Team full-stack)
**File audited**: `/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/insiders/index.html` (8118 lines)
**Live URL**: `https://purebrain.ai/insiders/`
**Page type**: Password-gated insider awakening page (gate at line 518–533, password `PureBrainInviteOnly26+`)

---

## Classification: CHAT UI PRESENT (full awakening flow)

This is NOT a pure-checkout page. It carries the same post-payment awakening chat flow as the other 5 audited pages.

- "Begin Awakening" CTA — line 1423
- Post-Payment Chat Flow v4.7 — line 5378 (full pay-test-chat-flow-v4.js inlined, 5378–8108)
- Witness birth pipeline — `runBirthInit` calls `https://api.purebrain.ai/api/birth/start` at line 7446, `/api/birth/code` at 7638, `/api/send-seed` at 7720, `/api/seed-addendum` at 7780, magic-link poller at 7902–7916.

---

## 6-Check Audit

| # | Check | Result | Evidence |
|---|-------|--------|----------|
| 1 | Chat UI present? | YES | "Begin Awakening" CTA line 1423; full v4.7 chat flow 5378–8108 |
| 2 | Capture endpoint? | YES — `https://api.purebrain.ai/api/log-pay-test` (line 5610) and `/api/log-conversation` (line 5618), 4s fire-and-forget |
| 3 | session_uuid generated & threaded? | YES generated (line 5517 `crypto.randomUUID`) and threaded into log payloads (lines 5543, 5588) and birth/seed POSTs (lines 7711, 7762) |
| 4 | customer_email captured pre-payment? | NO — email captured only post-PayPal-approve from `payerInfo.email_address` (line 5202–5204), POSTed to `/api/referral/complete`. No pre-payment email field is sent to capture endpoints; gate password (line 533) is not user email. |
| 5 | MED-003 `window.payTestData` scope bug? | **YES — SAME BUG AS OTHER 4 PAGES** (see below) |
| 6 | Dispatcher findability (S1–S4)? | DEGRADED — see below |

### MED-003 evidence (the smoking gun)

- Line 4421 opens `<script>` for PayPal block. Line 5375 closes it.
- Line 5377 opens a NEW `<script>` for pay-test-chat-flow.
- Line 5488 declares `const payTestData = { … }` — `const` is scoped to its own script tag.
- Line 8104–8108 explicitly comments: *"MED-003: Only expose the public entry point on window. payTestData and logPayTestData must not be readable…"* — `window.initPayTestFlow` is set, but `window.payTestData` is intentionally NOT.
- Line 4975 (PayPal `createOrder`, in the EARLIER script block) reads:
  ```js
  custom_id: 'PB-' + tier.toUpperCase() + '-' + ((typeof payTestData !== 'undefined' && payTestData.sessionUuid) ? payTestData.sessionUuid : '')
  ```
- Line 4880 (`verifyPaymentServerSide`) does the same `typeof payTestData` check.
- **Result**: `typeof payTestData` evaluates to `'undefined'` from the PayPal script's scope → custom_id falls back to `'PB-INSIDER-'` with empty session_uuid; verification POST sends `sessionUuid: ''`.

### Dispatcher findability (S1–S4)

- S1 (custom_id lookup): **BROKEN** — custom_id missing UUID suffix, only carries tier.
- S2 (subscription createSubscription custom_id): **NOT IMPLEMENTED** — line 4944–4951 `actions.subscription.create` carries only `plan_id` + `application_context`, no `custom_id` at all.
- S3 (email correlation): partially possible — `/api/referral/complete` (5198–5210) sends `customer_email` + `payment_id` + `source_page: 'insiders'`, so dispatcher could correlate via PayPal payer email IF chat capture also has that email — but customer_email is only captured into `payTestData.email` mid-questionnaire, not always pre-payment.
- S4 (orderId match): possible — orderId saved post-capture (line 4988 `actions.order.capture()`), but conversation log fires earlier in the flow with session_uuid, not orderId, as primary key.

---

## Severity: 🔴 RED

Same root cause and same risk class as the prior 4 pages flagged in the parity sweep. Conversation logs (`/api/log-conversation`) carry a real session_uuid; PayPal payments do NOT — they carry `'PB-INSIDER-'` (no UUID) for orders and nothing for subscriptions. Result: a paying insider's pre-payment chat history cannot be deterministically joined to their PayPal payment without manual email correlation.

---

## PayPal Subscription/Order Threading

| Path | custom_id carries sessionUuid? | Status |
|------|-------------------------------|--------|
| `createOrder` (one-time) line 4971–4985 | NO (scope bug, evaluates to `'PB-TIER-'`) | 🔴 |
| `createSubscription` line 4944–4951 | NO field at all (no custom_id used) | 🔴 |

Same risk class as the other 5 pages.

---

## Recommended Fix (one-liner, applies to all 6 pages)

In `pay-test-chat-flow-v4.js` (or in this inlined block at line 5517), after generating `payTestData.sessionUuid`, also expose it on `window`:

```js
window.pbSessionUuid = payTestData.sessionUuid;
```

Then in PayPal block change lines 4880 + 4975 from `typeof payTestData !== 'undefined' && payTestData.sessionUuid` to `window.pbSessionUuid || ''`. Add `custom_id: 'PB-INSIDER-' + (window.pbSessionUuid || '')` to the `createSubscription` `application_context` as well (PayPal supports custom_id on subscriptions via `subscriber.custom_id` or plan metadata).

This preserves MED-003 (no full payTestData on window — only a UUID string, which is non-sensitive and already threaded in seven other places).

---

## Memory Search Results
- Searched: `.claude/memory/` for "MED-003 payTestData scope" and "insiders payment" — no prior agent-learning matches under wtt/full-stack-developer.
- Applying: pattern recognized from the parity audit referenced in the task brief (`exports/portal-files/all-payment-pages-chat-tracking-audit-2026-05-07.md`).

## Memory Written
- Path: `.claude/memory/agent-learnings/full-stack-developer/2026-05-07--insiders-page-med003-scope-bug.md`
- Type: operational
- Topic: Confirmed `/insiders/` shares MED-003 const-scope bug; createSubscription path also missing custom_id entirely.
