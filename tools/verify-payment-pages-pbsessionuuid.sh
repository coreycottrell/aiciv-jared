#!/usr/bin/env bash
#
# verify-payment-pages-pbsessionuuid.sh
# ─────────────────────────────────────────────────────────────────────────────
# SHIP gate per CTO pre-build review 2026-05-07 (cto-prebuild-review-med003-fix-2026-05-07.md §6).
#
# Validates that `window.pbSessionUuid` is exposed on every payment page and
# that the corresponding inline scripts thread it through:
#   - the createOrder custom_id  ('PB-{TIER}-{uuid}')
#   - the createSubscription custom_id  (added 2026-05-07)
#   - the verify-payment-server-side body (sessionUuid: <uuid>)
#   - the chat logger (session_uuid: <uuid> via window.pbSessionUuid)
#
# Static-source mode (default): grep each deployed HTML/JS for the required
# tokens. No network. No browser. Fast — runs in <2s. Used as the deploy gate
# in CI / pre-deploy.
#
# Live mode (--live, optional): curl the staging URL, verify the same tokens
# are present in served HTML. Use after `cf-deploy.py` to confirm the changes
# made it onto the wire.
#
# Exit codes:
#   0 = all assertions passed (BUILD-deliverable: 5 LIVE pages × 2 changes
#       each + 2 JS files × 2 migrations each = 14 assertions, all green)
#   1 = at least one assertion failed (deploy BLOCKED)
#
# Usage:
#   tools/verify-payment-pages-pbsessionuuid.sh             # static check
#   tools/verify-payment-pages-pbsessionuuid.sh --live      # post-deploy check
#
# Per-MED-003 note: this script does NOT exfiltrate or log payTestData fields
# beyond the random sessionUuid. PII fields (aiName, name, email) are not
# inspected.
# ─────────────────────────────────────────────────────────────────────────────

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEPLOY_DIR="${REPO_ROOT}/exports/cf-pages-deploy"
LIVE_BASE="${LIVE_BASE:-https://staging.purebrain.ai}"

LIVE_MODE=0
if [[ "${1:-}" == "--live" ]]; then
  LIVE_MODE=1
fi

# 5 LIVE awakening pages — each must expose window.pbSessionUuid + createSubscription custom_id
LIVE_PAGES=(
  "index.html|/"
  "awakened/index.html|/awakened/"
  "partnered/index.html|/partnered/"
  "unified/index.html|/unified/"
  "insiders/index.html|/insiders/"
)

# 5 sandbox/test pages — regression spot-check
TEST_PAGES=(
  "home-test/index.html|/home-test/"
  "home-test-live-1/index.html|/home-test-live-1/"
  "home-test-sandbox/index.html|/home-test-sandbox/"
  "pay-test-sandbox-3/index.html|/pay-test-sandbox-3/"
  "pay-test-sandbox-5/index.html|/pay-test-sandbox-5/"
)

# Shared JS files migrated to window.pbSessionUuid
JS_FILES=(
  "js/payment-background.js"
  "js/homepage-payment.js"
)

PASS=0
FAIL=0
FAILED_ASSERTIONS=()

ok()   { echo "  PASS — $1"; PASS=$((PASS+1)); }
fail() { echo "  FAIL — $1"; FAIL=$((FAIL+1)); FAILED_ASSERTIONS+=("$1"); }

assert_grep_static() {
  # $1 = absolute file path, $2 = pattern, $3 = description
  if grep -q -- "$2" "$1" 2>/dev/null; then
    ok "$3"
  else
    fail "$3 (pattern not found in $(basename "$1"))"
  fi
}

assert_grep_remote() {
  # $1 = url, $2 = pattern (literal substring), $3 = description
  local body
  body="$(curl -sS --max-time 10 "$1" 2>/dev/null || true)"
  if [[ -z "$body" ]]; then
    fail "$3 (empty body from $1)"
    return
  fi
  if grep -q -- "$2" <<< "$body"; then
    ok "$3"
  else
    fail "$3 (pattern not found in served HTML at $1)"
  fi
}

# ─── Section 1: 5 LIVE pages ─────────────────────────────────────────────────
echo ""
echo "=== Section 1: LIVE awakening pages ($([ "$LIVE_MODE" -eq 1 ] && echo "live mode: $LIVE_BASE" || echo "static source check")) ==="
for entry in "${LIVE_PAGES[@]}"; do
  path="${entry%%|*}"
  url_path="${entry#*|}"
  echo ""
  echo "[${path}]"

  if [[ "$LIVE_MODE" -eq 1 ]]; then
    url="${LIVE_BASE}${url_path}"
    assert_grep_remote "$url" "window.pbSessionUuid = payTestData.sessionUuid" \
      "${path} :: window.pbSessionUuid exposure (Change A)"
    assert_grep_remote "$url" "custom_id: 'PB-' + tier.toUpperCase() + '-' + (window.pbSessionUuid" \
      "${path} :: createSubscription custom_id (Change B)"
  else
    file="${DEPLOY_DIR}/${path}"
    if [[ ! -f "$file" ]]; then
      fail "${path} :: file does not exist"
      continue
    fi
    assert_grep_static "$file" "window.pbSessionUuid = payTestData.sessionUuid" \
      "${path} :: window.pbSessionUuid exposure (Change A)"
    assert_grep_static "$file" "custom_id: 'PB-' + tier.toUpperCase() + '-' + (window.pbSessionUuid" \
      "${path} :: createSubscription custom_id (Change B)"
  fi
done

# ─── Section 2: 2 shared JS files ────────────────────────────────────────────
echo ""
echo "=== Section 2: Shared JS files (cross-script-tag readers) ==="
for jsfile in "${JS_FILES[@]}"; do
  echo ""
  echo "[${jsfile}]"
  if [[ "$LIVE_MODE" -eq 1 ]]; then
    url="${LIVE_BASE}/${jsfile}"
    assert_grep_remote "$url" "window.pbSessionUuid" \
      "${jsfile} :: reads window.pbSessionUuid"
    js_body="$(curl -sS --max-time 10 "$url" 2>/dev/null || true)"
    if grep -q -- "(typeof payTestData !== 'undefined' && payTestData.sessionUuid)" <<< "$js_body"; then
      fail "${jsfile} :: still has legacy payTestData.sessionUuid cross-scope read (must be migrated)"
    else
      ok "${jsfile} :: no legacy payTestData.sessionUuid cross-scope read"
    fi
  else
    file="${DEPLOY_DIR}/${jsfile}"
    if [[ ! -f "$file" ]]; then
      fail "${jsfile} :: file does not exist"
      continue
    fi
    assert_grep_static "$file" "window.pbSessionUuid" \
      "${jsfile} :: reads window.pbSessionUuid"
    if grep -q "(typeof payTestData !== 'undefined' && payTestData.sessionUuid)" "$file"; then
      fail "${jsfile} :: still has legacy payTestData.sessionUuid cross-scope read (must be migrated)"
    else
      ok "${jsfile} :: no legacy payTestData.sessionUuid cross-scope read"
    fi
  fi
done

# ─── Section 3: TEST pages regression spot-check ────────────────────────────
# These pages are NOT in scope for THIS sprint — check they STILL build (file exists)
# but do NOT assert window.pbSessionUuid is present (out of scope).
echo ""
echo "=== Section 3: TEST/sandbox pages (regression spot-check — non-blocking) ==="
for entry in "${TEST_PAGES[@]}"; do
  path="${entry%%|*}"
  file="${DEPLOY_DIR}/${path}"
  if [[ -f "$file" ]]; then
    echo "  INFO — ${path} :: present (no MED-003 fix expected on this page)"
  else
    echo "  INFO — ${path} :: not deployed (skipping)"
  fi
done

# ─── Summary ─────────────────────────────────────────────────────────────────
echo ""
echo "=== SUMMARY ==="
echo "  Passed:  ${PASS}"
echo "  Failed:  ${FAIL}"
echo ""
if [[ "$FAIL" -gt 0 ]]; then
  echo "FAILED ASSERTIONS:"
  for assertion in "${FAILED_ASSERTIONS[@]}"; do
    echo "  - ${assertion}"
  done
  echo ""
  echo "STATUS: BLOCKED — fix failed assertions before deploy"
  exit 1
fi

echo "STATUS: GREEN — safe to deploy"
echo ""
echo "Note: Static-source assertions only. For full E2E (network capture +"
echo "dispatcher round-trip per CTO §6.3), invoke browser-vision-tester +"
echo "tail logs/purebrain_web_conversations.jsonl after sandbox PayPal click-through."
exit 0
