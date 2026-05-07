-- Referral System v1 Sprint — D1 Schema Migration (PART B: Clients Additions)
-- Date: 2026-05-07
-- Status: 🔴 HELD — DO NOT APPLY YET
--
-- HELD RATIONALE:
--   The clients table currently lives in purebrain-social D1 (drift).
--   Per constitutional domain-isolation rule (May 7, 2026), purebrain-social
--   must NEVER touch referrals/clients. Cross-DB binding to social is BANNED.
--
--   Chy admitted clients-in-social is drift; extraction is planned but not yet
--   executed. This file is held until the clients extraction sprint completes.
--
-- APPLY TARGET (post-extraction):
--   purebrain-clients D1 (the new dedicated DB created during extraction sprint)
--   NOT purebrain-social
--   NOT purebrain-referrals
--
-- DO NOT APPLY this file until:
--   1. Clients extraction sprint has completed
--   2. purebrain-clients D1 exists and contains the clients table
--   3. Worker bindings updated to read clients from purebrain-clients
--   4. CTO has reviewed the apply target
--
-- WHEN READY (post-extraction):
--   cd /home/jared/projects/AI-CIV/aether/workers/referrals-api
--   export CLOUDFLARE_API_TOKEN=$(grep "^CF_API_TOKEN=" ../../.env | cut -d'=' -f2)
--   npx wrangler d1 execute purebrain-clients --remote --file migrations/0002b-clients-additions.sql
--
-- ============================================================================

-- ALTER existing clients table for plan-upgrade auto-recalc (SPEC §4.2)
-- Track previous amount to detect plan upgrades for commission recalc
-- SQLite limitation: No "IF NOT EXISTS" for ALTER TABLE ADD COLUMN
-- If column already exists, this will error — acceptable for idempotent retry (error is benign)
ALTER TABLE clients ADD COLUMN previous_monthly_amount REAL;
ALTER TABLE clients ADD COLUMN plan_changed_at INTEGER;

-- ALTER clients table for Support Tier flag (E1 — Jared #2 locked decision)
ALTER TABLE clients ADD COLUMN is_support_tier INTEGER DEFAULT 0;

-- Record this migration as applied (assumes schema_migrations exists in target D1)
INSERT INTO schema_migrations (migration_name, applied_at)
VALUES ('0002b-clients-additions', strftime('%s', 'now'))
ON CONFLICT(migration_name) DO NOTHING;

-- ============================================================================
-- End of migration 0002b-clients-additions.sql
--
-- This file completes the v1 sprint schema additions (companion to 0002a).
-- Apply only after clients extraction. Constitutional rule: domain isolation.
