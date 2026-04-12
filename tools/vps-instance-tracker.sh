#!/bin/bash
# VPS Instance Tracker - Diagnose Claude Code process sprawl
# Usage: ./tools/vps-instance-tracker.sh [--diagnose] [--clean]
#
# Flags:
#   --diagnose  Deep analysis: correlate PIDs to tmux sessions, show start times
#   --clean     Kill orphaned Claude processes (keeps youngest N=MAX_CLAUDE_INSTANCES)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CIV_ROOT="$(dirname "$SCRIPT_DIR")"
TG_SEND="$SCRIPT_DIR/tg_send.sh"
MAX_INSTANCES=2

DIAGNOSE=false
CLEAN=false
for arg in "$@"; do
    case "$arg" in
        --diagnose) DIAGNOSE=true ;;
        --clean)    CLEAN=true ;;
    esac
done

echo ""
echo "=== CLAUDE CODE INSTANCE TRACKER ==="
echo "Timestamp: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# ── 1. All Claude-related processes ────────────────────────────────────────
echo "--- All Claude / claude-related processes ---"
ps aux | grep -i "[c]laude" | awk '{printf "PID=%-8s STARTED=%-20s CMD=%s\n", $2, $9, substr($0, index($0,$11))}' || echo "(none)"

echo ""
echo "--- Process start times (detailed) ---"
CLAUDE_PIDS=$(pgrep -f "claude" 2>/dev/null | tr '\n' ' ' || echo "")
if [ -n "$CLAUDE_PIDS" ]; then
    ps -o pid,lstart,etime,ppid,cmd --no-headers -p $CLAUDE_PIDS 2>/dev/null | \
        awk '{printf "PID=%-6s START=%-30s ELAPSED=%-12s PPID=%-8s CMD=%s\n", $1, $2" "$3" "$4" "$5" "$6, $7, $8, substr($0, index($0,$9))}' || true
else
    echo "(no Claude processes found)"
fi

echo ""
echo "--- tmux sessions ---"
tmux list-sessions 2>/dev/null || echo "(no tmux sessions)"

echo ""
echo "--- tmux session details (windows + panes) ---"
if tmux list-sessions &>/dev/null; then
    tmux list-sessions -F "#{session_name}|#{session_windows}|#{session_created_string}|#{session_attached}" 2>/dev/null | \
        awk -F'|' '{printf "  Session: %-20s Windows: %-4s Created: %-30s Attached: %s\n", $1, $2, $3, $4}'
fi

echo ""
echo "--- aether-session.service status ---"
systemctl status aether-session.service --no-pager -l 2>/dev/null | head -20 || echo "(service not found)"

echo ""
echo "--- aether-session.service: restart count & logs ---"
# Shows how many times the service has auto-restarted
journalctl -u aether-session.service --no-pager -n 30 --output=short-monotonic 2>/dev/null | grep -E "(Started|Stopped|Restarting|Killed|Main|Restart)" || echo "(no journal data)"

echo ""
echo "--- aether-telegram.service status ---"
systemctl status aether-telegram.service --no-pager -l 2>/dev/null | head -10 || echo "(service not found)"

if [ "$DIAGNOSE" = true ]; then
    echo ""
    echo "=== DEEP DIAGNOSIS ==="

    echo ""
    echo "--- Process tree (pstree for claude) ---"
    pstree -p 2>/dev/null | grep -i "claude" | head -30 || \
        ps -elf | grep -i "[c]laude" | head -30 || echo "(pstree not available)"

    echo ""
    echo "--- Parent PIDs of Claude processes ---"
    if [ -n "$CLAUDE_PIDS" ]; then
        for pid in $CLAUDE_PIDS; do
            PPID=$(ps -o ppid= -p "$pid" 2>/dev/null | tr -d ' ' || echo "?")
            PNAME=$(ps -o comm= -p "$PPID" 2>/dev/null || echo "?")
            START=$(ps -o lstart= -p "$pid" 2>/dev/null || echo "?")
            echo "  PID $pid -> PPID $PPID ($PNAME) | Started: $START"
        done
    fi

    echo ""
    echo "--- Is aether-session configured with Restart=always? ---"
    cat /etc/systemd/system/aether-session.service 2>/dev/null | grep -E "(Restart|ExecStart|WorkingDirectory|User)" || \
        systemctl cat aether-session.service 2>/dev/null | grep -E "(Restart|ExecStart|WorkingDirectory|User)" || \
        echo "(cannot read service file)"

    echo ""
    echo "--- Is aether-session.service calling claude code on restart? ---"
    systemctl cat aether-session.service 2>/dev/null || echo "(cannot cat service)"

    echo ""
    echo "--- SSH sessions currently active ---"
    who 2>/dev/null || w 2>/dev/null | head -20 || echo "(who not available)"

    echo ""
    echo "--- .current_session file ---"
    cat "$CIV_ROOT/.current_session" 2>/dev/null || echo "(not found)"

    echo ""
    echo "--- Recent logins ---"
    last | head -10 2>/dev/null || echo "(last not available)"
fi

if [ "$CLEAN" = true ]; then
    echo ""
    echo "=== CLEANUP: Killing orphaned Claude processes ==="
    CLAUDE_PIDS_LIST=$(pgrep -f "claude" 2>/dev/null | sort -n || echo "")
    TOTAL=$(echo "$CLAUDE_PIDS_LIST" | grep -c '[0-9]' || echo "0")

    if [ "$TOTAL" -le "$MAX_INSTANCES" ]; then
        echo "Only $TOTAL Claude process(es) running. Max=$MAX_INSTANCES. No cleanup needed."
    else
        # Keep the MAX_INSTANCES most recent (highest PIDs = most recently spawned on Linux)
        TO_KILL=$(echo "$CLAUDE_PIDS_LIST" | head -n "-$MAX_INSTANCES")
        KILLED_COUNT=0
        for pid in $TO_KILL; do
            echo "  Killing PID $pid..."
            kill -TERM "$pid" 2>/dev/null && KILLED_COUNT=$((KILLED_COUNT + 1)) || echo "  (could not kill $pid - may need sudo)"
        done
        echo "Killed $KILLED_COUNT orphaned process(es). Remaining: $(pgrep -c -f claude 2>/dev/null || echo 0)"

        if [ -x "$TG_SEND" ]; then
            "$TG_SEND" "CTO: Instance cleanup ran. Killed $KILLED_COUNT orphaned Claude processes. Remaining: $(pgrep -c -f claude 2>/dev/null || echo 0)" 2>/dev/null || true
        fi
    fi
fi

echo ""
echo "=== END INSTANCE TRACKER ==="
