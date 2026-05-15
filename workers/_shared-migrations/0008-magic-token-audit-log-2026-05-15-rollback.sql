-- Rollback migration 0008: magic token exchange audit log
-- Date: 2026-05-15

DROP INDEX IF EXISTS idx_mtal_outcome;
DROP INDEX IF EXISTS idx_mtal_invite_id;
DROP INDEX IF EXISTS idx_mtal_ts;
DROP TABLE IF EXISTS magic_token_audit_log;
