#!/usr/bin/env bash
#
# voice_tts_wedge_cron.sh — recurring scheduler wrapper around tools/voice_tts_wedge_check.py
#
# WHAT THIS IS (and is NOT):
#   This is a thin DETECTION + ALERT wrapper. It runs the CANONICAL, CORRECT wedge
#   detector (tools/voice_tts_wedge_check.py, committed 703a950) and reacts to its
#   EXIT CODE only. It never inspects raw processing counts, never applies any
#   per-job-duration alarm threshold of its own, and never restarts anything
#   (restart contract is DEAD + Jared-gated). All wedge logic lives in the detector.
#
#   Detector exit codes (do not change these here, only react to them):
#     0 = HEALTHY / HEALTHY_IDLE / UNKNOWN   -> log only
#     1 = endpoint unreachable               -> log only (transient blip, do NOT page)
#     2 = REAL WEDGE                         -> log + Telegram alert to Jared
#
# SCHEDULING NOTE:
#   The detector's full two-poll check blocks ~MAX_JOB_TIME (default 900s / 15 min) by
#   design (it gives the slow serial GPU box a full per-job window to advance the head).
#   Cron fires this every 20 min; flock -n prevents pileup if a run runs long.
#
# SMOKE TEST (no 15-min wait): VOICE_WEDGE_POLL_GAP=5 ./tools/voice_tts_wedge_cron.sh
#
set -uo pipefail

AETHER_ROOT="/home/jared/projects/AI-CIV/aether"
DETECTOR="tools/voice_tts_wedge_check.py"
PYTHON="/usr/bin/python3"
LOG_FILE="${AETHER_ROOT}/logs/voice-tts-wedge.log"
LOCK_FILE="/tmp/voice_tts_wedge.lock"
TG_CONFIG="${AETHER_ROOT}/config/telegram_config.json"
TG_CHAT_ID="548906264"   # Jared

mkdir -p "${AETHER_ROOT}/logs"

log_line() {
    # one-line timestamped (UTC) message to the log file
    printf '%s %s\n' "$(date -u '+%Y-%m-%dT%H:%M:%SZ')" "$1" >> "${LOG_FILE}"
}

send_telegram_alert() {
    # $1 = reason string from the detector JSON
    local reason="$1"

    if [ ! -f "${TG_CONFIG}" ]; then
        log_line "[ALERT-SKIP] telegram_config.json missing at ${TG_CONFIG} — wedge detected but cannot page Jared."
        return 0
    fi

    local token
    token=$("${PYTHON}" -c "import json,sys; print(json.load(open('${TG_CONFIG}'))['bot_token'])" 2>/dev/null)
    if [ -z "${token}" ]; then
        log_line "[ALERT-SKIP] could not read bot_token from ${TG_CONFIG} — wedge detected but cannot page Jared."
        return 0
    fi

    local text
    text="<b>REAL TTS WEDGE on voice.purebrain.ai</b>%0A%0AThe serial GPU TTS worker queue-head is NOT advancing across a full per-job window.%0A%0A<b>Reason:</b> ${reason}%0A%0ADetection + alert only — NO auto-restart (restart is Jared-gated)."

    local http_code
    http_code=$(curl -s -o /dev/null -w '%{http_code}' \
        "https://api.telegram.org/bot${token}/sendMessage" \
        --data-urlencode "chat_id=${TG_CHAT_ID}" \
        --data-urlencode "text=${text}" \
        -d "parse_mode=HTML" \
        -d "disable_web_page_preview=true" 2>/dev/null)

    if [ "${http_code}" = "200" ]; then
        log_line "[ALERT-SENT] Telegram wedge alert delivered to chat ${TG_CHAT_ID} (HTTP 200)."
    else
        log_line "[ALERT-FAIL] Telegram send returned HTTP ${http_code:-000}."
    fi
}

run_check() {
    cd "${AETHER_ROOT}" || { log_line "[ERROR] cannot cd to ${AETHER_ROOT}"; return 1; }

    local out rc
    out=$("${PYTHON}" "${DETECTOR}" --json 2>&1)
    rc=$?

    # Collapse the JSON to a single line for the log entry.
    local json_oneline
    json_oneline=$(printf '%s' "${out}" | tr '\n' ' ' | tr -s ' ')

    # Pull the reason field for the alert (best-effort; falls back to whole output).
    local reason
    reason=$(printf '%s' "${out}" | "${PYTHON}" -c \
        "import json,sys
try:
    d=json.load(sys.stdin); print(d.get('reason',''))
except Exception:
    pass" 2>/dev/null)
    [ -z "${reason}" ] && reason="(no reason field) ${json_oneline}"

    case "${rc}" in
        2)
            log_line "[WEDGE exit=2] ${json_oneline}"
            send_telegram_alert "${reason}"
            ;;
        1)
            # Unreachable = transient network blip. Log, do NOT page Jared.
            log_line "[UNREACHABLE exit=1 — no alert] ${json_oneline}"
            ;;
        0)
            log_line "[OK exit=0] ${json_oneline}"
            ;;
        *)
            log_line "[UNEXPECTED exit=${rc}] ${json_oneline}"
            ;;
    esac
}

# flock -n: if a previous (long) run still holds the lock, skip this cycle quietly.
exec 9>"${LOCK_FILE}"
if ! flock -n 9; then
    log_line "[SKIP] previous run still holding ${LOCK_FILE} — skipping this cycle (no pileup)."
    exit 0
fi

run_check
