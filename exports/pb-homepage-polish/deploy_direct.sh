#!/bin/bash
# Direct deployment of pb-homepage-polish plugin
# Uses WP REST API plugin upload endpoint

WP_URL="https://purebrain.ai"
WP_USER="purebrain@puremarketing.ai"
WP_PASS="41w3 xWWZ 11em UXgj hjAF sx2T"
PLUGIN_DIR="$(dirname "$0")"

echo "=== pb-homepage-polish deployment ==="

# Step 1: Create zip
echo "[1] Creating plugin zip..."
cd "$PLUGIN_DIR" || exit 1
rm -f pb-homepage-polish.zip
mkdir -p tmp-zip/pb-homepage-polish
cp pb-homepage-polish.php tmp-zip/pb-homepage-polish/
cd tmp-zip && zip -r ../pb-homepage-polish.zip pb-homepage-polish/ && cd ..
rm -rf tmp-zip
echo "    Created: $PLUGIN_DIR/pb-homepage-polish.zip"

# Step 2: Check if plugin already exists
echo "[2] Checking plugin status..."
STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
  -u "${WP_USER}:${WP_PASS}" \
  "${WP_URL}/wp-json/wp/v2/plugins/pb-homepage-polish%2Fpb-homepage-polish.php")

echo "    HTTP status: $STATUS"

if [ "$STATUS" = "200" ]; then
    echo "    Plugin exists. Activating..."
    RESULT=$(curl -s -X PUT \
      -u "${WP_USER}:${WP_PASS}" \
      -H "Content-Type: application/json" \
      -d '{"status":"active"}' \
      "${WP_URL}/wp-json/wp/v2/plugins/pb-homepage-polish%2Fpb-homepage-polish.php")
    echo "    Activation result: $RESULT"
else
    echo "    Plugin not found. Uploading..."
    RESULT=$(curl -s -X POST \
      -u "${WP_USER}:${WP_PASS}" \
      -F "file=@${PLUGIN_DIR}/pb-homepage-polish.zip" \
      "${WP_URL}/wp-json/wp/v2/plugins")
    echo "    Upload result: $RESULT"

    # Extract status from result
    PLUGIN_STATUS=$(echo "$RESULT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('status','unknown'))" 2>/dev/null)
    echo "    Plugin status: $PLUGIN_STATUS"

    if [ "$PLUGIN_STATUS" != "active" ]; then
        echo "    Activating plugin..."
        ACTIVATE=$(curl -s -X PUT \
          -u "${WP_USER}:${WP_PASS}" \
          -H "Content-Type: application/json" \
          -d '{"status":"active"}' \
          "${WP_URL}/wp-json/wp/v2/plugins/pb-homepage-polish%2Fpb-homepage-polish.php")
        echo "    Activation: $ACTIVATE"
    fi
fi

echo ""
echo "=== Deployment complete ==="
echo "Verify at: ${WP_URL}"
