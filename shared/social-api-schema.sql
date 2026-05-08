CREATE TABLE teams (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    created_at TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);

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
CREATE INDEX idx_users_team ON users(team_id);
CREATE INDEX idx_users_email ON users(email);

CREATE TABLE ai_partners (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    partner_name TEXT NOT NULL,
    partner_endpoint TEXT NOT NULL,
    api_key_encrypted TEXT,
    voice_profile TEXT,
    created_at TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    UNIQUE(user_id, partner_name)
);

CREATE TABLE social_accounts (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    platform TEXT NOT NULL,
    account_handle TEXT NOT NULL,
    account_display_name TEXT,
    auth_type TEXT NOT NULL,
    credentials_encrypted TEXT,
    session_token_encrypted TEXT,
    surf_profile_id TEXT,
    last_verified_at TEXT,
    health_status TEXT DEFAULT 'unknown',
    created_at TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    UNIQUE(user_id, platform, account_handle)
);
CREATE INDEX idx_social_accounts_user ON social_accounts(user_id);

CREATE TABLE content_items (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    social_account_id TEXT NOT NULL,
    platform TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'draft',
    scheduled_at TEXT,
    body TEXT NOT NULL,
    media_refs TEXT,
    thread_parent_id TEXT,
    generated_by TEXT,
    approved_by TEXT,
    approved_at TEXT,
    rejection_reason TEXT,
    routing_decision TEXT,
    retry_count INTEGER DEFAULT 0,
    last_error TEXT,
    posted_at TEXT,
    post_url TEXT,
    verification_status TEXT,
    performance_metrics TEXT,
    created_at TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    updated_at TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);
CREATE INDEX idx_content_user_status ON content_items(user_id, status);
CREATE INDEX idx_content_scheduled ON content_items(status, scheduled_at);
CREATE INDEX idx_content_account ON content_items(social_account_id);

CREATE TABLE sessions (
    token TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    user_agent TEXT,
    ip_address TEXT,
    created_at TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);
CREATE INDEX idx_sessions_user ON sessions(user_id);
