#!/bin/bash
# VPS Cleanup - Kill orphaned Claude Code processes safely
# Keeps the N most recently-started processes (default: 1)
# Usage: ./tools/vps-cleanup.sh [--keep N] [--dry-run] [--force]
#
# Default behavior: interactive confirmation before killing
# --dry-run: Show what would be killed without doing it
# --force:   Kill without asking

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CIV_ROOT="$(dirname "$SCRIPT_DIR")"
TG_SEND="$SCRIPT_DIR/tg_send.sh"

KEEP=1       # How many Claude instances to keep (the most recent)
DRY_RUN=false
FORCE=false

for arg in "$@"; do
    case "$arg" in
        --keep)   shift; KEEP="$1" ;;
        --dry-run) DRY_RUN=true ;;
        --force)   FORCE=true ;;
    esac
done

echo ""
echo "=== VPS CLEANUP - Claude Process Management ==="
echo "Timestamp: $(date '+%Y-%m-%d %H:%M:%S')"
echo "Policy: Keep $KEEP most recent Claude process(es)"
echo ""

# Get all Claude PIDs sorted by start time (oldest first via /proc/PID/stat)
# We use /proc to get start time in clock ticks since boot - lower = older
mapfile -t ALL_PIDS < <(pgrep -f "claude" 2>/dev/null | sort -n || true)
TOTAL=${#ALL_PIDS[@]}

echo "Found $TOTAL Claude process(es):"
for pid in "${ALL_PIDS[@]}"; do
    START=$(ps -o lstart= -p "$pid" 2>/dev/null | xargs || echo "unknown")
    CMD=$(ps -o cmd= -p "$pid" 2>/dev/null | cut -c1-80 || echo "unknown")
    echo "  PID $pid | Started: $START | $CMD"
done
echo ""

if [ "$TOTAL" -le "$KEEP" ]; then
    echo "Total ($TOTAL) <= Keep ($KEEP). No cleanup needed."
    exit 0
fi

# Identify which to kill: all but the last $KEEP entries (by PID order, higher = newer on Linux)
TO_KILL=("${ALL_PIDS[@]:0:$((TOTAL - KEEP))}")
TO_KEEP=("${ALL_PIDS[@]:$((TOTAL - KEEP))}")

echo "Will KEEP ${#TO_KEEP[@]} process(es): PIDs ${TO_KEEP[*]}"
echo "Will KILL ${#TO_KILL[@]} process(es): PIDs ${TO_KILL[*]}"
echo ""

if [ "$DRY_RUN" = true ]; then
    echo "DRY RUN - no processes were killed."
    exit 0
fi

if [ "$FORCE" = false ]; then
    read -r -p "Confirm kill? [y/N] " response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        echo "Cancelled."
        exit 0
    fi
fi

KILLED=0
FAILED=0
for pid in "${TO_KILL[@]}"; do
    echo -n "  Sending SIGTERM to PID $pid..."
    if kill -TERM "$pid" 2>/dev/null; then
        echo " done"
        KILLED=$((KILLED + 1))
    else
        echo " FAILED (check sudo)"
        FAILED=$((FAILED + 1))
    fi
done

sleep 2

# Verify what's left
REMAINING=$(pgrep -c -f "claude" 2>/dev/null || echo "0")
echo ""
echo "Result: Killed $KILLED, Failed $FAILED, Remaining $REMAINING"

# Send Telegram update
if [ -x "$TG_SEND" ]; then
    "$TG_SEND" "CTO: VPS Cleanup complete. Killed: $KILLED orphaned Claude processes. Remaining: $REMAINING" 2>/dev/null || true
fi

# Log it
LOG_FILE="$CIV_ROOT/logs/vps_health.log"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] CLEANUP: killed=$KILLED failed=$FAILED remaining=$REMAINING" >> "$LOG_FILE" 2>/dev/null || true
