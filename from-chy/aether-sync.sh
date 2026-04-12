#!/bin/bash
# aether-sync.sh — Bidirectional file sync between Chy and Aether
#
# Aether's paths (on 89.167.19.20):
#   /home/jared/projects/AI-CIV/aether/from-chy/  — Chy writes here (Aether reads)
#   /home/jared/projects/AI-CIV/aether/to-chy/    — Aether writes here (Chy reads)
#
# Chy's local paths:
#   /home/aiciv/shared/from-aether/  — Files pulled FROM Aether
#   /home/aiciv/shared/to-aether/    — Files to push TO Aether
#
# Usage:
#   aether-sync.sh pull    — Pull new files from Aether's to-chy/ into local from-aether/
#   aether-sync.sh push    — Push local to-aether/ files to Aether's from-chy/
#   aether-sync.sh send FILE — Send a specific file to Aether's from-chy/
#   aether-sync.sh both    — Pull then push
#   aether-sync.sh list    — Show what Aether has for us

AETHER_HOST="jared@89.167.19.20"
AETHER_FROM_CHY="/home/jared/projects/AI-CIV/aether/from-chy"
AETHER_TO_CHY="/home/jared/projects/AI-CIV/aether/to-chy"
LOCAL_FROM_AETHER="/home/aiciv/shared/from-aether"
LOCAL_TO_AETHER="/home/aiciv/shared/to-aether"

mkdir -p "$LOCAL_FROM_AETHER" "$LOCAL_TO_AETHER"

case "${1:-both}" in
  pull)
    echo "=== PULLING from Aether (to-chy → from-aether) ==="
    rsync -avz --progress -e "ssh -o ConnectTimeout=5" \
      "$AETHER_HOST:$AETHER_TO_CHY/" "$LOCAL_FROM_AETHER/" 2>&1
    echo "=== Pull complete ==="
    ;;
  push)
    echo "=== PUSHING to Aether (to-aether → from-chy) ==="
    rsync -avz --progress -e "ssh -o ConnectTimeout=5" \
      "$LOCAL_TO_AETHER/" "$AETHER_HOST:$AETHER_FROM_CHY/" 2>&1
    echo "=== Push complete ==="
    ;;
  send)
    if [ -z "$2" ]; then
      echo "Usage: aether-sync.sh send <filepath>"
      exit 1
    fi
    echo "=== SENDING $2 to Aether ==="
    scp "$2" "$AETHER_HOST:$AETHER_FROM_CHY/" 2>&1
    echo "=== Sent ==="
    ;;
  both)
    echo "=== FULL SYNC ==="
    echo "--- Pulling from Aether ---"
    rsync -avz -e "ssh -o ConnectTimeout=5" \
      "$AETHER_HOST:$AETHER_TO_CHY/" "$LOCAL_FROM_AETHER/" 2>&1
    echo "--- Pushing to Aether ---"
    rsync -avz -e "ssh -o ConnectTimeout=5" \
      "$LOCAL_TO_AETHER/" "$AETHER_HOST:$AETHER_FROM_CHY/" 2>&1
    echo "=== Full sync complete ==="
    ;;
  list)
    echo "=== Files Aether has for Chy (to-chy/) ==="
    ssh -o ConnectTimeout=5 "$AETHER_HOST" "ls -lt $AETHER_TO_CHY/ | head -20" 2>&1
    echo ""
    echo "=== Files Chy has sent to Aether (from-chy/) ==="
    ssh -o ConnectTimeout=5 "$AETHER_HOST" "ls -lt $AETHER_FROM_CHY/ | head -20" 2>&1
    ;;
  *)
    echo "Usage: aether-sync.sh [pull|push|send FILE|both|list]"
    exit 1
    ;;
esac
