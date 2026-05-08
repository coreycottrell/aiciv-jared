-- ================================================================
-- PUREBRAIN SOCIAL DATABASE - CURRENT STATE SNAPSHOT
-- ================================================================
-- Purpose: Pre-migration snapshot of purebrain-social D1 for reference
-- Date: 2026-05-08 (Phase 0 gate-zero)
-- Sprint: Tier 3 Extraction (clients-api + payments-api separation)
--
-- This file documents the FULL current state of purebrain-social D1
-- before any tables are migrated out to new databases.
--
-- Constitutional Reference: feedback_project_domain_isolation_constitutional.md
-- Spec: exports/portal-files/TIER3-EXTRACTION-SPEC-2026-05-08.md
-- ================================================================

-- ================================================================
-- TABLES TO BE MIGRATED OUT (Phase 6)
-- ================================================================
-- These tables will be COPIED to new databases, then DROPPED from
-- purebrain-social after 24h verification window (Phase 9).

-- ----------------------------------------------------------------
-- CLIENTS DOMAIN → purebrain-clients D1
-- ----------------------------------------------------------------

-- clients table (64 rows)
CREATE TABLE clients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    name TEXT DEFAULT '',
    ai_name TEXT DEFAULT '',
    company TEXT DEFAULT '',
    tier TEXT DEFAULT 'unknown',
    payment_status TEXT DEFAULT 'none',
    paypal_subscription_id TEXT DEFAULT '',
    total_paid REAL DEFAULT 0,
    first_seen_at TEXT DEFAULT '',
    last_active_at TEXT DEFAULT '',
    status TEXT DEFAULT 'active',
    monthly_amount REAL DEFAULT 0,
    joined_date TEXT DEFAULT '',
    source TEXT DEFAULT '',
    hidden INTEGER DEFAULT 0,
    notes TEXT DEFAULT '',
    goes_by TEXT DEFAULT '',
    magic_link TEXT
);

-- users table (32 rows)
CREATE TABLE users (
    id TEXT PRIMARY KEY,
    team_id TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'contributor',
    billing_tier TEXT NOT NULL DEFAULT 'team_member',
    password_hash TEXT,
    oauth_provider_id TEXT,
    last_login_at TEXT,
    created_at TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_team ON users(team_id);

-- sessions table (577 rows)
CREATE TABLE sessions (
    token TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    user_agent TEXT,
    ip_address TEXT,
    created_at TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);

CREATE INDEX idx_sessions_user ON sessions(user_id);

-- team_invites table (35 rows)
CREATE TABLE team_invites (
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

-- ----------------------------------------------------------------
-- PAYMENTS DOMAIN → purebrain-payments D1
-- ----------------------------------------------------------------

-- paypal_events table (DOES NOT EXIST - 0 rows)
-- Schema to be defined in Phase 2 when payments-api is built

-- ================================================================
-- TABLES REMAINING IN purebrain-social (after extraction)
-- ================================================================
-- These tables stay in purebrain-social D1 as they are the actual
-- "social" domain (content publishing, scheduling, analytics).
--
-- NOTE: Full schema for remaining tables should be documented here
-- by reading from live D1 using:
--   wrangler d1 execute purebrain-social --remote --command ".schema"
--
-- Known remaining tables (to be verified in Phase 1):
-- - posts
-- - scheduled_posts
-- - platforms
-- - platform_tokens
-- - analytics
-- - content_calendar
-- - approval_queue
-- - team_members
-- ================================================================

-- ================================================================
-- WORKERS CURRENTLY BOUND TO purebrain-social D1
-- ================================================================
-- Per CTO review (cto-prebuild-review-clients-extraction-2026-05-08.md):
--
-- 1. social-api (workers/social-api/wrangler.toml:7)
--    - Reads clients (will be removed)
--    - Owns posts, scheduled_posts, etc (stays)
--
-- 2. admin-api (workers/admin-api/wrangler.toml:7)
--    - Primary CRUD over clients/users/team_invites
--    - Will fold into clients-api Worker (Phase 3)
--
-- 3. agentmail-webhook (workers/agentmail-webhook/wrangler.toml:7)
--    - Writes ai_name + magic_link to clients table
--    - Will rebind to purebrain-clients D1 OR call clients-api bridge (Phase 5)
--
-- 4. paypal-webhook (workers/paypal-webhook/wrangler.toml:7)
--    - Inserts/updates clients on payment events
--    - Will rebind to purebrain-payments D1 + call clients-api bridge (Phase 4)
--
-- 5. meetings-api (workers/meetings-api/wrangler.toml:7)
--    - Reads users/sessions for auth
--    - Will call clients-api bridge endpoint POST /api/auth/validate-token (Phase 5)
--
-- 6. blog-publisher (workers/blog-publisher/wrangler.toml:7)
--    - Reads users/sessions for auth
--    - Will call clients-api bridge endpoint POST /api/auth/validate-token (Phase 5)
--
-- ================================================================
-- MIGRATION VERIFICATION BASELINE
-- ================================================================
-- Row counts as of 2026-05-08 (full details in purebrain-social-row-counts-2026-05-08.md):
--
-- Tables to migrate:
-- - clients: 64 rows
-- - users: 32 rows
-- - sessions: 577 rows
-- - team_invites: 35 rows
-- - paypal_events: 0 rows (table doesn't exist yet)
--
-- Total client-domain rows: 708
--
-- Phase 6 data migration MUST verify these exact counts after import.
-- ================================================================

-- ================================================================
-- POST-MIGRATION STATE (after Phase 9 cleanup)
-- ================================================================
-- After successful cutover + 24h verification:
-- 1. DROP clients, users, sessions, team_invites from purebrain-social D1
-- 2. Remove client-related routes from social-api Worker
-- 3. Delete admin-api Worker (folded into clients-api)
-- 4. Delete paypal-webhook Worker (folded into payments-api)
--
-- Remaining Workers bound to purebrain-social:
-- - social-api (posts, scheduled_posts, analytics only)
--
-- All client/auth operations route through:
-- - clients-api Worker → purebrain-clients D1
--
-- All payment operations route through:
-- - payments-api Worker → purebrain-payments D1
-- ================================================================
