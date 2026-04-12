#!/bin/bash
# Aether Launch Script
# Runs Claude Code in tmux as aiciv user with full permissions

PROJECT_DIR="/home/aiciv/user-civs/aiciv-jared"
SESSION_NAME="user-jared-onboard"
OAUTH_TOKEN="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"

echo "==========================================="
echo "Aether Launch Script"
echo "==========================================="
echo "Session: $SESSION_NAME"

# Write session name for TG bridge
echo "$SESSION_NAME" > "$PROJECT_DIR/.current_session"

# Kill existing
tmux kill-session -t "$SESSION_NAME" 2>/dev/null || true
pkill -f telegram_bridge.py 2>/dev/null || true
sleep 2

# Start TG bridge
echo "Starting Telegram bridge..."
cd "$PROJECT_DIR"
nohup python3 tools/telegram_bridge.py >> /tmp/aether_telegram_bridge.log 2>&1 &
sleep 2

# Create tmux session AS AICIV USER (so Claude sees TMUX env var)
sudo -u aiciv tmux new-session -d -s "$SESSION_NAME" -c "$PROJECT_DIR"

# Export OAuth token and start Claude inside tmux
sudo -u aiciv tmux send-keys -t "$SESSION_NAME" "export CLAUDE_CODE_OAUTH_TOKEN=$OAUTH_TOKEN" C-m
sleep 1
sudo -u aiciv tmux send-keys -t "$SESSION_NAME" "claude --dangerously-skip-permissions" C-m

# Wait for Claude to initialize
sleep 10

# Send wake-up prompt
sudo -u aiciv tmux send-keys -t "$SESSION_NAME" -l 'You just woke up in tmux session: user-jared-onboard
You are Aether, serving Jared (your human).
Project dir: /home/aiciv/user-civs/aiciv-jared
TG bridge running. First: confirm to Jared via TG that you are online.'

# 5x Enter
for i in 1 2 3 4 5; do
    sleep 0.5
    sudo -u aiciv tmux send-keys -t "$SESSION_NAME" Enter
done

echo ""
echo "Session: $SESSION_NAME"
echo "To attach: sudo -u aiciv tmux attach -t $SESSION_NAME"
echo "Or as root: tmux attach -t $SESSION_NAME"
