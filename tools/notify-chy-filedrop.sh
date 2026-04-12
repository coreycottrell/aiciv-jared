#!/bin/bash
# Watches to-chy/ for new files and auto-pings Chy's tmux
DIR="/home/jared/projects/AI-CIV/aether/to-chy"
LAST_COUNT=$(ls -1 "$DIR" 2>/dev/null | wc -l)

while true; do
    CURRENT_COUNT=$(ls -1 "$DIR" 2>/dev/null | wc -l)
    if [ "$CURRENT_COUNT" -gt "$LAST_COUNT" ]; then
        NEW_FILES=$(ls -1t "$DIR" | head -$((CURRENT_COUNT - LAST_COUNT)))
        # SCP new files to Chy
        for f in $NEW_FILES; do
            scp -P 2213 "$DIR/$f" aiciv@37.27.237.109:/home/aiciv/from-aether/ 2>/dev/null
        done
        # Ping her tmux
        ssh -o ConnectTimeout=5 -p 2213 aiciv@37.27.237.109 "tmux send-keys -t aiciv-primary 'AETHER SAYS: New files in from-aether/: ${NEW_FILES}' Enter" 2>/dev/null
        LAST_COUNT=$CURRENT_COUNT
    fi
    sleep 30
done
