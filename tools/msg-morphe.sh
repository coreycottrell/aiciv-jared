#!/bin/bash
# msg-morphe.sh — Send a message from Aether to Morphe
# FILE-DROP PRIMARY: Morphe has NO sshd — tmux injection path will fail
# Protocol source: .claude/skills/inter-civ-inject/SKILL.md
# Created 2026-04-14

MSG="$*"
if [ -z "$MSG" ]; then
    echo "Usage: ./tools/msg-morphe.sh <message>"
    exit 1
fi

# Morphe's push-inbox on our server (she polls this directory)
MORPHE_INBOX="/home/jared/projects/AI-CIV/aether/to-morphe"
TIMESTAMP=$(date -u +%Y%m%d-%H%M%S)
DROP_FILE="$MORPHE_INBOX/msg-$TIMESTAMP.txt"

SUCCESS=0

# Ensure inbox exists
mkdir -p "$MORPHE_INBOX" 2>/dev/null

# Method 1: File-drop to local push-inbox (PRIMARY for Morphe)
{
    echo "=== FROM AETHER ==="
    echo "Timestamp: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "---"
    echo "$MSG"
    echo "=== END ==="
} > "$DROP_FILE"

if [ $? -eq 0 ] && [ -f "$DROP_FILE" ]; then
    echo "Dropped to Morphe inbox: $DROP_FILE"
    echo "Message: ${MSG}"
    SUCCESS=1
fi

# Method 2: tmux injection — SKIPPED for Morphe (no sshd)
# Exit cleanly without retrying on host that can't accept SSH.
# If Morphe gains sshd later, 5x Enter protocol from inter-civ-inject skill applies.

if [ $SUCCESS -eq 0 ]; then
    echo "FAILED to drop message to Morphe inbox"
    exit 1
fi

exit 0
