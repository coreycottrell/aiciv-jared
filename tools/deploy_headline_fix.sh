#!/bin/bash
# CTO Deploy: Headline Capitalization Fix
# Date: 2026-03-14

set -e

AETHER="/home/jared/projects/AI-CIV/aether"
cd "$AETHER"

echo "=== CTO: Headline Uppercase Fix Deploy ==="
echo ""

# Step 1: Apply CSS fixes
echo "Step 1: Applying CSS text-transform: uppercase fixes..."
python3 tools/fix_headline_uppercase.py

echo ""

# Step 2: Verify fixes applied
echo "Step 2: Verifying fixes..."

for FILE in \
    "exports/cf-pages-deploy/index.html" \
    "exports/cf-pages-deploy/pay-test-2/index.html" \
    "exports/cf-pages-deploy/pay-test-sandbox-3/index.html"
do
    COUNT=$(grep -c "text-transform: uppercase" "$FILE" || true)
    HEADING_COUNT=$(grep -c "pb-demo-section__heading" "$FILE" | head -1 || echo "0")
    echo "  $FILE:"
    echo "    text-transform: uppercase occurrences: $COUNT"
    # Check no bad gradient override remains
    BAD=$(grep -c "pb-demo-section__heading span" "$FILE" || true)
    if [ "$BAD" -gt 0 ]; then
        echo "    WARNING: span gradient override still present ($BAD)"
    else
        echo "    Brand color span rule: CLEAN (inline styles respected)"
    fi
done

echo ""

# Step 3: Deploy to CF Pages
echo "Step 3: Deploying to Cloudflare Pages..."
CLOUDFLARE_API_TOKEN="HCXgNwiDOla_CbhoIkDAqBWTlTPwKxN5JeKsZJ9_" \
CLOUDFLARE_ACCOUNT_ID="d526a3e9498dd167509003004df03290" \
npx wrangler pages deploy exports/cf-pages-deploy \
    --project-name=purebrain-staging \
    --branch=main

echo ""
echo "=== DEPLOY COMPLETE ==="
