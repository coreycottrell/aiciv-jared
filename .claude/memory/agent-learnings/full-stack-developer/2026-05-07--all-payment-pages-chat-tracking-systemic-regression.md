# All Payment Pages Chat Tracking — Systemic Regression (MED-003 scope bug)

**Date**: 2026-05-07
**Type**: gotcha
**Discovered while**: Auditing parity across all 10 live payment pages after Sheila Keeper cross-contamination.

## TL;DR
A security hardening commit tagged `MED-003` removed `window.payTestData` from global exports across every payment page template. Chat-side logger still reads `payTestData` via bare global symbol. Because `payTestData` is declared `const` inside a separate inline `<script>` tag from the chat code, it is invisible to the chat code. Every payment-page chat conversation logged since MED-003 has `session_uuid: null`. The dispatcher's S2-uuid lookup never matches; pages fall through to S5-payerName fuzzy match — same failure class as Sheila.

## What works (the trap)
- `crypto.randomUUID` populates `payTestData.sessionUuid` correctly.
- `sessionStorage.setItem('pb_sessionUuid', ...)` mirrors it.
- The chat code uses `typeof payTestData !== 'undefined' ? payTestData.sessionUuid : null`.
- This APPEARS defensive but silently turns into `null` on every load because `const payTestData = {}` does NOT create a `window.payTestData` property in classic (non-module) `<script>` blocks. Each `<script>` tag has its own top-level lexical scope.

## Why /partnered/ "worked" before
Either S1-orderId fired (one-time `createOrder` paths still embed `custom_id`) OR S4-recent fired (same-session pay within 30 min of chat). Subscriptions carry no `custom_id`, so S1 cannot fire. Slow subscribers (capture >30 min later) drop into S5.

## Pages affected (all 10 live)
- `/`, `/awakened/`, `/insiders/`, `/insiders/awakened/`, `/insiders/pay-test-awakened/`, `/partnered/`, `/unified/`, `/home-test/`, `/home-test-live-1/`, `/home-test-sandbox/`

## File:line evidence
- MED-003 marker: `partnered/index.html:5632`, `awakened/index.html:5563`, `insiders/index.html:5444`, `insiders/awakened/index.html:5419`, `unified/index.html:5580`.
- Chat-side scope-blind read: `js/payment-background.js:414`, `js/payment-background.js:421`.
- Inline-page chat-side scope-blind read: `index.html:10395`.
- payTestData declaration: `partnered/index.html:5676` (inside `<script>` 5670-…), declared with `const`.
- Chat code script-tag boundaries (homepage): 9983-11574 vs payTestData 13309-16050.
- Subscription-button missing custom_id: `partnered/index.html:5132-5140` (no `custom_id` field). One-time `createOrder` at `partnered/index.html:5163` does have `custom_id` (with same scope-blind read).
- Dispatcher S2 read: `tools/purebrain_log_server.py:988-994`.

## Forward fix candidates
1. Append `window.payTestData = payTestData;` at end of declaration script tag on every page.
2. Or change `const payTestData =` to `var payTestData =` (var IS hoisted as a window property in classic script context).
3. Add `subscriber.custom_id` (or `application_context.custom_id`) to every subscription `createSubscription` block.
4. Disable S5-payerName until (1) and (3) land + a permanent guard that fails-red on any S5 win.
5. Constitutional guard: deploy-time headless test posts one chat exchange per payment page and asserts the JSONL line has non-null `session_uuid`.

## Why this matters / why it's a gotcha
- Defensive `typeof X !== 'undefined'` LOOKS bulletproof but silently degrades when X is in another `<script>` tag.
- `const` and `let` at script top-level look like globals but aren't.
- Removing `window.X` exports as a "security hardening" without auditing readers is the second-order bug.

## What the dispatcher expects
- `session_uuid` (top-level) OR `metadata.sessionUuid` populated when chat POSTs to `/api/log-conversation`.
- Either one being non-null makes S2 deterministic and avoids fuzzy fallbacks.

## Cross-references
- `exports/portal-files/sheila-keeper-seed-trace-2026-05-07.md`
- `exports/portal-files/all-payment-pages-chat-tracking-audit-2026-05-07.md`
- `feedback_seed_flow_never_deviate.md` (AI-name-must-populate)
- `feedback_magic_link_pipeline_constitutional.md` (UUID pipeline lock)
