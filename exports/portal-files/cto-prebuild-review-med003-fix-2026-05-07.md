# CTO Pre-Build Review — MED-003 Scope-Bug Fix

**Agent**: cto
**Domain**: Technology Strategy & Architecture
**Date**: 2026-05-07
**Subject**: `window.pbSessionUuid` exposure across 5 LIVE awakening pages
**Spec**: `exports/portal-files/NEW-ONBOARDING-FLOW-SPEC-2026-04-01.md` §2, §5, §6, §16
**Authorization**: Jared (CEO) greenlit at 2026-05-07

---

## 1. Architecture Soundness

**Verdict: SOUND, with one timing caveat.**

`window.pbSessionUuid = payTestData.sessionUuid;` placed immediately after the UUID generation line (e.g. `awakened/index.html:5636`) is correct. `window.X` assignments cross all classic-script lexical boundaries in the same document, so both the PayPal block (separate `<script>` tag) and `payment-background.js` (separate file) will see it.

**Race-condition window**: The chat-side logger in `payment-background.js:414, 421` is defined inside `logConversationToBackend()`, which is called on chat-message events. By the time a user types anything, the inline `<script>` block at line 5496+ has fully executed (synchronous parse-and-run), so `window.pbSessionUuid` is set. **No race.**

**One real edge case**: `awakened/index.html:2414` reads `payTestData.aiName` from a *different* inline script tag (lines 2399-2456). This script defines `showPricing()` inside an IIFE — the IIFE *runs* at parse time, but `showPricing()` is only *invoked* after naming-ceremony completion via `window.closeCelebrationAndShowPricing`. By then the payTestData script has executed. This pattern works today by accident, and it will continue to work. **No fix required for the aiName read** — it is not on the seed-routing critical path.

---

## 2. Other Cross-Scope Reads Audit

I grepped `payTestData` across all 5 LIVE pages and shared JS. **Critical reader sites:**

| File:line | Reader | Field needed | Action |
|---|---|---|---|
| `index.html:12837`, `awakened/index.html:4999`, `partnered/index.html:5068`, `unified/index.html:5016`, `insiders/index.html:~5xxx`, `insiders/awakened/index.html:~5xxx` | `verifyPaymentServerSide` | `sessionUuid` | **MIGRATE to `window.pbSessionUuid`** |
| `index.html:12932`, `awakened/index.html:5094`, `partnered/index.html:5163`, `unified/index.html:~5xxx` | PayPal `createOrder` custom_id | `sessionUuid` | **MIGRATE** |
| `js/payment-background.js:414, 421` (loaded by awakened/) | log-conversation `session_uuid` | `sessionUuid` | **MIGRATE** |
| `js/homepage-payment.js:457, 552` (loaded by `/`) | verify + custom_id | `sessionUuid` | **MIGRATE** |
| `awakened/index.html:2414` | showPricing | `aiName` | **DO NOT migrate** (PII concern, not on seed path, currently works) |

**Reads I checked that are safely intra-scope (no migration needed)**: lines 5636-8228 inside the `payTestData`-owning script — those access `payTestData` directly because they live in the same lexical scope.

**Subscription path gap (HIGH priority)**: `awakened/index.html:5063-5071`, `partnered/index.html:5132-5140`, and homepage `index.html:12901-12911` declare `createSubscription` with NO `custom_id` field at all. **The proposed fix does not address this.** Subscription payments will continue to be opaque to the dispatcher S1 strategy regardless of this fix. See Required Edits §7.

---

## 3. Spec Compliance

- **§2 (`payTestData` data object)**: Spec defines payTestData as the canonical funnel state, not as a global. `window.pbSessionUuid` is a *minimal projection* of one field — does not violate the data-object contract.
- **§5 (PayPal Smart Buttons)**: Spec requires `custom_id` to be `PB-{TIER}-{sessionUuid}` on every order/subscription. Fix restores this for orders. Subscriptions still non-compliant after this fix.
- **§6 (post-payment verification)**: Spec requires sessionUuid in verify POST. Fix restores this.
- **§16 (MED-003 hardening)**: Spec section preserved — payTestData (PII) remains scope-isolated; only the random UUID escapes.

---

## 4. Race-Condition Concern

The `window.pbSessionUuid = payTestData.sessionUuid` line MUST be placed AFTER the UUID generation, not after the `const payTestData = {...}` literal. The literal initializes `sessionUuid: null`. The crypto.randomUUID assignment happens on the next line.

**Required placement**: immediately after `try { sessionStorage.setItem('pb_sessionUuid', payTestData.sessionUuid); } catch(e) {}` (e.g. `awakened/index.html:5637`). The brief's instruction "after `const payTestData = {...}` declaration" is ambiguous — clarify in the BUILD ticket.

---

## 5. Backward-Compat

No code reads `typeof window.pbSessionUuid === 'undefined'` today (verified by grep). Adding the property breaks nothing. Third-party scripts gaining read access to a random UUID is a non-issue (no PII, useless without dispatcher DB).

`sessionStorage.getItem('pb_sessionUuid')` already exists as a fallback in `verifyPaymentServerSide`. After this fix, `window.pbSessionUuid` and `sessionStorage` carry the same value — defensive layering is fine.

---

## 6. Test Plan Adequacy

**Proposed plan (PayPal sandbox E2E + 12 spec checks per page) is INSUFFICIENT for SHIP.** Required additions:

1. **Headless assertion** per page: `window.pbSessionUuid` must be a valid UUID v4 string after page load + 1s.
2. **Network capture** during sandbox PayPal flow: assert the verify-payment POST body contains `sessionUuid: "<uuid>"` (NOT `""`) and the conversation-log POST body contains `session_uuid: "<uuid>"` (NOT `null`).
3. **Dispatcher round-trip** (the only true verification): run a sandbox payment end-to-end on each of the 5 pages, then `tail logs/purebrain_web_conversations.jsonl` and confirm `session_uuid` is non-null. Then trigger a fake payment-verify and confirm S2-uuid strategy fires (not S3 or S5-blocked).
4. **Regression check on 4 sandbox/test pages**: spot-check `pay-test-sandbox-3`, `home-test`, `home-test-live-1`, `home-test-sandbox` to confirm no inadvertent breakage (those pages have the same const-scope pattern).
5. **Subscription path**: even though this fix doesn't touch createSubscription, run one sandbox subscription and confirm the existing failure mode (no custom_id) is unchanged — i.e., dispatcher still falls back to S3-email or hard-blocks. Document this as known gap pending follow-up.

---

## 7. Verdict

**GO-WITH-EDITS**

### Required Edits Before BUILD

1. **Clarify race-safe placement**: The `window.pbSessionUuid = payTestData.sessionUuid` assignment goes AFTER the `crypto.randomUUID` line, not after the `const payTestData = {...}` literal. Document exact line per page in BUILD ticket.

2. **Migrate `payment-background.js:414, 421`** and **`homepage-payment.js:457, 552`** in the same sprint. The brief mentions "chat-side logger" but does not name these files explicitly. Without these migrations, the homepage and awakened-page chat logs continue to write `session_uuid: null` regardless of the inline-script fix.

3. **Open a separate (URGENT) ticket for createSubscription custom_id gap.** Add `custom_id: 'PB-' + tier.toUpperCase() + '-' + (window.pbSessionUuid || '')` to the subscription path. PayPal supports `custom_id` on subscription via `application_context` or via plan metadata — verify mechanism with security-engineer before BUILD. This is OUT OF SCOPE for the current fix but MUST not be deferred more than 48h. Without it, every recurring-subscription payment remains S1-opaque and falls into the new S5-disabled hard-block path → manual review queue grows indefinitely.

4. **Headless E2E assertion script** (item 6.1 + 6.2 above) must be added to deploy gate before merging to production. Sandbox-only manual click-through is insufficient given that this exact bug class shipped silently in MED-003.

5. **Do NOT migrate `awakened/index.html:2414` aiName read.** That read is intra-IIFE-via-deferred-invocation and works today. Migrating it would require exposing aiName on window, violating MED-003 PII intent.

### Key Concerns Summary

- **Architecture: SOUND** — UUID-only window exposure preserves MED-003 PII intent.
- **Coverage: INCOMPLETE as written** — must include `payment-background.js` and `homepage-payment.js`, not just the 5 inline page bodies.
- **Subscription gap: UNADDRESSED** — separate ticket required.
- **Test plan: INSUFFICIENT** — needs headless network-capture + dispatcher round-trip, not just visual sandbox.

---

**Final**: GO-WITH-EDITS. Ship the fix WITH edits 1-4 incorporated. Edit 3 (subscription custom_id) is a follow-up ticket, not a blocker for this sprint.

— cto, 2026-05-07
