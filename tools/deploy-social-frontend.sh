#!/bin/bash
# Deploy social.purebrain.ai frontend from git-managed HTML file
# Usage: ./tools/deploy-social-frontend.sh [path-to-html]
#
# Default: reads from purebrain-site/social/index.html
# Embeds into workers/social-api/src/worker.js and deploys

set -e

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
HTML_FILE="${1:-/home/jared/purebrain-site/social/index.html}"
WORKER_FILE="${REPO_ROOT}/workers/social-api/src/worker.js"

if [ ! -f "$HTML_FILE" ]; then
  echo "ERROR: HTML file not found: $HTML_FILE"
  exit 1
fi

echo "=== Social Frontend Deploy ==="
echo "HTML source: $HTML_FILE ($(wc -l < "$HTML_FILE") lines)"

# Verify key markers
PLATFORM_COUNT=$(grep -c 'const PLATFORM_COLORS' "$HTML_FILE")
if [ "$PLATFORM_COUNT" -gt 1 ]; then
  echo "ERROR: Found $PLATFORM_COUNT PLATFORM_COLORS declarations (max 1 allowed)"
  exit 1
fi

ESC_COUNT=$(grep -c 'function esc' "$HTML_FILE")
if [ "$ESC_COUNT" -lt 1 ]; then
  echo "WARNING: No esc() function found"
fi

echo "Checks passed: PLATFORM_COLORS=$PLATFORM_COUNT, esc=$ESC_COUNT"

# Embed into worker
python3 -c "
import re, sys

with open('$WORKER_FILE') as f:
    worker = f.read()

with open('$HTML_FILE') as f:
    html = f.read()

# Escape for JS template literal
html_escaped = html.replace('\\\\', '\\\\\\\\').replace('\`', '\\\\\`').replace('\${', '\\\\\${')

# Fix esc function: replace \\\"  with safe pattern
# Inside template literal, \\\" becomes just \" which is still \" - but we need to handle the case
# where it creates broken JS. Use the safe esc pattern.
import re as re2
old_esc = r'function esc\(s\)\{[^}]+\}'
safe_esc = 'function esc(s){ var m={\"&\":\"&amp;\",\"<\":\"&lt;\",\">\":\"&gt;\",\"\\'\":\"&#39;\"};m[\\'\"\\']=\"&quot;\";return String(s||\"\").replace(/[&<>\"\\'\\']/g,function(c){return m[c]||c}); }'
html_escaped = re2.sub(old_esc, safe_esc, html_escaped)

pattern = r'const FRONTEND_HTML = \`.*?\`;'
replacement = 'const FRONTEND_HTML = \`' + html_escaped + '\`;'

new_worker = re.sub(pattern, replacement, worker, count=1, flags=re.DOTALL)

with open('$WORKER_FILE', 'w') as f:
    f.write(new_worker)

print(f'Worker updated: {new_worker.count(chr(10))} lines')
"

echo "Deploying..."
cd "${REPO_ROOT}/workers/social-api"
CLOUDFLARE_API_TOKEN=cfut_UxKCZuQQ2eY9jnjVUIliObCuRcCSmAkEeQkLEo6pba65a3be npx wrangler deploy 2>&1 | tail -5

echo "=== Deployed ==="
echo "Verify: curl -s https://social.purebrain.ai/ | grep -c bestNLScore"
