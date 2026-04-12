#!/bin/bash
# =============================================================================
# boop_runner.sh - Single BOOP Executor
# Aether AI Collective - Autonomous BOOP System
#
# Usage: boop_runner.sh <boop-name>
# Example: boop_runner.sh telegram-health-boop
#
# Launches a mini Claude Code session for one BOOP task, logs output,
# updates last_run in state file, sends result summary to Telegram.
# =============================================================================

set -euo pipefail

BOOP_NAME="${1:-}"

if [[ -z "$BOOP_NAME" ]]; then
    echo "ERROR: BOOP name required. Usage: boop_runner.sh <boop-name>" >&2
    exit 1
fi

CIV_ROOT="/home/jared/projects/AI-CIV/aether"
LOG_DIR="$CIV_ROOT/logs/boops"
STATE_FILE="$CIV_ROOT/.claude/scheduled-tasks-state.json"
TELEGRAM_CONFIG="$CIV_ROOT/config/telegram_config.json"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="$LOG_DIR/${BOOP_NAME}-${TIMESTAMP}.log"

# Ensure log dir exists
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
# Read BOOP config from state file
# =============================================================================
BOOP_DATA=$(python3 -c "
import json, sys
try:
    state = json.load(open('$STATE_FILE'))
    task = state['tasks'].get('$BOOP_NAME')
    if not task:
        print('ERROR: BOOP not found')
        sys.exit(1)
    print(json.dumps(task))
except Exception as e:
    print(f'ERROR: {e}')
    sys.exit(1)
" 2>&1)

if echo "$BOOP_DATA" | grep -q "^ERROR"; then
    echo "[$TIMESTAMP] ERROR: $BOOP_DATA" | tee -a "$LOG_FILE"
    send_telegram "[BOOP ERROR] $BOOP_NAME: $BOOP_DATA"
    exit 1
fi

DESCRIPTION=$(echo "$BOOP_DATA" | python3 -c "import json,sys; print(json.load(sys.stdin).get('description', '$BOOP_NAME'))")
AGENT=$(echo "$BOOP_DATA" | python3 -c "import json,sys; print(json.load(sys.stdin).get('agent', 'unknown-agent'))")
CATEGORY=$(echo "$BOOP_DATA" | python3 -c "import json,sys; print(json.load(sys.stdin).get('category', ''))")

echo "[$TIMESTAMP] Starting BOOP: $BOOP_NAME" | tee -a "$LOG_FILE"
echo "[$TIMESTAMP] Agent: $AGENT | Category: $CATEGORY" | tee -a "$LOG_FILE"
echo "[$TIMESTAMP] Description: $DESCRIPTION" | tee -a "$LOG_FILE"
echo "[$TIMESTAMP] ---" | tee -a "$LOG_FILE"

# =============================================================================
# Build the prompt for the mini Claude Code session
# =============================================================================
PROMPT="You are the ${AGENT} agent running an autonomous BOOP task.

BOOP NAME: ${BOOP_NAME}
CATEGORY: ${CATEGORY}
DESCRIPTION: ${DESCRIPTION}

WORKING DIRECTORY: ${CIV_ROOT}

INSTRUCTIONS:
1. Execute this scheduled task fully and concisely
2. Use only what tools you need
3. Be brief - max 10 turns
4. At the end, output a line starting with 'RESULT:' followed by 1-2 sentences summarizing what was done

This is an autonomous background session. No human is watching. Do the work and finish cleanly."

# =============================================================================
# Run mini Claude Code session
# =============================================================================
START_TIME=$(date +%s)

# Unset CLAUDECODE so this is not treated as a nested session
unset CLAUDECODE

set +e
claude --print \
    -p "$PROMPT" \
    --allowedTools "Bash,Read,Write,Grep,Glob,WebFetch,WebSearch" \
    --max-turns 10 \
    2>&1 | tee -a "$LOG_FILE"
EXIT_CODE=${PIPESTATUS[0]}
set -e

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

echo "" | tee -a "$LOG_FILE"
echo "[$TIMESTAMP] BOOP completed in ${DURATION}s with exit code: $EXIT_CODE" | tee -a "$LOG_FILE"

# =============================================================================
# Update last_run in state file
# =============================================================================
python3 -c "
import json
from datetime import datetime, timezone
state_file = '$STATE_FILE'
try:
    state = json.load(open(state_file))
    state['tasks']['$BOOP_NAME']['last_run'] = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    with open(state_file, 'w') as f:
        json.dump(state, f, indent=2)
    print('last_run updated')
except Exception as e:
    print(f'WARNING: Could not update last_run: {e}')
" | tee -a "$LOG_FILE" || true

# =============================================================================
# Extract RESULT line and send Telegram summary
# =============================================================================
RESULT_LINE=$(grep "^RESULT:" "$LOG_FILE" | tail -1 | sed 's/^RESULT: *//' || echo "Task completed")

if [[ $EXIT_CODE -eq 0 ]]; then
    STATUS_EMOJI="OK"
    send_telegram "[BOOP] ${BOOP_NAME} done (${DURATION}s)
${RESULT_LINE}"
else
    STATUS_EMOJI="FAILED"
    send_telegram "[BOOP FAILED] ${BOOP_NAME} (exit ${EXIT_CODE}, ${DURATION}s)
Check: $LOG_FILE"
fi

echo "[$TIMESTAMP] Telegram notified. Status: $STATUS_EMOJI" | tee -a "$LOG_FILE"
exit $EXIT_CODE
