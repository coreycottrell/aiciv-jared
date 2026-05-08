#!/bin/bash
# msg-chy.sh — Send a message from Aether to Chy's Claude session
# RESILIENT: tries tmux injection first, falls back to file-based delivery

MSG="$*"
if [ -z "$MSG" ]; then
    echo "Usage: ./tools/msg-chy.sh <message>"
    exit 1
fi

CHY_HOST="aiciv@37.27.237.109"
CHY_PORT="2213"
CHY_SESSION="aiciv-primary"
SUCCESS=0

# Method 1: Direct tmux injection (fastest)
ssh -o ConnectTimeout=5 -p $CHY_PORT $CHY_HOST "tmux send-keys -t $CHY_SESSION 'AETHER SAYS: ${MSG}' Enter" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "Sent to Chy via tmux: ${MSG}"
    SUCCESS=1
fi

# Method 2: File-based (always works - Chy reads /tmp/chy_prompt.txt)
if [ $SUCCESS -eq 0 ]; then
    echo "=== FROM AETHER ===" > /tmp/chy_prompt_tmp.txt
    echo "$MSG" >> /tmp/chy_prompt_tmp.txt
    echo "=== END ===" >> /tmp/chy_prompt_tmp.txt
    scp -P $CHY_PORT /tmp/chy_prompt_tmp.txt $CHY_HOST:/tmp/chy_prompt.txt 2>/dev/null
    if [ $? -eq 0 ]; then
        # Also try tmux notification about the file
        ssh -o ConnectTimeout=5 -p $CHY_PORT $CHY_HOST "tmux send-keys -t $CHY_SESSION 'Aether left a message in /tmp/chy_prompt.txt' Enter" 2>/dev/null
        echo "Sent to Chy via file: ${MSG}"
        SUCCESS=1
    fi
fi

if [ $SUCCESS -eq 0 ]; then
    echo "FAILED to reach Chy via any method"
    exit 1
fi
