-- Track 1 DDL — purebrain-clients (excludes ALTER, which is driver-conditional)
-- 2026-05-14 Day 1 Auth Decoupling EXTEND

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

CREATE INDEX IF NOT EXISTS idx_magic_links_session ON magic_links(session_uuid);
CREATE INDEX IF NOT EXISTS idx_magic_links_email ON magic_links(human_email);
CREATE UNIQUE INDEX IF NOT EXISTS idx_magic_links_unique ON magic_links(magic_link);

CREATE TABLE IF NOT EXISTS password_resets (
    token TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    email TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    created_at TEXT NOT NULL,
    used INTEGER DEFAULT 0
);
