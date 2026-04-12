#!/bin/bash
# Test script for PureSurf LinkedIn fixes
set -e

APIKEY=$(python3 -c "import json; d=json.load(open('/opt/baas/baas_keys.json')); print(list(d.get('keys',{}).keys())[0])")
BASE="http://localhost:8901"

echo "=== PURESURF LINKEDIN FIX VERIFICATION ==="
echo "API Key: ${APIKEY:0:10}..."
echo ""

# Step 1: Create fresh LinkedIn session
echo "--- STEP 1: Create fresh LinkedIn session ---"
RESULT=$(curl -s -X POST "$BASE/sessions" \
  -H "Content-Type: application/json" \
  -H "x-api-key: $APIKEY" \
  -d '{"session_id": "linkedin-test-fix-0406", "proxy_provider": "floppydata-jared"}')
echo "$RESULT" | python3 -m json.tool 2>/dev/null || echo "$RESULT"
echo ""

# Wait for session to fully initialize
sleep 5

# Step 2: Check if proxy is working (check IP)
echo "--- STEP 2: Verify proxy (navigate to IP check) ---"
RESULT=$(curl -s -X POST "$BASE/sessions/linkedin-test-fix-0406/navigate" \
  -H "Content-Type: application/json" \
  -H "x-api-key: $APIKEY" \
  -d '{"url": "https://api.ipify.org?format=json"}')
echo "$RESULT" | python3 -m json.tool 2>/dev/null || echo "$RESULT"
echo ""

sleep 3

# Step 3: Get page content to see IP
echo "--- STEP 3: Get IP from page ---"
RESULT=$(curl -s -X POST "$BASE/sessions/linkedin-test-fix-0406/evaluate" \
  -H "Content-Type: application/json" \
  -H "x-api-key: $APIKEY" \
  -d '{"expression": "document.body.innerText"}' 2>/dev/null)
echo "IP result: $RESULT"
echo ""

# Step 4: Navigate to LinkedIn
echo "--- STEP 4: Navigate to linkedin.com ---"
RESULT=$(curl -s -X POST "$BASE/sessions/linkedin-test-fix-0406/navigate" \
  -H "Content-Type: application/json" \
  -H "x-api-key: $APIKEY" \
  -d '{"url": "https://www.linkedin.com/"}')
echo "$RESULT" | python3 -m json.tool 2>/dev/null || echo "$RESULT"
echo ""

sleep 5

# Step 5: Check final URL and title
echo "--- STEP 5: Check page state ---"
RESULT=$(curl -s "$BASE/sessions/linkedin-test-fix-0406" \
  -H "x-api-key: $APIKEY")
echo "$RESULT" | python3 -m json.tool 2>/dev/null || echo "$RESULT"
echo ""

# Step 6: Navigate to feed
echo "--- STEP 6: Navigate to linkedin.com/feed/ ---"
RESULT=$(curl -s -X POST "$BASE/sessions/linkedin-test-fix-0406/navigate" \
  -H "Content-Type: application/json" \
  -H "x-api-key: $APIKEY" \
  -d '{"url": "https://www.linkedin.com/feed/"}')
echo "$RESULT" | python3 -m json.tool 2>/dev/null || echo "$RESULT"
echo ""

sleep 5

# Step 7: Final check
echo "--- STEP 7: Final page state ---"
RESULT=$(curl -s "$BASE/sessions/linkedin-test-fix-0406" \
  -H "x-api-key: $APIKEY")
echo "$RESULT" | python3 -m json.tool 2>/dev/null || echo "$RESULT"
echo ""

# Step 8: Check rate limit status
echo "--- STEP 8: Rate limit status ---"
RESULT=$(curl -s "$BASE/proactive-rate-limits/linkedin.com" \
  -H "x-api-key: $APIKEY" 2>/dev/null)
echo "$RESULT" | python3 -m json.tool 2>/dev/null || echo "$RESULT"
echo ""

# Cleanup
echo "--- CLEANUP: Delete test session ---"
curl -s -X DELETE "$BASE/sessions/linkedin-test-fix-0406" \
  -H "x-api-key: $APIKEY" | python3 -m json.tool 2>/dev/null
echo ""

echo "=== TEST COMPLETE ==="
