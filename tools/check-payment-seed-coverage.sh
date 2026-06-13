#!/bin/bash
# ============================================================
# PAYMENT -> SEED COVERAGE CROSS-CHECK
# Confirms every payment got a welcome email / seed pipeline run.
#
# Created: 2026-06-13
#
# THE JOIN PROBLEM (why this tool exists):
#   logs/purebrain_payments.jsonl  is keyed by orderId (I-xxx) and carries
#       a `payerEmail` field.
#   logs/seed_sent_uuids.json      is a flat list keyed by SESSION UUID.
#   --> orderId and UUID do NOT join. You cannot prove a payment got a seed
#       by intersecting those two files.
#
#   The reliable join is the PAYER EMAIL, which appears in
#   logs/agentmail_monitor.log on success lines:
#       "Welcome email sent to <email>"
#       "Magic link pipeline complete for UUID=email:<email>"   (email-keyed runs)
#   This script checks, for each payment's payerEmail, whether such a
#   success line exists.
#
# LIMITATIONS (be honest):
#   * EMAIL-LEVEL JOIN ONLY. If the same email made multiple payments, we
#     cannot distinguish them -- one welcome line "covers" all of that
#     email's payments. So a repeat customer with one welcome will show as
#     covered even if a later payment was never seeded. Treat multi-payment
#     emails as "needs manual confirmation," not "proven covered."
#   * It proves a welcome/pipeline line was LOGGED, not that the customer
#     received & opened it. Delivery is a separate concern.
#   * Magic-link lines keyed by a raw UUID (not email:) cannot be matched
#     back to an email here -- only "Welcome email sent to <email>" and
#     "...UUID=email:<email>" lines count as evidence.
#   * Case-insensitive email match; emails are compared verbatim otherwise.
#   * LOG WINDOW: agentmail_monitor.log only goes back so far (it gets
#     rotated/truncated). Payments older than the first line in the monitor
#     log CANNOT have evidence here even if they were seeded fine at the
#     time. This script reports how many "missing" payments predate the log
#     window so they are not mistaken for fresh P0s. Genuine P0 = a RECENT
#     payment (inside the log window) with no welcome line.
#   * Obvious test/sandbox emails (sb-*@personal.example.com,
#     *@aether-test*.invalid, *.example.com) are real records in the log but
#     are not paying customers -- they are tagged [test] in the output.
#
# EXIT CODES:
#   0  = every payment's payerEmail has welcome/seed evidence
#   1  = at least one payment lacks evidence (potential P0)
# ============================================================

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PAYMENTS="$ROOT/logs/purebrain_payments.jsonl"
MONITOR="$ROOT/logs/agentmail_monitor.log"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'

if [ ! -f "$PAYMENTS" ]; then
    echo -e "${RED}ERROR${NC} payments log not found: $PAYMENTS"
    exit 1
fi
if [ ! -f "$MONITOR" ]; then
    echo -e "${RED}ERROR${NC} agentmail monitor log not found: $MONITOR"
    exit 1
fi

echo "=============================================="
echo "  PAYMENT -> SEED COVERAGE CROSS-CHECK"
echo "  $(date)"
echo "=============================================="
echo ""

# Build a lowercase set of emails that have welcome/seed evidence.
# Sources:
#   "Welcome email sent to <email>"
#   "Magic link pipeline complete for UUID=email:<email>"
EVIDENCE=$(mktemp)
trap 'rm -f "$EVIDENCE"' EXIT
{
    grep -oE 'Welcome email sent to [^ (]+@[^ (]+' "$MONITOR" 2>/dev/null \
        | sed -E 's/.*Welcome email sent to //'
    grep -oE 'UUID=email:[^ ]+@[^ ]+' "$MONITOR" 2>/dev/null \
        | sed -E 's/.*UUID=email://'
} | tr '[:upper:]' '[:lower:]' | sed -E 's/[.,;:]+$//' | sort -u > "$EVIDENCE"

# First timestamp present in the monitor log == start of the evidence window.
# Anything paid before this cannot have evidence here regardless of seeding.
LOG_WINDOW_START=$(grep -oE '^[0-9]{4}-[0-9]{2}-[0-9]{2}' "$MONITOR" 2>/dev/null | head -1)
echo "Evidence log window starts: ${LOG_WINDOW_START:-unknown} (payments before this can't be confirmed here)"
echo ""

# Unique payer emails from the payments log (jq tolerates trailing junk lines).
# Track per email: payment count AND the LATEST payment date (YYYY-MM-DD), so
# we can tell whether a missing email is recent (real P0) or pre-window.
declare -A PAY_COUNT
declare -A PAY_LATEST
while IFS=$'\t' read -r email ts; do
    [ -z "$email" ] && continue
    el=$(echo "$email" | tr '[:upper:]' '[:lower:]')
    PAY_COUNT["$el"]=$(( ${PAY_COUNT["$el"]:-0} + 1 ))
    day="${ts:0:10}"
    if [ -z "${PAY_LATEST[$el]}" ] || [[ "$day" > "${PAY_LATEST[$el]}" ]]; then
        PAY_LATEST["$el"]="$day"
    fi
done < <(jq -r 'select(.payerEmail != null and .payerEmail != "") | [.payerEmail, (.server_timestamp // "")] | @tsv' "$PAYMENTS" 2>/dev/null)

TOTAL_PAYMENTS=$(jq -r 'select(.payerEmail != null and .payerEmail != "") | .payerEmail' "$PAYMENTS" 2>/dev/null | wc -l | tr -d ' ')
UNIQUE_EMAILS=${#PAY_COUNT[@]}

is_test_email() {
    case "$1" in
        sb-*@personal.example.com|*@aether-test*.invalid|*@*.example.com|*@*.invalid) return 0 ;;
        *) return 1 ;;
    esac
}

COVERED=0
MISSING_RECENT=0     # potential genuine P0 (inside log window, real-looking email)
MISSING_OTHER=0      # pre-window or test -- not actionable P0s
MISSING_RECENT_LIST=()
MISSING_OTHER_LIST=()
MULTI_LIST=()

for email in "${!PAY_COUNT[@]}"; do
    n=${PAY_COUNT[$email]}
    latest=${PAY_LATEST[$email]}
    if grep -qxF "$email" "$EVIDENCE"; then
        COVERED=$((COVERED + 1))
        if [ "$n" -gt 1 ]; then
            MULTI_LIST+=("$email ($n payments, 1+ welcome -- manual confirm later payments)")
        fi
    else
        # Classify the miss.
        tag=""
        recent=1
        if is_test_email "$email"; then
            tag="[test]"; recent=0
        elif [ -n "$LOG_WINDOW_START" ] && [ -n "$latest" ] && [[ "$latest" < "$LOG_WINDOW_START" ]]; then
            tag="[pre-window: last paid $latest]"; recent=0
        fi
        if [ "$recent" -eq 1 ]; then
            MISSING_RECENT=$((MISSING_RECENT + 1))
            MISSING_RECENT_LIST+=("$email ($n payment(s), last $latest -- NO welcome/seed evidence)")
        else
            MISSING_OTHER=$((MISSING_OTHER + 1))
            MISSING_OTHER_LIST+=("$email ($n payment(s)) $tag")
        fi
    fi
done

echo "Total payment records (with payerEmail): $TOTAL_PAYMENTS"
echo "Unique payer emails:                     $UNIQUE_EMAILS"
echo -e "Emails WITH welcome/seed evidence:       ${GREEN}$COVERED${NC}"
echo -e "Recent emails WITHOUT evidence (P0):     $([ "$MISSING_RECENT" -gt 0 ] && echo -e "${RED}$MISSING_RECENT${NC}" || echo -e "${GREEN}0${NC}")"
echo -e "Pre-window / test misses (not P0):       ${YELLOW}$MISSING_OTHER${NC}"
echo ""

if [ "${#MULTI_LIST[@]}" -gt 0 ]; then
    echo -e "${YELLOW}NOTE -- multi-payment emails (email-join can't distinguish each payment):${NC}"
    for m in "${MULTI_LIST[@]}"; do
        echo "  - $m"
    done
    echo ""
fi

if [ "${#MISSING_OTHER_LIST[@]}" -gt 0 ]; then
    echo -e "${YELLOW}Not actionable (predate log window or test/sandbox emails):${NC}"
    for m in "${MISSING_OTHER_LIST[@]}"; do
        echo "  - $m"
    done
    echo ""
fi

if [ "$MISSING_RECENT" -gt 0 ]; then
    echo -e "${RED}POTENTIAL P0 -- RECENT payments (in log window) with NO welcome/seed evidence:${NC}"
    for m in "${MISSING_RECENT_LIST[@]}"; do
        echo -e "  ${RED}!${NC} $m"
    done
    echo ""
    echo "=============================================="
    echo -e "  ${RED}COVERAGE GAP: $MISSING_RECENT recent payment(s) need manual seed verification${NC}"
    echo "=============================================="
    exit 1
else
    echo "=============================================="
    echo -e "  ${GREEN}No recent coverage gaps -- all in-window payer emails have welcome/seed evidence${NC}"
    if [ "$MISSING_OTHER" -gt 0 ]; then
        echo -e "  ${YELLOW}($MISSING_OTHER older/test record(s) unverifiable here -- see above)${NC}"
    fi
    echo "=============================================="
    exit 0
fi
