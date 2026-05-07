-- Referral System v1 Sprint — D1 Schema Migration
-- Date: 2026-05-07
-- CTO Review: APPROVED (10 amendments applied)
-- Purpose: Add partner_applications, rate_adjustments, payout_requests v2 tables,
--          add tier_at_write column for safe retroactive recalc,
--          add UNIQUE constraint on (pb_ref, payment_id) for idempotent /referrals/complete,
--          add indexes for admin queue queries
--
-- Apply via:
--   cd /home/jared/projects/AI-CIV/aether/workers/referrals-api
--   export CLOUDFLARE_API_TOKEN=$(grep "^CF_API_TOKEN=" ../../.env | cut -d'=' -f2)
--   npx wrangler d1 execute purebrain-referrals --remote --file migrations/0002-v1-sprint-schema.sql
--
-- Rollback via:
--   npx wrangler d1 execute purebrain-referrals --remote --file migrations/0002-v1-sprint-schema.rollback.sql
--
-- ============================================================================

-- New table: partner_applications (C2 — approval flow)
-- (CTO Edit #3: indexes on email, status for admin queue queries)
CREATE TABLE IF NOT EXISTS partner_applications (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  email TEXT NOT NULL UNIQUE,
  full_name TEXT NOT NULL,
  audience_size INTEGER,
  application_data TEXT,  -- JSON serialized application form data
  status TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending', 'approved', 'rejected', 'needs_30d_use')),
  applied_at INTEGER NOT NULL,
  reviewed_at INTEGER,
  reviewed_by TEXT,       -- Admin email who approved/rejected
  rejection_reason TEXT,
  reviewer_override_reason TEXT  -- CTO Q3: admin override for <30d users
);

CREATE INDEX IF NOT EXISTS idx_partner_apps_email ON partner_applications(email);
CREATE INDEX IF NOT EXISTS idx_partner_apps_status ON partner_applications(status);

-- New table: rate_adjustments (C3 — audit trail for retroactive recalc)
-- Legal record of tier changes + retroactive commission recalculations
-- (CTO Edit #3: index on partner_id for partner-specific audit queries)
CREATE TABLE IF NOT EXISTS rate_adjustments (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  partner_id TEXT NOT NULL,  -- references referrers.referral_code
  old_rate REAL NOT NULL,
  new_rate REAL NOT NULL,
  trigger_event TEXT NOT NULL CHECK(trigger_event IN ('100_referrals', '1000_referrals', 'manual')),
  affected_commission_count INTEGER NOT NULL,
  total_dollars_recalculated REAL NOT NULL,
  created_at INTEGER NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_rate_adj_partner ON rate_adjustments(partner_id);

-- New table: payout_requests v2 (C4 — partner-facing payout request flow)
-- (CTO Edit #9: drop bank method for v1, PayPal only)
-- NOTE: This table replaces the legacy payout_requests table structure.
--       Legacy table had: request_id, referral_code, paypal_email, amount, status, created_at, created_at_ts, paid_at, batch_id, notes
--       V2 adds: partner_id FK, $50 min CHECK, paid_via_split_id for paypal_auto_split.py audit trail
-- DECISION: Keep legacy table as-is, create v2 as new table name payout_requests_v2 to avoid disruption
CREATE TABLE IF NOT EXISTS payout_requests_v2 (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  partner_id TEXT NOT NULL,  -- references referrers.referral_code
  amount REAL NOT NULL CHECK(amount >= 50),  -- $50 minimum per spec
  payout_method TEXT NOT NULL DEFAULT 'paypal' CHECK(payout_method = 'paypal'),  -- v1: PayPal only
  paypal_email TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'requested' CHECK(status IN ('requested', 'approved', 'paid', 'rejected')),
  requested_at INTEGER NOT NULL,
  paid_at INTEGER,
  paid_via_split_id TEXT  -- references paypal_auto_split.py run ID for audit
);

CREATE INDEX IF NOT EXISTS idx_payout_v2_partner ON payout_requests_v2(partner_id);
CREATE INDEX IF NOT EXISTS idx_payout_v2_status ON payout_requests_v2(status);
CREATE INDEX IF NOT EXISTS idx_payout_v2_partner_status ON payout_requests_v2(partner_id, status);

-- ALTER existing clients table for plan-upgrade auto-recalc (SPEC §4.2)
-- Track previous amount to detect plan upgrades for commission recalc
-- SQLite limitation: No "IF NOT EXISTS" for ALTER TABLE ADD COLUMN
-- If column already exists, this will error — acceptable for idempotent retry (error is benign)
ALTER TABLE clients ADD COLUMN previous_monthly_amount REAL;
ALTER TABLE clients ADD COLUMN plan_changed_at INTEGER;

-- ALTER clients table for Support Tier flag (E1 — Jared #2 locked decision)
ALTER TABLE clients ADD COLUMN is_support_tier INTEGER DEFAULT 0;

-- ALTER commission_payments for safe retroactive recalc (CTO Edit #2)
-- tier_at_write preserves the tier at time of write, enabling idempotent recalc
-- commission_source tracks payment source type for Support Tier 25% override
ALTER TABLE commission_payments ADD COLUMN tier_at_write TEXT;
ALTER TABLE commission_payments ADD COLUMN commission_source TEXT DEFAULT 'standard' CHECK(commission_source IN ('standard', 'support_tier', 'plan_upgrade_recalc', 'milestone_recalc'));

-- ALTER referrals table to add pb_ref and payment_id columns for attribution
-- These columns enable the B2 pending row creation + webhook lookup flow
-- SQLite limitation: ALTER TABLE limitations mean we accept error if columns exist
ALTER TABLE referrals ADD COLUMN pb_ref TEXT;
ALTER TABLE referrals ADD COLUMN payment_id TEXT;

-- UNIQUE constraint on (pb_ref, payment_id) (CTO Edit #4)
-- Prevents duplicate attribution on /referrals/complete retry (B3 payment page POST can double-fire)
-- SQLite limitation: Cannot ALTER TABLE to add UNIQUE constraint, must use CREATE UNIQUE INDEX
-- WHERE clause filters out legacy rows with NULL values
CREATE UNIQUE INDEX IF NOT EXISTS uniq_referrals_pbref_payment
  ON referrals(pb_ref, payment_id)
  WHERE pb_ref IS NOT NULL AND payment_id IS NOT NULL;

-- Schema migrations log table (CTO sequencing requirement)
-- Tracks which migrations have been applied to prevent re-runs
CREATE TABLE IF NOT EXISTS schema_migrations (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  migration_name TEXT NOT NULL UNIQUE,
  applied_at INTEGER NOT NULL
);

-- Record this migration as applied
INSERT INTO schema_migrations (migration_name, applied_at)
VALUES ('0002-v1-sprint-schema', strftime('%s', 'now'))
ON CONFLICT(migration_name) DO NOTHING;

-- ============================================================================
-- End of migration 0002-v1-sprint-schema.sql
