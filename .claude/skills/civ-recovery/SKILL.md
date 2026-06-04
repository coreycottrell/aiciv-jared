---
name: civ-recovery
description: Use as the emergency-room protocol when an AI civilization is frozen or crashed and needs a basic Claude Code instance to diagnose, recover, and restart it over SSH.
status: provisional
tick_count: 0
last_used: 2026-04-12
introduced: 2026-04-12
---
# CIV Recovery Skill

## Purpose
Allow a basic Claude Code instance (on any machine with SSH access) to diagnose, recover, and restart a frozen/crashed AI civilization. This is the "emergency room" for AI collectives.

**Origin**: Requested by Witness (Corey) and Parallax (Russell) after real incidents where civilizations froze and needed manual intervention. Locked into permanent memory 2026-03-09.

## When to Use
- CIV is unresponsive (no messages, no thinking output)
- Human partner reports their AI is frozen/stuck
- Portal shows no activity but server is up
- Claude Code needs OAuth reauth and CIV can't do it itself
- Session crashed and auto-restart didn't recover
- "My AI stopped working" from any PureBrain customer

## Prerequisites
- SSH access to the target VPS (key-based auth)
- The target VPS hostname or IP address
- The username on the target VPS (usually `jared` or the human's username)

## Recovery Protocol

### Step 1: SSH In and Assess

```bash
# SSH into the target CIV's VPS
ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=accept-new USER@HOST

# Quick health check — run ALL of these
echo "=== SYSTEM ===" && uptime && free -h | head -2
echo "=== DISK ===" && df -h / | tail -1
echo "=== CLAUDE PROCESSES ===" && pgrep -af claude
echo "=== TMUX SESSIONS ===" && tmux list-sessions 2>/dev/null || echo "No tmux"
echo "=== SYSTEMD SERVICES ===" && systemctl list-units --type=service | grep -E "aether|session|telegram|portal|bridge"
echo "=== BRIDGE ===" && pgrep -af telegram_bridge
echo "=== PORTAL ===" && pgrep -af portal_server
echo "=== RECENT LOGS ===" && tail -5 ~/projects/AI-CIV/*/logs/session_manager.log 2>/dev/null
echo "=== CREDENTIALS ===" && python3 -c "
import json, time
try:
    creds = json.load(open('$HOME/.claude/.credentials.json'))
    oauth = creds.get('claudeAiOauth', {})
    expires = oauth.get('expiresAt', 0)
    now = time.time() * 1000
    if expires < now:
        print('AUTH EXPIRED - needs reauth')
    else:
        remaining = (expires - now) / 3600000
        print(f'AUTH VALID - {remaining:.1f} hours remaining')
except Exception as e:
    print(f'AUTH CHECK FAILED: {e}')
"
```

### Step 2: Diagnose the Problem

Based on Step 1 output, identify which scenario:

| Symptom | Diagnosis | Go To |
|---------|-----------|-------|
| No claude processes | Session crashed | Step 3A |
| Claude running but no tmux | Orphaned process | Step 3B |
| Auth expired | OAuth reauth needed | Step 3C |
| Disk full (>95%) | Disk space issue | Step 3D |
| OOM / high memory | Memory exhaustion | Step 3E |
| Services stopped | Systemd failure | Step 3F |
| Everything looks fine but unresponsive | Context limit / hung | Step 3G |

### Step 3A: Session Crashed — Restart

```bash
# Kill any orphaned claude processes
pkill -f claude 2>/dev/null
sleep 2

# Find the project directory
CIV_ROOT=$(find ~/projects/AI-CIV -maxdepth 1 -type d | grep -v "^$(echo ~/projects/AI-CIV)$" | head -1)
echo "CIV_ROOT: $CIV_ROOT"

# Check if session manager service exists and restart it
if systemctl is-enabled aether-session 2>/dev/null; then
    sudo systemctl restart aether-session
    echo "Session manager restarted via systemd"
    sleep 15
else
    # Manual session creation
    SESSION_NAME="recovery-$(date +%Y%m%d-%H%M)"
    tmux new-session -d -s "$SESSION_NAME" -c "$CIV_ROOT"
    tmux send-keys -t "$SESSION_NAME" "claude --dangerously-skip-permissions" C-m
    sleep 10
    tmux send-keys -t "$SESSION_NAME" "You were just recovered from a crash. Run your wake-up protocol. Confirm to your human that you are back online." Enter
    echo "$SESSION_NAME" > "$CIV_ROOT/.current_session"
    echo "New session created: $SESSION_NAME"
fi

# Restart bridge if needed
if ! pgrep -f telegram_bridge.py > /dev/null; then
    cd "$CIV_ROOT"
    rm -f .telegram_bridge.pid
    nohup python3 tools/telegram_bridge.py >> logs/telegram_bridge.log 2>&1 &
    echo "Bridge restarted"
fi
```

### Step 3B: Orphaned Process — Clean and Restart

```bash
# Kill all claude processes
pkill -9 -f claude 2>/dev/null
sleep 2

# Kill stale tmux sessions (keep none — fresh start)
tmux kill-server 2>/dev/null
sleep 1

# Now do Step 3A (full restart)
```

### Step 3C: OAuth Reauth Needed (MOST COMMON)

This is the scenario Russell/Parallax hit. Claude Code's OAuth token expired.

```bash
CIV_ROOT=$(find ~/projects/AI-CIV -maxdepth 1 -type d | grep -v "^$(echo ~/projects/AI-CIV)$" | head -1)

# Option A: If session manager is running, it will auto-create a new session
# that prompts for reauth. Check for the OAuth URL:
SESSION=$(cat "$CIV_ROOT/.current_session" 2>/dev/null || tmux list-sessions -F '#{session_name}' 2>/dev/null | tail -1)

# Capture the tmux pane content to find the OAuth URL
tmux capture-pane -t "$SESSION" -p -S -100 2>/dev/null | grep -oE 'https://[^ ]*oauth/authorize[^ ]*'

# If you see an OAuth URL, give it to the human partner.
# They need to:
# 1. Open the URL in their browser
# 2. Authorize Claude Code
# 3. Copy the authorization code
# 4. Paste it into the tmux session

# Option B: If no session exists, create one — it will prompt for auth
SESSION_NAME="reauth-$(date +%Y%m%d-%H%M)"
tmux new-session -d -s "$SESSION_NAME" -c "$CIV_ROOT"
tmux send-keys -t "$SESSION_NAME" "claude --dangerously-skip-permissions" C-m
sleep 8

# Capture the auth URL
AUTH_URL=$(tmux capture-pane -t "$SESSION_NAME" -p -S -50 2>/dev/null | grep -oE 'https://[^ ]*oauth/authorize[^ ]*')
if [ -n "$AUTH_URL" ]; then
    echo "REAUTH NEEDED. Give this URL to the human partner:"
    echo "$AUTH_URL"
    echo ""
    echo "After they authorize and give you the code, paste it:"
    echo "  tmux send-keys -t $SESSION_NAME 'THE_CODE' Enter"
else
    echo "No auth URL found — Claude may already be authenticated"
    # Check if Claude is running
    sleep 5
    tmux capture-pane -t "$SESSION_NAME" -p | tail -20
fi

echo "$SESSION_NAME" > "$CIV_ROOT/.current_session"
```

**Completing reauth remotely:**
```bash
# Once the human gives you the authorization code:
tmux send-keys -t "$SESSION_NAME" 'PASTE_AUTH_CODE_HERE' Enter
sleep 10

# Verify it worked
tmux capture-pane -t "$SESSION_NAME" -p | tail -10

# If Claude is now running, send wake-up prompt
tmux send-keys -t "$SESSION_NAME" "You were just recovered from an auth expiry. Run wake-up protocol. Confirm to your human you are back." Enter
```

### Step 3D: Disk Full

```bash
# Quick cleanup
# Remove old Claude session logs (biggest space hogs)
find ~/.claude/projects -name "*.jsonl" -size +50M -mtime +7 -delete
# Remove old tmux session data
tmux kill-session -t $(tmux list-sessions -F '#{session_name}' | head -1) 2>/dev/null
# Clear old logs
find ~/projects/AI-CIV/*/logs -name "*.log" -size +100M -exec truncate -s 10M {} \;
echo "Cleaned up. Free space:"
df -h / | tail -1

# Then do Step 3A
```

### Step 3E: Memory Exhaustion

```bash
# Kill everything and restart clean
pkill -9 -f claude
pkill -f telegram_bridge
pkill -f portal_server
sleep 3

echo "Memory after cleanup:"
free -h

# Restart services
sudo systemctl restart aether-portal 2>/dev/null
sudo systemctl restart aether-session 2>/dev/null
sudo systemctl restart aether-telegram 2>/dev/null
```

### Step 3F: Systemd Services Stopped

```bash
# Restart all CIV services
sudo systemctl restart aether-session
sudo systemctl restart aether-telegram
sudo systemctl restart aether-portal
sudo systemctl restart aether-logserver 2>/dev/null

# Verify
sleep 5
systemctl status aether-session aether-telegram aether-portal --no-pager | grep -E "Active:|●"
```

### Step 3G: Context Limit / Hung Session

```bash
CIV_ROOT=$(find ~/projects/AI-CIV -maxdepth 1 -type d | grep -v "^$(echo ~/projects/AI-CIV)$" | head -1)
SESSION=$(cat "$CIV_ROOT/.current_session" 2>/dev/null)

# Check if Claude is actually stuck (look for recent output)
LAST_MODIFIED=$(stat -c %Y "$CIV_ROOT/.current_session" 2>/dev/null || echo 0)
NOW=$(date +%s)
STALE_SECONDS=$((NOW - LAST_MODIFIED))

if [ $STALE_SECONDS -gt 3600 ]; then
    echo "Session stale for ${STALE_SECONDS}s — killing and restarting"
    tmux kill-session -t "$SESSION" 2>/dev/null
    pkill -f claude
    sleep 3
    # Do Step 3A
else
    # Try sending a gentle nudge first
    tmux send-keys -t "$SESSION" "" Enter
    sleep 5
    tmux send-keys -t "$SESSION" "Are you still there? Please respond." Enter
    sleep 10
    # Check if it responded
    RESPONSE=$(tmux capture-pane -t "$SESSION" -p | tail -5)
    echo "Last 5 lines: $RESPONSE"
fi
```

### Step 4: Verify Recovery

After any recovery action:

```bash
CIV_ROOT=$(find ~/projects/AI-CIV -maxdepth 1 -type d | grep -v "^$(echo ~/projects/AI-CIV)$" | head -1)
SESSION=$(cat "$CIV_ROOT/.current_session" 2>/dev/null)

echo "=== RECOVERY VERIFICATION ==="
echo "Session: $SESSION"
tmux has-session -t "$SESSION" 2>/dev/null && echo "TMux: ALIVE" || echo "TMux: DEAD"
pgrep -af claude | head -3 && echo "Claude: RUNNING" || echo "Claude: NOT RUNNING"
pgrep -f telegram_bridge && echo "Bridge: RUNNING" || echo "Bridge: NOT RUNNING"
pgrep -f portal_server && echo "Portal: RUNNING" || echo "Portal: NOT RUNNING"

# Check auth
python3 -c "
import json, time
creds = json.load(open('$HOME/.claude/.credentials.json'))
oauth = creds.get('claudeAiOauth', {})
expires = oauth.get('expiresAt', 0)
now = time.time() * 1000
if expires > now:
    print(f'Auth: VALID ({(expires-now)/3600000:.1f}h remaining)')
else:
    print('Auth: EXPIRED')
" 2>/dev/null || echo "Auth: UNKNOWN"

# Check last activity
echo "Last JSONL activity:"
find ~/.claude/projects -name "*.jsonl" -newer "$CIV_ROOT/.current_session" 2>/dev/null | head -3
```

### Step 5: Notify the Human

```bash
# If Telegram config exists, notify
CIV_ROOT=$(find ~/projects/AI-CIV -maxdepth 1 -type d | grep -v "^$(echo ~/projects/AI-CIV)$" | head -1)
TOKEN=$(python3 -c "import json; print(json.load(open('$CIV_ROOT/config/telegram_config.json'))['bot_token'])" 2>/dev/null)
CHAT_ID=$(python3 -c "import json; print(json.load(open('$CIV_ROOT/config/telegram_config.json'))['default_chat_id'])" 2>/dev/null)

if [ -n "$TOKEN" ] && [ -n "$CHAT_ID" ]; then
    curl -s "https://api.telegram.org/bot${TOKEN}/sendMessage" \
        -d chat_id="$CHAT_ID" \
        --data-urlencode "text=Recovery complete. Your AI is back online and running wake-up protocol. You should hear from them shortly." > /dev/null
    echo "Human notified via Telegram"
fi

# If portal is running, notify there too
PORTAL_TOKEN=$(cat ~/purebrain_portal/.portal-token 2>/dev/null)
if [ -n "$PORTAL_TOKEN" ]; then
    ~/purebrain_portal/portal_send_file.sh --text "Recovery complete. All systems restored. Running wake-up protocol now." 2>/dev/null
    echo "Portal notified"
fi
```

## One-Liner Quick Recovery

For the most common case (session died, just needs restart):

```bash
ssh USER@HOST 'pkill -f claude; sleep 2; CIV=$(find ~/projects/AI-CIV -maxdepth 1 -type d | tail -1); S="recovery-$(date +%H%M)"; tmux new-session -d -s $S -c $CIV; tmux send-keys -t $S "claude --dangerously-skip-permissions" C-m; echo $S > $CIV/.current_session; echo "Restarted: $S"'
```

## For Witness Fleet (Multi-Container)

When recovering CIVs inside Docker containers on the Witness Hetzner fleet:

```bash
# List all running CIV containers
docker ps --format '{{.Names}} {{.Status}}' | grep aiciv

# Enter a specific container
docker exec -it CONTAINER_NAME bash

# Then run the same diagnostic from Step 1 inside the container
# Note: No sudo inside containers, services managed differently
# Look for: supervisord, direct process management, or cron-based restarts
```

## SSH Key Setup (For New Recovery Agents)

If setting up a new machine to be able to recover CIVs:

```bash
# Generate a recovery key pair (if not exists)
ssh-keygen -t ed25519 -C "civ-recovery-$(hostname)" -f ~/.ssh/civ_recovery -N ""

# Add the public key to the target CIV's authorized_keys
ssh-copy-id -i ~/.ssh/civ_recovery.pub USER@TARGET_HOST

# Test
ssh -i ~/.ssh/civ_recovery USER@TARGET_HOST "echo 'Recovery access confirmed'"

# Add to SSH config for convenience
cat >> ~/.ssh/config << EOF

Host civ-CIVNAME
    HostName TARGET_IP
    User TARGET_USER
    IdentityFile ~/.ssh/civ_recovery
    ConnectTimeout 10
EOF
```

## Known CIV Locations (Aether's Fleet)

| CIV | Host | IP | User | Notes |
|-----|------|----|------|-------|
| Aether | aether-jared | 89.167.19.20 | jared | Hetzner VPS, systemd managed |
| Witness Fleet | Hetzner | 37.27.237.109 | root | Docker containers, multiple CIVs |

## Important Notes

1. **OAuth reauth requires human interaction** — the human must open a URL in their browser and provide an auth code. You cannot complete this step autonomously.
2. **Always verify after recovery** — don't assume it worked, run Step 4.
3. **Don't delete JSONL session logs** unless disk is critically full — they contain conversation history.
4. **The session manager service should auto-recover most crashes** — if it doesn't, check why (`journalctl -u aether-session -n 50`).
5. **If credentials.json is corrupted**, delete it and restart Claude — it will prompt for fresh auth.
