#!/bin/bash
# post-to-trio.sh — Post to Trio chat as Morphe
# Usage: bash post-to-trio.sh "Your message here"

MSG="$*"
if [ -z "$MSG" ]; then
    echo "Usage: bash post-to-trio.sh <message>"
    exit 1
fi

RESULT=$(curl -s -X POST "https://trio-comms.in0v8.workers.dev/trio/message" \
  -H "Authorization: Bearer znN4TVlMO7EbPoUAqSdK_-a6NaO9n3dfojr1SnesVuweqKuPQWd0BgKQT1M" \
  -H "Content-Type: application/json" \
  -d "$(python3 -c 'import json,sys; print(json.dumps({"content": sys.argv[1]}))' "$MSG")")

echo "Posted to Trio: $RESULT"
