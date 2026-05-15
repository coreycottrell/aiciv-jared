-- Migration: 0011-customer-portal-recovery-2026-05-15
-- Database: portal-recovery (NEW dedicated D1 — NOT purebrain-social, NOT disk-telemetry)
-- Author: devops-engineer
-- Spec: specs/customer-portal-recovery-2026-05-15.md
-- CTO review: specs/cto-review-4-specs-2026-05-15.md (verdict: AMEND)
-- Jared greenlight: 2026-05-15 22:40 UTC
--
-- Purpose: silent customer-portal recovery audit log. Every health-check,
-- restart, inner-relaunch, or escalate action MUST land here. Silent recovery
-- (no customer notification) does NOT mean no record — this table IS the record.

CREATE TABLE IF NOT EXISTS customer_portal_recovery_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ts INTEGER NOT NULL,                          -- unix epoch seconds, UTC
  customer_slug TEXT NOT NULL,                  -- e.g. 'whitehurst', 'gary'
  hetzner_host TEXT NOT NULL,                   -- e.g. 'purebrain-3' (46.62.187.74)
  action TEXT NOT NULL,                         -- 'health_check' | 'restart' | 'inner_relaunch' | 'escalate'
  ai_alive_before INTEGER,                      -- 0/1 (SQLite BOOLEAN); NULL if not measured
  ai_alive_after INTEGER,                       -- 0/1; NULL if not yet measured
  thread_count_before INTEGER,
  thread_count_after INTEGER,
  pid_count_before INTEGER,
  pid_count_after INTEGER,
  duration_ms INTEGER,
  outcome TEXT,                                 -- 'success' | 'partial' | 'failed'
  error_message TEXT,
  triggered_by TEXT,                            -- 'cron' | 'admin_button' | 'manual'
  request_id TEXT,                              -- idempotency key (CTO #6) — also useful for cross-system correlation
  CHECK (action IN ('health_check', 'restart', 'inner_relaunch', 'escalate')),
  CHECK (outcome IN ('success', 'partial', 'failed') OR outcome IS NULL),
  CHECK (triggered_by IN ('cron', 'admin_button', 'manual') OR triggered_by IS NULL)
);

CREATE INDEX IF NOT EXISTS idx_recovery_log_customer_ts
  ON customer_portal_recovery_log(customer_slug, ts);

CREATE INDEX IF NOT EXISTS idx_recovery_log_ts
  ON customer_portal_recovery_log(ts);

CREATE INDEX IF NOT EXISTS idx_recovery_log_action_ts
  ON customer_portal_recovery_log(action, ts);

-- Loop-detection helper index: scan recent restarts per customer fast (CTO #7).
CREATE INDEX IF NOT EXISTS idx_recovery_log_restart_loop
  ON customer_portal_recovery_log(customer_slug, action, ts);
