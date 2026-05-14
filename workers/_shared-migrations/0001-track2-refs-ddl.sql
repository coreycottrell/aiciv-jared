-- Track 2 DDL — purebrain-referrals (CREATE auth_*-prefixed tables)
-- 2026-05-14 Day 1 Auth Decoupling EXTEND

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

CREATE TABLE IF NOT EXISTS auth_sessions (
    token TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    user_agent TEXT,
    ip_address TEXT,
    created_at TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);
CREATE INDEX IF NOT EXISTS idx_auth_sessions_user ON auth_sessions(user_id);

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

CREATE TABLE IF NOT EXISTS auth_password_resets (
    token TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    email TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    created_at TEXT NOT NULL,
    used INTEGER DEFAULT 0
);
