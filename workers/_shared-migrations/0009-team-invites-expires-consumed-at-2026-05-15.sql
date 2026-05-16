-- Migration 0009: Add TTL and consumed-at columns to team_invites
-- Applied to: purebrain-social D1
-- Date: 2026-05-15
-- Purpose: Enable magic-link token expiry and consumption tracking

-- ALTER TABLE is safe for D1 (idempotent via try/catch in worker bootstrap)
ALTER TABLE team_invites ADD COLUMN expires_at  TEXT;   -- ISO-8601 UTC, nullable = no expiry
ALTER TABLE team_invites ADD COLUMN consumed_at TEXT;   -- ISO-8601 UTC, set on exchange
