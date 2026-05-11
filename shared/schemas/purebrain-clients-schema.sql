-- ================================================================
-- PUREBRAIN CLIENTS DATABASE SCHEMA
-- ================================================================
-- Purpose: Client authentication, user management, session handling, team invites
-- Migration Source: purebrain-social D1 (pre-Tier3-extraction)
-- Migration Date: 2026-05-08 (Phase 0 gate-zero)
-- Destination: purebrain-clients D1 (new database for clients-api Worker)
--
-- Constitutional Reference: feedback_project_domain_isolation_constitutional.md
-- Spec: exports/portal-files/TIER3-EXTRACTION-SPEC-2026-05-08.md
-- CTO Review: exports/portal-files/cto-prebuild-review-clients-extraction-2026-05-08.md
-- ================================================================

-- ----------------------------------------------------------------
-- TABLE: clients
-- ----------------------------------------------------------------
-- Primary customer/organization records
-- 64 rows as of 2026-05-08 (see purebrain-social-row-counts-2026-05-08.md)
--
-- Note: This table was added ad-hoc during Apr 21-23 sprint and was never
-- in version control until now (per CTO finding). This is gate-zero fix.
-- ----------------------------------------------------------------
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

-- ----------------------------------------------------------------
-- TABLE: users
-- ----------------------------------------------------------------
-- User accounts (team members within client organizations)
-- 32 rows as of 2026-05-08
--
-- Relationship: users.team_id maps to client organization context
-- Auth: password_hash uses PBKDF2-SHA256 with 100k iterations
-- ----------------------------------------------------------------
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

-- ----------------------------------------------------------------
-- TABLE: sessions
-- ----------------------------------------------------------------
-- Active user sessions (opaque token-based auth)
-- 577 rows as of 2026-05-08
--
-- Critical for cutover: tokens are opaque random strings (not JWTs),
-- so they remain valid when migrated to new D1 (per CTO review).
-- No forced re-login required.
-- ----------------------------------------------------------------
CREATE TABLE sessions (
    token TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    user_agent TEXT,
    ip_address TEXT,
    created_at TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);

CREATE INDEX idx_sessions_user ON sessions(user_id);

-- ----------------------------------------------------------------
-- TABLE: team_invites
-- ----------------------------------------------------------------
-- Pending team member invitations
-- 35 rows as of 2026-05-08
--
-- Note: Phase 10 bulk credentials resend will target users in this table
-- who haven't accepted invites yet (after 24h verification window passes)
-- ----------------------------------------------------------------
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

-- ================================================================
-- MIGRATION NOTES
-- ================================================================
-- Phase 6 data migration will:
-- 1. Export these 4 tables from purebrain-social D1
-- 2. Import into purebrain-clients D1
-- 3. Verify row counts match baselines exactly:
--    - clients: 64
--    - users: 32
--    - sessions: 577
--    - team_invites: 35
--    - TOTAL: 708 rows
--
-- Workers to rebind from purebrain-social → purebrain-clients:
-- - admin-api (will fold into clients-api)
-- - agentmail-webhook (via bridge API or direct D1 rebind)
--
-- Workers that will call clients-api via bridge:
-- - paypal-webhook → POST /api/internal/clients (create/update on payment)
-- - meetings-api → POST /api/auth/validate-token (session validation)
-- - blog-publisher → POST /api/auth/validate-token (session validation)
-- ================================================================
