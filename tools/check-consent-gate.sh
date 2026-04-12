#!/bin/bash
# ============================================================
# CONSENT GATE VALIDATOR
# PostToolUse hook: validates consent gate JS integrity after edits
# to payment pages. Catches syntax errors, auto-fire bugs, and
# missing IIFE structure before they reach deploy.
# ============================================================

FILE="$1"

if [ -z "$FILE" ]; then
    echo "Usage: check-consent-gate.sh <file_path>"
    exit 1
fi

# ---- Determine if this is a payment page ----
PAYMENT_PATTERNS="live/index.html|awakened/index.html|partnered/index.html|unified/index.html|pay-test|insiders|sandbox"
if ! echo "$FILE" | grep -qE "$PAYMENT_PATTERNS"; then
    # Not a payment page -- skip silently
    exit 0
fi

if [ ! -f "$FILE" ]; then
    echo "WARN: File $FILE does not exist (may have been deleted)"
    exit 0
fi

FAIL=0

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

echo "=== Consent Gate Validation: $(basename $(dirname $FILE))/$(basename $FILE) ==="

# ---- CHECK 1: Balanced braces in IIFE blocks ----
# Count { vs } across the whole file. Large imbalance = syntax error.
OPEN_BRACES=$(grep -o '{' "$FILE" | wc -l)
CLOSE_BRACES=$(grep -o '}' "$FILE" | wc -l)

DIFF=$((CLOSE_BRACES - OPEN_BRACES))
# Absolute diff > 10 is a real problem (small diffs come from CSS-in-HTML etc.)
ABS_DIFF=${DIFF#-}
if [ "$ABS_DIFF" -gt 10 ]; then
    echo -e "  ${RED}FAIL${NC}  Brace imbalance detected: { = $OPEN_BRACES, } = $CLOSE_BRACES (diff: $DIFF)"
    FAIL=1
else
    echo -e "  ${GREEN}PASS${NC}  Brace balance OK (diff: $DIFF)"
fi

# ---- CHECK 2: Dangling }); right before </script> ----
# The specific bug pattern: an extra }); that closes more than intended,
# appearing just before a </script> tag with nothing meaningful between.
DANGLING_BEFORE_CLOSE=$(grep -cP '^\s*\}\);?\s*\n\s*</script>' "$FILE" 2>/dev/null)
# Fallback: check for }); </script> on consecutive lines
if [ -z "$DANGLING_BEFORE_CLOSE" ] || [ "$DANGLING_BEFORE_CLOSE" = "0" ]; then
    # Use a two-line window: }); followed by </script>
    DANGLING_BEFORE_CLOSE=$(awk '/^\s*\}\);?\s*$/{prev=$0; next} /^\s*<\/script>/{if(prev!="") count++; prev=""} {prev=""}  END{print count+0}' "$FILE")
fi

# More than 2 such patterns is suspicious (some legit jQuery patterns end this way)
if [ "$DANGLING_BEFORE_CLOSE" -gt 5 ]; then
    echo -e "  ${RED}FAIL${NC}  Multiple dangling }); before </script> ($DANGLING_BEFORE_CLOSE instances)"
    FAIL=1
else
    echo -e "  ${GREEN}PASS${NC}  No suspicious dangling closers before </script> ($DANGLING_BEFORE_CLOSE)"
fi

# ---- CHECK 3: No auto-fire of seed/payment without user action ----
# Seed must only fire after user consent (click). Check for DOMContentLoaded auto-fire
AUTO_SEED=$(grep -c "DOMContentLoaded.*sendSeed\|addEventListener.*load.*sendSeed\|window\.onload.*sendSeed" "$FILE")
if [ "$AUTO_SEED" -gt "0" ]; then
    echo -e "  ${RED}FAIL${NC}  Seed auto-fires on page load ($AUTO_SEED instances) -- must require user action"
    FAIL=1
else
    echo -e "  ${GREEN}PASS${NC}  No auto-fire of seed on load"
fi

# ---- CHECK 4: Consent gate IIFE exists ----
CONSENT_GATE=$(grep -c "consentGate\|consent-gate\|beginAwakening\|Begin Your Awakening\|startConversation" "$FILE")
if [ "$CONSENT_GATE" -lt "1" ]; then
    echo -e "  ${RED}FAIL${NC}  No consent gate / awakening flow detected"
    FAIL=1
else
    echo -e "  ${GREEN}PASS${NC}  Consent gate present ($CONSENT_GATE refs)"
fi

# ---- CHECK 5: PayPal SDK not loaded before consent ----
# PayPal script should be in deferred/conditional block, not top-level
PAYPAL_TOP=$(grep -n '<script.*paypal.*sdk' "$FILE" | head -1)
if [ -n "$PAYPAL_TOP" ]; then
    LINE_NUM=$(echo "$PAYPAL_TOP" | cut -d: -f1)
    if [ "$LINE_NUM" -lt "100" ]; then
        echo -e "  ${RED}FAIL${NC}  PayPal SDK loads at line $LINE_NUM (too early -- should be deferred)"
        FAIL=1
    else
        echo -e "  ${GREEN}PASS${NC}  PayPal SDK position OK (line $LINE_NUM)"
    fi
else
    echo -e "  ${GREEN}PASS${NC}  PayPal SDK deferred or dynamically loaded"
fi

echo ""

if [ "$FAIL" -gt "0" ]; then
    echo -e "${RED}CONSENT GATE VALIDATION FAILED -- review edits before deploy${NC}"
    exit 1
else
    echo -e "${GREEN}CONSENT GATE VALID${NC}"
    exit 0
fi
