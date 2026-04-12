-- D1 Migration: Referral System Schema
-- Database: purebrain-referrals
-- Migrated from: portal_server.py SQLite on app.purebrain.ai
-- Date: 2026-04-06

-- Core referrer accounts
CREATE TABLE IF NOT EXISTS referrers (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    user_name     TEXT NOT NULL DEFAULT '',
    user_email    TEXT NOT NULL UNIQUE COLLATE NOCASE,
    referral_code TEXT NOT NULL UNIQUE COLLATE NOCASE,
    paypal_email  TEXT NOT NULL DEFAULT '',
    password_hash TEXT NOT NULL DEFAULT '',
    created_at    TEXT NOT NULL
);

-- Individual referral records
CREATE TABLE IF NOT EXISTS referrals (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    referrer_id    INTEGER NOT NULL REFERENCES referrers(id),
    referred_email TEXT NOT NULL DEFAULT '' COLLATE NOCASE,
    referred_name  TEXT NOT NULL DEFAULT '',
    status         TEXT NOT NULL DEFAULT 'pending',
    created_at     TEXT NOT NULL,
    completed_at   TEXT
);

-- Referral link click tracking
CREATE TABLE IF NOT EXISTS referral_clicks (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    referral_code TEXT NOT NULL COLLATE NOCASE,
    ip_hash       TEXT NOT NULL DEFAULT '',
    clicked_at    TEXT NOT NULL
);

-- Rewards/earnings ledger
CREATE TABLE IF NOT EXISTS rewards (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    referrer_id INTEGER NOT NULL REFERENCES referrers(id),
    referral_id INTEGER REFERENCES referrals(id),
    reward_type TEXT NOT NULL DEFAULT 'cash',
    reward_value REAL NOT NULL DEFAULT 0.0,
    issued_at   TEXT NOT NULL
);

-- Recurring commission payments from referred member subscriptions
CREATE TABLE IF NOT EXISTS commission_payments (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    referrer_id      INTEGER NOT NULL REFERENCES referrers(id),
    referral_id      INTEGER NOT NULL REFERENCES referrals(id),
    payer_email      TEXT NOT NULL DEFAULT '' COLLATE NOCASE,
    order_id         TEXT NOT NULL DEFAULT '',
    payment_amount   REAL NOT NULL DEFAULT 0.0,
    commission_rate  REAL NOT NULL DEFAULT 0.05,
    commission_value REAL NOT NULL DEFAULT 0.0,
    tier             TEXT NOT NULL DEFAULT '',
    created_at       TEXT NOT NULL
);

-- Admin viewer tokens
CREATE TABLE IF NOT EXISTS admin_tokens (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    token      TEXT NOT NULL UNIQUE,
    email      TEXT NOT NULL DEFAULT '',
    name       TEXT NOT NULL DEFAULT '',
    role       TEXT NOT NULL DEFAULT 'viewer',
    created_at TEXT NOT NULL
);

-- Affiliate login sessions (replaces in-memory dict from portal_server.py)
CREATE TABLE IF NOT EXISTS affiliate_sessions (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    token         TEXT NOT NULL UNIQUE,
    referral_code TEXT NOT NULL COLLATE NOCASE,
    expires_at    INTEGER NOT NULL
);

-- Password reset tokens (replaces in-memory dict from portal_server.py)
CREATE TABLE IF NOT EXISTS password_reset_tokens (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    token      TEXT NOT NULL UNIQUE,
    email      TEXT NOT NULL COLLATE NOCASE,
    expires_at INTEGER NOT NULL
);

-- Rate limiting (replaces in-memory dicts from portal_server.py)
CREATE TABLE IF NOT EXISTS rate_limits (
    key          TEXT PRIMARY KEY,
    count        INTEGER NOT NULL DEFAULT 0,
    window_start INTEGER NOT NULL DEFAULT 0
);

-- Payout requests (replaces JSONL file from portal_server.py)
CREATE TABLE IF NOT EXISTS payout_requests (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    request_id    TEXT NOT NULL UNIQUE,
    referral_code TEXT NOT NULL,
    paypal_email  TEXT NOT NULL DEFAULT '',
    amount        REAL NOT NULL DEFAULT 0.0,
    status        TEXT NOT NULL DEFAULT 'pending',
    created_at    TEXT NOT NULL,
    created_at_ts INTEGER NOT NULL DEFAULT 0,
    paid_at       TEXT,
    batch_id      TEXT DEFAULT '',
    notes         TEXT DEFAULT ''
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_referrals_referrer_id ON referrals(referrer_id);
CREATE INDEX IF NOT EXISTS idx_referrals_referred_email ON referrals(referred_email);
CREATE INDEX IF NOT EXISTS idx_referral_clicks_code ON referral_clicks(referral_code);
CREATE INDEX IF NOT EXISTS idx_rewards_referrer_id ON rewards(referrer_id);
CREATE INDEX IF NOT EXISTS idx_commission_referrer_id ON commission_payments(referrer_id);
CREATE INDEX IF NOT EXISTS idx_commission_order_id ON commission_payments(order_id);
CREATE INDEX IF NOT EXISTS idx_sessions_token ON affiliate_sessions(token);
CREATE INDEX IF NOT EXISTS idx_sessions_expires ON affiliate_sessions(expires_at);
CREATE INDEX IF NOT EXISTS idx_reset_tokens_token ON password_reset_tokens(token);
CREATE INDEX IF NOT EXISTS idx_payout_requests_code ON payout_requests(referral_code);
