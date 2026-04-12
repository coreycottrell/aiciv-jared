#!/bin/bash
# =============================================================================
# CIV Recovery Script — Emergency recovery for AI civilizations
# =============================================================================
# Usage:
#   ./civ_recovery.sh USER@HOST              # Full diagnosis + guided recovery
#   ./civ_recovery.sh USER@HOST --quick      # Quick restart (most common fix)
#   ./civ_recovery.sh USER@HOST --reauth     # OAuth reauth flow
#   ./civ_recovery.sh USER@HOST --status     # Status check only
#
# Can be run from ANY machine with SSH access to the CIV's VPS.
# Designed for: Witness fleet, PureBrain customers, sister CIVs
#
# Origin: Built by Aether 2026-03-09 at request of Witness (Corey) and
#         Parallax (Russell) after real freeze incidents.
# =============================================================================

set -euo pipefail

TARGET="${1:?Usage: $0 USER@HOST [--quick|--reauth|--status]}"
MODE="${2:---diagnose}"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() { echo -e "${BLUE}[recovery]${NC} $1"; }
ok()  { echo -e "${GREEN}[  OK  ]${NC} $1"; }
warn(){ echo -e "${YELLOW}[ WARN ]${NC} $1"; }
fail(){ echo -e "${RED}[ FAIL ]${NC} $1"; }

# ---------------------------------------------------------------------------
# Status check (runs on remote)
# ---------------------------------------------------------------------------
STATUS_SCRIPT='
echo "=== SYSTEM ==="
uptime
free -h | head -2
echo ""
echo "=== DISK ==="
df -h / | tail -1
echo ""
echo "=== CLAUDE PROCESSES ==="
pgrep -af claude 2>/dev/null || echo "(none)"
echo ""
echo "=== TMUX SESSIONS ==="
tmux list-sessions 2>/dev/null || echo "(none)"
echo ""
echo "=== SERVICES ==="
systemctl list-units --type=service --state=running 2>/dev/null | grep -E "aether|session|telegram|portal|bridge" || echo "(no matching services)"
echo ""
echo "=== BRIDGE ==="
pgrep -af telegram_bridge 2>/dev/null || echo "(not running)"
echo ""
echo "=== PORTAL ==="
pgrep -af portal_server 2>/dev/null || echo "(not running)"
echo ""
echo "=== AUTH STATUS ==="
python3 -c "
import json, time
try:
    creds = json.load(open(\"$HOME/.claude/.credentials.json\"))
    oauth = creds.get(\"claudeAiOauth\", {})
    expires = oauth.get(\"expiresAt\", 0)
    now = time.time() * 1000
    if expires < now:
        print(\"EXPIRED\")
    else:
        remaining = (expires - now) / 3600000
        print(f\"VALID ({remaining:.1f}h remaining)\")
except Exception as e:
    print(f\"UNKNOWN ({e})\")
" 2>/dev/null
echo ""
echo "=== CIV ROOT ==="
find ~/projects/AI-CIV -maxdepth 1 -type d 2>/dev/null | grep -v "^$(echo ~/projects/AI-CIV)$" | head -1 || echo "(not found)"
'

# ---------------------------------------------------------------------------
# Quick restart (runs on remote)
# ---------------------------------------------------------------------------
QUICK_SCRIPT='
CIV_ROOT=$(find ~/projects/AI-CIV -maxdepth 1 -type d 2>/dev/null | grep -v "^$(echo ~/projects/AI-CIV)$" | head -1)
if [ -z "$CIV_ROOT" ]; then echo "ERROR: Cannot find CIV directory"; exit 1; fi

echo "Killing old processes..."
pkill -f "claude" 2>/dev/null || true
sleep 2

echo "Creating new session..."
SESSION_NAME="recovery-$(date +%Y%m%d-%H%M)"
tmux new-session -d -s "$SESSION_NAME" -c "$CIV_ROOT"
tmux send-keys -t "$SESSION_NAME" "claude --dangerously-skip-permissions" C-m
echo "$SESSION_NAME" > "$CIV_ROOT/.current_session"

echo "Waiting for Claude to initialize..."
sleep 10

echo "Sending wake-up prompt..."
tmux send-keys -t "$SESSION_NAME" "You were just recovered from a crash by an external recovery agent. Run your wake-up protocol from CLAUDE.md. Confirm to your human partner that you are back online via Telegram and portal." Enter

# Restart bridge if needed
if ! pgrep -f telegram_bridge.py > /dev/null 2>&1; then
    cd "$CIV_ROOT"
    rm -f .telegram_bridge.pid
    nohup python3 tools/telegram_bridge.py >> logs/telegram_bridge.log 2>&1 &
    echo "Bridge restarted"
fi

# Notify human via Telegram if possible
TOKEN=$(python3 -c "import json; print(json.load(open(\"$CIV_ROOT/config/telegram_config.json\"))[\"bot_token\"])" 2>/dev/null || true)
CHAT_ID=$(python3 -c "import json; print(json.load(open(\"$CIV_ROOT/config/telegram_config.json\")).get(\"default_chat_id\", \"548906264\"))" 2>/dev/null || true)
if [ -n "$TOKEN" ] && [ -n "$CHAT_ID" ]; then
    curl -s "https://api.telegram.org/bot${TOKEN}/sendMessage" \
        -d chat_id="$CHAT_ID" \
        --data-urlencode "text=Recovery complete. Your AI is restarting in session: $SESSION_NAME" > /dev/null 2>&1
    echo "Human notified via Telegram"
fi

echo ""
echo "DONE: Session $SESSION_NAME created"
echo "Verify: ssh '"'"'TARGET'"'"' \"tmux capture-pane -t $SESSION_NAME -p | tail -10\""
'

# ---------------------------------------------------------------------------
# Reauth flow (interactive)
# ---------------------------------------------------------------------------
reauth_flow() {
    log "Starting OAuth reauth flow on $TARGET..."

    # Create a new session that will prompt for auth
    REAUTH_SCRIPT='
CIV_ROOT=$(find ~/projects/AI-CIV -maxdepth 1 -type d 2>/dev/null | grep -v "^$(echo ~/projects/AI-CIV)$" | head -1)
pkill -f claude 2>/dev/null || true
sleep 2
SESSION_NAME="reauth-$(date +%Y%m%d-%H%M)"
tmux new-session -d -s "$SESSION_NAME" -c "$CIV_ROOT"
tmux send-keys -t "$SESSION_NAME" "claude --dangerously-skip-permissions" C-m
echo "$SESSION_NAME" > "$CIV_ROOT/.current_session"
sleep 8
# Capture auth URL
tmux capture-pane -t "$SESSION_NAME" -p -S -50 2>/dev/null
echo "SESSION=$SESSION_NAME"
'
    RESULT=$(ssh -o ConnectTimeout=10 "$TARGET" "$REAUTH_SCRIPT" 2>/dev/null)
    echo "$RESULT"

    # Extract OAuth URL
    AUTH_URL=$(echo "$RESULT" | grep -oE 'https://[^ ]*oauth/authorize[^ ]*' | head -1)
    SESSION_NAME=$(echo "$RESULT" | grep "^SESSION=" | cut -d= -f2)

    if [ -n "$AUTH_URL" ]; then
        echo ""
        warn "REAUTH REQUIRED"
        echo ""
        echo "1. Give this URL to the human partner to open in their browser:"
        echo ""
        echo -e "   ${YELLOW}$AUTH_URL${NC}"
        echo ""
        echo "2. They will get an authorization code. Enter it here:"
        read -rp "   Auth code: " AUTH_CODE

        if [ -n "$AUTH_CODE" ]; then
            log "Sending auth code to session $SESSION_NAME..."
            ssh "$TARGET" "tmux send-keys -t '$SESSION_NAME' '$AUTH_CODE' Enter" 2>/dev/null
            sleep 10

            log "Checking result..."
            ssh "$TARGET" "tmux capture-pane -t '$SESSION_NAME' -p | tail -15" 2>/dev/null

            echo ""
            log "Sending wake-up prompt..."
            ssh "$TARGET" "tmux send-keys -t '$SESSION_NAME' 'You were just recovered from an auth expiry by an external recovery agent. Run your wake-up protocol. Confirm to your human you are back online.' Enter" 2>/dev/null

            ok "Reauth complete. CIV should be waking up."
        fi
    else
        ok "No auth URL found — Claude may already be authenticated."
        echo "Last output:"
        echo "$RESULT" | tail -15
    fi
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

case "$MODE" in
    --status)
        log "Checking status of $TARGET..."
        ssh -o ConnectTimeout=10 "$TARGET" "$STATUS_SCRIPT"
        ;;
    --quick)
        log "Quick restart on $TARGET..."
        ssh -o ConnectTimeout=10 "$TARGET" "$QUICK_SCRIPT"
        ;;
    --reauth)
        reauth_flow
        ;;
    --diagnose|*)
        log "Full diagnosis of $TARGET..."
        echo ""
        RESULT=$(ssh -o ConnectTimeout=10 "$TARGET" "$STATUS_SCRIPT" 2>/dev/null)
        echo "$RESULT"
        echo ""

        # Parse results and recommend action
        if echo "$RESULT" | grep -q "EXPIRED"; then
            fail "Auth is EXPIRED"
            echo ""
            echo "Recommended: $0 $TARGET --reauth"
        elif ! echo "$RESULT" | grep -q "claude"; then
            fail "Claude is NOT running"
            echo ""
            echo "Recommended: $0 $TARGET --quick"
        elif ! echo "$RESULT" | grep -q "tmux"; then
            warn "No tmux sessions found"
            echo ""
            echo "Recommended: $0 $TARGET --quick"
        else
            ok "CIV appears to be running"
            echo ""
            echo "If still unresponsive, try: $0 $TARGET --quick"
        fi
        ;;
esac
