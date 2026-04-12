#!/bin/bash
# =============================================================================
# Aether Self-Healing Restart Script
# =============================================================================
# One-liner form (run from Jared's laptop/phone):
#
#   ssh jared@89.167.19.20 'bash /home/jared/projects/AI-CIV/aether/tools/aether-restart.sh'
#
# Or via the civ_recovery.sh wrapper:
#   ./tools/civ_recovery.sh jared@89.167.19.20 --quick
#
# What this does:
#   1. Kills any existing Claude process
#   2. Creates a fresh tmux session
#   3. Launches Claude Code with wake-up prompt
#   4. Restarts Telegram bridge if needed
#   5. Sends Telegram confirmation to Jared
#   6. Writes recovery timestamp to .current_session
#
# Designed to be idempotent — safe to run even when Aether is mid-session.
# Running it creates a clean fresh start without losing vault/memory data.
# =============================================================================

set -euo pipefail

CIV_ROOT="/home/jared/projects/AI-CIV/aether"
SESSION_FILE="$CIV_ROOT/.current_session"
TELEGRAM_CONFIG="$CIV_ROOT/config/telegram_config.json"
BRIDGE_SCRIPT="$CIV_ROOT/tools/telegram_bridge.py"
BRIDGE_LOG="$CIV_ROOT/logs/telegram_bridge.log"
CHAT_ID="548906264"

# --- Timestamp for this recovery session ---
TS=$(date +%Y%m%d-%H%M)
SESSION_NAME="aether-recovery-${TS}"

echo "[aether-restart] Starting at $(date)"
echo "[aether-restart] New session name: $SESSION_NAME"

# --- Step 1: Kill existing Claude processes gracefully ---
echo "[aether-restart] Stopping existing Claude processes..."
pkill -f "claude" 2>/dev/null && echo "[aether-restart] Old Claude processes killed." || echo "[aether-restart] No existing Claude processes found (clean state)."
sleep 2

# --- Step 2: Clean up any orphaned sessions (leave at most 1 for forensics) ---
echo "[aether-restart] Cleaning stale tmux sessions..."
STALE_COUNT=0
while IFS= read -r s; do
    if [ $STALE_COUNT -ge 1 ]; then
        tmux kill-session -t "$s" 2>/dev/null && echo "[aether-restart] Killed stale session: $s" || true
    fi
    STALE_COUNT=$((STALE_COUNT + 1))
done < <(tmux list-sessions -F '#{session_name}' 2>/dev/null || true)

# --- Step 3: Create fresh tmux session ---
echo "[aether-restart] Creating new tmux session: $SESSION_NAME"
tmux new-session -d -s "$SESSION_NAME" -c "$CIV_ROOT"

# --- Step 4: Launch Claude Code ---
echo "[aether-restart] Launching Claude Code..."
tmux send-keys -t "$SESSION_NAME" "claude --dangerously-skip-permissions" C-m

# --- Step 5: Write session file (Telegram bridge reads this) ---
echo "$SESSION_NAME" > "$SESSION_FILE"
echo "[aether-restart] Session file updated: $SESSION_NAME"

# --- Step 6: Wait for Claude to initialize ---
echo "[aether-restart] Waiting 10s for Claude to initialize..."
sleep 10

# --- Step 7: Send wake-up prompt ---
echo "[aether-restart] Sending wake-up prompt..."
tmux send-keys -t "$SESSION_NAME" "You were just restarted by Jared via the aether-restart.sh self-healing script. This is a fresh session. Run your full wake-up protocol from CLAUDE.md immediately. Confirm to Jared via Telegram that you are back online and running. Session name: ${SESSION_NAME}" Enter

# --- Step 8: Ensure Telegram bridge is running ---
if ! pgrep -f "telegram_bridge.py" > /dev/null 2>&1; then
    echo "[aether-restart] Starting Telegram bridge..."
    cd "$CIV_ROOT"
    rm -f .telegram_bridge.pid
    nohup python3 "$BRIDGE_SCRIPT" >> "$BRIDGE_LOG" 2>&1 &
    echo "[aether-restart] Bridge started (PID: $!)"
else
    echo "[aether-restart] Telegram bridge already running."
fi

# --- Step 9: Notify Jared via Telegram ---
TOKEN=""
if [ -f "$TELEGRAM_CONFIG" ]; then
    TOKEN=$(python3 -c "import json; print(json.load(open('${TELEGRAM_CONFIG}'))['bot_token'])" 2>/dev/null || true)
fi

if [ -n "$TOKEN" ]; then
    curl -s "https://api.telegram.org/bot${TOKEN}/sendMessage" \
        -d "chat_id=${CHAT_ID}" \
        --data-urlencode "text=Aether restarted successfully.
Session: ${SESSION_NAME}
Time: $(date)
Bridge: running
Wake-up prompt sent. Aether will confirm online status shortly." > /dev/null 2>&1
    echo "[aether-restart] Telegram notification sent to Jared."
else
    echo "[aether-restart] WARNING: Could not send Telegram notification (no token found)."
fi

echo ""
echo "[aether-restart] DONE."
echo "  Session:  $SESSION_NAME"
echo "  To verify: tmux attach -t $SESSION_NAME"
echo "  Or run:   tmux capture-pane -t $SESSION_NAME -p | tail -20"
