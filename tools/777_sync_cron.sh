#!/usr/bin/env bash
# =============================================================================
# 777 Command Center — 60-Second Sync Cron
# =============================================================================
# Runs every 60s (or cron interval of your choice).
# 1. Refreshes data.json from Google Sheets via 777_data_fetcher.py
# 2. Applies pending bidirectional edits to Sheets via 777_sheets_writer.py
# 3. Logs all activity with timestamps to logs/777-sync.log
# 4. Lockfile prevents overlapping runs
#
# CRON EXAMPLE (every 60s via two 30s-offset entries):
#   * * * * *       cd /home/jared/projects/AI-CIV/aether && bash tools/777_sync_cron.sh
#   * * * * * sleep 30 && cd /home/jared/projects/AI-CIV/aether && bash tools/777_sync_cron.sh
#
# Author: PTT full-stack-developer
# =============================================================================

set -euo pipefail

# ── Paths ─────────────────────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(dirname "$SCRIPT_DIR")"
LOG_FILE="$ROOT/logs/777-sync.log"
LOCKFILE="/tmp/777_sync.lock"
PYTHON="python3"

# ── Timestamp helper ──────────────────────────────────────────────────────────
ts() { date '+%Y-%m-%d %H:%M:%S'; }

log() {
    echo "[$(ts)] $*" >> "$LOG_FILE"
}

log_stdout() {
    echo "[$(ts)] $*" | tee -a "$LOG_FILE"
}

# ── Ensure logs dir exists ─────────────────────────────────────────────────────
mkdir -p "$(dirname "$LOG_FILE")"
mkdir -p "$ROOT/data"

# ── Lockfile guard ────────────────────────────────────────────────────────────
# If lock exists and the PID it contains is still running, exit.
if [ -f "$LOCKFILE" ]; then
    LOCK_PID=$(cat "$LOCKFILE" 2>/dev/null || echo "")
    if [ -n "$LOCK_PID" ] && kill -0 "$LOCK_PID" 2>/dev/null; then
        log "SKIP — previous run (PID $LOCK_PID) still running. Exiting."
        exit 0
    else
        log "STALE lock (PID $LOCK_PID) removed."
        rm -f "$LOCKFILE"
    fi
fi

# Write our PID to lockfile
echo $$ > "$LOCKFILE"

# Ensure lockfile is removed on exit (normal or error)
cleanup() {
    rm -f "$LOCKFILE"
}
trap cleanup EXIT

# ── Start ─────────────────────────────────────────────────────────────────────
log_stdout "=== 777 sync started (PID $$) ==="
START_TS=$(date +%s)

cd "$ROOT"

# ── Step 1: Fetch from Google Sheets → data.json ──────────────────────────────
log "STEP 1: Running 777_data_fetcher.py..."
FETCH_EXIT=0
FETCH_OUTPUT=$($PYTHON tools/777_data_fetcher.py 2>&1) || FETCH_EXIT=$?

if [ "$FETCH_EXIT" -eq 0 ]; then
    log "FETCH OK — data.json refreshed."
    log "  Output tail: $(echo "$FETCH_OUTPUT" | tail -3 | tr '\n' '|')"
else
    log "FETCH FAILED (exit $FETCH_EXIT) — keeping previous data.json."
    log "  Error: $(echo "$FETCH_OUTPUT" | tail -5 | tr '\n' '|')"
fi

# ── Step 1.5: Warm D1 cache from fresh data.json ──────────────────────────────
if [ "$FETCH_EXIT" -eq 0 ]; then
    CACHE_OUTPUT=$($PYTHON tools/777_d1_cache.py 2>&1) || true
    log "CACHE: $(echo "$CACHE_OUTPUT" | tail -2 | tr '\n' '|')"
fi

# ── Step 2: Apply pending edits back to Sheets ────────────────────────────────
PENDING_FILE="$ROOT/exports/777-command-center/pending-edits.json"

PENDING_COUNT=0
if [ -f "$PENDING_FILE" ]; then
    # Count unsynced edits using python (handles JSON reliably)
    PENDING_COUNT=$($PYTHON -c "
import json, sys
try:
    data = json.load(open('$PENDING_FILE'))
    edits = data.get('edits', [])
    unsynced = [e for e in edits if not e.get('synced_at')]
    print(len(unsynced))
except Exception as e:
    print(0)
" 2>/dev/null || echo "0")
fi

if [ "$PENDING_COUNT" -gt 0 ]; then
    log "STEP 2: $PENDING_COUNT pending edit(s) found — running 777_sheets_writer.py..."
    WRITE_EXIT=0
    WRITE_OUTPUT=$($PYTHON tools/777_sheets_writer.py 2>&1) || WRITE_EXIT=$?

    if [ "$WRITE_EXIT" -eq 0 ]; then
        log "WRITE OK — pending edits applied to Sheets."
        log "  Output tail: $(echo "$WRITE_OUTPUT" | tail -3 | tr '\n' '|')"
    else
        log "WRITE FAILED (exit $WRITE_EXIT) — edits remain queued."
        log "  Error: $(echo "$WRITE_OUTPUT" | tail -5 | tr '\n' '|')"
    fi
else
    log "STEP 2: No pending edits. Skipping Sheets write."
fi

# ── Done ──────────────────────────────────────────────────────────────────────
END_TS=$(date +%s)
ELAPSED=$(( END_TS - START_TS ))

log_stdout "=== 777 sync complete in ${ELAPSED}s ==="

# Warn if we're approaching the 30s target
if [ "$ELAPSED" -gt 30 ]; then
    log "WARNING: Run took ${ELAPSED}s — longer than 30s target. Consider investigating."
fi

exit 0
