# ST# — target_user_id allowlist hardening (14-day post-SHIP follow-up)

**Opened**: 2026-05-02 (B9 QA gate, dept-systems-technology)
**Parent**: `inbox/dept-routing/ST-2026-05-02-bsky-distribution-fix.md`
**Source finding**: B8 SECURITY HIGH-2 (security-engineer-tech, 2026-05-02)
**Status**: OPEN — scheduled for ≤14 days post-B10 SHIP
**Owner**: ptt-fullstack (BUILD), security-engineer-tech (review), ptt-qa (verify)

---

## The finding (verbatim from B8 SECURITY)

> **HIGH-2 — `target_user_id` lacks allowlist**: System callers can attribute content to ANY user_id. Mitigation: `social_accounts.is_house_account` column + strict `target_user_id === houseAcct.user_id` check. 14-day post-SHIP fix.

## Why it's not a B9 blocker

The override path is gated behind `sess.role === "system"`, which requires the synthetic system session bearer token (`ROUTER_API_KEY`). Only two callers hold that token today:

1. blog-publish-hook (this BUILD chain)
2. ContentRouter (existing internal Worker)

Both call with `target_user_id` only against the @purebrain.ai house account. There is NO external attack surface today — exploitation requires possession of `ROUTER_API_KEY`, at which point an attacker has already broken trust boundary entirely.

The hardening turns the contract from "trust the caller" → "verify the caller is targeting an allowed (house) account", which is defense-in-depth, not a live vulnerability.

## What needs to happen (≤14 days)

1. **Schema change**: Add `is_house_account BOOLEAN DEFAULT 0` column to `social_accounts`. Backfill `1` for the @purebrain.ai row only (and any future house accounts).
2. **Code change** in `workers/social-api/src/worker.js` `handleCreateContent`:
   - When `sess.role === "system"` AND `body.target_user_id` is supplied:
     - Require `houseAcct.is_house_account === 1`
     - Require `target_user_id === houseAcct.user_id` (no cross-account attribution)
   - Otherwise reject with 403 "system override only valid for house accounts"
3. **Tests**: 3 new cases in social-api test suite:
   - system role + house account + matching target_user_id → ALLOWED
   - system role + non-house account + any target_user_id → 403
   - system role + house account + mismatched target_user_id → 403
4. **Migration**: New `migrations/0003_house_account_flag.sql`
5. **Re-deploy**: BUILD → SECURITY → QA → SHIP, full chain

## Handshake-queue tracking (Row 72)

Per dispatch from Aether (B9 QA brief):
> "Handshake Queue Row 72 already exists — verify it's still OPEN."

The handshake queue lives at `/home/aiciv/shared/handshake-queue.md` which is **not accessible from the aether project filesystem** (sister-container scope, Triangle Operating System). Verification of Row 72 must be performed by:

- Aether (Primary) — has handshake-queue access via Triangle OS, OR
- operations-analyst (OP#) during the B11 verify pass

This memo serves as the in-aether canonical record. If Row 72 does not exist or has closed, OP# is to re-open it pointing at this memo.

## Acceptance criteria for closure

- [ ] Schema migration deployed to production D1 (`is_house_account` column live)
- [ ] social-api code change deployed (allowlist check live)
- [ ] 3 new tests green
- [ ] B11 OP# verifies hardening with a synthetic non-house attribution attempt → must return 403

---

**Routing**: Dept-systems-technology owns this. ptt-fullstack to spec the migration; security-engineer-tech to re-review pre-deploy; ptt-qa to run the 3-test verification; devops-engineer to ship.

**Cadence**: Re-evaluate at the next BUILD chain BOOP. If 10 days elapsed without progress, escalate to Jared via portal.
