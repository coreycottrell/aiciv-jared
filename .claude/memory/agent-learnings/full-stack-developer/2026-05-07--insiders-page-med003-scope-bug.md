# /insiders/ page — MED-003 const-scope bug + missing subscription custom_id

**Date**: 2026-05-07
**Type**: operational
**File**: `exports/cf-pages-deploy/insiders/index.html` (live: `https://purebrain.ai/insiders/`)

## Finding

`/insiders/` is a full awakening page (chat UI + Witness birth pipeline), password-gated by `PureBrainInviteOnly26+` (line 533). It shares the same MED-003 scope bug as the other 4 audited pay-test pages, plus an additional gap.

## Root cause

Two separate `<script>` tags carry the integration:
- PayPal block: `<script>` at line 4421 → `</script>` at 5375.
- Pay-test-chat-flow block: `<script>` at line 5377 → `</script>` at 8108. Declares `const payTestData` at line 5488. Hardens MED-003 by NOT exposing payTestData on window (lines 8104–8108).

`const` is scoped to its own script tag. The PayPal block's `typeof payTestData !== 'undefined'` checks (lines 4880, 4975) therefore evaluate FALSE → custom_id falls back to `'PB-TIER-'` with empty UUID, sessionUuid in verify POST is `''`.

## Additional gap unique to this audit

`createSubscription` (line 4944–4951) carries NO custom_id field at all. So even if MED-003 is patched on the order path, subscription path remains opaque to the dispatcher.

## Fix pattern (applies to all 6 pages)

Expose just the UUID string on window (low sensitivity, already threaded in 7+ places):

```js
// after line 5517
window.pbSessionUuid = payTestData.sessionUuid;
```

Then in PayPal block:
- Replace `typeof payTestData !== 'undefined' && payTestData.sessionUuid` with `window.pbSessionUuid || ''` at lines 4880, 4975.
- Add a custom_id-bearing field to `createSubscription` (subscriber.custom_id or plan metadata).

## Why this matters

Prevents conversation logs (which DO carry session_uuid) from being orphaned from their PayPal payment. Currently dispatcher must fall back to email correlation, which fails when email isn't captured pre-payment.

## Related artifacts

- Spot-check report: `exports/portal-files/insiders-page-tracking-spotcheck-2026-05-07.md`
- Parity audit (referenced in task brief): `exports/portal-files/all-payment-pages-chat-tracking-audit-2026-05-07.md`
