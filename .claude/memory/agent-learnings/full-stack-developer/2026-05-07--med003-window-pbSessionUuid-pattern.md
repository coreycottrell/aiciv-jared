# MED-003 `window.pbSessionUuid` Escape-Hatch Pattern

**Date**: 2026-05-07
**Type**: teaching
**Topic**: how to thread a single field across multiple inline `<script>` tags + external JS without violating PII scope-isolation

---

## Context

MED-003 made `payTestData` const-scoped inside one inline script tag for PII protection (aiName, name, email). That broke 4 cross-scope readers that legitimately needed only the random `sessionUuid`:
- PayPal createOrder/createSubscription `custom_id`
- verifyPaymentServerSide POST body
- payment-background.js chat logger
- homepage-payment.js verify + custom_id

Result: `session_uuid: null` in chat logs → S5-disabled hard-block in dispatcher → Sheila/Couplify household-payer routing broke 2026-05-07.

## Pattern

**Expose ONLY the random non-PII field on `window`** as a minimal projection of payTestData. Place the assignment IMMEDIATELY after `crypto.randomUUID()` runs (NOT after the `const payTestData = {...}` literal, which initializes sessionUuid as null).

```javascript
payTestData.sessionUuid = (crypto.randomUUID ? crypto.randomUUID() : '...');
window.pbSessionUuid = payTestData.sessionUuid; // MED-003 escape hatch
```

Cross-scope readers then use `window.pbSessionUuid || ''` instead of `(typeof payTestData !== 'undefined' && payTestData.sessionUuid)`.

## Why It's Race-Safe

Classic-script `<script>` tags are parsed and executed synchronously top-to-bottom. By the time:
- a chat-message event fires (user action) → payment-background.js logger reads window.pbSessionUuid ✓
- a Subscribe/Pay button is clicked → PayPal SDK calls createSubscription/createOrder ✓
- a deferred IIFE invokes showPricing() → reads payTestData.aiName ✓

…the inline script tag containing `payTestData.sessionUuid = crypto.randomUUID()` has already run.

## Why aiName Is NOT Migrated

Migrating `awakened/index.html:2414` `payTestData.aiName` read to window would expose aiName globally → MED-003 PII violation. Today it works via deferred-IIFE invocation (showPricing only fires after naming-ceremony completion, by which time payTestData script has executed). Leave it alone.

## createSubscription Custom_id Gap (BONUS FIX)

createSubscription on all 5 LIVE pages had NO custom_id field at all (separate bug from MED-003 — pre-existed, just now fixed in same sprint). Without it, every recurring-subscription payment is opaque to dispatcher S1 (custom_id parse) → falls to S3-email or S5-blocked → manual review queue. PayPal SDK accepts `custom_id` as a top-level param in `actions.subscription.create({})` — same format as createOrder.

## Verification Pattern (SHIP gate)

Static-source grep is sufficient for deploy gate when:
1. Pattern is unique enough to not false-positive (`window.pbSessionUuid = payTestData.sessionUuid`)
2. Both positive (must contain new pattern) AND negative (must NOT contain legacy `(typeof payTestData !== 'undefined' && payTestData.sessionUuid)`) assertions are run
3. Script runs <2s so it can be a pre-commit/CI hook
4. Has a `--live` mode for post-deploy verification against served HTML

Full E2E (browser + network capture + dispatcher round-trip) is still required separately — this script is the *cheap fast* gate, not the *complete* gate.

## File Paths Referenced

- `exports/cf-pages-deploy/{,awakened,partnered,unified,insiders}/index.html`
- `exports/cf-pages-deploy/js/payment-background.js`
- `exports/cf-pages-deploy/js/homepage-payment.js`
- `tools/verify-payment-pages-pbsessionuuid.sh` (new, this commit)
- `exports/portal-files/cto-prebuild-review-med003-fix-2026-05-07.md`
- `exports/portal-files/NEW-ONBOARDING-FLOW-SPEC-2026-04-01.md`

## Commit

`250f5f5` on `main` (worktree at `/tmp/aether-main-wt`). NOT pushed.

## Gotchas Future Agents Should Know

1. **`/home/jared/projects/AI-CIV/aether` may be on a feature branch**. `main` is checked out at `/tmp/aether-main-wt` as a worktree. Don't `git checkout main` in the primary path — it'll fail. `cd` to the worktree instead.
2. **Insiders page is older** — has UUID generation but NO `sessionStorage.setItem('pb_sessionUuid', ...)` line. Don't blindly look for that anchor; use the `crypto.randomUUID()` line as the anchor instead.
3. **createSubscription functions appear at lower line numbers than UUID generation** in some pages. The function DEFINITION is parsed then; the function INVOCATION happens on user click after page load. `window.pbSessionUuid` will be set by then.
4. **Don't migrate `payTestData.aiName` reads**. The deferred-IIFE pattern works today; migrating would violate MED-003 PII intent.
