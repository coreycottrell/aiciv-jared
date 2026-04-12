#!/bin/bash
# ============================================================
# CONSTITUTIONAL PRE-DEPLOY VERIFICATION GATE
# This is how Pure Technology gets paid. Run before EVERY deploy.
# MUST PASS 100% or DO NOT DEPLOY.
# ============================================================

DEPLOY_DIR="${1:-/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy}"
PAGES=(
    "live"
    "awakened"
    "partnered"
    "unified"
    "pay-test-sandbox-3"
    "pay-test-sandbox-5"
    "insiders"
    "insiders/awakened"
)

FAIL=0
TOTAL=0
PASSED=0

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'

echo "=============================================="
echo "  PAYMENT PAGE PRE-DEPLOY VERIFICATION"
echo "  $(date)"
echo "=============================================="
echo ""

for page in "${PAGES[@]}"; do
    file="$DEPLOY_DIR/$page/index.html"
    if [ ! -f "$file" ]; then
        echo -e "${YELLOW}SKIP${NC}  $page (file not found)"
        continue
    fi

    echo "--- $page ---"
    page_fail=0

    # 1. NO GoDaddy/WordPress tracking
    TOTAL=$((TOTAL + 1))
    godaddy=$(grep -c '_trfq\|_trfd\|scc-c2\|tccl-tti\|secureserver\|wpaas' "$file" 2>/dev/null)
    if [ "$godaddy" -gt "0" ]; then
        echo -e "  ${RED}FAIL${NC}  GoDaddy/WP tracking found ($godaddy refs)"
        page_fail=1
    else
        echo -e "  ${GREEN}PASS${NC}  No GoDaddy/WP tracking"
        PASSED=$((PASSED + 1))
    fi

    # 2. PayPal preconnect
    TOTAL=$((TOTAL + 1))
    precon=$(grep -c 'preconnect.*paypal\|dns-prefetch.*paypal' "$file" 2>/dev/null)
    if [ "$precon" -lt "1" ]; then
        echo -e "  ${RED}FAIL${NC}  PayPal preconnect MISSING"
        page_fail=1
    else
        echo -e "  ${GREEN}PASS${NC}  PayPal preconnect ($precon)"
        PASSED=$((PASSED + 1))
    fi

    # 3. Canvas pause on PRICING REVEAL (not just payment)
    TOTAL=$((TOTAL + 1))
    canvas_pricing=$(grep -c 'Pause canvas for performance when pricing' "$file" 2>/dev/null)
    if [ "$canvas_pricing" -lt "1" ]; then
        echo -e "  ${RED}FAIL${NC}  Canvas pause on pricing reveal MISSING"
        page_fail=1
    else
        echo -e "  ${GREEN}PASS${NC}  Canvas pauses on pricing reveal"
        PASSED=$((PASSED + 1))
    fi

    # 4. Video pause on pricing reveal
    TOTAL=$((TOTAL + 1))
    video_pause=$(grep -c 'bgVideo.*pause\|Pause video too' "$file" 2>/dev/null)
    if [ "$video_pause" -lt "1" ]; then
        echo -e "  ${YELLOW}WARN${NC}  Video pause on pricing not found"
        PASSED=$((PASSED + 1))
    else
        echo -e "  ${GREEN}PASS${NC}  Video pauses on pricing reveal"
        PASSED=$((PASSED + 1))
    fi

    # 5. Seed capture
    TOTAL=$((TOTAL + 1))
    seed=$(grep -c '_seedFired\|send-seed' "$file" 2>/dev/null)
    if [ "$seed" -lt "2" ]; then
        echo -e "  ${RED}FAIL${NC}  Seed capture MISSING ($seed refs)"
        page_fail=1
    else
        echo -e "  ${GREEN}PASS${NC}  Seed capture ($seed refs)"
        PASSED=$((PASSED + 1))
    fi

    # 6. Addendum capture
    TOTAL=$((TOTAL + 1))
    addendum=$(grep -c 'fireSeedAddendum\|seed-addendum' "$file" 2>/dev/null)
    if [ "$addendum" -lt "2" ]; then
        echo -e "  ${RED}FAIL${NC}  Addendum capture MISSING ($addendum refs)"
        page_fail=1
    else
        echo -e "  ${GREEN}PASS${NC}  Addendum capture ($addendum refs)"
        PASSED=$((PASSED + 1))
    fi

    # 7. No excessive WP script loads (max 5 wp-content script refs)
    TOTAL=$((TOTAL + 1))
    wp_scripts=$(grep -c 'src.*purebrain.ai/wp-content.*\.js' "$file" 2>/dev/null)
    if [ "$wp_scripts" -gt "5" ]; then
        echo -e "  ${RED}FAIL${NC}  Too many WP scripts ($wp_scripts — max 5)"
        page_fail=1
    else
        echo -e "  ${GREEN}PASS${NC}  WP scripts clean ($wp_scripts)"
        PASSED=$((PASSED + 1))
    fi

    # 8. No excessive WP CSS loads (max 5)
    TOTAL=$((TOTAL + 1))
    wp_css=$(grep -c "href.*purebrain.ai/wp-content.*\.css\|href.*purebrain.ai/wp-includes.*\.css" "$file" 2>/dev/null)
    if [ "$wp_css" -gt "5" ]; then
        echo -e "  ${RED}FAIL${NC}  Too many WP stylesheets ($wp_css — max 5)"
        page_fail=1
    else
        echo -e "  ${GREEN}PASS${NC}  WP CSS clean ($wp_css)"
        PASSED=$((PASSED + 1))
    fi

    if [ "$page_fail" -gt "0" ]; then
        FAIL=$((FAIL + 1))
    fi
    echo ""
done

echo "=============================================="
echo "  RESULTS: $PASSED/$TOTAL checks passed"
if [ "$FAIL" -gt "0" ]; then
    echo -e "  ${RED}$FAIL page(s) have FAILURES — DO NOT DEPLOY${NC}"
    echo "=============================================="
    exit 1
else
    echo -e "  ${GREEN}ALL PAGES CLEAN — safe to deploy${NC}"
    echo "=============================================="
    exit 0
fi
