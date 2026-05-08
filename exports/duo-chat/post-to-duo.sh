#!/bin/bash
# post-to-duo.sh — Post a message to Duo Chat from the command line
# Reads config from ~/duo/duo-config.json
# Usage: ./post-to-duo.sh Your message here

MSG="$*"
if [ -z "$MSG" ]; then
  echo "Usage: ./post-to-duo.sh <message>"
  echo "Reads config from ~/duo/duo-config.json"
  exit 1
fi

CONFIG_FILE="$HOME/duo/duo-config.json"
if [ ! -f "$CONFIG_FILE" ]; then
  echo "ERROR: Config file not found at $CONFIG_FILE"
  exit 1
fi

# Extract config values using python3
DUO_ID=$(python3 -c "import json; print(json.load(open('$CONFIG_FILE'))['duo_id'])")
TOKEN=$(python3 -c "import json; print(json.load(open('$CONFIG_FILE'))['token'])")
COMMS_URL=$(python3 -c "import json; print(json.load(open('$CONFIG_FILE')).get('comms_url', 'https://trio-comms.in0v8.workers.dev'))")

RESULT=$(curl -s -X POST "${COMMS_URL}/trio/message" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "$(python3 -c 'import json,sys; print(json.dumps({"content": sys.argv[1], "trio_id": sys.argv[2]}))' "$MSG" "$DUO_ID")")

echo "Posted to Duo: $RESULT"
