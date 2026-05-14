-- =============================================================================
-- Rollback for Migration 0001 — Auth Decoupling Day 1 (EXTEND)
-- Date: 2026-05-14
-- =============================================================================
-- Apply in REVERSE order to a given DB. Each track is independent.
-- All statements idempotent (IF EXISTS) — safe to re-run.
--
-- The `display_name` column on clients.users is NOT dropped on rollback.
-- It is backward-compatible (NULL default; pre-existing code never read it)
-- and dropping risks data loss if any code has started writing to it.
-- =============================================================================


-- ----- TRACK 1 rollback (purebrain-clients) -----
-- Run with: wrangler d1 execute purebrain-clients --remote --file=<this section>

DROP INDEX IF EXISTS idx_magic_links_unique;
DROP INDEX IF EXISTS idx_magic_links_email;
DROP INDEX IF EXISTS idx_magic_links_session;
DROP TABLE IF EXISTS magic_links;

DROP TABLE IF EXISTS password_resets;

-- (Backfilled users / team_invites: delta was ZERO at apply time —
--  no rows to roll back. Original 33 users + 35 team_invites preserved.)


-- ----- TRACK 2 rollback (purebrain-referrals) -----
-- Run with: wrangler d1 execute purebrain-referrals --remote --file=<this section>

DROP INDEX IF EXISTS idx_auth_magic_links_unique;
DROP INDEX IF EXISTS idx_auth_magic_links_email;
DROP INDEX IF EXISTS idx_auth_magic_links_session;
DROP TABLE IF EXISTS auth_magic_links;

DROP TABLE IF EXISTS auth_password_resets;

DROP TABLE IF EXISTS auth_team_invites;

DROP INDEX IF EXISTS idx_auth_sessions_user;
DROP TABLE IF EXISTS auth_sessions;

DROP INDEX IF EXISTS idx_auth_users_email;
DROP INDEX IF EXISTS idx_auth_users_team;
DROP TABLE IF EXISTS auth_users;

-- (Legacy `sessions`, `affiliate_sessions`, `referrers`, etc. NOT touched.)


-- ----- LAST RESORT (catastrophic) -----
-- wrangler d1 execute purebrain-clients --remote \
--   --file=/home/jared/projects/clients-api/backups/2026-05-14/purebrain-clients-pre-extend.sql
--
-- wrangler d1 execute purebrain-referrals --remote \
--   --file=/tmp/referrals-api/backups/2026-05-14/purebrain-referrals-pre-create.sql
