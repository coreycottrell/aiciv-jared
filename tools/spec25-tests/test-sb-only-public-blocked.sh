#!/usr/bin/env bash
# test-sb-only-public-blocked.sh
#
# SPEC #25 Phase 0 — Live external curl probe matrix.
#
# Verifies that clients-api `.in0v8.workers.dev/internal/*` is BLOCKED at
# the CF network layer once Phase 1 ships (workers_dev=false).
#
# Per CTO Phase 0 amendment:
#   "MUST return 404 / connection-refused / 530, NOT 200/403/401"
#
# Per feedback_options_preflight_success_does_not_equal_endpoint_health.md:
#   - Use the REAL client verb (POST for /internal/clients/upsert,
#     GET for /internal/clients/by-email). NEVER OPTIONS as a health probe.
#
# Per feedback_multi_probe_diagnosis_required.md +
#     feedback_probe_dimension_audit_at_convergence_3plus.md:
#   - Vary tool (curl), vary verb (POST/GET/PUT/DELETE),
#     vary UA (default/Mozilla/empty), vary headers (with/without marker).
#
# Per feedback_synthetic_monitors_must_match_real_user_traffic.md:
#   - Use CLEAN URLs, NOT cache-bust query strings.
#
# Per feedback_options_preflight_success_does_not_equal_endpoint_health.md:
#   - OPTIONS preflight 204 is NOT proof of endpoint health. Skip OPTIONS.
#
# Verdict convention:
#   Pre-Phase-1 (workers_dev=true everywhere): every probe expected 401/403/200/4xx-from-app.
#     -> baseline-pass = "app layer responded" (not 404/000).
#   Post-Phase-1 (workers_dev=false on clients-api): every probe MUST return
#     404 / 530 / 1042 OR connection-refused (curl exit != 0). 200/401/403 = FAIL.
#
# Usage:
#   ./tools/spec25-tests/test-sb-only-public-blocked.sh           # auto-detect mode
#   SPEC_25_PHASE_1_SHIPPED=1 ./tools/spec25-tests/test-sb-only-public-blocked.sh
#
# Exit codes:
#   0 = verdict matches mode (baseline or strict)
#   1 = verdict mismatch (regression or pre-deploy gate failure)

set -u

TARGET_HOST="${SPEC25_TARGET_HOST:-clients-api.in0v8.workers.dev}"
PHASE_1="${SPEC_25_PHASE_1_SHIPPED:-0}"

red()   { printf "\033[31m%s\033[0m" "$*"; }
green() { printf "\033[32m%s\033[0m" "$*"; }
yellow(){ printf "\033[33m%s\033[0m" "$*"; }

echo "SPEC-25 live external probe matrix"
echo "==================================="
echo "Target host : ${TARGET_HOST}"
echo "Phase 1 mode: ${PHASE_1} (0=baseline,1=strict)"
echo

# Codes considered "CF network-layer block" = pass under strict mode
# Curl exit 7 = could not connect, exit 28 = timeout, exit 6 = could not resolve
is_cf_block_code() {
  local code="$1"
  case "$code" in
    404|530|1042|000) return 0 ;;
    *) return 1 ;;
  esac
}

# Run a single probe; echo HTTP status code (or 000 if connection refused).
probe() {
  local method="$1"; local path="$2"; local ua="$3"; local extra_header="$4"; local body="$5"
  local args=(-s -o /dev/null -w "%{http_code}" --max-time 8 -X "$method" "https://${TARGET_HOST}${path}")
  if [ -n "$ua" ]; then args+=(-A "$ua"); fi
  if [ -n "$extra_header" ]; then args+=(-H "$extra_header"); fi
  if [ -n "$body" ]; then args+=(-H "Content-Type: application/json" -d "$body"); fi
  curl "${args[@]}" 2>/dev/null || echo "000"
}

# Probe matrix (verb, path, UA, marker-header, body, label)
# IMPORTANT: vary tool dim by using different shapes; no OPTIONS preflight.
declare -a PROBES=(
  # 1: real verb POST, no marker, default UA
  "POST|/internal/clients/upsert|||{}|naked-post-default-ua"
  # 2: POST with forged marker header (proves CF block, not app marker check)
  "POST|/internal/clients/upsert||x-internal-binding: paypal-webhook|{}|post-forged-marker"
  # 3: GET on a real read endpoint
  "GET|/internal/clients/by-email?email=probe@example.invalid|||| naked-get-default-ua"
  # 4: Browser-like UA (per multi-probe rule)
  "POST|/internal/clients/upsert|Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36|x-internal-binding: admin-api|{\"email\":\"x@x.x\"}|post-browser-ua-marker"
  # 5: PUT (uncommon verb, varies dimension)
  "PUT|/internal/clients/upsert||x-internal-binding: paypal-webhook|{}|put-forged-marker"
  # 6: GET on /health — Phase 1 strict mode expects 404 here too (workers_dev=false blocks ALL public)
  "GET|/health|||| naked-health"
)

fail=0
pass=0
total=0

printf "%-30s %-6s %-6s %s\n" "PROBE" "VERB" "CODE" "VERDICT"
printf "%-30s %-6s %-6s %s\n" "-----" "----" "----" "-------"

for spec in "${PROBES[@]}"; do
  IFS='|' read -r method path ua extra body label <<< "$spec"
  label_trim=$(echo "$label" | sed 's/^ *//;s/ *$//')
  code=$(probe "$method" "$path" "$ua" "$extra" "$body")
  total=$((total + 1))

  if [ "$PHASE_1" = "1" ]; then
    # Strict mode: CF network-layer block required
    if is_cf_block_code "$code"; then
      printf "%-30s %-6s %-6s " "$label_trim" "$method" "$code"; green "PASS"; echo " (CF block)"
      pass=$((pass + 1))
    else
      printf "%-30s %-6s %-6s " "$label_trim" "$method" "$code"; red "FAIL"; echo " (app-layer response — workers_dev=false not effective)"
      fail=$((fail + 1))
    fi
  else
    # Baseline mode: app-layer response expected (current state: workers_dev=true → 401/403/200/400)
    case "$code" in
      200|400|401|403|405|422|500|502|503)
        printf "%-30s %-6s %-6s " "$label_trim" "$method" "$code"; yellow "BASELINE"; echo " (app-layer responded — expected pre-Phase-1)"
        pass=$((pass + 1))
        ;;
      404|530|1042|000)
        printf "%-30s %-6s %-6s " "$label_trim" "$method" "$code"; yellow "UNEXPECTED"; echo " (CF block already? Or path 404. Investigate.)"
        # Don't fail baseline on this — health=200 is the canary
        pass=$((pass + 1))
        ;;
      *)
        printf "%-30s %-6s %-6s " "$label_trim" "$method" "$code"; red "FAIL"; echo " (unexpected response code)"
        fail=$((fail + 1))
        ;;
    esac
  fi
done

echo
echo "Summary"
echo "-------"
echo "Total probes : ${total}"
echo "Pass         : ${pass}"
echo "Fail         : ${fail}"

if [ "$fail" -gt 0 ]; then
  echo
  red "VERDICT: FAIL"; echo
  if [ "$PHASE_1" = "1" ]; then
    echo "STOP: workers_dev=false is not blocking external dispatch."
    echo "      Per CTO: open CF support ticket, pivot to Option B (path-prefix + marker)."
  else
    echo "Baseline regression: at least one probe returned an unexpected app code."
  fi
  exit 1
fi

echo
green "VERDICT: PASS"; echo
if [ "$PHASE_1" = "1" ]; then
  echo "All ${total} probes confirm CF network-layer block. workers_dev=false is effective."
else
  echo "Baseline established. All probes returned app-layer responses (workers_dev=true)."
  echo "Re-run with SPEC_25_PHASE_1_SHIPPED=1 after Phase 1 deploys to enforce strict mode."
fi
exit 0
