-- Migration 0008: magic token exchange audit log
-- Applied to: purebrain-social D1 (same DB as team_invites / sessions)
-- Date: 2026-05-15
-- Purpose: Audit all magic-link exchange attempts for security review

CREATE TABLE IF NOT EXISTS magic_token_audit_log (
  id          TEXT    PRIMARY KEY,              -- UUID v4
  invite_id   TEXT    NOT NULL,                 -- FK team_invites.id (not enforced — D1 no FK)
  user_id     TEXT    NOT NULL,                 -- users.id of the redeemer
  ip          TEXT    NOT NULL,                 -- CF-Connecting-IP (IPv4 or IPv6)
  ua_present  INTEGER NOT NULL DEFAULT 0,       -- 1 if User-Agent header was present, else 0
  outcome     TEXT    NOT NULL,                 -- 'ok' | 'expired' | 'consumed' | 'invalid' | 'disabled'
  ts          TEXT    NOT NULL                  -- ISO-8601 UTC
);

CREATE INDEX IF NOT EXISTS idx_mtal_ts        ON magic_token_audit_log(ts);
CREATE INDEX IF NOT EXISTS idx_mtal_invite_id ON magic_token_audit_log(invite_id);
CREATE INDEX IF NOT EXISTS idx_mtal_outcome   ON magic_token_audit_log(outcome, ts);
