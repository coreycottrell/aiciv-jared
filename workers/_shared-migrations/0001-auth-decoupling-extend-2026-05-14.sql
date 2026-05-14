-- =============================================================================
-- Migration: 0001 — Auth Decoupling Day 1 (EXTEND, not REPLACE)
-- Date: 2026-05-14
-- Author: full-stack-developer (per ST# amended brief)
-- =============================================================================
--
-- TWO TARGETS, separate runs:
--   Track 1: purebrain-clients (EXTEND existing auth tables)
--   Track 2: purebrain-referrals (CREATE auth_*-prefixed tables; legacy `sessions` untouched)
--
-- SOURCE: purebrain-social (READ-ONLY, schemas captured 2026-05-14 23:00 UTC)
--
-- IDEMPOTENCY: All CREATE TABLE statements use IF NOT EXISTS.
--              ALTER TABLE ADD COLUMN is guarded by a separate has-column check
--              executed by the migration driver (cannot be expressed in pure SQL).
--
-- BACKFILL: INSERT OR IGNORE keyed on PK/UNIQUE. Re-run safe.
--           SKIPS sessions/magic_links/password_resets (trust artifacts, let them re-issue).
--
-- ROLLBACK: See section "ROLLBACK SQL" at bottom of this file.
-- =============================================================================


-- =============================================================================
-- TRACK 1 — purebrain-clients (EXTEND)
-- =============================================================================
-- Run with: wrangler d1 execute purebrain-clients --remote --file=<this file>
-- (Comment out Track 2 section first, or split into per-track files.)
-- See migration driver script for orchestrated execution.

-- Step 1.1 — Add display_name to users
--   SQLite ALTER TABLE … ADD COLUMN does not support IF NOT EXISTS.
--   Driver must pre-check with:
--     SELECT COUNT(*) AS has_col FROM pragma_table_info('users') WHERE name='display_name';
--   If has_col=0, execute:
--     ALTER TABLE users ADD COLUMN display_name TEXT;
--   If has_col=1, SKIP.
--
-- The ALTER statement (driver-conditional):
ALTER TABLE users ADD COLUMN display_name TEXT;

-- Step 1.2 — Create magic_links (matches source schema byte-for-byte)
CREATE TABLE IF NOT EXISTS magic_links (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_uuid TEXT,
    ai_name TEXT,
    human_name TEXT,
    human_email TEXT,
    paypal_email TEXT,
    container TEXT,
    magic_link TEXT NOT NULL,
    original_link TEXT,
    status TEXT DEFAULT 'ready',
    received_at TEXT DEFAULT (datetime('now')),
    welcome_sent INTEGER DEFAULT 0,
    welcome_sent_at TEXT
);

-- Step 1.2 indexes (parity with source)
CREATE INDEX IF NOT EXISTS idx_magic_links_session ON magic_links(session_uuid);
CREATE INDEX IF NOT EXISTS idx_magic_links_email ON magic_links(human_email);
CREATE UNIQUE INDEX IF NOT EXISTS idx_magic_links_unique ON magic_links(magic_link);

-- Step 1.3 — Create password_resets (matches source schema byte-for-byte)
CREATE TABLE IF NOT EXISTS password_resets (
    token TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    email TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    created_at TEXT NOT NULL,
    used INTEGER DEFAULT 0
);
-- (source has zero explicit indexes on password_resets; PK suffices)

-- Step 1.4 — Backfill users (delta-only via INSERT OR IGNORE on email UNIQUE)
--   Driver generates per-row INSERTs from /tmp/auth-day1-v3/source-users-full.json
--   See backfill-clients-users.sql (generated)

-- Step 1.5 — SKIP sessions backfill (trust boundary, let users re-login)
-- Step 1.6 — Backfill team_invites (delta-only via INSERT OR IGNORE on id PK)
--   Driver generates per-row INSERTs from /tmp/auth-day1-v3/source-team_invites-full.json
--   See backfill-clients-team_invites.sql (generated)


-- =============================================================================
-- TRACK 2 — purebrain-referrals (CREATE auth_*-prefixed tables)
-- =============================================================================
-- Run with: wrangler d1 execute purebrain-referrals --remote --file=<this file>
-- Legacy `sessions` table (30 rows, orphaned) is NOT touched.

-- Step 2.1.1 — auth_users (matches source users schema, with display_name baked in)
CREATE TABLE IF NOT EXISTS auth_users (
    id TEXT PRIMARY KEY,
    team_id TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'contributor',
    billing_tier TEXT NOT NULL DEFAULT 'team_member',
    password_hash TEXT,
    oauth_provider_id TEXT,
    last_login_at TEXT,
    created_at TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    display_name TEXT
);
CREATE INDEX IF NOT EXISTS idx_auth_users_team ON auth_users(team_id);
CREATE INDEX IF NOT EXISTS idx_auth_users_email ON auth_users(email);

-- Step 2.1.2 — auth_sessions (matches source sessions schema)
CREATE TABLE IF NOT EXISTS auth_sessions (
    token TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    user_agent TEXT,
    ip_address TEXT,
    created_at TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);
CREATE INDEX IF NOT EXISTS idx_auth_sessions_user ON auth_sessions(user_id);

-- Step 2.1.3 — auth_team_invites (matches source team_invites schema)
CREATE TABLE IF NOT EXISTS auth_team_invites (
    id TEXT PRIMARY KEY,
    email TEXT NOT NULL,
    role TEXT DEFAULT 'member',
    invited_by TEXT,
    invited_at TEXT,
    status TEXT DEFAULT 'pending',
    accepted_at TEXT,
    accepted_by_user_id TEXT,
    team_id TEXT,
    source TEXT DEFAULT 'admin',
    token TEXT,
    name TEXT
);
-- (source has zero explicit indexes on team_invites; PK suffices)

-- Step 2.1.4 — auth_magic_links (matches source magic_links schema)
CREATE TABLE IF NOT EXISTS auth_magic_links (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_uuid TEXT,
    ai_name TEXT,
    human_name TEXT,
    human_email TEXT,
    paypal_email TEXT,
    container TEXT,
    magic_link TEXT NOT NULL,
    original_link TEXT,
    status TEXT DEFAULT 'ready',
    received_at TEXT DEFAULT (datetime('now')),
    welcome_sent INTEGER DEFAULT 0,
    welcome_sent_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_auth_magic_links_session ON auth_magic_links(session_uuid);
CREATE INDEX IF NOT EXISTS idx_auth_magic_links_email ON auth_magic_links(human_email);
CREATE UNIQUE INDEX IF NOT EXISTS idx_auth_magic_links_unique ON auth_magic_links(magic_link);

-- Step 2.1.5 — auth_password_resets (matches source password_resets schema)
CREATE TABLE IF NOT EXISTS auth_password_resets (
    token TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    email TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    created_at TEXT NOT NULL,
    used INTEGER DEFAULT 0
);

-- Step 2.2 — Backfill auth_users from purebrain-social
--   Driver generates from /tmp/auth-day1-v3/source-users-full.json
--   See backfill-refs-auth_users.sql (generated)

-- Step 2.3 — Backfill auth_team_invites from purebrain-social
--   Driver generates from /tmp/auth-day1-v3/source-team_invites-full.json
--   See backfill-refs-auth_team_invites.sql (generated)

-- Step 2.4 — SKIP auth_sessions / auth_magic_links / auth_password_resets backfill
--   (trust artifacts; let them re-issue naturally on next login/magic-link request)


-- =============================================================================
-- ROLLBACK SQL — apply in reverse order if catastrophic
-- =============================================================================
-- NOTE: SQLite < v3.35 does NOT support DROP COLUMN.
--       D1 currently uses SQLite 3.45.x so DROP COLUMN is supported, BUT
--       leaving `display_name` in place is harmless (defaults to NULL).
--       We recommend NOT dropping the column on rollback.
--
-- For Track 1 rollback:
--   DROP TABLE IF EXISTS password_resets;
--   DROP TABLE IF EXISTS magic_links;
--   -- (leave display_name column alone — backward-compatible NULL)
--   -- Backfilled users (if any) identifiable by inserted IDs from migration log.
--   -- Last resort: wrangler d1 execute purebrain-clients --remote \
--   --   --file=/home/jared/projects/clients-api/backups/2026-05-14/purebrain-clients-pre-extend.sql
--
-- For Track 2 rollback:
--   DROP TABLE IF EXISTS auth_password_resets;
--   DROP TABLE IF EXISTS auth_magic_links;
--   DROP TABLE IF EXISTS auth_team_invites;
--   DROP TABLE IF EXISTS auth_sessions;
--   DROP TABLE IF EXISTS auth_users;
--   -- All isolated; no impact on existing referrals/affiliate_sessions/etc.
--   -- Last resort: wrangler d1 execute purebrain-referrals --remote \
--   --   --file=/tmp/referrals-api/backups/2026-05-14/purebrain-referrals-pre-create.sql
