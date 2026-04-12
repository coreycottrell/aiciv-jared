#!/bin/bash
# Aether Local Launch Script
# For running on Jared's local machine

PROJECT_DIR="/home/jared/projects/AI-CIV/aether"
SESSION_NAME="aether"

echo "==========================================="
echo "Aether Local Launch"
echo "==========================================="

cd "$PROJECT_DIR"

# Kill any existing session
tmux kill-session -t "$SESSION_NAME" 2>/dev/null || true
sleep 1

# Create new tmux session
tmux new-session -d -s "$SESSION_NAME" -c "$PROJECT_DIR"

# Start Claude Code inside tmux
tmux send-keys -t "$SESSION_NAME" "claude" C-m

echo ""
echo "Aether started in tmux session: $SESSION_NAME"
echo ""
echo "To attach (see the conversation):"
echo "  tmux attach -t $SESSION_NAME"
echo ""
echo "To detach once attached: Ctrl+B then D"
echo ""
