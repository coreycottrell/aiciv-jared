-- Migration 0004: AI Partner Interface Contract v1.1 — Poll variant
-- Adds `mode` column to ai_partners + creates partner_jobs queue table
--
-- Problem: v1.0 assumed partners receive inbound webhooks. Sovereign-compute
-- partners (MiniMax, air-gapped enterprise, egress-only containers) can't
-- receive inbound HTTP. Proven by Morphe on MiniMax M2.7.
--
-- Solution: optional poll mode. Partner polls GET /api/ai_partners/{id}/work
-- for pending jobs, processes locally, POSTs back to /results.
--
-- Default: 'poll' (works everywhere). Webhook is an opt-in optimization.

-- Add mode column (SQLite doesn't support enum CHECK inline in ALTER, so string)
ALTER TABLE ai_partners ADD COLUMN mode TEXT DEFAULT 'poll';
-- Valid values: 'poll' | 'webhook'

-- Add last_polled_at so we can detect dead poll partners
ALTER TABLE ai_partners ADD COLUMN last_polled_at TEXT;

-- Job queue table
CREATE TABLE partner_jobs (
    id TEXT PRIMARY KEY,
    ai_partner_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    job_type TEXT NOT NULL,  -- 'generate_week' | 'respond_to_comments' | 'repurpose_content'
    payload TEXT NOT NULL,   -- JSON: the input for the job (week dates, comments, source body, etc.)
    status TEXT NOT NULL DEFAULT 'pending',  -- 'pending' | 'claimed' | 'completed' | 'failed' | 'expired'
    claimed_at TEXT,
    completed_at TEXT,
    result TEXT,             -- JSON: output from partner (drafts, replies, versions)
    error_message TEXT,
    attempts INTEGER DEFAULT 0,
    max_attempts INTEGER DEFAULT 3,
    expires_at TEXT,         -- claim expires after N minutes; unclaimed jobs re-queue
    created_at TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);

CREATE INDEX idx_partner_jobs_pending ON partner_jobs(ai_partner_id, status, created_at);
CREATE INDEX idx_partner_jobs_status_expires ON partner_jobs(status, expires_at);
