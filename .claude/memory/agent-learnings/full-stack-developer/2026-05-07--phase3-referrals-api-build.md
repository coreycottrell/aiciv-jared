# Phase 3 BUILD — referrals-api Worker (referral-v1 branch)

**Date**: 2026-05-07
**Type**: operational
**Topic**: Phase 3 BUILD execution pattern — referrals-api Worker code-only on branch

## Memory Search Results
- Searched `.claude/memory/agent-learnings/full-stack-developer/` for "referral|payout|commission|webhook" — found `2026-04-15--referral-unification-prereq-failure.md` (prereq failure on April 15 — different scope).
- Found in cto memory (referenced via SPEC): `2026-05-07--referral-v1-prebuild-review.md` — provided 10 amendments + race-condition map.
- Reused: tier_at_write strategy (CTO §1.3) for safe idempotent recalc; INSERT OR IGNORE pattern for idempotent /referrals/complete; chunked recalc to avoid CF Worker 30s CPU limit.

## What Worked

### Forward-additive build over stale line numbers
The work order referenced line numbers from a +1382 LOC delta (e.g., "line 546 of paypal-webhook"). The current file was already 590 clean LOC — the historical delta had been absorbed by earlier commits. Rather than re-create the delta to "fix" it, I applied the spec items as **forward additions** to the clean baseline. Documented this in commit messages so reviewers don't search for phantom edits.

### Discrete commits per work item
8 commits, one per work item. Each commit:
- Cites SPEC item number + CTO amendment number
- Notes "referral-v1 branch only. Not deployed."
- Passes `node --check` before staging
- Independently revertable

### Idempotency from DB constraints
- UNIQUE INDEX `uniq_referrals_pbref_payment` on `(pb_ref, payment_id)` makes `INSERT OR IGNORE` collapse double-fires automatically. No application-layer dedup logic needed.
- DB CHECK `payout_requests_v2.amount >= 50` makes the $50 min unbypassable from any client.
- DB CHECK `payout_method = 'paypal'` enforces v1 PayPal-only constraint.

### Backwards-compatible commission write path
Kept legacy code path that accepts pre-computed `commission_value` from caller (paypal-webhook unchanged), AND added new path that computes from `payment_amount + partner_tier + plan_id`. Both paths now write `tier_at_write` so audit trail is consistent regardless of caller. Means paypal-webhook can be updated separately without coordination dance.

### tier_at_write as recalc gate
The recalc query filters `WHERE tier_at_write != target_tier` — automatically skips already-recalc'd rows. Makes the endpoint safely re-runnable. Combined with `commission_source != 'support_tier'`, Support Tier rows are locked at 25% regardless of partner tier changes (legal commitment honored).

## What Didn't Work / Gotchas

### `git add <specific-file>` picked up an untracked sibling file
On commit 2 (B2), `git add workers/referrals-api/src/worker.js` resulted in the commit also including `workers/purebrain-portal-proxy/wrangler.toml` (8 lines, untracked). Investigation: no pre-commit hook present; mechanism unclear (possibly index race with parallel agent). Outcome was harmless (file was scaffolding for the parallel B1 agent), but the lesson is: **on shared branches with parallel agents, verify `git diff --cached` before commit**, not just the path you intended to stage.

### Parallel-agent commits interleaved on the same branch
Another agent committed `e2be7e0` (frontend/portal-proxy build summary) between my Item 2 and Item 3 commits. Not a problem for correctness — work streams were on different files — but `git log --oneline` shows interleaved history. Mitigation: filter by file path when listing your commits (`git log -- workers/referrals-api/`).

### SPEC's stale line-number references
SPEC §5 A3 said "duplicate formula at `paypal-webhook/worker.js:546`" but that file is 513 lines, and the formula referenced wasn't there. CTO review caught one half (corrected target to `referrals-api/worker.js`) but the line numbers still pointed to a +1382 LOC delta no longer present. Lesson: **before BUILD, run `git log --all --oneline -- <file>` + `wc -l <file>` to verify the SPEC's anchor still exists**. If not, build forward-additively and document the deviation.

## Patterns Captured

### "Forward fix on absorbed delta" pattern
When a SPEC references line numbers from an uncommitted delta that has since been committed/refactored, the right move is:
1. Acknowledge the spec's intent (the architectural change being requested)
2. Build the architectural change as a forward addition to current HEAD
3. Document the deviation in the commit message + deliverable summary

DO NOT attempt to recreate the historical delta to "match" the SPEC's line numbers. That introduces stale code.

### Dual-mode endpoint with auth split
`/referrals/complete` now serves two callers (legacy admin + new public). Mode dispatched by body shape (presence of `pb_ref` vs `referral_id`). Auth check happens AFTER mode dispatch — public mode requires no token; admin mode requires token. Single endpoint, two contracts, clean. Beats two endpoints with confused naming.

### Audit columns that double as recalc gates
`tier_at_write` serves three purposes simultaneously:
1. Audit trail (legal record of tier at time of write)
2. Recalc filter (only rows where `tier_at_write != target` get touched)
3. Idempotency proof (re-running recalc converges to consistent state)

One column, three properties. The recalc logic becomes essentially declarative.

## Files Touched

- `workers/referrals-api/src/worker.js` — 590 → 1255 LOC (8 commits)
- `workers/referrals-api/wrangler.toml` — declared SUPPORT_TIER_PLAN_IDS env var
- `exports/portal-files/phase3-referrals-api-build-2026-05-07.md` — deliverable summary

## Verification

- All 8 commits pass `node --check`
- All 23 routes confirmed via grep
- All constitutional invariants present:
  - `tier_at_write` set on every commission INSERT
  - `INSERT OR IGNORE` on /referrals/complete
  - `TIER_RATES` validation on every tier-accepting route
  - `computeCommission` + `isSupportTierPlan` for E1
- Branch: `referral-v1` (NOT main, NOT deployed)
- No `wrangler deploy` ever invoked

## Cross-references

- SPEC: `exports/portal-files/REFERRAL-SYSTEM-V1-SPEC-2026-05-07.md`
- CTO review: `exports/portal-files/cto-prebuild-review-referral-v1-2026-05-07.md`
- D1 schema: `workers/referrals-api/migrations/0002a-referrals-only-schema.sql` (applied)
- Deliverable: `exports/portal-files/phase3-referrals-api-build-2026-05-07.md`
- Parallel agent build: `exports/portal-files/phase3-frontend-portal-proxy-build-2026-05-07.md` (commit e2be7e0)
