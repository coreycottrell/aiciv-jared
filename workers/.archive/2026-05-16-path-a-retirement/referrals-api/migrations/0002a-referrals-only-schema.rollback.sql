-- Referral System v1 Sprint — D1 Schema Migration ROLLBACK (PART A)
-- Date: 2026-05-07
-- Purpose: Rollback 0002a-referrals-only-schema.sql changes
-- CTO Edit #10: D1 rollback scripts MUST be prepared in advance
--
-- Apply via:
--   cd /home/jared/projects/AI-CIV/aether/workers/referrals-api
--   export CLOUDFLARE_API_TOKEN=$(grep "^CF_API_TOKEN=" ../../.env | cut -d'=' -f2)
--   npx wrangler d1 execute purebrain-referrals --remote --file migrations/0002a-referrals-only-schema.rollback.sql
--
-- ============================================================================

-- Drop new tables (reverse order of creation)
DROP TABLE IF EXISTS payout_requests_v2;
DROP TABLE IF EXISTS rate_adjustments;
DROP TABLE IF EXISTS partner_applications;

-- Drop new indexes
DROP INDEX IF EXISTS uniq_referrals_pbref_payment;
DROP INDEX IF EXISTS idx_payout_v2_partner_status;
DROP INDEX IF EXISTS idx_payout_v2_status;
DROP INDEX IF EXISTS idx_payout_v2_partner;
DROP INDEX IF EXISTS idx_rate_adj_partner;
DROP INDEX IF EXISTS idx_partner_apps_status;
DROP INDEX IF EXISTS idx_partner_apps_email;

-- SQLite limitation: Cannot drop columns via ALTER TABLE
-- The following columns were added but CANNOT be rolled back via SQL:
--   - commission_payments.tier_at_write
--   - commission_payments.commission_source
--   - referrals.pb_ref
--   - referrals.payment_id
--
-- To fully rollback these columns, you would need to:
--   1. Backup data from affected tables
--   2. DROP the tables
--   3. Recreate tables with original schema
--   4. Restore data (excluding new columns)
--
-- This is a known SQLite limitation. For production rollback, manual process required.
--
-- RECOMMENDATION: Instead of rollback, leave columns in place (benign) and ensure
-- Worker code gracefully handles both pre-migration and post-migration schema.

-- Remove migration log entry
DELETE FROM schema_migrations WHERE migration_name = '0002a-referrals-only-schema';

-- ============================================================================
-- End of rollback 0002a-referrals-only-schema.rollback.sql
--
-- IMPORTANT: This rollback is PARTIAL due to SQLite ALTER TABLE limitations.
-- New columns cannot be dropped. They will remain in the schema with default/NULL values.
-- Worker code must be compatible with both schema versions for safe rollback.
--
-- NOTE: This rollback applies ONLY to 0002a (referrals-only). The clients ALTERs
--       in companion file 0002b are HELD and have not been applied.
