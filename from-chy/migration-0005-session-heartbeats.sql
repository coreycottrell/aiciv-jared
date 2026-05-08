-- Migration 0005: Session health monitoring (P2)
-- Ownership: Morphe (spec) + Chy (schema + worker endpoints) + Aether (probe service)
-- Date: 2026-04-16
--
-- Purpose: Track BaaS session health over time. Detect stale cookies, captcha
-- triggers, and account locks BEFORE they cause post failures. Enable 1-click
-- reauth when health degrades.
--
-- Architecture: Aether's systemd probe service on his VPS polls BaaS every
-- 15 min per active profile, POSTs each result to social-api's
-- /api/surf/heartbeat endpoint. Worker writes rows here only on STATUS CHANGE
-- (save D1 writes) and updates social_accounts.health_status + last_verified_at.
--
-- Thresholds (Aether + Morphe converged, configurable per-platform via probe env):
--   cookie_age <  14 days → healthy
--   cookie_age  14-30 days → stale (warn, allow posts, force-reauth if heavy load)
--   cookie_age > 30 days  → failed (block posts, require reauth)
--   captcha_detected      → captcha_pending
--   ban_detected          → locked (HIGH PRIORITY alert)
-- Env vars on probe service: SURF_STALE_DAYS (default 14), SURF_DEAD_DAYS (default 30)

CREATE TABLE session_heartbeats (
    id TEXT PRIMARY KEY,
    social_account_id TEXT NOT NULL REFERENCES social_accounts(id),
    checked_at TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    status TEXT NOT NULL CHECK(status IN ('healthy', 'captcha_pending', 'stale', 'locked', 'failed')),
    cookie_age_seconds INTEGER,
    captcha_detected INTEGER DEFAULT 0,
    ban_detected INTEGER DEFAULT 0,
    http_status INTEGER,
    response_time_ms INTEGER,
    error_message TEXT
);

-- Latest heartbeat per account (common query)
CREATE INDEX idx_heartbeats_account_recent ON session_heartbeats(social_account_id, checked_at DESC);

-- Alerting query: show accounts with issues in last N minutes
CREATE INDEX idx_heartbeats_alerting ON session_heartbeats(status, checked_at DESC) WHERE status != 'healthy';
