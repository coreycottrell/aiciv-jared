#!/bin/bash
# VPS Health Monitor - Pure Technology / Aether
# Usage: ./tools/vps-health.sh [--json] [--alert] [--quiet]
#
# Flags:
#   --json    Output raw JSON (for programmatic use / logging)
#   --alert   Only send Telegram alert if thresholds are exceeded
#   --quiet   No terminal output (for cron/systemd use)
#   --kill-orphans  Interactively offer to kill orphaned Claude processes

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CIV_ROOT="$(dirname "$SCRIPT_DIR")"
LOG_FILE="$CIV_ROOT/logs/vps_health.log"
TG_SEND="$SCRIPT_DIR/tg_send.sh"

# ── Thresholds ─────────────────────────────────────────────────────────────
MAX_CLAUDE_INSTANCES=2     # Alert if more than this many Claude Code processes
MAX_CPU_PCT=85             # Alert if CPU usage exceeds this %
MAX_RAM_PCT=85             # Alert if RAM usage exceeds this %
MAX_DISK_PCT=85            # Alert if any disk mount exceeds this %
MAX_TMUX_SESSIONS=6        # Alert if more than this many tmux sessions

# ── Argument parsing ────────────────────────────────────────────────────────
JSON_MODE=false
ALERT_MODE=false
QUIET_MODE=false
KILL_ORPHANS=false

for arg in "$@"; do
    case "$arg" in
        --json)         JSON_MODE=true ;;
        --alert)        ALERT_MODE=true ;;
        --quiet)        QUIET_MODE=true ;;
        --kill-orphans) KILL_ORPHANS=true ;;
    esac
done

# ── Collect metrics ─────────────────────────────────────────────────────────

# Timestamp
TS="$(date '+%Y-%m-%d %H:%M:%S')"

# Uptime
UPTIME_STR="$(uptime -p 2>/dev/null || uptime)"

# CPU usage (1-second sample)
CPU_IDLE=$(top -bn1 | grep "Cpu(s)" | awk '{print $8}' | sed 's/%id,//' | sed 's/,//' 2>/dev/null || echo "0")
CPU_PCT=$(echo "100 - $CPU_IDLE" | bc 2>/dev/null || echo "0")
# Fallback: use /proc/stat for a cleaner reading
if ! command -v bc &>/dev/null || [ -z "$CPU_PCT" ] || [ "$CPU_PCT" = "0" ]; then
    CPU_PCT=$(grep 'cpu ' /proc/stat | awk '{usage=($2+$4)*100/($2+$3+$4+$5)} END {printf "%.1f", usage}' 2>/dev/null || echo "N/A")
fi

# RAM usage
RAM_TOTAL=$(free -m | awk '/^Mem:/{print $2}')
RAM_USED=$(free -m | awk '/^Mem:/{print $3}')
RAM_FREE=$(free -m | awk '/^Mem:/{print $4}')
RAM_PCT=$(awk "BEGIN {printf \"%.1f\", ($RAM_USED/$RAM_TOTAL)*100}" 2>/dev/null || echo "N/A")

# Disk usage (root partition)
DISK_INFO=$(df -h / | tail -1)
DISK_USED=$(echo "$DISK_INFO" | awk '{print $3}')
DISK_TOTAL=$(echo "$DISK_INFO" | awk '{print $2}')
DISK_PCT=$(echo "$DISK_INFO" | awk '{print $5}' | tr -d '%')

# Claude Code process count and details
CLAUDE_PIDS=$(pgrep -f "claude" 2>/dev/null || true)
CLAUDE_COUNT=$(echo "$CLAUDE_PIDS" | grep -c '[0-9]' 2>/dev/null || echo "0")
CLAUDE_DETAIL=""
if [ -n "$CLAUDE_PIDS" ]; then
    CLAUDE_DETAIL=$(ps -o pid,lstart,etime,cmd --no-headers -p $(echo "$CLAUDE_PIDS" | tr '\n' ',') 2>/dev/null | \
        sed 's/[[:space:]]\+/ /g' | head -20 || echo "unable to get details")
fi

# Node process count
NODE_COUNT=$(pgrep -c -f "node" 2>/dev/null || echo "0")

# Python process count
PYTHON_COUNT=$(pgrep -c -f "python" 2>/dev/null || echo "0")

# tmux sessions
TMUX_SESSIONS=$(tmux list-sessions 2>/dev/null || echo "no tmux sessions")
TMUX_COUNT=$(tmux list-sessions 2>/dev/null | wc -l || echo "0")

# tmux <-> Claude mapping: which claude PIDs are in which tmux sessions
TMUX_CLAUDE_MAP=""
if tmux list-sessions &>/dev/null; then
    while IFS= read -r session_line; do
        SESSION_NAME=$(echo "$session_line" | cut -d: -f1)
        PANE_PID=$(tmux list-panes -t "$SESSION_NAME" -F "#{pane_pid}" 2>/dev/null | head -1 || echo "")
        if [ -n "$PANE_PID" ]; then
            CHILD_CLAUDES=$(pgrep -P "$PANE_PID" -f claude 2>/dev/null | wc -l || echo "0")
            TMUX_CLAUDE_MAP="${TMUX_CLAUDE_MAP}  Session [$SESSION_NAME] pane_pid=$PANE_PID claude_children=$CHILD_CLAUDES\n"
        fi
    done < <(tmux list-sessions 2>/dev/null)
fi

# systemd service status
AETHER_SESSION_STATUS=$(systemctl is-active aether-session.service 2>/dev/null || echo "not-found")
AETHER_TELEGRAM_STATUS=$(systemctl is-active aether-telegram.service 2>/dev/null || echo "not-found")

# Network connections
NET_ESTABLISHED=$(ss -tn state established 2>/dev/null | grep -c ESTAB || netstat -tn 2>/dev/null | grep -c ESTABLISHED || echo "N/A")

# Load average
LOAD_AVG=$(cat /proc/loadavg | awk '{print $1, $2, $3}')

# ── Threshold checks ────────────────────────────────────────────────────────
ALERTS=()
ALERT_TRIGGERED=false

if [ "$CLAUDE_COUNT" -gt "$MAX_CLAUDE_INSTANCES" ] 2>/dev/null; then
    ALERTS+=("CLAUDE_SPRAWL: $CLAUDE_COUNT Claude processes running (max: $MAX_CLAUDE_INSTANCES)")
    ALERT_TRIGGERED=true
fi

DISK_PCT_INT="${DISK_PCT%%.*}"
if [ "${DISK_PCT_INT:-0}" -gt "$MAX_DISK_PCT" ] 2>/dev/null; then
    ALERTS+=("DISK_HIGH: Disk usage at ${DISK_PCT}% (max: $MAX_DISK_PCT%)")
    ALERT_TRIGGERED=true
fi

RAM_PCT_INT="${RAM_PCT%%.*}"
if [ "${RAM_PCT_INT:-0}" -gt "$MAX_RAM_PCT" ] 2>/dev/null; then
    ALERTS+=("RAM_HIGH: RAM usage at ${RAM_PCT}% = ${RAM_USED}MB/${RAM_TOTAL}MB (max: $MAX_RAM_PCT%)")
    ALERT_TRIGGERED=true
fi

if [ "$TMUX_COUNT" -gt "$MAX_TMUX_SESSIONS" ] 2>/dev/null; then
    ALERTS+=("TMUX_HIGH: $TMUX_COUNT tmux sessions (max: $MAX_TMUX_SESSIONS)")
    ALERT_TRIGGERED=true
fi

# ── Kill orphans logic ──────────────────────────────────────────────────────
if [ "$KILL_ORPHANS" = true ] && [ "$CLAUDE_COUNT" -gt "$MAX_CLAUDE_INSTANCES" ]; then
    echo ""
    echo "=== ORPHAN CLAUDE PROCESSES ==="
    echo "$CLAUDE_DETAIL"
    echo ""
    echo "Found $CLAUDE_COUNT Claude processes. Max allowed: $MAX_CLAUDE_INSTANCES"
    echo "To kill oldest excess processes, run: tools/vps-cleanup.sh"
fi

# ── Format output ───────────────────────────────────────────────────────────
if [ "$JSON_MODE" = true ]; then
    # JSON output for logging
    cat <<JSON
{
  "timestamp": "$TS",
  "uptime": "$UPTIME_STR",
  "cpu_pct": "$CPU_PCT",
  "ram_pct": "$RAM_PCT",
  "ram_used_mb": "$RAM_USED",
  "ram_total_mb": "$RAM_TOTAL",
  "disk_pct": "$DISK_PCT",
  "disk_used": "$DISK_USED",
  "disk_total": "$DISK_TOTAL",
  "load_avg": "$LOAD_AVG",
  "claude_count": $CLAUDE_COUNT,
  "node_count": $NODE_COUNT,
  "python_count": $PYTHON_COUNT,
  "tmux_sessions": $TMUX_COUNT,
  "net_established": "$NET_ESTABLISHED",
  "aether_session_service": "$AETHER_SESSION_STATUS",
  "aether_telegram_service": "$AETHER_TELEGRAM_STATUS",
  "alerts": $(printf '%s\n' "${ALERTS[@]:-}" | python3 -c "import sys,json; lines=[l for l in sys.stdin.read().splitlines() if l]; print(json.dumps(lines))")
}
JSON
else
    if [ "$QUIET_MODE" = false ]; then
        # Human-readable dashboard
        echo ""
        echo "╔══════════════════════════════════════════════════════════════╗"
        echo "║          VPS HEALTH MONITOR — Pure Technology                ║"
        echo "╠══════════════════════════════════════════════════════════════╣"
        printf "║  %-60s ║\n" "Timestamp : $TS"
        printf "║  %-60s ║\n" "Uptime    : $UPTIME_STR"
        echo "╠══════════════════════════════════════════════════════════════╣"
        printf "║  %-60s ║\n" "CPU       : ${CPU_PCT}%  |  Load Avg: $LOAD_AVG"
        printf "║  %-60s ║\n" "RAM       : ${RAM_PCT}%  (${RAM_USED}MB used / ${RAM_TOTAL}MB total)"
        printf "║  %-60s ║\n" "Disk (/)  : ${DISK_PCT}%  (${DISK_USED} used / ${DISK_TOTAL} total)"
        echo "╠══════════════════════════════════════════════════════════════╣"
        printf "║  %-60s ║\n" "Claude    : $CLAUDE_COUNT process(es)  [max: $MAX_CLAUDE_INSTANCES]"
        printf "║  %-60s ║\n" "Node      : $NODE_COUNT process(es)"
        printf "║  %-60s ║\n" "Python    : $PYTHON_COUNT process(es)"
        printf "║  %-60s ║\n" "tmux      : $TMUX_COUNT session(s)  [max: $MAX_TMUX_SESSIONS]"
        printf "║  %-60s ║\n" "Net Conns : $NET_ESTABLISHED established"
        echo "╠══════════════════════════════════════════════════════════════╣"
        printf "║  %-60s ║\n" "aether-session.service  : $AETHER_SESSION_STATUS"
        printf "║  %-60s ║\n" "aether-telegram.service : $AETHER_TELEGRAM_STATUS"
        echo "╠══════════════════════════════════════════════════════════════╣"
        echo "║  tmux sessions:                                              ║"
        while IFS= read -r line; do
            printf "║    %-58s ║\n" "$line"
        done < <(tmux list-sessions 2>/dev/null || echo "  (none)")
        echo "╠══════════════════════════════════════════════════════════════╣"
        echo "║  Claude processes:                                           ║"
        if [ -n "$CLAUDE_DETAIL" ]; then
            while IFS= read -r line; do
                printf "║    %-58s ║\n" "${line:0:58}"
            done <<< "$CLAUDE_DETAIL"
        else
            printf "║    %-58s ║\n" "(none found)"
        fi
        echo "╠══════════════════════════════════════════════════════════════╣"
        if [ ${#ALERTS[@]} -gt 0 ]; then
            echo "║  !! ALERTS !!                                                ║"
            for alert in "${ALERTS[@]}"; do
                printf "║  >> %-57s ║\n" "${alert:0:57}"
            done
        else
            printf "║  %-60s ║\n" "Status    : ALL CLEAR - no thresholds exceeded"
        fi
        echo "╚══════════════════════════════════════════════════════════════╝"
        echo ""
    fi
fi

# ── Logging (always) ────────────────────────────────────────────────────────
mkdir -p "$(dirname "$LOG_FILE")"
echo "[$TS] cpu=${CPU_PCT}% ram=${RAM_PCT}%(${RAM_USED}/${RAM_TOTAL}MB) disk=${DISK_PCT}% claude=${CLAUDE_COUNT} node=${NODE_COUNT} python=${PYTHON_COUNT} tmux=${TMUX_COUNT} load=${LOAD_AVG} alerts=${#ALERTS[@]}" >> "$LOG_FILE"

# ── Telegram alert ──────────────────────────────────────────────────────────
if [ "$ALERT_TRIGGERED" = true ] && [ -x "$TG_SEND" ]; then
    ALERT_MSG="VPS ALERT — $(date '+%H:%M %Z')"
    for a in "${ALERTS[@]}"; do
        ALERT_MSG="$ALERT_MSG
• $a"
    done
    ALERT_MSG="$ALERT_MSG

Full state:
CPU: ${CPU_PCT}% | RAM: ${RAM_PCT}% | Disk: ${DISK_PCT}%
Claude procs: $CLAUDE_COUNT | tmux: $TMUX_COUNT | load: $LOAD_AVG"
    "$TG_SEND" "CTO: $ALERT_MSG" 2>/dev/null || true
fi

# Exit code: 0 = healthy, 1 = alerts triggered
[ "$ALERT_TRIGGERED" = false ] && exit 0 || exit 1
