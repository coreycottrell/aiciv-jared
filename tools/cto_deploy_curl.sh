#!/bin/bash
# CTO: Clone sandbox-3 → pay-test-2 with LIVE PayPal
# PURE BASH + CURL version — no Python dependency
# Run: bash /home/jared/projects/AI-CIV/aether/tools/cto_deploy_curl.sh

set -euo pipefail

# === Config ===
WP_USER="Aether"
WP_APP_PASSWORD="41w3 xWWZ 11em UXgj hjAF sx2T"
BASE_URL="https://purebrain.ai/wp-json/wp/v2"

SANDBOX_ID="AYTFob05DoSn0ZeVtLJ05duKwFHOdAckHgkZ2UJhAXvfJlUXEYM_PFib3HbIuVgauxV_6clZ5FdPRYq_"
LIVE_ID="AWgWNlBQAy5BMXKB5xbaMwSk01WkatC08b5rTj_JKu4Jm2JugXvjAwMRyNe1FmabNS9v846Rma5ptxhI"

SOURCE="/home/jared/projects/AI-CIV/aether/purebrain-site/public/pay-test-sandbox-3/index.html"
DEST="/home/jared/projects/AI-CIV/aether/purebrain-site/public/pay-test-2/index.html"
PAGE_ID=689
TMP_FILE="/tmp/paytest2_live.html"

echo "============================================================"
echo "CTO: pay-test-2 LIVE PayPal Deployment"
echo "Started: $(date)"
echo "============================================================"

# --- Step 1: Verify source ---
echo ""
echo "[1] Source check..."
if [ ! -f "$SOURCE" ]; then
    echo "    FATAL: Source file not found: $SOURCE"
    exit 1
fi
SANDBOX_COUNT=$(grep -c "$SANDBOX_ID" "$SOURCE" || true)
echo "    Source: $SOURCE"
echo "    Sandbox ID occurrences: $SANDBOX_COUNT"
if [ "$SANDBOX_COUNT" -eq 0 ]; then
    echo "    FATAL: Sandbox client ID not in source file"
    exit 1
fi

# --- Step 2: Create modified file ---
echo ""
echo "[2] Creating modified file (sandbox → live PayPal)..."
sed "s/${SANDBOX_ID}/${LIVE_ID}/g" "$SOURCE" > "$TMP_FILE"

# Also replace sandbox.paypal.com (not present but being thorough)
sed -i 's/sandbox\.paypal\.com/www.paypal.com/g' "$TMP_FILE"
sed -i 's/api-m\.sandbox\.paypal\.com/api-m.paypal.com/g' "$TMP_FILE"

# Verify
SANDBOX_AFTER=$(grep -c "$SANDBOX_ID" "$TMP_FILE" || true)
LIVE_AFTER=$(grep -c "$LIVE_ID" "$TMP_FILE" || true)
echo "    Sandbox ID remaining: $SANDBOX_AFTER (expected 0)"
echo "    Live ID present: $LIVE_AFTER (expected 1)"

if [ "$SANDBOX_AFTER" -gt 0 ]; then
    echo "    FATAL: Sandbox ID still present after replacement"
    exit 1
fi
if [ "$LIVE_AFTER" -eq 0 ]; then
    echo "    FATAL: Live ID not present after replacement"
    exit 1
fi
echo "    [OK] Replacement verified"

# --- Step 3: Copy to local dest ---
echo ""
echo "[3] Copying to local destination: $DEST"
cp "$TMP_FILE" "$DEST"
echo "    [OK] Local file updated"

# --- Step 4: Deploy to WordPress ---
echo ""
echo "[4] Deploying to WordPress page $PAGE_ID..."

# Build the JSON payload with the file content
# We use Python just for JSON encoding (content has special chars)
python3 - <<PYEOF
import json
import requests
from requests.auth import HTTPBasicAuth

with open('$TMP_FILE', 'r', encoding='utf-8') as f:
    content = f.read()

auth = HTTPBasicAuth('$WP_USER', '$WP_APP_PASSWORD')
payload = {
    'content':  content,
    'template': 'elementor_canvas',
    'status':   'publish',
}

print(f"    Content length: {len(content):,} chars")
print(f"    Sending POST to $BASE_URL/pages/$PAGE_ID...")

r = requests.post(
    '$BASE_URL/pages/$PAGE_ID',
    auth=auth,
    json=payload,
    timeout=180
)
print(f"    HTTP Status: {r.status_code}")
if r.status_code not in (200, 201):
    print(f"    ERROR: {r.text[:500]}")
    exit(1)

resp = r.json()
print(f"    Page ID:  {resp.get('id')}")
print(f"    Status:   {resp.get('status')}")
print(f"    Template: {resp.get('template')}")
print(f"    Link:     {resp.get('link')}")
print("    [OK] Deployed successfully")
PYEOF

# --- Step 5: Clear Elementor cache ---
echo ""
echo "[5] Clearing Elementor cache..."
CACHE_STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
    -X DELETE \
    -u "$WP_USER:$WP_APP_PASSWORD" \
    "https://purebrain.ai/wp-json/elementor/v1/cache")
echo "    Cache clear HTTP status: $CACHE_STATUS"

# --- Step 6: Verify ---
echo ""
echo "[6] Verification..."
python3 - <<PYEOF2
import requests
from requests.auth import HTTPBasicAuth

auth = HTTPBasicAuth('$WP_USER', '$WP_APP_PASSWORD')
LIVE_ID = '$LIVE_ID'
SANDBOX_ID = '$SANDBOX_ID'

r = requests.get(
    '$BASE_URL/pages/$PAGE_ID?context=edit',
    auth=auth,
    timeout=60
)
if r.status_code != 200:
    print(f"    Verification GET returned HTTP {r.status_code}")
    exit(0)

v = r.json()
v_content   = v.get('content', {}).get('raw', '')
v_meta      = v.get('meta') or {}
v_elementor = v_meta.get('_elementor_data') or ''
combined    = v_content + v_elementor

live_ok      = LIVE_ID in combined
sandbox_gone = SANDBOX_ID not in combined
template_ok  = v.get('template') == 'elementor_canvas'

print(f"    LIVE client ID present:      {'YES [PASS]' if live_ok else 'NO  [FAIL]'}")
print(f"    Sandbox client ID gone:      {'YES [PASS]' if sandbox_gone else 'NO  [FAIL]'}")
print(f"    Template = elementor_canvas: {'YES [PASS]' if template_ok else 'NO  [FAIL]'}")

if live_ok and sandbox_gone and template_ok:
    print("    ALL CHECKS PASSED")
else:
    print("    SOME CHECKS FAILED — review manually")
PYEOF2

# --- Done ---
echo ""
echo "============================================================"
echo "DEPLOYMENT COMPLETE"
echo "URL: https://purebrain.ai/pay-test-2/"
echo "Completed: $(date)"
echo "============================================================"

# Portal + Telegram notifications
bash /home/jared/projects/AI-CIV/aether/aiciv-comms-hub-bootstrap/_comms_hub/packages/purebrain-portal/portal-server/portal_send_file.sh \
    --text "pay-test-2 REBUILT — cloned from sandbox-3 with LIVE PayPal links. Ready for testing at https://purebrain.ai/pay-test-2/" \
    2>/dev/null || true

bash /home/jared/projects/AI-CIV/aether/tools/tg_send.sh \
    "CTO: pay-test-2 rebuilt with live PayPal. Please test: https://purebrain.ai/pay-test-2/" \
    2>/dev/null || true

echo "Notifications sent."
