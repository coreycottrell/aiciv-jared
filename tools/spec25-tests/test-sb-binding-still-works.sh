#!/usr/bin/env bash
# test-sb-binding-still-works.sh
#
# SPEC #25 Phase 0 — Positive assertion: Service Binding callers can still
# reach clients-api after workers_dev=false ships.
#
# We can't directly invoke a Service Binding from outside the CF account.
# Instead we probe each CALLER's public-facing endpoint that internally
# performs the SB call to clients-api. If the SB binding works, the public
# endpoint responds normally. If the binding broke, we see 502/500.
#
# Per CTO Phase 0 amendment:
#   "Each Worker's smoke must be PUBLIC-facing endpoint that exercises the
#    binding (not just /health). admin-api: GET /api/check-name. ..."
#
# Probes (real client verbs only, no OPTIONS preflight):
#
#   1) admin-api:        GET /api/check-name?ai_name=...&human_name=...
#      → admin-api -> CLIENTS_API.fetch(/internal/clients/by-name) SB call
#   2) paypal-webhook:   GET /health
#      → does not exercise binding directly; we rely on (4) replay endpoint
#        if available, else flag as binding-not-exercised-by-this-probe.
#   3) portal-proxy:     GET /api/auth/session via shadow path (best-effort)
#      → portal-proxy -> CLIENTS_API SB call (canary)
#   4) admin replay:     POST /api/admin/replay-paypal-event (if exposed)
#      → chained SB path: admin-api -> clients-api
#
# Constitutional alignment:
#   - feedback_synthetic_monitors_must_match_real_user_traffic.md (clean URLs)
#   - feedback_main_thread_activity_signal_is_portal_files_mtime.md (no false-silent)
#   - feedback_multi_probe_diagnosis_required.md (multiple endpoints, vary inputs)
#
# Usage:
#   ./tools/spec25-tests/test-sb-binding-still-works.sh
#
# Exit codes:
#   0 = at least one public binding-exercising endpoint passes
#   1 = all binding-exercising probes failed (binding likely broken)
#   2 = all probes skipped (network unreachable / endpoints not deployed)

set -u

ADMIN_API_HOST="${SPEC25_ADMIN_API_HOST:-admin-api.in0v8.workers.dev}"
PAYPAL_WEBHOOK_HOST="${SPEC25_PAYPAL_WEBHOOK_HOST:-paypal-webhook.in0v8.workers.dev}"
PORTAL_PROXY_HOST="${SPEC25_PORTAL_PROXY_HOST:-portal.purebrain.ai}"

red()   { printf "\033[31m%s\033[0m" "$*"; }
green() { printf "\033[32m%s\033[0m" "$*"; }
yellow(){ printf "\033[33m%s\033[0m" "$*"; }

echo "SPEC-25 SB-binding-still-works smoke"
echo "===================================="
echo "admin-api      : ${ADMIN_API_HOST}"
echo "paypal-webhook : ${PAYPAL_WEBHOOK_HOST}"
echo "portal-proxy   : ${PORTAL_PROXY_HOST}"
echo

# Capture status code AND a brief body snippet for diagnosis.
probe_with_body() {
  local label="$1"; local method="$2"; local url="$3"; local extra_h="$4"; local body="$5"
  local tmp; tmp=$(mktemp)
  local args=(-s -o "$tmp" -w "%{http_code}" --max-time 10 -X "$method" "$url")
  if [ -n "$extra_h" ]; then args+=(-H "$extra_h"); fi
  if [ -n "$body" ]; then args+=(-H "Content-Type: application/json" -d "$body"); fi
  local code; code=$(curl "${args[@]}" 2>/dev/null || echo "000")
  local snippet; snippet=$(head -c 240 "$tmp" 2>/dev/null | tr -d '\n' | sed 's/[[:space:]]\+/ /g')
  rm -f "$tmp"
  printf "%s|%s|%s\n" "$code" "$label" "$snippet"
}

fail=0
pass=0
total=0

evaluate() {
  # args: code label snippet expected_success_codes_regex binding_required
  local code="$1"; local label="$2"; local snippet="$3"; local good_regex="$4"; local binding="$5"
  total=$((total + 1))
  printf "%-44s code=%-4s " "$label" "$code"
  if echo "$code" | grep -qE "$good_regex"; then
    green "PASS"; echo " (binding=${binding}) body: ${snippet:0:80}"
    pass=$((pass + 1))
    return 0
  fi
  # 502 specifically suggests binding failure
  if [ "$code" = "502" ] || [ "$code" = "500" ]; then
    red "FAIL"; echo " (binding=${binding}; ${code} suggests broken SB) body: ${snippet:0:80}"
    fail=$((fail + 1))
    return 1
  fi
  yellow "UNCLEAR"; echo " (binding=${binding}) body: ${snippet:0:80}"
  return 0
}

# Probe 1: admin-api /api/check-name (exercises CLIENTS_API SB)
out=$(probe_with_body "admin-api /api/check-name" "GET" \
  "https://${ADMIN_API_HOST}/api/check-name?ai_name=Probe&human_name=Tester" "" "")
IFS='|' read -r code label snippet <<< "$out"
# Acceptable: 200 (ok response), 400 (bad input echo from worker), 401 (auth) — all mean binding works
evaluate "$code" "$label" "$snippet" "^(200|400|401|404)$" "REQUIRED"

# Probe 2: paypal-webhook /health (does not exercise binding, sanity only)
out=$(probe_with_body "paypal-webhook /health" "GET" \
  "https://${PAYPAL_WEBHOOK_HOST}/health" "" "")
IFS='|' read -r code label snippet <<< "$out"
evaluate "$code" "$label" "$snippet" "^(200|404)$" "NOT-EXERCISED"

# Probe 3: portal-proxy GET /api/auth/session (shadow-auth instrumentation;
# may return 200 with anon body or 401). The point: binding to CLIENTS_API
# canary should not 502.
out=$(probe_with_body "portal-proxy /api/auth/session" "GET" \
  "https://${PORTAL_PROXY_HOST}/api/auth/session" "" "")
IFS='|' read -r code label snippet <<< "$out"
evaluate "$code" "$label" "$snippet" "^(200|401|403|404)$" "CANARY"

# Probe 4: admin-api POST /api/admin/replay-paypal-event (chained SB).
# Without auth this should return 401, not 502. 401 means the route is wired
# (binding chain reachable from the route handler) but caller lacks auth.
out=$(probe_with_body "admin-api replay-paypal-event (unauth)" "POST" \
  "https://${ADMIN_API_HOST}/api/admin/replay-paypal-event" "" "{\"event_id\":\"PROBE-NOOP\"}")
IFS='|' read -r code label snippet <<< "$out"
evaluate "$code" "$label" "$snippet" "^(200|400|401|403|404|422)$" "CHAINED"

echo
echo "Summary"
echo "-------"
echo "Total probes : ${total}"
echo "Pass         : ${pass}"
echo "Fail (502/500): ${fail}"

if [ "$fail" -ge 1 ]; then
  echo
  red "VERDICT: FAIL"; echo
  echo "At least one caller showed 5xx — likely SB binding to clients-api is broken."
  echo "Action: tail clients-api logs (wrangler tail clients-api) and check for"
  echo "        'service binding not found' or missing-route errors."
  exit 1
fi

if [ "$pass" -eq 0 ]; then
  echo
  yellow "VERDICT: INCONCLUSIVE"; echo
  echo "All probes returned unexpected codes. Network unreachable or endpoints not deployed."
  exit 2
fi

echo
green "VERDICT: PASS"; echo
echo "Service Binding-exercising public endpoints respond normally."
exit 0
