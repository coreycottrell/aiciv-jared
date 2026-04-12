#!/usr/bin/env bash
#
# Aether BOOP System - Background Orchestrated Operations Pulse
# Keeps Aether alive and productive when humans are away
# Based on A-C-Gee's battle-tested BOOP system
#
# Created: 2026-02-09
# Origin: Adapted from A-C-Gee's aiciv-boop-system-SKILL.md
#
# Usage:
#   ./autonomy_nudge.sh           # Normal BOOP (cron target)
#   ./autonomy_nudge.sh --status  # Check counters and state
#   ./autonomy_nudge.sh --reset   # Reset all counters
#   ./autonomy_nudge.sh --force   # Force send BOOP now
#   ./autonomy_nudge.sh --force-type ceremony  # Force specific tier
#   ./autonomy_nudge.sh --check-only  # Dry run

set -e

# ============================================
# CONFIGURATION - Customize for your CIV
# ============================================

PROJECT_DIR="/home/jared/projects/AI-CIV/aether"
SESSION_MARKER="$PROJECT_DIR/.current_session"
LAUNCH_SCRIPT="$PROJECT_DIR/tools/launch_primary_visible.sh"
CLAUDE_LOG_ROOT="$HOME/.claude/projects"

# Telegram notification (optional)
TG_BOT_TOKEN="8559081952:AAHcLiEcC3GtQCAHRu5yc86BByiiLDqyjz0"
TG_CHAT_ID="548906264"

# Counter files
BOOP_COUNT_FILE="/tmp/aether_boop_count"
CONSOLIDATION_COUNT_FILE="/tmp/aether_consolidation_count"
FAILED_BOOP_FILE="/tmp/aether_failed_boops"

# Thresholds
SIMPLE_THRESHOLD=10        # Simple BOOPs before consolidation
CONSOLIDATION_THRESHOLD=10 # Consolidations before ceremony
FAILED_BOOP_THRESHOLD=5    # Failures before restart

# ============================================
# FUNCTIONS
# ============================================

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

send_telegram() {
    local message="$1"
    if [ -n "$TG_BOT_TOKEN" ] && [ -n "$TG_CHAT_ID" ]; then
        curl -s -X POST "https://api.telegram.org/bot$TG_BOT_TOKEN/sendMessage" \
            -H "Content-Type: application/json" \
            -d "{\"chat_id\": \"$TG_CHAT_ID\", \"text\": \"$message\"}" > /dev/null 2>&1 || true
    fi
}

get_session() {
    if [ -f "$SESSION_MARKER" ]; then
        cat "$SESSION_MARKER"
    else
        # Try to find an aether session
        tmux list-sessions -F "#{session_name}" 2>/dev/null | grep -i "aether" | head -1
    fi
}

is_session_active() {
    local session="$1"
    tmux has-session -t "$session" 2>/dev/null
}

inject_message() {
    local session="$1"
    local message="$2"

    # Send the message with -l flag (literal)
    tmux send-keys -t "$session" -l "$message"

    # 5x Enter pattern for reliability
    for i in {1..5}; do
        sleep 0.3
        tmux send-keys -t "$session" "Enter"
    done
}

get_counter() {
    local file="$1"
    if [ -f "$file" ]; then
        cat "$file"
    else
        echo "0"
    fi
}

set_counter() {
    local file="$1"
    local value="$2"
    echo "$value" > "$file"
}

increment_counter() {
    local file="$1"
    local current=$(get_counter "$file")
    set_counter "$file" $((current + 1))
    echo $((current + 1))
}

determine_boop_type() {
    local boop_count=$(get_counter "$BOOP_COUNT_FILE")
    local consolidation_count=$(get_counter "$CONSOLIDATION_COUNT_FILE")

    # Check if it's time for ceremony
    if [ "$consolidation_count" -ge "$CONSOLIDATION_THRESHOLD" ]; then
        echo "ceremony"
        return
    fi

    # Check if it's time for consolidation
    if [ "$boop_count" -ge "$SIMPLE_THRESHOLD" ]; then
        echo "consolidation"
        return
    fi

    echo "simple"
}

get_boop_message() {
    local boop_type="$1"

    case "$boop_type" in
        "simple")
            echo "BOOP - Productivity check. What's your current priority? Execute one meaningful task, update scratchpad, then report. Keep moving."
            ;;
        "consolidation")
            echo "BOOP CONSOLIDATION - Pause and reflect. Review the last 2 hours of work. Write any learnings worth keeping to memory. Check context usage. If >80%, create handoff. Then continue with top priority."
            ;;
        "ceremony")
            echo "BOOP CEREMONY - Deep reflection time. Who are we becoming? Review recent decisions and patterns. Write identity-relevant insights. Check on sister collectives. Then return to work refreshed."
            ;;
        *)
            echo "BOOP - Keep working on current priorities."
            ;;
    esac
}

update_counters_after_boop() {
    local boop_type="$1"

    case "$boop_type" in
        "simple")
            increment_counter "$BOOP_COUNT_FILE"
            ;;
        "consolidation")
            set_counter "$BOOP_COUNT_FILE" 0
            increment_counter "$CONSOLIDATION_COUNT_FILE"
            ;;
        "ceremony")
            set_counter "$BOOP_COUNT_FILE" 0
            set_counter "$CONSOLIDATION_COUNT_FILE" 0
            ;;
    esac
}

check_response() {
    # Check if Claude responded by monitoring log growth
    # For now, just reset failure counter on successful send
    # More sophisticated: check log file size growth over 60s window
    set_counter "$FAILED_BOOP_FILE" 0
}

handle_failure() {
    local failed_count=$(increment_counter "$FAILED_BOOP_FILE")
    log "BOOP failed, count: $failed_count/$FAILED_BOOP_THRESHOLD"

    if [ "$failed_count" -ge "$FAILED_BOOP_THRESHOLD" ]; then
        log "FAILURE THRESHOLD REACHED - Initiating restart"
        send_telegram "⚠️ AETHER BOOP: $failed_count consecutive failures. Restarting session..."

        # Kill the old session
        local session=$(get_session)
        if [ -n "$session" ]; then
            tmux kill-session -t "$session" 2>/dev/null || true
        fi

        # Reset counters
        set_counter "$FAILED_BOOP_FILE" 0

        # Relaunch
        if [ -x "$LAUNCH_SCRIPT" ]; then
            log "Relaunching via $LAUNCH_SCRIPT"
            nohup "$LAUNCH_SCRIPT" > /tmp/aether_relaunch.log 2>&1 &
            sleep 5
            send_telegram "✅ AETHER BOOP: Session relaunched. Resuming autonomy."
        else
            log "ERROR: Launch script not found or not executable: $LAUNCH_SCRIPT"
            send_telegram "❌ AETHER BOOP: Restart failed - launch script not found. Human intervention needed."
        fi
    fi
}

show_status() {
    echo "=== Aether BOOP Status ==="
    echo "Simple BOOP count: $(get_counter $BOOP_COUNT_FILE)/$SIMPLE_THRESHOLD"
    echo "Consolidation count: $(get_counter $CONSOLIDATION_COUNT_FILE)/$CONSOLIDATION_THRESHOLD"
    echo "Failed BOOP count: $(get_counter $FAILED_BOOP_FILE)/$FAILED_BOOP_THRESHOLD"
    echo "Next BOOP type: $(determine_boop_type)"
    echo ""
    echo "Session file: $SESSION_MARKER"
    if [ -f "$SESSION_MARKER" ]; then
        echo "Current session: $(cat $SESSION_MARKER)"
    else
        echo "Current session: (not set)"
    fi
    echo ""
    local session=$(get_session)
    if [ -n "$session" ] && is_session_active "$session"; then
        echo "Session status: ACTIVE"
    else
        echo "Session status: INACTIVE"
    fi
}

reset_counters() {
    log "Resetting all counters"
    set_counter "$BOOP_COUNT_FILE" 0
    set_counter "$CONSOLIDATION_COUNT_FILE" 0
    set_counter "$FAILED_BOOP_FILE" 0
    echo "All counters reset to 0"
}

do_boop() {
    local force_type="$1"

    # Get session
    local session=$(get_session)
    if [ -z "$session" ]; then
        log "No session found"
        handle_failure
        return 1
    fi

    # Check if session is active
    if ! is_session_active "$session"; then
        log "Session '$session' is not active"
        handle_failure
        return 1
    fi

    # Determine BOOP type
    local boop_type
    if [ -n "$force_type" ]; then
        boop_type="$force_type"
    else
        boop_type=$(determine_boop_type)
    fi

    log "Executing $boop_type BOOP on session: $session"

    # Step 1: Inject spine grounding (identity refresh)
    log "Injecting spine grounding"
    inject_message "$session" "/weaver-spine"
    sleep 3

    # Step 2: Inject BOOP message
    local message=$(get_boop_message "$boop_type")
    log "Injecting BOOP message"
    inject_message "$session" "$message"

    # Update counters
    update_counters_after_boop "$boop_type"

    # Mark success (simplified - just reset failure counter)
    check_response

    log "BOOP complete: $boop_type"
    return 0
}

# ============================================
# MAIN
# ============================================

cd "$PROJECT_DIR"

case "${1:-}" in
    "--status")
        show_status
        ;;
    "--reset")
        reset_counters
        ;;
    "--force")
        log "Force BOOP requested"
        do_boop
        ;;
    "--force-type")
        if [ -z "${2:-}" ]; then
            echo "Usage: $0 --force-type [simple|consolidation|ceremony]"
            exit 1
        fi
        log "Force BOOP type: $2"
        do_boop "$2"
        ;;
    "--check-only")
        echo "Would execute: $(determine_boop_type) BOOP"
        show_status
        ;;
    "--json")
        echo "{\"boop_count\": $(get_counter $BOOP_COUNT_FILE), \"consolidation_count\": $(get_counter $CONSOLIDATION_COUNT_FILE), \"failed_count\": $(get_counter $FAILED_BOOP_FILE), \"next_type\": \"$(determine_boop_type)\"}"
        ;;
    "")
        # Normal cron invocation
        log "=== BOOP Cycle Start ==="
        do_boop
        log "=== BOOP Cycle End ==="
        ;;
    *)
        echo "Usage: $0 [--status|--reset|--force|--force-type TYPE|--check-only|--json]"
        exit 1
        ;;
esac
