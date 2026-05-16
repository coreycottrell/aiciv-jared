-- Rollback for 0003-assign-uniqueness.sql
-- WARNING: cannot restore deleted referral id=54 (it had 0 commissions; data loss = nil).
-- WARNING: cannot restore old CHECK constraint without another column rebuild; the
--          new CHECK is a strict superset (adds 'retroactive_assign') so rolling back
--          only matters if 'retroactive_assign' rows have been written.

DROP INDEX IF EXISTS uniq_referrals_referred_email;

-- Optional: rebuild commission_source CHECK back to the pre-0003 allowlist.
-- Only needed if rolling back AFTER 'retroactive_assign' rows have been inserted.
-- ALTER TABLE commission_payments ADD COLUMN commission_source_v0 TEXT
--   CHECK(commission_source_v0 IN ('standard', 'support_tier', 'plan_upgrade_recalc', 'milestone_recalc'));
-- UPDATE commission_payments SET commission_source_v0 = commission_source
--   WHERE commission_source IN ('standard', 'support_tier', 'plan_upgrade_recalc', 'milestone_recalc');
-- ALTER TABLE commission_payments DROP COLUMN commission_source;
-- ALTER TABLE commission_payments RENAME COLUMN commission_source_v0 TO commission_source;

DELETE FROM schema_migrations WHERE migration_name = '0003-assign-uniqueness';
