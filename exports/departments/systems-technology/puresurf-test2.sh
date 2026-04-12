#!/bin/bash
# Test script v2 for PureSurf LinkedIn fixes — uses correct API params
set -e

APIKEY=$(python3 -c "import json; d=json.load(open('/opt/baas/baas_keys.json')); print(list(d.get('keys',{}).keys())[0])")
BASE="http://localhost:8901"
SESSION="linkedin-fix-test"

echo "=== PURESURF LINKEDIN FIX VERIFICATION v2 ==="
echo ""

# Clean up any existing session first
echo "--- CLEANUP: Remove any old test session ---"
curl -s -X DELETE "$BASE/sessions/$SESSION" -H "x-api-key: $APIKEY" 2>/dev/null || true
sleep 1

# Step 1: Create fresh LinkedIn session with profile_name
echo "--- STEP 1: Create fresh LinkedIn session (profile_name=$SESSION) ---"
RESULT=$(curl -s -X POST "$BASE/sessions" \
  -H "Content-Type: application/json" \
  -H "x-api-key: $APIKEY" \
  -d "{\"profile_name\": \"$SESSION\", \"proxy_provider\": \"floppydata-jared\"}")
echo "$RESULT" | python3 -m json.tool 2>/dev/null || echo "$RESULT"

SID=$(echo "$RESULT" | python3 -c "import json,sys; print(json.load(sys.stdin).get('session_id',''))" 2>/dev/null)
echo "Session ID: $SID"
if [ -z "$SID" ] || [ "$SID" = "" ]; then
    echo "FAIL: Could not create session"
    exit 1
fi
echo "PASS: Session created"
echo ""

sleep 3

# Step 2: Navigate to ipify to verify proxy is working
echo "--- STEP 2: Verify proxy (check IP) ---"
RESULT=$(curl -s -X POST "$BASE/sessions/$SID/navigate" \
  -H "Content-Type: application/json" \
  -H "x-api-key: $APIKEY" \
  -d '{"url": "https://api.ipify.org?format=json"}')
echo "$RESULT" | python3 -m json.tool 2>/dev/null || echo "$RESULT"
echo ""

sleep 3

# Step 3: Get page content to see IP
echo "--- STEP 3: Get IP from page ---"
RESULT=$(curl -s -X POST "$BASE/sessions/$SID/evaluate" \
  -H "Content-Type: application/json" \
  -H "x-api-key: $APIKEY" \
  -d '{"script": "document.body.innerText"}')
echo "Page content: $RESULT"
echo ""

sleep 2

# Step 4: Navigate to LinkedIn homepage
echo "--- STEP 4: Navigate to linkedin.com ---"
RESULT=$(curl -s -X POST "$BASE/sessions/$SID/navigate" \
  -H "Content-Type: application/json" \
  -H "x-api-key: $APIKEY" \
  -d '{"url": "https://www.linkedin.com/"}')
echo "$RESULT" | python3 -m json.tool 2>/dev/null || echo "$RESULT"
echo ""

sleep 5

# Step 5: Check page URL
echo "--- STEP 5: Check current URL ---"
RESULT=$(curl -s -X POST "$BASE/sessions/$SID/evaluate" \
  -H "Content-Type: application/json" \
  -H "x-api-key: $APIKEY" \
  -d '{"script": "JSON.stringify({url: window.location.href, title: document.title})"}')
echo "Page state: $RESULT"
echo ""

# Step 6: Navigate to feed
echo "--- STEP 6: Navigate to linkedin.com/feed/ ---"
RESULT=$(curl -s -X POST "$BASE/sessions/$SID/navigate" \
  -H "Content-Type: application/json" \
  -H "x-api-key: $APIKEY" \
  -d '{"url": "https://www.linkedin.com/feed/"}')
echo "$RESULT" | python3 -m json.tool 2>/dev/null || echo "$RESULT"
echo ""

sleep 5

# Step 7: Final URL check
echo "--- STEP 7: Final page state ---"
RESULT=$(curl -s -X POST "$BASE/sessions/$SID/evaluate" \
  -H "Content-Type: application/json" \
  -H "x-api-key: $APIKEY" \
  -d '{"script": "JSON.stringify({url: window.location.href, title: document.title})"}')
echo "Final state: $RESULT"
echo ""

# Step 8: Test anti-detection — verify no Chrome artifacts
echo "--- STEP 8: Anti-detection verification ---"
RESULT=$(curl -s -X POST "$BASE/sessions/$SID/evaluate" \
  -H "Content-Type: application/json" \
  -H "x-api-key: $APIKEY" \
  -d '{"script": "JSON.stringify({hasChrome: !!window.chrome, pluginNames: Array.from(navigator.plugins).map(p=>p.name), mimeTypes: Array.from(navigator.mimeTypes).map(m=>m.type), webdriver: navigator.webdriver})"}')
echo "Anti-detection: $RESULT"
echo ""

# Step 9: Check rate limit status
echo "--- STEP 9: Rate limit check ---"
RESULT=$(curl -s "$BASE/health" -H "x-api-key: $APIKEY" 2>/dev/null)
echo "$RESULT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(json.dumps(d.get('proactive_rate_limits',{}).get('linkedin.com',{}), indent=2))" 2>/dev/null || echo "Could not parse"
echo ""

# Cleanup
echo "--- CLEANUP: Delete test session ---"
curl -s -X DELETE "$BASE/sessions/$SID" -H "x-api-key: $APIKEY" 2>/dev/null | python3 -m json.tool 2>/dev/null || true
echo ""

echo "=== TEST COMPLETE ==="
