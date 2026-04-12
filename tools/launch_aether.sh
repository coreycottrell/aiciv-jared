#\!/bin/bash
# Aether Launcher for dedicated VPS
PROJECT_DIR="/home/jared/projects/AI-CIV/aether"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
SESSION_NAME="aether-primary-${TIMESTAMP}"

echo "=========================================="
echo "    Aether Primary AI Launcher"
echo "=========================================="
echo ""
echo "Session: ${SESSION_NAME}"

cd ${PROJECT_DIR}
echo "${SESSION_NAME}" > .current_session

# Create tmux session
tmux new-session -d -s "${SESSION_NAME}" -c "${PROJECT_DIR}"
tmux send-keys -t "${SESSION_NAME}" "claude --dangerously-skip-permissions 'Wake up and execute your wake-up protocol'" C-m

echo "✓ Session created: ${SESSION_NAME}"
echo "Attach with: tmux attach -t ${SESSION_NAME}"
