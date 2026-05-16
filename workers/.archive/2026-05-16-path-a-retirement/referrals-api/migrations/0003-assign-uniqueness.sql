-- ============================================================================
-- 0003-assign-uniqueness.sql
-- CTO pre-build 2026-05-12 — Bug 1 (idempotency) + Bug 2 (retro backfill)
--
-- 1. Resolves the in-prod self-dup (referral id=54 dup of id=42, both Laurie
--    Clifton → Ian Wheaton, 0 commissions on the dup). Pre-flight evidence:
--    /home/jared/exports/portal-files/referrals-dup-preflight-2026-05-12.json
-- 2. Creates UNIQUE INDEX on referred_email (partial, excludes placeholder rows)
--    enforcing the constitutional "one client = one referral, ever" rule.
-- 3. Extends commission_payments.commission_source CHECK to allow
--    'retroactive_assign' for the Bug 2 backfill path.
--
-- All steps idempotent: rerunning is safe.
-- ============================================================================

-- STEP 1 — Remove the in-prod self-dup (referral id=54).
-- Safety: the dup has NO commission_payments rows (verified pre-flight).
-- Same referrer (id=63 Ian Wheaton) on both — no contested attribution.
DELETE FROM referrals
 WHERE id = 54
   AND referred_email = 'lapc@att.net'
   AND referrer_id = 63
   AND NOT EXISTS (SELECT 1 FROM commission_payments WHERE referral_id = 54);

-- STEP 2 — UNIQUE INDEX on referred_email (partial, excludes legacy placeholders).
-- paypal-webhook writes 'paypal_<txn>@pending' rows before
-- /internal/complete-by-email resolves them; those must remain non-unique.
CREATE UNIQUE INDEX IF NOT EXISTS uniq_referrals_referred_email
  ON referrals(referred_email)
  WHERE referred_email IS NOT NULL
    AND referred_email != ''
    AND referred_email NOT LIKE 'paypal_%@pending';

-- STEP 3 — Extend commission_source CHECK constraint to allow 'retroactive_assign'.
-- SQLite can't ALTER a CHECK in place; rebuild via temp column copy.
ALTER TABLE commission_payments ADD COLUMN commission_source_v2 TEXT
  CHECK(commission_source_v2 IN (
    'standard', 'support_tier', 'plan_upgrade_recalc', 'milestone_recalc', 'retroactive_assign'
  ));
UPDATE commission_payments SET commission_source_v2 = COALESCE(commission_source, 'standard');
ALTER TABLE commission_payments DROP COLUMN commission_source;
ALTER TABLE commission_payments RENAME COLUMN commission_source_v2 TO commission_source;

-- STEP 4 — Record migration application.
INSERT INTO schema_migrations (migration_name, applied_at)
VALUES ('0003-assign-uniqueness', strftime('%s', 'now'))
ON CONFLICT(migration_name) DO NOTHING;
