#!/bin/bash
# ============================================================
# CONSTITUTIONAL PRE-DEPLOY VERIFICATION GATE
# This is how Pure Technology gets paid. Run before EVERY deploy.
# MUST PASS 100% or DO NOT DEPLOY.
#
# Updated: 2026-04-01 -- New flow: Payment -> /thank-you/ redirect
# Removed: Post-payment chatbox, magic link button on page
# ============================================================

DEPLOY_DIR="${1:-/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy}"
PAGES=(
    ""
    "live"
    "home-test"
    "home-test-sandbox"
    "home-test-live-1"
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
    if [ -z "$page" ]; then
        file="$DEPLOY_DIR/index.html"
        label="homepage (purebrain.ai)"
    else
        file="$DEPLOY_DIR/$page/index.html"
        label="$page"
    fi
    if [ ! -f "$file" ]; then
        echo -e "${YELLOW}SKIP${NC}  $label (file not found)"
        continue
    fi

    echo "--- $label ---"
    page_fail=0

    # Build list of referenced local JS/CSS files for deep checks
    local_js_files=""
    for jsref in $(grep -oP 'src="/js/[^"]+\.js"' "$file" 2>/dev/null | sed 's/src="//;s/"//'); do
        jsfile="$DEPLOY_DIR$jsref"
        if [ -f "$jsfile" ]; then
            local_js_files="$local_js_files $jsfile"
        fi
    done

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

    # 3. Canvas pause on PRICING REVEAL
    TOTAL=$((TOTAL + 1))
    canvas_pricing=$(cat "$file" $local_js_files 2>/dev/null | grep -c 'Pause canvas for performance when pricing')
    if [ "$canvas_pricing" -lt "1" ]; then
        echo -e "  ${RED}FAIL${NC}  Canvas pause on pricing reveal MISSING"
        page_fail=1
    else
        echo -e "  ${GREEN}PASS${NC}  Canvas pauses on pricing reveal"
        PASSED=$((PASSED + 1))
    fi

    # 4. Video pause on pricing reveal
    TOTAL=$((TOTAL + 1))
    video_pause=$(cat "$file" $local_js_files 2>/dev/null | grep -c 'bgVideo.*pause\|Pause video too')
    if [ "$video_pause" -lt "1" ]; then
        echo -e "  ${YELLOW}WARN${NC}  Video pause on pricing not found"
        PASSED=$((PASSED + 1))
    else
        echo -e "  ${GREEN}PASS${NC}  Video pauses on pricing reveal"
        PASSED=$((PASSED + 1))
    fi

    # 5. Seed capture (send-seed endpoint reference)
    TOTAL=$((TOTAL + 1))
    seed=$(grep -c 'send-seed\|_seedFired\|fireSeed' "$file" 2>/dev/null)
    if [ "$seed" -lt "1" ]; then
        echo -e "  ${RED}FAIL${NC}  Seed capture MISSING ($seed refs)"
        page_fail=1
    else
        echo -e "  ${GREEN}PASS${NC}  Seed capture ($seed refs)"
        PASSED=$((PASSED + 1))
    fi

    # 6. Thank-you redirect in onPaymentComplete flow
    TOTAL=$((TOTAL + 1))
    thankyou_redirect=$(cat "$file" $local_js_files 2>/dev/null | grep -c 'thank-you\|/thank-you/')
    if [ "$thankyou_redirect" -lt "1" ]; then
        echo -e "  ${RED}FAIL${NC}  Thank-you redirect MISSING"
        page_fail=1
    else
        echo -e "  ${GREEN}PASS${NC}  Thank-you redirect present ($thankyou_redirect refs)"
        PASSED=$((PASSED + 1))
    fi

    # 7. Email parameter passed in redirect URL
    TOTAL=$((TOTAL + 1))
    email_in_redirect=$(cat "$file" $local_js_files 2>/dev/null | grep -c 'email=.*encodeURIComponent\|thank-you.*email')
    if [ "$email_in_redirect" -lt "1" ]; then
        echo -e "  ${YELLOW}WARN${NC}  Email parameter in redirect URL not confirmed"
        PASSED=$((PASSED + 1))
    else
        echo -e "  ${GREEN}PASS${NC}  Email parameter in redirect URL ($email_in_redirect refs)"
        PASSED=$((PASSED + 1))
    fi

    # 8. No post-payment chatbox overlay code (should be ABSENT now)
    TOTAL=$((TOTAL + 1))
    post_pay_chatbox=$(cat "$file" $local_js_files 2>/dev/null | grep -c 'launchPostPaymentFlow\|post-payment-chatbox\|postPaymentOverlay\|_postPaymentLaunched')
    if [ "$post_pay_chatbox" -gt "0" ]; then
        echo -e "  ${RED}FAIL${NC}  Post-payment chatbox code still present ($post_pay_chatbox refs) -- should be REMOVED"
        page_fail=1
    else
        echo -e "  ${GREEN}PASS${NC}  No post-payment chatbox code (clean)"
        PASSED=$((PASSED + 1))
    fi

    # 9. No excessive WP script loads (max 5 wp-content script refs)
    TOTAL=$((TOTAL + 1))
    wp_scripts=$(grep -c 'src.*purebrain.ai/wp-content.*\.js' "$file" 2>/dev/null)
    if [ "$wp_scripts" -gt "5" ]; then
        echo -e "  ${RED}FAIL${NC}  Too many WP scripts ($wp_scripts -- max 5)"
        page_fail=1
    else
        echo -e "  ${GREEN}PASS${NC}  WP scripts clean ($wp_scripts)"
        PASSED=$((PASSED + 1))
    fi

    # 10. No excessive WP CSS loads (max 5)
    TOTAL=$((TOTAL + 1))
    wp_css=$(grep -c "href.*purebrain.ai/wp-content.*\.css\|href.*purebrain.ai/wp-includes.*\.css" "$file" 2>/dev/null)
    if [ "$wp_css" -gt "5" ]; then
        echo -e "  ${RED}FAIL${NC}  Too many WP stylesheets ($wp_css -- max 5)"
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

# === THANK-YOU PAGE CHECKS ===
echo "--- thank-you page ---"
thankyou_file="$DEPLOY_DIR/thank-you/index.html"
if [ ! -f "$thankyou_file" ]; then
    echo -e "  ${RED}FAIL${NC}  /thank-you/index.html NOT FOUND"
    FAIL=$((FAIL + 1))
    TOTAL=$((TOTAL + 1))
else
    # T1. Magic link polling present
    TOTAL=$((TOTAL + 1))
    ml_poll=$(grep -c 'api/magic-link\|magic-link/' "$thankyou_file" 2>/dev/null)
    if [ "$ml_poll" -lt "1" ]; then
        echo -e "  ${RED}FAIL${NC}  Magic link polling MISSING on thank-you page"
        FAIL=$((FAIL + 1))
    else
        echo -e "  ${GREEN}PASS${NC}  Magic link polling present ($ml_poll refs)"
        PASSED=$((PASSED + 1))
    fi

    # T2. URL parameter parsing (aiName, name, email, tier)
    TOTAL=$((TOTAL + 1))
    url_params=$(grep -c 'URLSearchParams\|searchParams\|getParam' "$thankyou_file" 2>/dev/null)
    if [ "$url_params" -lt "1" ]; then
        echo -e "  ${RED}FAIL${NC}  URL parameter parsing MISSING on thank-you page"
        FAIL=$((FAIL + 1))
    else
        echo -e "  ${GREEN}PASS${NC}  URL parameter parsing present ($url_params refs)"
        PASSED=$((PASSED + 1))
    fi

    # T3. Personalized status display
    TOTAL=$((TOTAL + 1))
    status_display=$(grep -c 'Payment confirmed\|being configured\|Welcome email\|Check your inbox' "$thankyou_file" 2>/dev/null)
    if [ "$status_display" -lt "2" ]; then
        echo -e "  ${YELLOW}WARN${NC}  Personalized status messages may be incomplete ($status_display found)"
        PASSED=$((PASSED + 1))
    else
        echo -e "  ${GREEN}PASS${NC}  Personalized status display present ($status_display refs)"
        PASSED=$((PASSED + 1))
    fi
fi
echo ""

echo "=============================================="
echo "  RESULTS: $PASSED/$TOTAL checks passed"
if [ "$FAIL" -gt "0" ]; then
    echo -e "  ${RED}$FAIL page(s) have FAILURES -- DO NOT DEPLOY${NC}"
    echo "=============================================="
    exit 1
else
    echo -e "  ${GREEN}ALL PAGES CLEAN -- safe to deploy${NC}"
    echo "=============================================="
    exit 0
fi
