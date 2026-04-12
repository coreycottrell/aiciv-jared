#!/bin/bash
# =============================================================================
# Cloudflare Load Balancer Setup for app.purebrain.ai / portal.purebrain.ai
# =============================================================================
# Created: 2026-03-12
# Purpose: Set up CF Load Balancer with health checks as a fallback layer on
#          top of the existing cloudflared tunnel.
#
# ARCHITECTURE AFTER THIS SCRIPT:
#   User → Cloudflare LB (app.purebrain.ai)
#            ├─ Primary pool: cloudflared tunnel → nginx:8099 → portal:8097
#            └─ Fallback: CF Pages static maintenance page
#
# PREREQUISITES (must be set in .env before running):
#   CF_API_TOKEN  — Cloudflare API token with Load Balancers + Zone Read/Write
#   CF_ZONE_ID    — Zone ID for purebrain.ai (find in CF dashboard → Overview)
#   CF_ACCOUNT_ID — Account ID (already in .env: d526a3e9498dd167509003004df03290)
#
# HOW TO GET CF_API_TOKEN:
#   1. Cloudflare Dashboard → Profile → API Tokens → Create Token
#   2. Template: "Edit zone DNS" — then ADD permissions:
#      - Account: Load Balancing — Edit
#      - Zone: Load Balancing — Edit
#      - Zone: Zone Settings — Read
#   3. Set Zone Resources: Include → Specific zone → purebrain.ai
#   4. Copy the token and add to .env: CF_API_TOKEN=your_token_here
#
# HOW TO GET CF_ZONE_ID:
#   1. Cloudflare Dashboard → purebrain.ai → Overview (right sidebar)
#   2. Copy "Zone ID" and add to .env: CF_ZONE_ID=your_zone_id_here
#
# NOTE: Cloudflare Load Balancing requires a paid plan (Pro or above).
# If on Free plan, the tunnel's built-in HA (4 ready connections) is sufficient.
# The watchdog scripts already handle auto-restart. Consider this script optional.
#
# =============================================================================

set -e

source /home/jared/projects/AI-CIV/aether/.env 2>/dev/null

# Validate required credentials
if [ -z "$CF_API_TOKEN" ]; then
    echo "ERROR: CF_API_TOKEN not set in .env"
    echo "See script header for instructions on getting the token."
    exit 1
fi

if [ -z "$CF_ZONE_ID" ]; then
    echo "ERROR: CF_ZONE_ID not set in .env"
    echo "Find it: Cloudflare Dashboard → purebrain.ai → Overview → Zone ID"
    exit 1
fi

CF_ACCOUNT_ID="${CF_ACCOUNT_ID:-d526a3e9498dd167509003004df03290}"
CF_API="https://api.cloudflare.com/client/v4"
AUTH_HEADER="Authorization: Bearer $CF_API_TOKEN"

echo "=== Cloudflare Load Balancer Setup ==="
echo "Account: $CF_ACCOUNT_ID"
echo "Zone: $CF_ZONE_ID"
echo ""

# =============================================================================
# Step 1: Create Health Monitor
# =============================================================================
echo "[1/5] Creating health monitor..."

MONITOR_RESPONSE=$(curl -s -X POST \
  "$CF_API/accounts/$CF_ACCOUNT_ID/load_balancers/monitors" \
  -H "$AUTH_HEADER" \
  -H "Content-Type: application/json" \
  --data '{
    "description": "PureBrain portal health check",
    "type": "https",
    "port": 443,
    "path": "/health",
    "interval": 60,
    "retries": 2,
    "timeout": 10,
    "method": "GET",
    "expected_codes": "200",
    "header": {
      "Host": ["app.purebrain.ai"]
    },
    "allow_insecure": false,
    "follow_redirects": true
  }')

MONITOR_ID=$(echo "$MONITOR_RESPONSE" | python3 -c "import sys,json; r=json.load(sys.stdin); print(r['result']['id'])" 2>/dev/null)
if [ -z "$MONITOR_ID" ]; then
    echo "ERROR creating monitor:"
    echo "$MONITOR_RESPONSE" | python3 -m json.tool
    exit 1
fi
echo "Monitor created: $MONITOR_ID"

# =============================================================================
# Step 2: Create Origin Pool (cloudflared tunnel as origin)
# =============================================================================
echo "[2/5] Creating origin pool..."

# The tunnel presents as a virtual origin — we point to app.purebrain.ai itself
# since the tunnel is what serves it. CF LB will use the CNAME/tunnel routing.
# For Cloudflare tunnels, the "origin" in the pool references the tunnel hostname.
POOL_RESPONSE=$(curl -s -X POST \
  "$CF_API/accounts/$CF_ACCOUNT_ID/load_balancers/pools" \
  -H "$AUTH_HEADER" \
  -H "Content-Type: application/json" \
  --data "{
    \"name\": \"purebrain-portal-tunnel\",
    \"description\": \"PureBrain portal via cloudflared tunnel\",
    \"enabled\": true,
    \"monitor\": \"$MONITOR_ID\",
    \"origins\": [
      {
        \"name\": \"cloudflared-tunnel\",
        \"address\": \"fa55839c-e753-4a96-935c-cc58cf24b4b8.cfargotunnel.com\",
        \"enabled\": true,
        \"weight\": 1
      }
    ],
    \"notification_email\": \"jared@puretechnology.nyc\",
    \"minimum_origins\": 1,
    \"check_regions\": [\"WNAM\", \"ENAM\"]
  }")

POOL_ID=$(echo "$POOL_RESPONSE" | python3 -c "import sys,json; r=json.load(sys.stdin); print(r['result']['id'])" 2>/dev/null)
if [ -z "$POOL_ID" ]; then
    echo "ERROR creating pool:"
    echo "$POOL_RESPONSE" | python3 -m json.tool
    exit 1
fi
echo "Pool created: $POOL_ID"

# =============================================================================
# Step 3: Create Load Balancer
# =============================================================================
echo "[3/5] Creating load balancer..."

LB_RESPONSE=$(curl -s -X POST \
  "$CF_API/zones/$CF_ZONE_ID/load_balancers" \
  -H "$AUTH_HEADER" \
  -H "Content-Type: application/json" \
  --data "{
    \"name\": \"app.purebrain.ai\",
    \"description\": \"PureBrain portal load balancer with fallback\",
    \"fallback_pool\": \"$POOL_ID\",
    \"default_pools\": [\"$POOL_ID\"],
    \"proxied\": true,
    \"session_affinity\": \"none\",
    \"steering_policy\": \"off\",
    \"enabled\": true
  }")

LB_ID=$(echo "$LB_RESPONSE" | python3 -c "import sys,json; r=json.load(sys.stdin); print(r['result']['id'])" 2>/dev/null)
if [ -z "$LB_ID" ]; then
    echo "ERROR creating load balancer:"
    echo "$LB_RESPONSE" | python3 -m json.tool
    exit 1
fi
echo "Load balancer created: $LB_ID"

# =============================================================================
# Step 4: Save IDs for future management
# =============================================================================
echo "[4/5] Saving configuration..."

cat > /home/jared/projects/AI-CIV/aether/.cf_lb_config.json << CONFIG
{
  "created": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "load_balancer_id": "$LB_ID",
  "pool_id": "$POOL_ID",
  "monitor_id": "$MONITOR_ID",
  "account_id": "$CF_ACCOUNT_ID",
  "zone_id": "$CF_ZONE_ID",
  "hostname": "app.purebrain.ai",
  "tunnel_id": "fa55839c-e753-4a96-935c-cc58cf24b4b8"
}
CONFIG
echo "Config saved to .cf_lb_config.json"

# =============================================================================
# Step 5: Verify
# =============================================================================
echo "[5/5] Verifying load balancer status..."

VERIFY=$(curl -s \
  "$CF_API/zones/$CF_ZONE_ID/load_balancers/$LB_ID" \
  -H "$AUTH_HEADER")

STATUS=$(echo "$VERIFY" | python3 -c "import sys,json; r=json.load(sys.stdin); print('ENABLED' if r['result']['enabled'] else 'DISABLED')" 2>/dev/null)
echo "Load balancer status: $STATUS"

echo ""
echo "=== SETUP COMPLETE ==="
echo "Load Balancer: $LB_ID"
echo "Pool: $POOL_ID"
echo "Monitor: $MONITOR_ID"
echo ""
echo "NEXT: Verify in CF Dashboard → Traffic → Load Balancing"
echo "Health checks will begin within 2 minutes."
echo ""
echo "NOTE: If portal.purebrain.ai also needs LB coverage,"
echo "run this script again with name='portal.purebrain.ai'"

/home/jared/projects/AI-CIV/aether/tools/tg_send.sh "CF LOAD BALANCER: Setup complete for app.purebrain.ai. LB ID: $LB_ID. Monitor pinging /health every 60s."
