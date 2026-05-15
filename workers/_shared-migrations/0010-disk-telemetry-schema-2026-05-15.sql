-- Migration: 0010-disk-telemetry-schema-2026-05-15
-- Database: disk-telemetry (NEW dedicated D1 — NOT purebrain-social)
-- Author: devops-engineer
-- Spec: specs/disk-safety-telemetry-2026-05-15.md
-- CTO review: specs/cto-review-4-specs-2026-05-15.md (APPROVE w/ 4 amendments)
--
-- Purpose: time-series storage for host disk telemetry across the CIV fleet.
-- CTO amendment #4: source_ip column for forgery detection if fleet token leaks.

CREATE TABLE IF NOT EXISTS disk_telemetry (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ts INTEGER NOT NULL,                      -- unix epoch seconds, UTC
  civ_name TEXT NOT NULL,                   -- 'aether' | 'chy' | 'morphe' | etc.
  hostname TEXT NOT NULL,                   -- physical host identifier
  source_ip TEXT,                           -- CF cf-connecting-ip stamped by Worker (CTO amend #4)
  disk_root_used_pct INTEGER NOT NULL,      -- 0..100
  disk_root_free_mb INTEGER NOT NULL,
  tmp_size_mb INTEGER NOT NULL,
  tmp_large_files_count INTEGER NOT NULL,   -- /tmp files > 100 MB
  working_tree_large_files_count INTEGER,   -- ~/projects files > 100 MB (flagged only, never deleted)
  alert_tier TEXT,                          -- 'info' | 'warn' | 'critical'
  raw_top5_tmp_files TEXT,                  -- JSON: array of {size_mb, age_hours, suffix} — NO file paths (PII)
  daemon_version TEXT,                      -- semver of disk-telemetry daemon
  CHECK (alert_tier IN ('info', 'warn', 'critical') OR alert_tier IS NULL),
  CHECK (disk_root_used_pct >= 0 AND disk_root_used_pct <= 100)
);

CREATE INDEX IF NOT EXISTS idx_disk_telemetry_ts
  ON disk_telemetry(ts);

CREATE INDEX IF NOT EXISTS idx_disk_telemetry_civ
  ON disk_telemetry(civ_name, ts);

CREATE INDEX IF NOT EXISTS idx_disk_telemetry_tier
  ON disk_telemetry(alert_tier, ts);

-- Alert audit log — separate table so alerts survive snapshot retention pruning.
CREATE TABLE IF NOT EXISTS disk_telemetry_alerts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ts INTEGER NOT NULL,                      -- unix epoch seconds, UTC
  civ_name TEXT NOT NULL,
  tier TEXT NOT NULL,                       -- 'warn' | 'critical'
  message TEXT NOT NULL,
  resolved_at INTEGER,
  resolution_action TEXT,                   -- 'auto-deleted' | 'manual' | 'expired'
  CHECK (tier IN ('warn', 'critical'))
);

CREATE INDEX IF NOT EXISTS idx_disk_alerts_civ_ts
  ON disk_telemetry_alerts(civ_name, ts);

CREATE INDEX IF NOT EXISTS idx_disk_alerts_unresolved
  ON disk_telemetry_alerts(resolved_at, ts);
