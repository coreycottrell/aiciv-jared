# MED-003 + createSubscription Fix — BUILD Receipt

**Agent**: full-stack-developer (PTT — dept-systems-technology)
**Date**: 2026-05-07
**Sprint**: MED-003 scope-bug fix + createSubscription `custom_id` gap
**Authorization**: Jared (CEO) greenlit at 2026-05-07
**Spec**: `exports/portal-files/NEW-ONBOARDING-FLOW-SPEC-2026-04-01.md` §2, §5, §6, §16
**CTO review**: `exports/portal-files/cto-prebuild-review-med003-fix-2026-05-07.md` (verdict: GO-WITH-EDITS)

---

## Branch State

- **Branch**: `main` (verified before AND after commit via `git branch --show-current`)
- **Worktree**: `/tmp/aether-main-wt` (main is checked out there; primary repo at `/home/jared/projects/AI-CIV/aether` is on `referral-v1`)
- **Pre-commit base**: `775c840 fix(dispatcher): correct variable names in S5-disable hard-block path`
- **Working tree at start**: clean (no uncommitted changes on main)

---

## Per-Page Change A — `window.pbSessionUuid` exposure (5 pages)

Each insertion is on the line IMMEDIATELY after the `crypto.randomUUID()` assignment to `payTestData.sessionUuid` (race-safe per CTO §4 — assignment runs synchronously at parse time before any PayPal/chat handler can fire).

| File | Inserted line | Adjacent UUID gen line |
|---|---|---|
| `exports/cf-pages-deploy/awakened/index.html` | **L5613** | L5611 |
| `exports/cf-pages-deploy/index.html` | **L13451** | L13449 |
| `exports/cf-pages-deploy/partnered/index.html` | **L5682** | L5680 |
| `exports/cf-pages-deploy/unified/index.html` | **L5630** | L5628 |
| `exports/cf-pages-deploy/insiders/index.html` | **L5494** | L5492 |

Inserted text (identical on all 5 pages):
```javascript
window.pbSessionUuid = payTestData.sessionUuid; // MED-003 escape hatch: expose UUID-only (no PII) for cross-script-tag readers — see CTO review 2026-05-07
```

**MED-003 PII compliance**: only the random UUID escapes scope. `aiName`/`name`/`email` remain inside `payTestData` lexical scope. Per CTO §1, `awakened/index.html:2414` (the `payTestData.aiName` deferred-IIFE read) is INTENTIONALLY NOT migrated — that pattern works via deferred invocation and migration would expose aiName on `window`, violating MED-003 intent.

---

## Per-Page Change B — `createSubscription` adds `custom_id` (5 pages)

CTO §2: createSubscription was previously missing `custom_id` ENTIRELY, meaning every recurring-subscription payment was opaque to dispatcher S1 (custom_id parse). Adding `'PB-' + tier.toUpperCase() + '-' + (window.pbSessionUuid || '')` matches the format used in createOrder on the same pages.

| File | Inserted line | Inside createSubscription block at |
|---|---|---|
| `exports/cf-pages-deploy/awakened/index.html` | **L5066** | L5063-L5072 |
| `exports/cf-pages-deploy/index.html` | **L12904** | L12901-L12910 |
| `exports/cf-pages-deploy/partnered/index.html` | **L5135** | L5132-L5141 |
| `exports/cf-pages-deploy/unified/index.html` | **L5083** | L5080-L5089 |
| `exports/cf-pages-deploy/insiders/index.html` | **L4947** | L4944-L4953 |

Inserted text:
```javascript
custom_id: 'PB-' + tier.toUpperCase() + '-' + (window.pbSessionUuid || ''),
```

**Note on placement**: even though createSubscription is defined at lower line numbers than the UUID generation in some pages (e.g. insiders L4944 vs UUID gen L5492), the function only EXECUTES when the user clicks Subscribe — long after page parse completes. By that time `window.pbSessionUuid` is set.

---

## Per-File Logger Migration (4 changes across 2 files)

Migrated cross-scope `(typeof payTestData !== 'undefined' && payTestData.sessionUuid)` reads to `window.pbSessionUuid`. Without this, the chat logger continued to write `session_uuid: null` regardless of the inline-script fix (CTO §7 Edit #2).

| File | Lines changed | Field |
|---|---|---|
| `exports/cf-pages-deploy/js/payment-background.js` | **L414** | `session_uuid` (top-level conversation log) |
| `exports/cf-pages-deploy/js/payment-background.js` | **L421** | `metadata.sessionUuid` |
| `exports/cf-pages-deploy/js/homepage-payment.js` | **L457** | `sessionUuid` (verify-payment POST body) |
| `exports/cf-pages-deploy/js/homepage-payment.js` | **L552** | `custom_id` (createOrder) |

`homepage-payment.js:457` retains the `sessionStorage.getItem('pb_sessionUuid')` fallback as defensive layering (CTO §5 — defensive layering is fine; both carry the same value after the fix).

---

## E2E Assertion Script (SHIP gate per CTO §6 / Edit #4)

**Path**: `tools/verify-payment-pages-pbsessionuuid.sh` (executable, 7,751 bytes)

**Static-source mode (default)**: 14 assertions across 5 LIVE pages × 2 changes each + 2 JS files × 2 (positive + negative) checks each. Runs in <2s. **First run on this commit: 14/14 PASS, STATUS: GREEN.**

**Live mode (`--live`)**: curl staging.purebrain.ai, verify served HTML carries the same tokens. Use post-deploy.

**Section 3**: 5 sandbox/test pages enumerated (informational only — out of scope this sprint).

**Per CTO §6 caveat**: static deploy gate only. Full E2E (sandbox PayPal click-through + `tail logs/purebrain_web_conversations.jsonl` + dispatcher S2-uuid round-trip) runs separately via browser-vision-tester before SHIP fully clears.

---

## Commit

- **Hash**: `250f5f5`
- **Branch**: `main`
- **Push status**: NOT pushed to origin (per instructions — awaiting Aether explicit auth)
- **Pre-commit hooks**: ran cleanly (no `--no-verify`)
- **Files in commit**: 8 files changed, 211 insertions(+), 4 deletions(-)

---

## Status

**BUILD-COMPLETE-PENDING-SEC-AND-QA**

Next gates per dispatch: SEC review → QA E2E → SHIP. No deploy executed (no `cf-deploy.py`, no `wrangler deploy`).
