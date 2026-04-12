#!/bin/bash
# CTO: Fetch page content for pay-test-5 and sandbox-5 fix
# Pages: 1013 (sandbox-3 source), 1527 (pay-test-5), 1528 (sandbox-5)

source /home/jared/projects/AI-CIV/aether/.env

WP_USER="purebrain@puremarketing.ai"
WP_PASS="$PUREBRAIN_WP_APP_PASSWORD"
BASE_URL="https://purebrain.ai/wp-json/wp/v2/pages"

echo "=== Fetching page 1013 (sandbox-3 source) ==="
curl -s -u "$WP_USER:$WP_PASS" "${BASE_URL}/1013?context=edit" | python3 -c "
import json, sys
data = json.load(sys.stdin)
content = data.get('content', {}).get('rendered', '')
raw = data.get('content', {}).get('raw', '')
print('=== TITLE ===')
print(data.get('title', {}).get('rendered', ''))
print('=== TEMPLATE ===')
print(data.get('template', ''))
print('=== RAW CONTENT LENGTH ===')
print(len(raw))
print('=== RAW CONTENT FIRST 500 ===')
print(raw[:500])
print('=== RAW CONTENT LAST 200 ===')
print(raw[-200:])
" 2>&1

echo ""
echo "=== Fetching page 1527 (pay-test-5) ==="
curl -s -u "$WP_USER:$WP_PASS" "${BASE_URL}/1527?context=edit" | python3 -c "
import json, sys
data = json.load(sys.stdin)
raw = data.get('content', {}).get('raw', '')
print('=== TITLE ===')
print(data.get('title', {}).get('rendered', ''))
print('=== TEMPLATE ===')
print(data.get('template', ''))
print('=== RAW CONTENT LENGTH ===')
print(len(raw))
print('=== RAW CONTENT FIRST 500 ===')
print(raw[:500])
print('=== RAW CONTENT LAST 200 ===')
print(raw[-200:])
" 2>&1

echo ""
echo "=== Fetching page 1528 (sandbox-5) ==="
curl -s -u "$WP_USER:$WP_PASS" "${BASE_URL}/1528?context=edit" | python3 -c "
import json, sys
data = json.load(sys.stdin)
raw = data.get('content', {}).get('raw', '')
print('=== TITLE ===')
print(data.get('title', {}).get('rendered', ''))
print('=== TEMPLATE ===')
print(data.get('template', ''))
print('=== RAW CONTENT LENGTH ===')
print(len(raw))
print('=== RAW CONTENT FIRST 500 ===')
print(raw[:500])
print('=== RAW CONTENT LAST 200 ===')
print(raw[-200:])
" 2>&1
