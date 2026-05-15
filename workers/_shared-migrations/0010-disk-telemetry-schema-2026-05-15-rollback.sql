-- Rollback: 0010-disk-telemetry-schema-2026-05-15
-- Drops the disk telemetry tables. Use only if migration must be reverted.

DROP INDEX IF EXISTS idx_disk_alerts_unresolved;
DROP INDEX IF EXISTS idx_disk_alerts_civ_ts;
DROP TABLE IF EXISTS disk_telemetry_alerts;

DROP INDEX IF EXISTS idx_disk_telemetry_tier;
DROP INDEX IF EXISTS idx_disk_telemetry_civ;
DROP INDEX IF EXISTS idx_disk_telemetry_ts;
DROP TABLE IF EXISTS disk_telemetry;
