-- Rollback migration 0009: Remove expires_at and consumed_at from team_invites
-- Date: 2026-05-15
-- Note: D1 does not support DROP COLUMN — this is a no-op placeholder for documentation

-- ALTER TABLE team_invites DROP COLUMN consumed_at;  -- Not supported in D1
-- ALTER TABLE team_invites DROP COLUMN expires_at;   -- Not supported in D1

-- Manual rollback: column values can be set to NULL but columns persist
