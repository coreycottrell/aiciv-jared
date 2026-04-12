#!/bin/bash
# Log Server Watchdog — pings verify-payment endpoint every 5 min
# If it fails 2x in a row, restarts aether-logserver service
# Also monitors agentmail_monitor.py and pushes ALARM to portal on failures

ENDPOINT="https://localhost:8443/api/spots-status"
LOG="/home/jared/projects/AI-CIV/aether/logs/logserver-watchdog.log"
FAIL_FILE="/tmp/logserver-watchdog-fails"

# Portal notification helper
PORTAL_TOKEN=$(cat /home/jared/purebrain_portal/.portal-token 2>/dev/null)
push_alarm() {
    local msg="$1"
    if [ -n "$PORTAL_TOKEN" ]; then
        curl -s -X POST "http://localhost:8097/api/chat" \
            -H "Authorization: Bearer $PORTAL_TOKEN" \
            -H "Content-Type: application/json" \
            -d "{\"message\": \"$msg\", \"role\": \"system\"}" 2>/dev/null
    fi
}

# ===== CHECK 1: Log Server Health =====
RESPONSE=$(curl -sk --max-time 10 "$ENDPOINT" 2>&1)
HTTP_CODE=$(curl -sk --max-time 10 -o /dev/null -w "%{http_code}" "$ENDPOINT" 2>/dev/null)

if [ "$HTTP_CODE" = "200" ]; then
    # Healthy — reset fail counter
    echo 0 > "$FAIL_FILE"
else
    # Failed — increment counter
    FAILS=$(cat "$FAIL_FILE" 2>/dev/null || echo 0)
    FAILS=$((FAILS + 1))
    echo "$FAILS" > "$FAIL_FILE"
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) WARN: Log server health check failed ($HTTP_CODE), fail count: $FAILS" >> "$LOG"

    if [ "$FAILS" -ge 2 ]; then
        echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) ACTION: Restarting aether-logserver (2+ consecutive failures)" >> "$LOG"
        sudo systemctl restart aether-logserver
        sleep 5
        # Verify restart worked
        NEW_CODE=$(curl -sk --max-time 10 -o /dev/null -w "%{http_code}" "$ENDPOINT" 2>/dev/null)
        if [ "$NEW_CODE" = "200" ]; then
            echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) RECOVERED: Log server restarted successfully" >> "$LOG"
            echo 0 > "$FAIL_FILE"
            push_alarm "🚨 ALARM: Log server was down and has been restarted. Pipeline may have missed payments during downtime. Please verify."
        else
            echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) CRITICAL: Log server restart failed! Manual intervention needed" >> "$LOG"
            push_alarm "🚨 ALARM: Log server restart FAILED. Manual intervention needed. Payment pipeline may be down."
        fi
    fi
fi

# ===== CHECK 2: AgentMail Monitor =====
if ! pgrep -f "agentmail_monitor.py" > /dev/null; then
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) ALARM: AgentMail monitor NOT running!" >> "$LOG"
    # Restart it
    nohup python3 tools/agentmail_monitor.py >> logs/agentmail_monitor.log 2>&1 &
    sleep 2
    # Verify it came back
    if pgrep -f "agentmail_monitor.py" > /dev/null; then
        echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) RECOVERED: AgentMail monitor restarted" >> "$LOG"
        push_alarm "🚨 ALARM: AgentMail monitor was dead — restarted. Magic links may have been missed. Checking now."
    else
        echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) CRITICAL: AgentMail monitor restart failed!" >> "$LOG"
        push_alarm "🚨 ALARM: AgentMail monitor restart FAILED. Magic links are NOT being processed. Manual intervention needed."
    fi
fi
