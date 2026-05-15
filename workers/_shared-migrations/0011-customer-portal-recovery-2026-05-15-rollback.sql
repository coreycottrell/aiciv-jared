-- Rollback: 0011-customer-portal-recovery-2026-05-15
-- Drops the audit log table introduced by 0011. Safe — no FK references elsewhere.

DROP INDEX IF EXISTS idx_recovery_log_restart_loop;
DROP INDEX IF EXISTS idx_recovery_log_action_ts;
DROP INDEX IF EXISTS idx_recovery_log_ts;
DROP INDEX IF EXISTS idx_recovery_log_customer_ts;
DROP TABLE IF EXISTS customer_portal_recovery_log;
