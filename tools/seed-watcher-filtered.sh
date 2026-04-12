#!/bin/bash
# Seed Watcher v2 — FILTERED notifications
# Only notifies Jared for:
#   1. Payment completion (PayPal verified) on pay-test-2 or pay-test-sandbox-2
#   2. Post-payment chatbox flow COMPLETION (conversation_complete event)
#   3. AI awakening + form completion on purebrain.ai (capabilities_revealed on main site)
#
# Does NOT notify for: conversation_start, message_exchange, or every chatbox message

TOKEN=$(python3 -c "import json; print(json.load(open('/home/jared/projects/AI-CIV/aether/config/telegram_config.json'))['bot_token'])")
CHAT_ID="548906264"

send_tg() {
    curl -s "https://api.telegram.org/bot${TOKEN}/sendMessage" \
        -d chat_id="$CHAT_ID" \
        --data-urlencode "text=$1" > /dev/null 2>&1
}

echo "Seed watcher v2 (filtered) started at $(date -u)"

# Watch conversation log — ONLY conversation_complete and capabilities_revealed on main site
tail -f -n 0 /home/jared/projects/AI-CIV/aether/logs/purebrain_web_conversations.jsonl 2>/dev/null | while read line; do
    # Parse event type
    event=$(echo "$line" | python3 -c "import sys,json; d=json.loads(sys.stdin.read()); print(d.get('metadata',{}).get('event_type',''))" 2>/dev/null)

    # FILTER: Only notify for conversation_complete or capabilities_revealed
    if [ "$event" = "conversation_complete" ] || [ "$event" = "capabilities_revealed" ]; then
        ts=$(echo "$line" | python3 -c "import sys,json; d=json.loads(sys.stdin.read()); print(d.get('server_timestamp','?'))" 2>/dev/null)
        msgs=$(echo "$line" | python3 -c "import sys,json; d=json.loads(sys.stdin.read()); print(len(d.get('messages',[])))" 2>/dev/null)
        url=$(echo "$line" | python3 -c "import sys,json; d=json.loads(sys.stdin.read()); print(d.get('metadata',{}).get('page_url','?'))" 2>/dev/null)
        ai=$(echo "$line" | python3 -c "import sys,json; d=json.loads(sys.stdin.read()); print(d.get('metadata',{}).get('ai_name','none'))" 2>/dev/null)

        if [ "$event" = "conversation_complete" ]; then
            send_tg "✅ CHATBOX FLOW COMPLETE
time: $ts
ai_name: $ai
messages: $msgs
page: $url"
        elif [ "$event" = "capabilities_revealed" ]; then
            send_tg "🧠 AI AWAKENED
time: $ts
ai_name: $ai
messages: $msgs
page: $url"
        fi
    fi
    # All other events (conversation_start, message_exchange, etc.) = silently ignored
done &

# Watch pay-test log — ONLY entries with a real orderId (actual payment)
tail -f -n 0 /home/jared/projects/AI-CIV/aether/logs/purebrain_pay_test.jsonl 2>/dev/null | while read line; do
    # Check if orderId exists and is not null/None/empty
    has_order=$(echo "$line" | python3 -c "
import sys,json
d=json.loads(sys.stdin.read())
oid = d.get('orderId','')
print('yes' if oid and oid != 'null' and oid != 'None' else 'no')
" 2>/dev/null)

    if [ "$has_order" = "yes" ]; then
        event=$(echo "$line" | python3 -c "import sys,json; d=json.loads(sys.stdin.read()); print(d.get('event','payment'))" 2>/dev/null)
        tier=$(echo "$line" | python3 -c "import sys,json; d=json.loads(sys.stdin.read()); print(d.get('tier','?'))" 2>/dev/null)
        name=$(echo "$line" | python3 -c "import sys,json; d=json.loads(sys.stdin.read()); print(d.get('name','?'))" 2>/dev/null)
        email=$(echo "$line" | python3 -c "import sys,json; d=json.loads(sys.stdin.read()); print(d.get('email','?'))" 2>/dev/null)
        order=$(echo "$line" | python3 -c "import sys,json; d=json.loads(sys.stdin.read()); print(d.get('orderId','?'))" 2>/dev/null)
        send_tg "💰 PAYMENT RECEIVED
tier: $tier
name: $name
email: $email
orderId: $order"
    fi
    # Entries without orderId (form submissions, chatbox data) = silently ignored
done &

# Watch payment verification log — ALWAYS notify (these are verified payments)
tail -f -n 0 /home/jared/projects/AI-CIV/aether/logs/purebrain_payments.jsonl 2>/dev/null | while read line; do
    order=$(echo "$line" | python3 -c "import sys,json; d=json.loads(sys.stdin.read()); print(d.get('orderId','?'))" 2>/dev/null)
    tier=$(echo "$line" | python3 -c "import sys,json; d=json.loads(sys.stdin.read()); print(d.get('tier','?'))" 2>/dev/null)
    status=$(echo "$line" | python3 -c "import sys,json; d=json.loads(sys.stdin.read()); print(d.get('status', d.get('event','verified')))" 2>/dev/null)
    send_tg "🔥 PAYMENT VERIFIED
orderId: $order
tier: $tier
status: $status"
done &

wait
