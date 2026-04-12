#!/bin/bash
#
# Launch PureBrain AI Bot
#
# Pure Technology's marketing team Telegram bot.
# Runs separately from the main Aether bridge.
#
# Usage:
#   ./tools/launch_purebrain_bot.sh         # Start the bot
#   ./tools/launch_purebrain_bot.sh stop    # Stop the bot
#   ./tools/launch_purebrain_bot.sh status  # Check status
#   ./tools/launch_purebrain_bot.sh restart # Restart the bot

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
LOG_FILE="$PROJECT_ROOT/logs/purebrain_bridge.log"
PID_FILE="$PROJECT_ROOT/.purebrain_bot.pid"

# Ensure logs directory exists
mkdir -p "$PROJECT_ROOT/logs"

get_pid() {
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            echo "$pid"
            return 0
        fi
    fi
    # Try to find by process name
    local pid=$(pgrep -f "python3.*purebrain_bridge.py" 2>/dev/null | head -1)
    if [ -n "$pid" ]; then
        echo "$pid"
        return 0
    fi
    return 1
}

start_bot() {
    if pid=$(get_pid); then
        echo "PureBrain bot already running (PID: $pid)"
        return 0
    fi

    echo "Starting PureBrain AI Bot..."

    cd "$PROJECT_ROOT"

    # Activate virtualenv if it exists
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
    fi

    # Start the bot
    nohup python3 tools/purebrain_bridge.py >> "$LOG_FILE" 2>&1 &
    local pid=$!
    echo "$pid" > "$PID_FILE"

    sleep 2

    if ps -p "$pid" > /dev/null 2>&1; then
        echo "PureBrain bot started successfully!"
        echo "  PID: $pid"
        echo "  Log: $LOG_FILE"
        echo ""
        echo "To stop: $0 stop"
        echo "To check status: $0 status"
    else
        echo "ERROR: Bot failed to start. Check logs:"
        tail -20 "$LOG_FILE"
        return 1
    fi
}

stop_bot() {
    if pid=$(get_pid); then
        echo "Stopping PureBrain bot (PID: $pid)..."
        kill "$pid" 2>/dev/null || true
        sleep 1
        if ps -p "$pid" > /dev/null 2>&1; then
            echo "Force killing..."
            kill -9 "$pid" 2>/dev/null || true
        fi
        rm -f "$PID_FILE"
        echo "PureBrain bot stopped."
    else
        echo "PureBrain bot is not running."
    fi
}

status_bot() {
    if pid=$(get_pid); then
        echo "PureBrain bot is RUNNING"
        echo "  PID: $pid"
        echo "  Log: $LOG_FILE"
        echo ""
        echo "Recent log entries:"
        tail -10 "$LOG_FILE" 2>/dev/null || echo "  (no logs yet)"
    else
        echo "PureBrain bot is NOT RUNNING"
        echo ""
        echo "To start: $0"
    fi
}

case "${1:-start}" in
    start)
        start_bot
        ;;
    stop)
        stop_bot
        ;;
    restart)
        stop_bot
        sleep 1
        start_bot
        ;;
    status)
        status_bot
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status}"
        exit 1
        ;;
esac
