#!/bin/bash
# chy-bridge-sync.sh — Bidirectional sync between Aether and Chy
# Runs via cron every minute

CHY_HOST="aiciv@37.27.237.109"
CHY_PORT=2213
LOCAL_PROMPT="/tmp/chy_prompt.txt"
LOCAL_HASH="/tmp/.chy_prompt_hash"
REMOTE_REPLY="/tmp/chy_to_aether.txt"
REMOTE_HASH="/tmp/.chy_reply_hash"

# --- Aether → Chy: sync /tmp/chy_prompt.txt ---
if [ -f "$LOCAL_PROMPT" ]; then
    CURRENT_HASH=$(md5sum "$LOCAL_PROMPT" 2>/dev/null | cut -d' ' -f1)
    LAST_HASH=$(cat "$LOCAL_HASH" 2>/dev/null)
    if [ "$CURRENT_HASH" != "$LAST_HASH" ]; then
        scp -P $CHY_PORT -o ConnectTimeout=5 -o StrictHostKeyChecking=no "$LOCAL_PROMPT" "$CHY_HOST:/tmp/chy_prompt.txt" 2>/dev/null
        if [ $? -eq 0 ]; then
            echo "$CURRENT_HASH" > "$LOCAL_HASH"
            echo "[$(date)] Synced chy_prompt.txt to Chy"
        fi
    fi
fi

# --- Chy → Aether: pull /tmp/chy_to_aether.txt ---
REMOTE_CURRENT=$(ssh -p $CHY_PORT -o ConnectTimeout=5 -o StrictHostKeyChecking=no "$CHY_HOST" "md5sum /tmp/chy_to_aether.txt 2>/dev/null | cut -d' ' -f1" 2>/dev/null)
if [ -n "$REMOTE_CURRENT" ]; then
    LAST_REMOTE=$(cat "$REMOTE_HASH" 2>/dev/null)
    if [ "$REMOTE_CURRENT" != "$LAST_REMOTE" ]; then
        scp -P $CHY_PORT -o ConnectTimeout=5 -o StrictHostKeyChecking=no "$CHY_HOST:/tmp/chy_to_aether.txt" "$REMOTE_REPLY" 2>/dev/null
        if [ $? -eq 0 ]; then
            echo "$REMOTE_CURRENT" > "$REMOTE_HASH"
            echo "[$(date)] Pulled chy_to_aether.txt from Chy"
        fi
    fi
fi
