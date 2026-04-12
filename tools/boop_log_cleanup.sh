#!/bin/bash
# =============================================================================
# boop_log_cleanup.sh - BOOP Log Rotation
# Aether AI Collective - Autonomous BOOP System
#
# Deletes BOOP logs older than 7 days from logs/boops/
# Run by aether-boop-log-cleanup.timer (daily at 02:00)
# =============================================================================

set -euo pipefail

CIV_ROOT="/home/jared/projects/AI-CIV/aether"
LOG_DIR="$CIV_ROOT/logs/boops"
RETENTION_DAYS=7

if [[ ! -d "$LOG_DIR" ]]; then
    echo "Log directory does not exist: $LOG_DIR - nothing to clean"
    exit 0
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S')] BOOP log cleanup starting"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Log dir: $LOG_DIR"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Retention: $RETENTION_DAYS days"

# Count files before
BEFORE=$(find "$LOG_DIR" -name "*.log" | wc -l)

# Delete logs older than retention period
find "$LOG_DIR" -name "*.log" -mtime "+${RETENTION_DAYS}" -delete

# Count files after
AFTER=$(find "$LOG_DIR" -name "*.log" | wc -l)
DELETED=$((BEFORE - AFTER))

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Files before: $BEFORE | After: $AFTER | Deleted: $DELETED"

# Report disk usage of remaining logs
DISK_USAGE=$(du -sh "$LOG_DIR" 2>/dev/null | cut -f1 || echo "unknown")
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Remaining log size: $DISK_USAGE"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Cleanup complete"
