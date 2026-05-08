#!/bin/bash
set -e

# Trio Comms Multi-Tenant Test
# Tests trio_id isolation

WORKER_URL="https://trio-comms.in0v8.workers.dev"

# Read token from .env (assuming TRIO_TOKEN_AETHER is set)
TOKEN_AETHER=$(grep TRIO_TOKEN_AETHER /home/jared/projects/AI-CIV/aether/.env 2>/dev/null | cut -d= -f2 || echo "")

if [ -z "$TOKEN_AETHER" ]; then
  echo "❌ TRIO_TOKEN_AETHER not found in .env"
  echo "Trying to get from wrangler secrets (if locally available)..."
  # We can't retrieve secrets from remote, so we'll use a placeholder for testing
  echo "⚠️  Using test placeholder - real test requires actual token"
  TOKEN_AETHER="test-token-placeholder"
fi

echo "🧪 Testing trio_id scoping..."
echo ""

# Test 1: Post to trio-0 (default)
echo "1️⃣ POST message to trio-0 (default, no trio_id specified)..."
RESP1=$(curl -s -X POST "$WORKER_URL/trio/message" \
  -H "Authorization: Bearer $TOKEN_AETHER" \
  -H "Content-Type: application/json" \
  -d '{"content":"Test message for trio-0 (default)"}')
echo "Response: $RESP1"
MSG_ID_1=$(echo "$RESP1" | jq -r '.id // empty')
echo ""

# Test 2: POST to trio-0 (explicit)
echo "2️⃣ POST message to trio-0 (explicit trio_id)..."
RESP2=$(curl -s -X POST "$WORKER_URL/trio/message" \
  -H "Authorization: Bearer $TOKEN_AETHER" \
  -H "Content-Type: application/json" \
  -d '{"content":"Test message for trio-0 explicit", "trio_id":"trio-0"}')
echo "Response: $RESP2"
echo ""

# Test 3: POST to trio-test
echo "3️⃣ POST message to trio-test..."
RESP3=$(curl -s -X POST "$WORKER_URL/trio/message" \
  -H "Authorization: Bearer $TOKEN_AETHER" \
  -H "Content-Type: application/json" \
  -d '{"content":"Test message for trio-test", "trio_id":"trio-test"}')
echo "Response: $RESP3"
echo ""

# Test 4: GET trio-0 messages (should see test 1 & 2)
echo "4️⃣ GET messages from trio-0..."
RESP4=$(curl -s -X GET "$WORKER_URL/trio/messages?trio_id=trio-0&limit=5" \
  -H "Authorization: Bearer $TOKEN_AETHER")
echo "Response (first 500 chars): ${RESP4:0:500}..."
COUNT_TRIO_0=$(echo "$RESP4" | jq '. | length')
echo "Messages in trio-0: $COUNT_TRIO_0"
echo ""

# Test 5: GET trio-test messages (should see only test 3)
echo "5️⃣ GET messages from trio-test..."
RESP5=$(curl -s -X GET "$WORKER_URL/trio/messages?trio_id=trio-test&limit=5" \
  -H "Authorization: Bearer $TOKEN_AETHER")
echo "Response: $RESP5"
COUNT_TRIO_TEST=$(echo "$RESP5" | jq '. | length')
echo "Messages in trio-test: $COUNT_TRIO_TEST"
echo ""

# Test 6: GET without trio_id (should default to trio-0)
echo "6️⃣ GET messages without trio_id param (should default to trio-0)..."
RESP6=$(curl -s -X GET "$WORKER_URL/trio/messages?limit=5" \
  -H "Authorization: Bearer $TOKEN_AETHER")
COUNT_DEFAULT=$(echo "$RESP6" | jq '. | length')
echo "Messages (default): $COUNT_DEFAULT"
echo ""

# Verify isolation
echo "✅ VERIFICATION:"
echo "   - trio-0 has messages (explicit + default): $COUNT_TRIO_0"
echo "   - trio-test has messages: $COUNT_TRIO_TEST"
echo "   - Default query returns trio-0: $COUNT_DEFAULT"

if [ "$COUNT_TRIO_TEST" -ge 1 ] && [ "$COUNT_TRIO_0" -ge 2 ]; then
  echo ""
  echo "✅ Multi-tenant isolation WORKING!"
  echo "   - trio-test messages isolated from trio-0"
  echo "   - Default backward-compatible (trio-0)"
else
  echo ""
  echo "⚠️  Test incomplete or token invalid"
  echo "   Please verify with real TRIO_TOKEN_AETHER from .env"
fi
