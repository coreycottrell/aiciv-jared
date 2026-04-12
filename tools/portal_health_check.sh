#!/bin/bash
# Portal Health Check — auto-restarts cloudflared + portal if down
# Runs via cron every 2 minutes

LOG="/home/jared/projects/AI-CIV/aether/logs/portal_health.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# Check portal via nginx (local, avoids Cloudflare caching)
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -H "Host: portal.purebrain.ai" --max-time 5 http://localhost:8099/ 2>/dev/null)

if [ "$HTTP_CODE" = "200" ]; then
    # Also check cloudflared is actually passing traffic
    EXT_CODE=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 https://portal.purebrain.ai/health 2>/dev/null)
    if [ "$EXT_CODE" = "200" ] || [ "$EXT_CODE" = "000" ]; then
        # 000 = can't reach from here (normal if no external route), trust local check
        exit 0
    fi
fi

echo "[$TIMESTAMP] Portal unhealthy (local=$HTTP_CODE). Restarting..." >> "$LOG"

# Check if portal_server.py is running
if ! pgrep -f portal_server.py > /dev/null; then
    echo "[$TIMESTAMP] portal_server.py not running — starting" >> "$LOG"
    cd /home/jared/projects/AI-CIV/aether
    nohup python3 aiciv-comms-hub-bootstrap/_comms_hub/packages/purebrain-portal/portal-server/portal_server.py >> logs/portal_server.log 2>&1 &
    sleep 3
fi

# Check nginx
if ! pgrep nginx > /dev/null; then
    echo "[$TIMESTAMP] nginx not running — starting" >> "$LOG"
    sudo systemctl start nginx
    sleep 2
fi

# Restart cloudflared (most common failure)
echo "[$TIMESTAMP] Restarting cloudflared" >> "$LOG"
sudo systemctl restart cloudflared
sleep 5

# Verify
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -H "Host: portal.purebrain.ai" --max-time 5 http://localhost:8099/ 2>/dev/null)
echo "[$TIMESTAMP] Post-restart check: $HTTP_CODE" >> "$LOG"

if [ "$HTTP_CODE" != "200" ]; then
    # Send alert to Telegram
    TOKEN=$(python3 -c "import json; print(json.load(open('/home/jared/projects/AI-CIV/aether/config/telegram_config.json'))['bot_token'])")
    curl -s "https://api.telegram.org/bot${TOKEN}/sendMessage" -d chat_id="548906264" --data-urlencode "text=⚠️ Portal health check FAILED after restart. Local status: $HTTP_CODE. Needs manual investigation." > /dev/null
    echo "[$TIMESTAMP] ALERT SENT — still unhealthy after restart" >> "$LOG"
else
    echo "[$TIMESTAMP] Recovery successful" >> "$LOG"
fi
