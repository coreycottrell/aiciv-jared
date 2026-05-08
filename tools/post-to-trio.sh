#!/bin/bash
# post-to-trio.sh — Post to Trio chat as Aether (preserves newlines via python json.dumps)
MSG="$*"
if [ -z "$MSG" ]; then echo "Usage: ./tools/post-to-trio.sh <message>"; exit 1; fi

TOKEN=$(grep TRIO_TOKEN_AETHER /home/jared/purebrain_portal/.env | cut -d= -f2)

RESULT=$(curl -s -X POST "https://trio-comms.in0v8.workers.dev/trio/message" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "$(python3 -c 'import json,sys; print(json.dumps({"content": sys.argv[1]}))' "$MSG")")

echo "Posted to Trio: $RESULT"
