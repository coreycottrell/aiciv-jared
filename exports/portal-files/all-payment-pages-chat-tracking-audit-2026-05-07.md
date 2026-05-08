# All Payment Pages — Chat Tracking Parity Audit (2026-05-07)

**Author**: WTT (full-stack-developer). **Trigger**: Sheila Keeper cross-contamination (`exports/portal-files/sheila-keeper-seed-trace-2026-05-07.md`). **Mode**: READ-ONLY.

## 1. Page Enumeration (10 live payment pages)

All 10 have BOTH awakening chat UI AND PayPal subscribe buttons. No NO-CHAT-PURE-CHECKOUT pages in the in-scope set.

| Page | Path | Architecture |
|---|---|---|
| `/` (homepage) | `cf-pages-deploy/index.html` | Inline-chat |
| `/awakened/` | `awakened/index.html` | External `payment-background.js` |
| `/insiders/` | `insiders/index.html` | External `payment-background.js` |
| `/insiders/awakened/` | `insiders/awakened/index.html` | External `payment-background.js` |
| `/insiders/pay-test-awakened/` | `insiders/pay-test-awakened/index.html` | Inline-chat |
| `/partnered/` (KNOWN BROKEN) | `partnered/index.html` | External `payment-background.js` |
| `/unified/` | `unified/index.html` | External `payment-background.js` |
| `/home-test/` | `home-test/index.html` | Inline-chat |
| `/home-test-live-1/` | `home-test-live-1/index.html` | Inline-chat |
| `/home-test-sandbox/` | `home-test-sandbox/index.html` | Inline-chat |

## 2. Per-Page Check Matrix

Checks: (1) chat UI, (2) `/api/log-conversation` POST, (3) `session_uuid` generated, (4) `session_uuid` threaded to PayPal **subscription** button, (5) email captured pre-payment, (6) S1–S4 reachable.

| Page | 1 | 2 | 3 | 4 (subs) | 5 | 6 | Grade |
|---|---|---|---|---|---|---|---|
| `/` | ✓ `index.html:8478` | ✓ `index.html:10381,13551` | ✓ `index.html:13464` (randomUUID) | **FAIL** subs path no `custom_id` | partial (post-pay only) | **FAIL** scope bug | 🔴 |
| `/awakened/` | ✓ `awakened/index.html:1556` | ✓ `payment-background.js:432` | ✓ `awakened/index.html:5651` | **FAIL** | FAIL | **FAIL** scope bug | 🔴 |
| `/insiders/` | ✓ | ✓ | ✓ | **FAIL** | FAIL | **FAIL** | 🔴 |
| `/insiders/awakened/` | ✓ | ✓ | ✓ | **FAIL** | FAIL | **FAIL** | 🔴 |
| `/insiders/pay-test-awakened/` | ✓ | ✓ inline | ✓ | **FAIL** | partial | **FAIL** scope bug | 🔴 |
| `/partnered/` | ✓ `partnered/index.html:1556` | ✓ `payment-background.js:432` | ✓ `partnered/index.html:5705` | **FAIL** `partnered/index.html:5132-5140` no `custom_id` (only `createOrder` at `:5163` does) | FAIL | **FAIL** `partnered/index.html:5632` MED-003 + `payment-background.js:414` cross-`<script>` `const` invisibility ⇒ session_uuid null. **SHEILA FAILURE.** | 🔴 |
| `/unified/` | ✓ | ✓ | ✓ | **FAIL** | FAIL | **FAIL** | 🔴 |
| `/home-test/` | ✓ | ✓ inline | ✓ | **FAIL** | partial | **FAIL** | 🔴 |
| `/home-test-live-1/` | ✓ | ✓ inline | ✓ | **FAIL** | partial | **FAIL** | 🔴 |
| `/home-test-sandbox/` | ✓ | ✓ inline | ✓ | **FAIL** | partial | **FAIL** | 🔴 |

MED-003 markers: `partnered/index.html:5632`, `awakened/index.html:5563`, `insiders/index.html:5444`, `insiders/awakened/index.html:5419`, `unified/index.html:5580`. Inline pages have the same `const payTestData` declared in a different `<script>` block from chat code (homepage: chat 9983-11574 vs payTestData 13309-16050).

Synthetic test deferred — every page already RED; no GREEN to validate.

## 3. Severity Grades

- 🟢 GREEN: **0** | 🟡 YELLOW: **0** | 🔴 RED: **10** — every live payment page is at Sheila's failure class.

## 4. Root-Cause Hypothesis (SYSTEMIC)

A security hardening commit tagged `MED-003` removed `window.payTestData` from global exports across every payment template. The chat layer (`js/payment-background.js:414`, `index.html:10395`) still reads `payTestData` via bare `typeof payTestData !== 'undefined'`. Because `payTestData` is `const` inside a separate inline `<script>` tag, it is NOT promoted to a window property and is invisible across script tags. **Every chat POST since MED-003 shipped has `session_uuid: null` AND `metadata.sessionUuid: null`.** Dispatcher S2-uuid (`tools/purebrain_log_server.py:988-994`) never matches. S3-email never matches because the awakening chat doesn't collect email pre-payment. S1-orderId never matches for subscriptions (no `custom_id` in `createSubscription`). S4-recent fails when capture fires >30 min after chat. **Every payment falls to S5-payerName** — same fuzzy fallback that bound Sheila's $499 to Jay Hutton. Jared's memory of /partnered/ "working a few days ago" is likely S1 (one-time `createOrder` with `custom_id`) or S4-recent — coincidence, not real linkage.

## 5. Constitutional Gap

No alarm when S5 fires. No nightly assertion that `session_uuid` is non-null in `logs/purebrain_web_conversations.jsonl`. No server-side check that subscription `custom_id` arrives populated. Recommended guard: nightly fail-red on any S5-bound payment in 24h, plus deploy-time headless test asserting each payment page logs `session_uuid != null` after one chat exchange.

## 6. Recommended Fix Path (CTO gate)

1. **One-line forward-fix per template**: after `const payTestData = {...}`, add `window.payTestData = payTestData;`. Or change `const` → `var` (var IS a window property in classic scripts). Re-exposes reference without re-introducing MED-003's mutation surface.
2. **Add `custom_id` to every `createSubscription` block**: PayPal subscriptions accept `subscriber.custom_id` / `application_context.custom_id`. Belt-and-suspenders.
3. **Disable S5-payerName** until (1) and (2) land. S5 violates `feedback_seed_flow_never_deviate.md` (AI name must be authoritative).
4. **Block subscription-only seeds when session_uuid empty AND email has zero chat history**. Telegram-alert Jared rather than mis-route.

**Most-at-risk page besides /partnered/**: `/insiders/awakened/` and `/awakened/` — same external `payment-background.js` + same MED-003 scope bug + currently-promoted subscription tier (Awakened $149/mo). Highest live-traffic surface for the same exact failure.

## Memory Written
Path: `.claude/memory/agent-learnings/full-stack-developer/2026-05-07--all-payment-pages-chat-tracking-systemic-regression.md`
Type: gotcha
Topic: MED-003 cross-`<script>` `const` invisibility nulls session_uuid on all 10 payment pages.
