#!/bin/bash
# Synthetic monitor for critical CF Pages paths.
# Cache-busted GET requests; writes alert to inbox/ on non-200.
#
# Created 2026-05-08 after /user-guide/ disappeared for ~46 hours
# (bulk deploy stripped it from manifest; stale CF cache masked the 404).
#
# Cron suggestion: */5 * * * * /home/jared/projects/AI-CIV/aether/tools/synthetic-monitor-critical-pages.sh

set -u

CIV_ROOT="${CIV_ROOT:-/home/jared/projects/AI-CIV/aether}"
LOG_FILE="${CIV_ROOT}/logs/critical-pages-monitor.log"
INBOX_DIR="${CIV_ROOT}/inbox"
HOST="https://purebrain.ai"

mkdir -p "${CIV_ROOT}/logs" "${INBOX_DIR}"

# Critical paths to monitor. Add more here as needed.
PATHS=(
  "/user-guide/"
  "/investment-opportunity/"
  "/blog/"
  "/admin/clients/"
)

NOW_UTC="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

DIVERGENCE_LOG="${CIV_ROOT}/logs/critical-pages-edge-divergence.log"

for path in "${PATHS[@]}"; do
  CB=$(date +%s%N | sha256sum | cut -c1-12)
  CB_URL="${HOST}${path}?_cb=${CB}"
  CLEAN_URL="${HOST}${path}"

  CB_STATUS=$(curl -s -o /dev/null -w "%{http_code}" --max-time 15 "$CB_URL")

  echo "${NOW_UTC} path=${path} cb_status=${CB_STATUS} cb=${CB}" >> "${LOG_FILE}"

  # Cache-bust passed → no further action
  if [[ "${CB_STATUS}" == "200" ]]; then
    continue
  fi

  # Cache-bust failed → paired-probe with clean URL to distinguish real outage
  # from out-of-repo CF edge-config rewrites (Transform Rules / Page Rules / `path/?*` cache-bust traps).
  CLEAN_STATUS=$(curl -s -o /dev/null -w "%{http_code}" --max-time 15 "$CLEAN_URL")

  echo "${NOW_UTC} path=${path} clean_status=${CLEAN_STATUS}" >> "${LOG_FILE}"

  if [[ "${CLEAN_STATUS}" == "200" ]]; then
    # Edge-config divergence: clean=200, cache-bust=non-200. Real users unaffected.
    # Log only — do NOT spam inbox/. Reviewed during weekly edge-config audit.
    echo "${NOW_UTC} EDGE_DIVERGENCE path=${path} cb=${CB_STATUS} clean=${CLEAN_STATUS}" >> "${DIVERGENCE_LOG}"
    continue
  fi

  # Both probes failed → real outage. Alert.
  SAFE_PATH=$(echo "${path}" | sed 's|/|_|g; s|^_||; s|_$||')
  [[ -z "${SAFE_PATH}" ]] && SAFE_PATH="root"
  ALERT_FILE="${INBOX_DIR}/critical-page-monitor-alert-${SAFE_PATH}-$(date -u +%Y%m%dT%H%M%S).md"
  cat > "${ALERT_FILE}" <<EOF
# CRITICAL PAGE MONITOR ALERT (paired-probe confirmed)

**Timestamp**: ${NOW_UTC}
**Path**: ${path}
**Cache-bust URL**: ${CB_URL} → ${CB_STATUS}
**Clean URL**: ${CLEAN_URL} → ${CLEAN_STATUS}
**Expected**: 200 on both

Both probes failed — real user impact confirmed.

## Action

1. Curl the path manually to confirm
2. Check CF Pages deployment manifest for path presence
3. If stripped: redeploy with cf-deploy.py (PROTECTED_PATHS should now block this for user-guide/, investment-opportunity/)
4. Flush CF cache for the path

Source: tools/synthetic-monitor-critical-pages.sh
EOF
  echo "${NOW_UTC} ALERT written: ${ALERT_FILE}" >> "${LOG_FILE}"
done
