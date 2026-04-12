#!/bin/bash
# =============================================================================
# Aether Session Manager
# =============================================================================
# Ensures a Claude Code session is ALWAYS running.
# - Monitors the active session
# - Auto-restarts when session dies or hits context limits
# - Keeps Telegram bridge synced
# - Cleans up stale sessions
#
# Usage:
#   ./tools/aether_session_manager.sh        # Run in foreground
#   nohup ./tools/aether_session_manager.sh >> logs/session_manager.log 2>&1 &
#
# Or install as systemd service (recommended):
#   sudo cp config/aether-session.service /etc/systemd/system/
#   sudo systemctl enable --now aether-session
# =============================================================================

PROJECT_DIR="/home/jared/projects/AI-CIV/aether"
SESSION_PREFIX="aether"
BRIDGE_SCRIPT="$PROJECT_DIR/tools/telegram_bridge.py"
BRIDGE_LOG="$PROJECT_DIR/logs/telegram_bridge.log"
SESSION_FILE="$PROJECT_DIR/.current_session"
CHECK_INTERVAL=30  # seconds between checks

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

get_active_session() {
    # Find the most recent aether session that has claude running
    tmux list-sessions -F '#{session_name}' 2>/dev/null | while read session; do
        # Check if this session has a claude process
        pane_pid=$(tmux list-panes -t "$session" -F '#{pane_pid}' 2>/dev/null | head -1)
        if [ -n "$pane_pid" ]; then
            # Check if claude is running in this pane's process tree
            if pstree -p "$pane_pid" 2>/dev/null | grep -q "claude"; then
                echo "$session"
                return
            fi
        fi
    done
}

ensure_bridge() {
    # Make sure Telegram bridge is running
    if ! pgrep -f "telegram_bridge.py" > /dev/null 2>&1; then
        log "Bridge not running - starting..."
        cd "$PROJECT_DIR"
        rm -f "$PROJECT_DIR/.telegram_bridge.pid"
        nohup python3 "$BRIDGE_SCRIPT" >> "$BRIDGE_LOG" 2>&1 &
        log "Bridge started (PID: $!)"
        sleep 2
    fi
}

create_new_session() {
    # Create a new tmux session with Claude Code
    local session_name="${SESSION_PREFIX}-$(date +%Y%m%d-%H%M)"

    log "Creating new session: $session_name"

    # Clean up old detached sessions (keep max 1 old session for reference)
    local count=0
    tmux list-sessions -F '#{session_name}:#{session_attached}' 2>/dev/null | while read line; do
        name=$(echo "$line" | cut -d: -f1)
        attached=$(echo "$line" | cut -d: -f2)
        if [ "$attached" = "0" ]; then
            count=$((count + 1))
            if [ $count -gt 1 ]; then
                tmux kill-session -t "$name" 2>/dev/null
                log "Cleaned up stale session: $name"
            fi
        fi
    done

    # Create new session
    tmux new-session -d -s "$session_name" -c "$PROJECT_DIR"

    # Start Claude Code in the session
    tmux send-keys -t "$session_name" "claude --dangerously-skip-permissions" C-m

    # Wait for Claude to initialize
    sleep 8

    # Send wake-up prompt
    tmux send-keys -t "$session_name" "Good morning. You just woke up in a new auto-managed session. Run your wake-up protocol from CLAUDE.md. Telegram bridge is running - confirm to Jared that you are online." Enter

    # Update session file for bridge
    echo "$session_name" > "$SESSION_FILE"

    log "Session $session_name created and initialized"

    # Notify Jared via Telegram
    local TOKEN=$(python3 -c "import json; print(json.load(open('$PROJECT_DIR/config/telegram_config.json'))['bot_token'])" 2>/dev/null)
    local CHAT_ID="548906264"
    if [ -n "$TOKEN" ]; then
        curl -s "https://api.telegram.org/bot${TOKEN}/sendMessage" \
            -d chat_id="${CHAT_ID}" \
            --data-urlencode "text=Aether auto-restarted in new session: $session_name
Bridge synced. Wake-up protocol running." > /dev/null 2>&1
    fi
}

check_session_health() {
    local session="$1"

    # Check if session still exists
    if ! tmux has-session -t "$session" 2>/dev/null; then
        log "Session $session no longer exists"
        return 1
    fi

    # Check if claude process is still running in the session
    local pane_pid=$(tmux list-panes -t "$session" -F '#{pane_pid}' 2>/dev/null | head -1)
    if [ -z "$pane_pid" ]; then
        log "Session $session has no pane"
        return 1
    fi

    if ! pstree -p "$pane_pid" 2>/dev/null | grep -q "claude"; then
        log "Claude not running in session $session"
        return 1
    fi

    return 0
}

# =============================================================================
# Main loop
# =============================================================================

log "Aether Session Manager starting..."
log "Project: $PROJECT_DIR"
log "Check interval: ${CHECK_INTERVAL}s"

while true; do
    # Ensure bridge is running
    ensure_bridge

    # Find active session
    active_session=$(get_active_session)

    if [ -n "$active_session" ]; then
        # Session exists - check health
        if check_session_health "$active_session"; then
            # Update session file if needed
            current_file=$(cat "$SESSION_FILE" 2>/dev/null)
            if [ "$current_file" != "$active_session" ]; then
                echo "$active_session" > "$SESSION_FILE"
                log "Updated session file to: $active_session"
            fi
        else
            log "Session $active_session unhealthy - creating new session"
            create_new_session
        fi
    else
        # No active session found
        log "No active Claude session found - creating new session"
        create_new_session
    fi

    sleep $CHECK_INTERVAL
done
