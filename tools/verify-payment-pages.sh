#!/bin/bash
# ============================================================
# CONSTITUTIONAL LIVE PAYMENT-PAGE VERIFICATION GATE
# This is how Pure Technology gets paid. Run nightly + before deploy.
#
# Updated: 2026-06-13 -- REWRITTEN to verify LIVE URLs, not local files.
#   WHY: Canonical source moved to puretechnyc/purebrain-site GitHub repo.
#        The old exports/cf-pages-deploy tree is DEAD, so the old
#        file-based checks printed "SKIP (file not found)" for every page
#        and exited 1 ("DO NOT DEPLOY") every night -- crying wolf while
#        the LIVE site was perfectly healthy. This version checks reality.
#
# WHAT IT CHECKS (per live page):
#   - HTTP 200 via GET  (CF Pages 404s on HEAD, so we MUST use GET)
#   - Correct pricing string(s) present for that page
#       Awakened $297 / Partnered $597 / Unified $1,097 / Insiders $74.50
#   - NO banned/legacy plan IDs (P-3VH*, P-43A*, P-2SA*)
#
# EXIT CODES:
#   0  = all pages 200 + pricing correct + no banned IDs (safe)
#   1  = a REAL failure: non-200, missing expected price, or banned ID
# ============================================================

BASE="${1:-https://purebrain.ai}"
BASE="${BASE%/}"   # strip trailing slash

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'

# Banned/legacy PayPal plan-ID prefixes that must NEVER appear on live pages.
BANNED_REGEX='P-3VH[A-Z0-9]*|P-43A[A-Z0-9]*|P-2SA[A-Z0-9]*'

# Pages to verify. Format: "path|expected_price_regex"
#   - path is appended to BASE (empty = homepage)
#   - expected_price_regex: a grep -E pattern the live HTML MUST contain.
#     Use "-" to skip the pricing check (e.g. /thank-you/ shows no price).
# NOTE: tier pages only render their OWN price (plus the homepage, which
#       renders all three). These expectations were verified against the
#       live site on 2026-06-13 -- do NOT demand all prices on every page.
PAGES=(
    "|\\\$297"                         # homepage shows all tiers; require at least $297
    "awakened|\\\$297"
    "partnered|\\\$597"
    "unified|\\\$1,?097"
    "insiders|\\\$74\\.50"
    "thank-you|-"                      # transactional page, no price string
)

FAIL=0
TOTAL=0
PASSED=0

echo "=============================================="
echo "  LIVE PAYMENT-PAGE VERIFICATION"
echo "  base: $BASE"
echo "  $(date)"
echo "=============================================="
echo ""

TMP=$(mktemp)
trap 'rm -f "$TMP"' EXIT

for entry in "${PAGES[@]}"; do
    path="${entry%%|*}"
    price_re="${entry##*|}"

    if [ -z "$path" ]; then
        url="$BASE/"
        label="homepage ($BASE/)"
    else
        url="$BASE/$path/"
        label="/$path/"
    fi

    echo "--- $label ---"
    page_fail=0

    # GET (NOT HEAD) -- CF Pages returns 404 on HEAD. Capture body + status.
    code=$(curl -s -L --max-time 30 -o "$TMP" -w "%{http_code}" "$url")

    # 1. HTTP 200
    TOTAL=$((TOTAL + 1))
    if [ "$code" = "200" ]; then
        echo -e "  ${GREEN}PASS${NC}  HTTP 200"
        PASSED=$((PASSED + 1))
    else
        echo -e "  ${RED}FAIL${NC}  HTTP $code (expected 200)"
        page_fail=1
        # If the fetch failed, skip content checks for this page -- they'd be noise.
        FAIL=$((FAIL + 1))
        echo ""
        continue
    fi

    # 2. Expected pricing string present
    TOTAL=$((TOTAL + 1))
    if [ "$price_re" = "-" ]; then
        echo -e "  ${GREEN}PASS${NC}  Pricing check N/A for this page"
        PASSED=$((PASSED + 1))
    else
        if grep -qE "$price_re" "$TMP" 2>/dev/null; then
            found=$(grep -oE '\$(297|597|1,?097|74\.50)' "$TMP" 2>/dev/null | sort -u | tr '\n' ' ')
            echo -e "  ${GREEN}PASS${NC}  Pricing present (found: ${found})"
            PASSED=$((PASSED + 1))
        else
            echo -e "  ${RED}FAIL${NC}  Expected price pattern '$price_re' NOT found"
            page_fail=1
        fi
    fi

    # 3. No banned/legacy plan IDs
    TOTAL=$((TOTAL + 1))
    banned_hits=$(grep -oE "$BANNED_REGEX" "$TMP" 2>/dev/null | sort -u | tr '\n' ' ')
    if [ -n "$banned_hits" ]; then
        echo -e "  ${RED}FAIL${NC}  BANNED plan ID(s) present: ${banned_hits}"
        page_fail=1
    else
        echo -e "  ${GREEN}PASS${NC}  No banned plan IDs (P-3VH/P-43A/P-2SA)"
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
    echo -e "  ${RED}$FAIL page(s) have REAL FAILURES -- investigate before deploy${NC}"
    echo "=============================================="
    exit 1
else
    echo -e "  ${GREEN}ALL LIVE PAGES HEALTHY -- pricing correct, no banned IDs${NC}"
    echo "=============================================="
    exit 0
fi
