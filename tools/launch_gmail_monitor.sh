#!/bin/bash
# Launch Gmail Monitor as background daemon
#
# Usage:
#   ./tools/launch_gmail_monitor.sh         # Start daemon
#   ./tools/launch_gmail_monitor.sh stop    # Stop daemon
#   ./tools/launch_gmail_monitor.sh status  # Check status
#   ./tools/launch_gmail_monitor.sh check   # One-time check

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
PID_FILE="/tmp/aether_gmail_monitor.pid"
LOG_FILE="$PROJECT_ROOT/logs/gmail_monitor.log"

cd "$PROJECT_ROOT"

case "$1" in
    stop)
        if [ -f "$PID_FILE" ]; then
            PID=$(cat "$PID_FILE")
            if kill -0 "$PID" 2>/dev/null; then
                echo "Stopping Gmail monitor (PID: $PID)..."
                kill "$PID"
                rm -f "$PID_FILE"
                echo "Stopped."
            else
                echo "Process not running, cleaning up PID file"
                rm -f "$PID_FILE"
            fi
        else
            echo "No PID file found. Gmail monitor may not be running."
        fi
        ;;

    status)
        if [ -f "$PID_FILE" ]; then
            PID=$(cat "$PID_FILE")
            if kill -0 "$PID" 2>/dev/null; then
                echo "Gmail monitor is RUNNING (PID: $PID)"
                echo "Log file: $LOG_FILE"
                echo ""
                echo "Recent logs:"
                tail -10 "$LOG_FILE"
            else
                echo "Gmail monitor is NOT running (stale PID file)"
                rm -f "$PID_FILE"
            fi
        else
            echo "Gmail monitor is NOT running"
        fi
        ;;

    check)
        echo "Running one-time email check..."
        python3 "$SCRIPT_DIR/gmail_monitor.py" check
        ;;

    stats)
        python3 "$SCRIPT_DIR/gmail_monitor.py" stats
        ;;

    *)
        # Start daemon
        if [ -f "$PID_FILE" ]; then
            PID=$(cat "$PID_FILE")
            if kill -0 "$PID" 2>/dev/null; then
                echo "Gmail monitor already running (PID: $PID)"
                exit 0
            fi
            rm -f "$PID_FILE"
        fi

        echo "Starting Gmail monitor daemon..."
        nohup python3 "$SCRIPT_DIR/gmail_monitor.py" daemon --interval 5 >> "$LOG_FILE" 2>&1 &
        echo $! > "$PID_FILE"
        echo "Started with PID: $(cat $PID_FILE)"
        echo "Log file: $LOG_FILE"
        ;;
esac
