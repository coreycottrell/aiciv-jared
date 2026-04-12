#!/bin/bash
# Aether Multi-Worker Launch Script
# Launches multiple Claude Code instances under Primary's coordination

PROJECT_DIR="/home/jared/projects/AI-CIV/aether"
OAUTH_TOKEN="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"

# Number of workers (default 2, can override with argument)
NUM_WORKERS=${1:-2}

echo "==========================================="
echo "Aether Multi-Worker Launch Script"
echo "==========================================="
echo "Project: $PROJECT_DIR"
echo "Workers to launch: $NUM_WORKERS"
echo ""

# Function to launch a worker
launch_worker() {
    local WORKER_NUM=$1
    local SESSION_NAME="aether-worker-$WORKER_NUM"
    
    echo "Launching $SESSION_NAME..."
    
    # Kill existing if any
    tmux kill-session -t "$SESSION_NAME" 2>/dev/null || true
    
    # Create new session
    tmux new-session -d -s "$SESSION_NAME" -c "$PROJECT_DIR"
    
    # Export OAuth token and start Claude
    tmux send-keys -t "$SESSION_NAME" "export CLAUDE_CODE_OAUTH_TOKEN=$OAUTH_TOKEN" C-m
    sleep 1
    tmux send-keys -t "$SESSION_NAME" "claude --dangerously-skip-permissions" C-m
    
    # Wait for Claude to initialize
    sleep 5
    
    # Send worker identity prompt
    tmux send-keys -t "$SESSION_NAME" -l "You are Aether Worker $WORKER_NUM.
You are a worker instance under Primary Aether's coordination.
Project dir: $PROJECT_DIR
Wait for tasks from Primary via tmux injection.
Say 'Worker $WORKER_NUM ready' to confirm."
    
    # Send Enter to submit
    for i in 1 2 3; do
        sleep 0.3
        tmux send-keys -t "$SESSION_NAME" Enter
    done
    
    echo "  $SESSION_NAME launched"
}

# Launch workers
for i in $(seq 1 $NUM_WORKERS); do
    launch_worker $i
done

echo ""
echo "==========================================="
echo "Workers Launched:"
tmux list-sessions | grep aether-worker || echo "  (waiting for sessions...)"
echo ""
echo "Commands:"
echo "  View all:     tmux list-sessions"
echo "  Attach:       tmux attach -t aether-worker-1"
echo "  Send task:    tmux send-keys -t aether-worker-1 'Your task here' Enter"
echo "  Kill all:     for s in \$(tmux ls | grep aether-worker | cut -d: -f1); do tmux kill-session -t \$s; done"
echo "==========================================="
