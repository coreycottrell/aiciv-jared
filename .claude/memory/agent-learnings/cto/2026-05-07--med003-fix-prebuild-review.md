# CTO Pre-Build Review — MED-003 sessionUuid Scope-Bug Fix

**Date**: 2026-05-07
**Type**: teaching + operational
**Topic**: window.pbSessionUuid as minimal-projection escape hatch from MED-003 const-scope isolation
**Verdict**: GO-WITH-EDITS

## Context

Sheila Keeper incident this morning: household-payer paid for someone else, S5 fuzzy-name fallback misrouted seed to a different "Jay". S5 disabled in commit 775c840. Remaining gap: when chat-logger writes `session_uuid: null` (because `payTestData` is `const`-scoped, invisible across `<script>` tags), S2-uuid strategy can't match → S3-email saves solo payers but household payers hard-block.

## Key teaching

**`const X` at script top-level does NOT create `window.X` in classic `<script>` tags.** Each tag has its own top-level lexical scope. `typeof X !== 'undefined'` from a sibling `<script>` evaluates FALSE silently. This was the root cause of MED-003's second-order bug.

**Minimal-projection fix pattern**: When you need to share ONE field across script-tag boundaries while keeping a sensitive object scope-isolated, project just the safe field onto window. `window.pbSessionUuid` exposes a random UUID (useless without dispatcher DB access) while keeping email/name/aiName scope-protected.

## Architecture facts verified

- 5 LIVE pages: `index.html`, `awakened/`, `partnered/`, `unified/`, `insiders/`, `insiders/awakened/` (parity audit says 10 if you include home-test variants — brief says 5).
- payTestData declaration site is consistent: line 5607 (awakened), 5676 (partnered), 13420 (homepage), 5488 (insiders), 5463 (insiders/awakened), 5624 (unified).
- UUID generation happens on the line AFTER the `const payTestData = {...}` literal (the literal initializes sessionUuid: null). Window assignment must go AFTER the crypto.randomUUID line, not after the literal.
- showPricing in awakened/2414 reads payTestData.aiName from a DIFFERENT script tag — works today because the IIFE defers invocation until after payTestData script has executed. Don't migrate (PII concern).

## Critical reader sites that MUST be migrated to window.pbSessionUuid

- `verifyPaymentServerSide` sessionUuid field (one per page, ~line 4999-12837)
- PayPal `createOrder` custom_id field (one per page)
- `js/payment-background.js:414, 421` — log-conversation POST (loaded by awakened/)
- `js/homepage-payment.js:457, 552` — homepage variant

## Scope creep avoided

The brief's "fix the 5 LIVE pages" misses the cross-file readers. Without migrating `payment-background.js` and `homepage-payment.js` in the same sprint, the inline-page fix is half a fix.

## Subscription custom_id gap

Separate from this fix: every page's `createSubscription` block has NO `custom_id` field at all. Recurring-subscription payments will continue to be S1-opaque post-fix. Flagged as required follow-up ticket within 48h, NOT a blocker for this sprint.

## Test plan inadequacy

Sandbox PayPal click-through is what produced MED-003 in the first place — same gap can ship again. Required SHIP gate additions:
1. Headless: assert `window.pbSessionUuid` is a UUID v4 after page load
2. Network capture: assert verify POST body has sessionUuid != ""
3. Dispatcher round-trip: tail JSONL, confirm session_uuid != null
4. Regression on 4 sandbox/test pages (same pattern, not in scope but at risk)

## Files referenced

- Review deliverable: `exports/portal-files/cto-prebuild-review-med003-fix-2026-05-07.md`
- Spec: `exports/portal-files/NEW-ONBOARDING-FLOW-SPEC-2026-04-01.md` §2, §5, §6, §16
- Prior memory: `.claude/memory/agent-learnings/full-stack-developer/2026-05-07--all-payment-pages-chat-tracking-systemic-regression.md`
- Prior memory: `.claude/memory/agent-learnings/full-stack-developer/2026-05-07--insiders-page-med003-scope-bug.md`
- Prior memory: `.claude/memory/agent-learnings/full-stack-developer/2026-05-07--s5-disable-ship-and-nameerror-postmortem.md`

## Tags

cto, prebuild-review, MED-003, payTestData, window-projection, const-scope, onboarding-spec, sessionUuid, paypal-custom-id, dispatcher-S2, security-architecture
