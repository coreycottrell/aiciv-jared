#!/usr/bin/env bash
# portal_deliver.sh — Deliver files to the PureBrain Portal with downloadable previews
#
# Usage:
#   ./tools/portal_deliver.sh /path/to/file.md "Optional caption message"
#   ./tools/portal_deliver.sh /path/to/file.png
#   ./tools/portal_deliver.sh /path/to/file.md "Blog post ready for review" "custom-display-name.md"
#
# Arguments:
#   $1 — Absolute path to the file (REQUIRED)
#   $2 — Caption/message to show above the file card (OPTIONAL)
#   $3 — Custom display name (OPTIONAL, defaults to basename of the file)
#
# This uses the /api/deliverable endpoint which:
#   1. Copies the file to portal_uploads/
#   2. Creates a [PORTAL_FILE:] chat entry with styled download card
#   3. Pushes via WebSocket for real-time rendering
#
# Supports: .md, .png, .jpg, .html, .pdf, .xlsx, .csv, .json, .txt, any file type
#
# IMPORTANT: This is the CANONICAL method for delivering files to the portal.
#            Do NOT use [FILE: /path] tags in chat — they don't render properly.
#            Always use this script or call /api/deliverable directly.

set -euo pipefail

FILE_PATH="${1:-}"
MESSAGE="${2:-}"
DISPLAY_NAME="${3:-}"

if [ -z "$FILE_PATH" ]; then
  echo "ERROR: No file path provided."
  echo "Usage: ./tools/portal_deliver.sh /path/to/file.md [caption] [display-name]"
  exit 1
fi

if [ ! -f "$FILE_PATH" ]; then
  echo "ERROR: File not found: $FILE_PATH"
  exit 1
fi

# Get display name from filename if not provided
if [ -z "$DISPLAY_NAME" ]; then
  DISPLAY_NAME="$(basename "$FILE_PATH")"
fi

# Find portal token
PORTAL_TOKEN=""
for token_file in /home/jared/purebrain_portal/.portal-token /home/jared/projects/AI-CIV/aether/exports/app-purebrain-ai-full-repo/portal-server/.portal-token; do
  if [ -f "$token_file" ]; then
    PORTAL_TOKEN="$(cat "$token_file")"
    break
  fi
done

if [ -z "$PORTAL_TOKEN" ]; then
  echo "ERROR: No portal token found."
  exit 1
fi

# Find portal port (default 8097)
PORTAL_PORT="8097"

# Build JSON payload
JSON_PAYLOAD=$(python3 -c "
import json, sys
payload = {
    'path': sys.argv[1],
    'name': sys.argv[2],
    'message': sys.argv[3]
}
print(json.dumps(payload))
" "$FILE_PATH" "$DISPLAY_NAME" "$MESSAGE")

# Deliver
RESPONSE=$(curl -s -H "Authorization: Bearer $PORTAL_TOKEN" \
  "http://localhost:${PORTAL_PORT}/api/deliverable" \
  -X POST -H "Content-Type: application/json" \
  -d "$JSON_PAYLOAD")

# Check result
if echo "$RESPONSE" | python3 -c "import json,sys; d=json.load(sys.stdin); assert d.get('ok')" 2>/dev/null; then
  URL=$(echo "$RESPONSE" | python3 -c "import json,sys; print(json.load(sys.stdin).get('url',''))")
  echo "OK: Delivered '$DISPLAY_NAME' to portal. URL: $URL"
else
  ERROR=$(echo "$RESPONSE" | python3 -c "import json,sys; print(json.load(sys.stdin).get('error','unknown'))" 2>/dev/null || echo "$RESPONSE")
  echo "ERROR: $ERROR"
  exit 1
fi
