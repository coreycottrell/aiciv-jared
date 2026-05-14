#!/usr/bin/env bash
# scripts/shadow-auth-readout.sh
#
# Day 2 Track D — Shadow-auth readout for the Day 3 cutover gate.
#
# Tails the purebrain-portal-proxy Worker for the compressed 1-2h shadow
# window per CTO amendment #1 (Jared-accepted 2026-05-14, replacing the
# original 24h window). Parses every `shadow_auth` event emitted by
# validateLeaderSessionShadow(), aggregates user_id/email/role matches,
# and prints a single-line verdict: GREENLIGHT, YELLOW, or BLOCK.
#
# Authority chain:
#   - ST# Day 2 brief §Track D.4
#   - CTO review 2026-05-14 §Day 3 (shadow-auth-gate)
#   - feedback_monitor_alive_does_not_equal_monitor_seeing.md (field-present-rate)
#   - feedback_options_preflight_success_does_not_equal_endpoint_health.md
#     (verdict explicitly verifies real validate-session calls, not preflight)
#
# Usage:
#   ./scripts/shadow-auth-readout.sh [duration_minutes]
#     Default duration_minutes = 90 (compressed shadow window)
#     Output JSONL: /tmp/shadow-auth-readout-YYYYMMDD-HHMMSS.jsonl
#     Summary:     stdout + /tmp/shadow-auth-readout-YYYYMMDD-HHMMSS.summary.json
#
# Exit codes:
#   0  — GREENLIGHT (Day 3 cutover unblocked from this gate)
#   1  — YELLOW (≤1% divergence; CTO judgement call)
#   2  — BLOCK (>1% divergence OR <100 samples OR field-presence holes)
#
# Pre-reqs:
#   - wrangler CLI available + authenticated (CLOUDFLARE_API_TOKEN OR `wrangler login`)
#   - jq + python3
#   - purebrain-portal-proxy worker DEPLOYED with Track D wrapper live
#     (NOT applicable Day 2 — Day 2 is held-branch only; this script runs
#     after Day 3 morning dispatch deploys the shadow wrapper.)

set -u
set -o pipefail

DURATION_MIN="${1:-90}"
if ! [[ "$DURATION_MIN" =~ ^[0-9]+$ ]] || (( DURATION_MIN < 1 )); then
  echo "ERROR: duration_minutes must be a positive integer, got: $DURATION_MIN" >&2
  exit 2
fi

if ! command -v wrangler >/dev/null 2>&1; then
  echo "ERROR: wrangler CLI not on PATH" >&2
  exit 2
fi
if ! command -v jq >/dev/null 2>&1; then
  echo "ERROR: jq not on PATH" >&2
  exit 2
fi
if ! command -v python3 >/dev/null 2>&1; then
  echo "ERROR: python3 not on PATH" >&2
  exit 2
fi

STAMP="$(date +%Y%m%d-%H%M%S)"
OUT_JSONL="/tmp/shadow-auth-readout-${STAMP}.jsonl"
OUT_SUMMARY="/tmp/shadow-auth-readout-${STAMP}.summary.json"
DURATION_SEC=$(( DURATION_MIN * 60 ))

echo "Shadow-auth readout starting:"
echo "  Worker:       purebrain-portal-proxy"
echo "  Window:       ${DURATION_MIN} min (${DURATION_SEC} sec)"
echo "  Raw output:   ${OUT_JSONL}"
echo "  Summary:      ${OUT_SUMMARY}"
echo

# Tail in background with a timeout. wrangler tail --format=json emits one
# event-message JSON per line; we filter for our shadow_auth evt.
#
# NOTE: wrangler tail event-message structure:
#   {"outcome":"ok","event_messages":[{"message":"...","level":"log",...}], ...}
# Our shadow log emits a JSON string via console.log(JSON.stringify(...)),
# so the inner message is itself a JSON string we must re-parse.

# Use `timeout` to cap the tail wall-clock. If `timeout` isn't installed,
# fall back to a background+kill pattern.
TAIL_RC=0
if command -v timeout >/dev/null 2>&1; then
  timeout "${DURATION_SEC}s" \
    wrangler tail purebrain-portal-proxy --format=json \
    | jq -c 'select((.event_messages // []) | map(.message? // "") | join(" ") | contains("shadow_auth"))' \
    > "${OUT_JSONL}" || TAIL_RC=$?
else
  # macOS / minimal env fallback
  wrangler tail purebrain-portal-proxy --format=json \
    | jq -c 'select((.event_messages // []) | map(.message? // "") | join(" ") | contains("shadow_auth"))' \
    > "${OUT_JSONL}" &
  TAIL_PID=$!
  sleep "${DURATION_SEC}"
  kill "${TAIL_PID}" 2>/dev/null || true
  wait "${TAIL_PID}" 2>/dev/null || true
fi

# timeout returns 124 on natural window expiry — treat as success
if (( TAIL_RC != 0 && TAIL_RC != 124 )); then
  echo "WARN: wrangler tail exited with code ${TAIL_RC}; continuing with partial data." >&2
fi

# Summarize. Verdict thresholds match the in-isolate /admin/shadow-auth-readout
# endpoint so the two readouts agree.
python3 - "${OUT_JSONL}" "${OUT_SUMMARY}" <<'PYEOF'
import json
import sys
import time

src = sys.argv[1]
dst = sys.argv[2]

total = 0
divergent = 0
both_ok = 0
neither_ok = 0
legacy_only_ok = 0
shadow_only_ok = 0
by_target = {"clients": 0, "referrals": 0, "unknown": 0}
field_present_sums = {
    "legacy_user_id": 0, "legacy_email": 0, "legacy_role": 0,
    "shadow_user_id": 0, "shadow_email": 0, "shadow_role": 0,
}
shadow_errors = {}

try:
    f = open(src)
except FileNotFoundError:
    print(f"ERROR: no tail output at {src}", file=sys.stderr)
    sys.exit(2)

for line in f:
    line = line.strip()
    if not line:
        continue
    try:
        outer = json.loads(line)
    except Exception:
        continue
    for em in outer.get("event_messages", []) or []:
        msg = em.get("message")
        if not isinstance(msg, str):
            continue
        try:
            ev = json.loads(msg)
        except Exception:
            continue
        if ev.get("evt") != "shadow_auth":
            continue
        total += 1
        if ev.get("divergent"):
            divergent += 1
        lo = bool(ev.get("legacy_ok"))
        so = bool(ev.get("shadow_ok"))
        if lo and so: both_ok += 1
        elif (not lo) and (not so): neither_ok += 1
        elif lo and (not so): legacy_only_ok += 1
        elif (not lo) and so: shadow_only_ok += 1
        t = ev.get("target") or "unknown"
        if t in by_target: by_target[t] += 1
        fp = ev.get("field_present") or {}
        for k in field_present_sums:
            if fp.get(k): field_present_sums[k] += 1
        se = ev.get("shadow_error")
        if se:
            shadow_errors[se] = shadow_errors.get(se, 0) + 1
f.close()

field_present_rate = {
    k: (v / total if total else None) for k, v in field_present_sums.items()
}
divergence_rate = (divergent / total) if total else None

# Verdict gate (matches /admin/shadow-auth-readout)
if total < 100:
    verdict = "BLOCK"
    verdict_reason = f"insufficient_samples ({total} < 100)"
elif divergent == 0 and field_present_rate.get("legacy_user_id") == 1.0 and field_present_rate.get("shadow_user_id") == 1.0:
    verdict = "GREENLIGHT"
    verdict_reason = "0 divergences, full field-presence"
elif divergence_rate is not None and divergence_rate <= 0.01:
    verdict = "YELLOW"
    verdict_reason = f"divergence_rate={divergence_rate:.4f} ≤ 0.01 (CTO judgement)"
else:
    verdict = "BLOCK"
    if divergence_rate is None:
        verdict_reason = "no usable samples"
    else:
        verdict_reason = f"divergence_rate={divergence_rate:.4f} > 0.01 OR field-presence holes"

summary = {
    "generated_at": int(time.time()),
    "source_file": src,
    "total": total,
    "divergent": divergent,
    "divergence_rate": divergence_rate,
    "both_ok": both_ok,
    "neither_ok": neither_ok,
    "legacy_only_ok": legacy_only_ok,
    "shadow_only_ok": shadow_only_ok,
    "by_target": by_target,
    "field_present_rate": field_present_rate,
    "shadow_errors": shadow_errors,
    "verdict": verdict,
    "verdict_reason": verdict_reason,
}

with open(dst, "w") as f:
    json.dump(summary, f, indent=2)

print(json.dumps(summary, indent=2))
print()
print(f"VERDICT: {verdict}")
print(f"REASON:  {verdict_reason}")

if verdict == "GREENLIGHT":
    sys.exit(0)
elif verdict == "YELLOW":
    sys.exit(1)
else:
    sys.exit(2)
PYEOF
RC=$?

echo
echo "Summary saved: ${OUT_SUMMARY}"
echo "Raw events:    ${OUT_JSONL}"
exit ${RC}
