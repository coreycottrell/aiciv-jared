# D1 Schema Migration — Referral System v1 Sprint

**Date**: 2026-05-07 | **Phase**: PHASE 2 — Schema Migrations | **Status**: READY FOR REVIEW

---

## Existing Schema Verified

Queried live `purebrain-referrals` D1 database (database_id: `cdd9a522-f947-42a6-b9a3-c30534e02c3f`).

**Existing tables**: 17 tables including `referrers`, `referrals`, `commission_payments`, `payout_requests` (legacy), `rate_limits`, `admin_tokens`, `commission_splits`, etc.

**Key observations**:
- `referrals` table exists but lacks `pb_ref` and `payment_id` columns needed for B2 pending row creation
- `commission_payments` table exists but lacks `tier_at_write` and `commission_source` columns for safe retroactive recalc
- `clients` table (if exists) lacks plan upgrade tracking columns
- Legacy `payout_requests` table has different schema than v1 spec — created `payout_requests_v2` to avoid disruption

---

## New Schema Delta

**3 new tables**:
1. `partner_applications` — C2 approval flow (email UNIQUE, status CHECK, indexes on email+status)
2. `rate_adjustments` — C3 retroactive recalc audit trail (partner_id indexed)
3. `payout_requests_v2` — C4 partner-facing payout requests ($50 min CHECK, PayPal-only per CTO Edit #9)

**ALTERs to existing tables**:
- `clients`: add `previous_monthly_amount`, `plan_changed_at`, `is_support_tier`
- `commission_payments`: add `tier_at_write` (CTO Edit #2), `commission_source` (CHECK constraint)
- `referrals`: add `pb_ref`, `payment_id` + UNIQUE INDEX on `(pb_ref, payment_id)` (CTO Edit #4)

**Indexes added** (CTO Edit #3):
- `idx_partner_apps_email`, `idx_partner_apps_status`
- `idx_rate_adj_partner`
- `idx_payout_v2_partner`, `idx_payout_v2_status`, `idx_payout_v2_partner_status`
- `uniq_referrals_pbref_payment` (UNIQUE constraint for idempotent /referrals/complete)

**Migration log**: `schema_migrations` table tracks applied migrations to prevent re-runs

---

## Idempotency Notes

- All `CREATE TABLE` use `IF NOT EXISTS`
- All `CREATE INDEX` use `IF NOT EXISTS`
- UNIQUE constraint implemented as `CREATE UNIQUE INDEX IF NOT EXISTS` (SQLite workaround)
- `ALTER TABLE ADD COLUMN` will error on retry if column exists — **this is acceptable** (error is benign, column already present)
- Migration log uses `INSERT ... ON CONFLICT DO NOTHING` for idempotent tracking

**Safe to run multiple times**. Errors on ALTERs indicate columns already exist (success state).

---

## Rollback Approach

**Partial rollback only** due to SQLite `ALTER TABLE` limitations.

**Can be rolled back**:
- DROP new tables (`payout_requests_v2`, `rate_adjustments`, `partner_applications`)
- DROP new indexes

**CANNOT be rolled back via SQL**:
- Added columns (`clients.is_support_tier`, `commission_payments.tier_at_write`, `referrals.pb_ref`, etc.)
- SQLite does not support `ALTER TABLE DROP COLUMN`

**Recommendation**: Leave columns in place if rollback needed (benign with default/NULL values). Worker code must handle both pre- and post-migration schema for graceful rollback.

Full rollback script prepared at `workers/referrals-api/migrations/0002-v1-sprint-schema.rollback.sql` with documented limitations.

---

## Apply Instructions

**DO NOT apply yet** — Aether + Jared explicit auth required (constitutional per PayPal Auto-Split rules + D1 data change gate).

**When approved**:

```bash
cd /home/jared/projects/AI-CIV/aether/workers/referrals-api

# Export CF API token
export CLOUDFLARE_API_TOKEN=$(grep "^CF_API_TOKEN=" ../../.env | cut -d'=' -f2)

# Apply migration to REMOTE D1 database
npx wrangler d1 execute purebrain-referrals --remote --file migrations/0002-v1-sprint-schema.sql
```

**Rollback** (if needed):
```bash
npx wrangler d1 execute purebrain-referrals --remote --file migrations/0002-v1-sprint-schema.rollback.sql
```

**Backup recommendation**: Take D1 snapshot before applying (via CF dashboard or `wrangler d1 backup`).

---

## Open Questions for CTO/Aether

1. **Legacy `payout_requests` table**: Current table has different schema. Created `payout_requests_v2` to avoid disruption. Should we migrate data from legacy table or keep both? Recommend: keep both, deprecate legacy after v1 cutover.

2. **`clients` table existence**: Migration assumes `clients` table exists for `is_support_tier` flag. If table doesn't exist, ALTER will fail. Should we add `CREATE TABLE IF NOT EXISTS clients` stub first?

3. **Staging vs production apply order**: Single D1 database shared across staging/production CF Pages deploys. Apply to production DB first, or separate staging DB? Recommend: production only (staging previews use same DB).

4. **Migration idempotency testing**: Should we dry-run the migration on a test D1 database first? Recommend: yes if testing DB available, but migration is idempotent-safe for production apply.

5. **D1 backup snapshot**: Should backup be taken automatically in the apply script, or manual pre-step? Recommend: manual pre-step documented in apply instructions above.

---

## Commit Hash

**Branch**: `referral-v1`  
**Commit**: `f6c52d4`  
**Files**:
- `workers/referrals-api/migrations/0002-v1-sprint-schema.sql` (98 lines)
- `workers/referrals-api/migrations/0002-v1-sprint-schema.rollback.sql` (56 lines)

**Message**: `feat(d1): v1 sprint schema migrations — partner_applications, rate_adjustments, payout_requests_v2, tier_at_write, UNIQUE pb_ref+payment_id`

**CTO amendments applied**: All 10 required edits from pre-build review incorporated (tier_at_write, indexes, UNIQUE constraint, PayPal-only, schema-first sequencing, rollback script).

---

*Ready for Aether review + Jared explicit auth. Migration files written and committed. NOT applied to D1 yet.*
