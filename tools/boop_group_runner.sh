#!/bin/bash
# =============================================================================
# boop_group_runner.sh - Group BOOP Executor
# Aether AI Collective - Autonomous BOOP System
#
# Usage: boop_group_runner.sh <group-name>
# Example: boop_group_runner.sh 30min
#
# Reads boop_config.json to get all BOOPs for a frequency group,
# then runs them sequentially. Sends ONE consolidated Telegram message.
#
# Called by systemd timer units via:
#   ExecStart=boop_group_runner.sh %i
# =============================================================================

set -euo pipefail

GROUP_NAME="${1:-}"

if [[ -z "$GROUP_NAME" ]]; then
    echo "ERROR: Group name required. Usage: boop_group_runner.sh <group-name>" >&2
    exit 1
fi

CIV_ROOT="/home/jared/projects/AI-CIV/aether"
CONFIG_FILE="$CIV_ROOT/tools/boop_config.json"
TELEGRAM_CONFIG="$CIV_ROOT/config/telegram_config.json"
LOG_DIR="$CIV_ROOT/logs/boops"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
GROUP_LOG="$LOG_DIR/group-${GROUP_NAME}-${TIMESTAMP}.log"

mkdir -p "$LOG_DIR"

# Ensure claude CLI is findable
export PATH="/home/jared/.local/bin:/home/jared/.nvm/versions/node/v22.14.0/bin:/usr/local/bin:/usr/bin:/bin"
export HOME="/home/jared"

# =============================================================================
# Helper: Send Telegram message
# =============================================================================
send_telegram() {
    local message="$1"
    local token chat_id
    token=$(python3 -c "import json; print(json.load(open('$TELEGRAM_CONFIG'))['bot_token'])" 2>/dev/null || echo "")
    chat_id=$(python3 -c "import json; print(json.load(open('$TELEGRAM_CONFIG'))['default_chat_id'])" 2>/dev/null || echo "548906264")

    if [[ -n "$token" ]]; then
        curl -s "https://api.telegram.org/bot${token}/sendMessage" \
            -d "chat_id=${chat_id}" \
            --data-urlencode "text=${message}" \
            -o /dev/null || true
    fi
}

# =============================================================================
# Read BOOPs for this group from config
# =============================================================================
BOOPS_JSON=$(python3 -c "
import json, sys
try:
    config = json.load(open('$CONFIG_FILE'))
    group = config['groups'].get('$GROUP_NAME')
    if not group:
        print('ERROR: Group not found: $GROUP_NAME')
        sys.exit(1)
    print(json.dumps(group['boops']))
except Exception as e:
    print(f'ERROR: {e}')
    sys.exit(1)
" 2>&1)

if echo "$BOOPS_JSON" | grep -q "^ERROR"; then
    echo "[$TIMESTAMP] ERROR: $BOOPS_JSON" | tee -a "$GROUP_LOG"
    send_telegram "[BOOP GROUP ERROR] $GROUP_NAME: $BOOPS_JSON"
    exit 1
fi

BOOP_LIST=$(echo "$BOOPS_JSON" | python3 -c "import json,sys; print(' '.join(json.load(sys.stdin)))")

echo "[$TIMESTAMP] BOOP Group Runner: $GROUP_NAME" | tee -a "$GROUP_LOG"
echo "[$TIMESTAMP] BOOPs to run: $BOOP_LIST" | tee -a "$GROUP_LOG"
echo "[$TIMESTAMP] ==============================================" | tee -a "$GROUP_LOG"

# =============================================================================
# Run each BOOP sequentially, collect results
# =============================================================================
RESULTS=""
PASS_COUNT=0
FAIL_COUNT=0
TOTAL_DURATION=0

for BOOP_NAME in $BOOP_LIST; do
    echo "" | tee -a "$GROUP_LOG"
    echo "[$TIMESTAMP] --- Starting: $BOOP_NAME ---" | tee -a "$GROUP_LOG"

    BOOP_START=$(date +%s)

    set +e
    "$CIV_ROOT/tools/boop_runner.sh" "$BOOP_NAME" >> "$GROUP_LOG" 2>&1
    BOOP_EXIT=$?
    set -e

    BOOP_END=$(date +%s)
    BOOP_DURATION=$((BOOP_END - BOOP_START))
    TOTAL_DURATION=$((TOTAL_DURATION + BOOP_DURATION))

    if [[ $BOOP_EXIT -eq 0 ]]; then
        PASS_COUNT=$((PASS_COUNT + 1))
        STATUS="OK"
    else
        FAIL_COUNT=$((FAIL_COUNT + 1))
        STATUS="FAIL(${BOOP_EXIT})"
    fi

    RESULTS="${RESULTS}  ${STATUS} ${BOOP_NAME} (${BOOP_DURATION}s)\n"
    echo "[$TIMESTAMP] --- Done: $BOOP_NAME | Exit: $BOOP_EXIT | Duration: ${BOOP_DURATION}s ---" | tee -a "$GROUP_LOG"
done

# =============================================================================
# Send consolidated Telegram summary
# =============================================================================
SUMMARY_MSG="[BOOP GROUP] ${GROUP_NAME} complete
Passed: ${PASS_COUNT} | Failed: ${FAIL_COUNT} | Total time: ${TOTAL_DURATION}s

$(echo -e "$RESULTS")"

send_telegram "$SUMMARY_MSG"

echo "" | tee -a "$GROUP_LOG"
echo "[$TIMESTAMP] Group complete. Passed: $PASS_COUNT | Failed: $FAIL_COUNT | Total: ${TOTAL_DURATION}s" | tee -a "$GROUP_LOG"

# Exit non-zero if any BOOP failed
if [[ $FAIL_COUNT -gt 0 ]]; then
    exit 1
fi
exit 0
