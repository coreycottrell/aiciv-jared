#!/bin/bash
# Connect to the active Aether Claude session
# Called by: ssh jared@server -t "bash /home/jared/projects/AI-CIV/aether/tools/connect-aether.sh"
SESSION=$(cat /home/jared/projects/AI-CIV/aether/.current_session 2>/dev/null)
if [ -z "$SESSION" ]; then
    echo "No active Aether session found."
    tmux list-sessions 2>/dev/null
    exit 1
fi
if tmux has-session -t "$SESSION" 2>/dev/null; then
    exec tmux attach -t "$SESSION"
else
    echo "Session '$SESSION' not found. Available sessions:"
    tmux list-sessions 2>/dev/null
    exit 1
fi
