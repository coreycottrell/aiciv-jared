#!/usr/bin/env bash
# check-wrangler-no-workers-dev.sh
#
# SPEC #25 Phase 0 — CI static assertion gate.
#
# Fails (exit 1) if any wrangler.toml for an SB-only Worker introduces or
# restores `workers_dev = true`. Designed for CI / pre-commit / pre-deploy.
#
# Per CTO Phase 0 amendment + SPEC OQ-5: turn the invariant
# "clients-api must have workers_dev = false" from documented to enforced.
#
# Starts narrow (clients-api only) since that is the only Worker scheduled
# for Option A (workers_dev = false). Extend SB_ONLY_WORKERS as more
# Workers become pure-internal.
#
# Constitutional alignment:
#   - feedback_skill_filed_does_not_equal_skill_enforced.md — wire the rule
#   - feedback_re-verification_methodology_must_vary.md — grep + regex two ways
#
# Usage:
#   ./tools/spec25-tests/check-wrangler-no-workers-dev.sh
# Exit codes:
#   0 = all SB-only workers have workers_dev=false (or pre-Phase-1 baseline note)
#   1 = at least one SB-only worker has workers_dev=true or is missing the line
#   2 = wrangler.toml file not found

set -u

# ---- config -----------------------------------------------------------------
# Map: friendly name -> wrangler.toml absolute path
declare -A SB_ONLY_WORKERS=(
  ["clients-api"]="/home/jared/projects/clients-api/wrangler.toml"
)

# Phase 1 baseline mode: before clients-api ships workers_dev=false, this
# script should NOT fail the build — it should report PRE-PHASE-1 baseline
# and exit 0. Once SPEC_25_PHASE_1_SHIPPED=1 (env var) it enforces strictly.
PHASE_1_SHIPPED="${SPEC_25_PHASE_1_SHIPPED:-0}"

# ---- helpers ----------------------------------------------------------------
red()   { printf "\033[31m%s\033[0m" "$*"; }
green() { printf "\033[32m%s\033[0m" "$*"; }
yellow(){ printf "\033[33m%s\033[0m" "$*"; }

# ---- main -------------------------------------------------------------------
fail=0
pre_phase1=0
total=0

echo "SPEC-25 wrangler.toml static assertion gate"
echo "============================================"
echo "Phase 1 shipped: ${PHASE_1_SHIPPED}"
echo

for worker in "${!SB_ONLY_WORKERS[@]}"; do
  toml="${SB_ONLY_WORKERS[$worker]}"
  total=$((total + 1))
  echo "--- ${worker} (${toml})"

  if [ ! -f "$toml" ]; then
    red "FAIL"; echo ": wrangler.toml not found at ${toml}"
    exit 2
  fi

  # Two-way grep (probe-dimension variation):
  # 1) literal grep for workers_dev = true
  # 2) regex grep for workers_dev anywhere
  match_true=$(grep -nE '^[[:space:]]*workers_dev[[:space:]]*=[[:space:]]*true[[:space:]]*$' "$toml" || true)
  match_any=$(grep -nE '^[[:space:]]*workers_dev[[:space:]]*=' "$toml" || true)

  if [ -n "$match_true" ]; then
    red "FAIL"; echo ": workers_dev = true present on SB-only worker"
    echo "         match: ${match_true}"
    fail=$((fail + 1))
    continue
  fi

  if [ -z "$match_any" ]; then
    # No workers_dev line at all → defaults to true at CF
    if [ "$PHASE_1_SHIPPED" = "1" ]; then
      red "FAIL"; echo ": workers_dev line is absent (CF default = true) — must be 'workers_dev = false'"
      fail=$((fail + 1))
    else
      yellow "BASELINE"; echo ": workers_dev line absent (pre-Phase-1 expected). Set SPEC_25_PHASE_1_SHIPPED=1 after Phase 1 lands to enforce."
      pre_phase1=$((pre_phase1 + 1))
    fi
    continue
  fi

  # workers_dev present, not true → must be false
  match_false=$(grep -nE '^[[:space:]]*workers_dev[[:space:]]*=[[:space:]]*false[[:space:]]*$' "$toml" || true)
  if [ -n "$match_false" ]; then
    green "PASS"; echo ": workers_dev = false on ${worker}"
    continue
  fi

  red "FAIL"; echo ": workers_dev line found but not parseable as true/false"
  echo "         match: ${match_any}"
  fail=$((fail + 1))
done

echo
echo "Summary"
echo "-------"
echo "Total SB-only workers checked: ${total}"
echo "Failures: ${fail}"
echo "Pre-Phase-1 baseline notices: ${pre_phase1}"

if [ "$fail" -gt 0 ]; then
  echo
  red "VERDICT: FAIL"; echo
  echo "Action: ensure each SB-only worker's wrangler.toml contains exactly:"
  echo "    workers_dev = false"
  exit 1
fi

if [ "$pre_phase1" -gt 0 ] && [ "$PHASE_1_SHIPPED" != "1" ]; then
  echo
  yellow "VERDICT: PASS (pre-Phase-1 baseline)"; echo
  echo "Re-run with SPEC_25_PHASE_1_SHIPPED=1 after Phase 1 ships to enforce strict mode."
  exit 0
fi

echo
green "VERDICT: PASS"; echo
exit 0
