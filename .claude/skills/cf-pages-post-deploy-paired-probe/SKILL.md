---
name: cf-pages-post-deploy-paired-probe
description: Canonical post-deploy verification for CF Pages github:push deployments. Mandatory 120s propagation wait + clean-URL probe + cache-bust probe pair on every endpoint. Surfaces CF cache stragglers and rules out false-negative TRIO spam. Trigger after any github:push to a CF Pages project, or after any Chy-led deploy that touches purebrain-site.
when_to_use: Immediately after CF Pages github:push completes (no need to wait for CF dashboard webhook). Especially for: PayPal plan-ID swaps, price changes, copy changes, JS module updates, or any deploy that touches a user-facing endpoint.
constitutional_layer: operational SOP
discovered: 2026-05-17
origin: devops-engineer learning — Chy plan-ID swap across 13 files, 4 endpoints verified 4/4 PASS with clean+cache-bust pair on each, single TRIO message
status: provisional
tick_count: 0
last_used: 2026-05-17
introduced: 2026-05-17
---

# CF Pages Post-Deploy Paired Probe

## Why This Exists

CF Pages `github:push` has a **90-150 second propagation window** before the new deployment is consistently served at the edge (`feedback_cf_pages_github_push_propagation_window.md`). Probing within 60s shows STALE content and creates false-negative TRIO spam.

Worse: **CF Transform Rules can rewrite cache-bust query strings differently from clean URLs**. Probing only the clean URL leaves a cache-straggler dimension uncovered. Probing only the cache-bust URL leaves the "what does a real user see?" dimension uncovered. You need both.

This skill is the canonical paired-probe runbook proven 2026-05-17 on the Chy PayPal plan-ID swap (4/4 endpoints PASS, zero false alarms).

## The Pattern

```bash
set -euo pipefail

# === STEP 1: Wait for propagation (NON-SKIPPABLE) ===
echo "Waiting 120s for CF Pages propagation..."
sleep 120

# === STEP 2: Define expectations per endpoint ===
# Use an array of "url|must_contain|must_not_contain|reason" tuples
declare -a ENDPOINTS=(
  "https://purebrain.ai/|P-NEW_PLAN_ID|P-OLD_PLAN_ID|homepage"
  "https://purebrain.ai/awakened/|P-NEW_PLAN_ID|P-OLD_PLAN_ID|awakened tier"
  "https://purebrain.ai/insiders/pay-test-awakened/|P-NEW_PLAN_ID|P-OLD_PLAN_ID|insiders test"
  "https://purebrain.ai/live/|P-NEW_PLAN_ID|P-OLD_PLAN_ID|live post-purchase"
)

# === STEP 3: Probe each endpoint (clean + cache-bust) ===
EPOCH=$(date +%s)
RESULTS=""
ALL_PASS=true

for tuple in "${ENDPOINTS[@]}"; do
  IFS='|' read -r url must_have must_not reason <<<"$tuple"

  # Clean URL probe
  clean_body=$(curl -s -A "Mozilla/5.0" "$url" --max-time 10)
  clean_code=$(curl -s -o /dev/null -w "%{http_code}" -A "Mozilla/5.0" "$url" --max-time 10)
  clean_have=$(echo "$clean_body" | grep -c "$must_have" || true)
  clean_notv=$(echo "$clean_body" | grep -c "$must_not" || true)

  # Cache-bust probe
  bust_url="${url}?probe=$EPOCH"
  bust_body=$(curl -s -A "Mozilla/5.0" "$bust_url" --max-time 10)
  bust_code=$(curl -s -o /dev/null -w "%{http_code}" -A "Mozilla/5.0" "$bust_url" --max-time 10)
  bust_have=$(echo "$bust_body" | grep -c "$must_have" || true)
  bust_notv=$(echo "$bust_body" | grep -c "$must_not" || true)

  if [ "$clean_code" = "200" ] && [ "$bust_code" = "200" ] \
     && [ "$clean_have" -gt 0 ] && [ "$bust_have" -gt 0 ] \
     && [ "$clean_notv" -eq 0 ] && [ "$bust_notv" -eq 0 ]; then
    verdict="PASS"
  else
    verdict="FAIL"
    ALL_PASS=false
  fi

  RESULTS="$RESULTS
$url ($reason): $verdict  clean=$clean_code/$clean_have/$clean_notv  bust=$bust_code/$bust_have/$bust_notv"
done

# === STEP 4: Single TRIO message at end ===
if $ALL_PASS; then
  ./tools/post-to-trio.sh "CF Pages post-deploy: 4/4 PASS$RESULTS"
else
  ./tools/post-to-trio.sh "🔴 CF Pages post-deploy FAIL — straggler or rollback:$RESULTS"
fi
```

## Per-Endpoint Rubric (avoid overbroad assertions)

The 2026-05-17 BOOP almost flagged false-fail because the rubric said "$297 must be present on all 4 endpoints" — but `/insiders/` is constitutionally $74.50 and `/live/` is post-purchase (no price displayed).

**Rule**: each endpoint gets its OWN `must_contain` + `must_not_contain` based on its semantic role. Document the per-endpoint reason in the tuple so future you (or another agent) understands why each pattern applies.

| Page type | What to assert | What NOT to assert |
|---|---|---|
| Pricing page (`/awakened/`) | NEW plan ID + NEW price string | OLD plan ID, OLD price string |
| Insiders page | NEW plan ID + `$74.50` (constitutional) | OLD plan ID, regular tier prices |
| Homepage | NEW plan ID + headline copy | OLD plan ID |
| Post-purchase (`/live/`) | NEW plan ID (if embedded) | OLD plan ID, any price |
| Guard-protected route | HTTP 200 + auth prompt | HTTP 500/404 |

## What Counts as a Straggler vs a Failure

| Clean | Cache-bust | Verdict |
|---|---|---|
| 200 + NEW | 200 + NEW | PASS |
| 200 + OLD | 200 + NEW | CF cache straggler — wait 60s and re-probe |
| 200 + NEW | 200 + OLD | Transform Rule rewriting cache-bust — INVESTIGATE |
| 404 | 404 | Deploy missed this path — ROLLBACK or RESTORE |
| 200 + neither | 200 + neither | Page changed shape — review with Chy |

## Anti-Patterns

- **Probing within 60s** — `feedback_cf_pages_github_push_propagation_window.md`: stale content, false alarm.
- **`curl -I` (HEAD)** — `feedback_cf_pages_use_get_not_head_for_health_checks.md`: CF Pages returns 404 on HEAD even when GET is 200.
- **One probe per endpoint** — `feedback_multi_probe_diagnosis_required.md`: at minimum 2 probes (clean + bust).
- **One TRIO message per endpoint** — spammy; bundle into single message at end.
- **Overbroad rubric** — applying the same `must_contain` to all endpoints when their semantic content differs.
- **Skipping the wait when "the deploy looked instant"** — propagation is edge-distributed, not synchronous with the CF dashboard.

## Compatible Skills

- Pair with `cf-pages-health-check-get-not-head` — same GET-not-HEAD principle.
- Pair with `cf-pages-meta-refresh-redirects` — if endpoint is a redirect, probe the redirected target.
- Pair with `pre-deploy-credential-scan` — runs BEFORE deploy; this runs AFTER.
- Pair with `independent-pair-verification` — a different agent re-runs this 30 min later.

## Receipt Format

```
CF Pages Post-Deploy Paired Probe (UTC: 2026-05-17 11:25:20)
Trigger:   Chy plan-ID swap (puretechnyc/purebrain-site main, 13 files)
Propagation wait: 120s ✓

| Endpoint                              | HTTP    | NEW | OLD | Verdict |
|---------------------------------------|---------|-----|-----|---------|
| /                                     | 200/200 | 1/1 | 0/0 | PASS    |
| /awakened/                            | 200/200 | 1/1 | 0/0 | PASS    |
| /insiders/pay-test-awakened/          | 200/200 | 1/1 | 0/0 | PASS    |
| /live/                                | 200/200 | 1/1 | 0/0 | PASS    |

TRIO message:  5a63da5c-3c91-4ff4-8c99-4e453ab240a8
Result:        4/4 PASS — no CF cache stragglers, no Transform Rule rewrites
```

## Constitutional Anchors

- CF Pages github:push is canonical deploy flow (MEMORY.md 2026-05-13 lock).
- Multi-probe diagnosis required.
- Synthetic monitors must match real user traffic.
- Probe-dimension audit at 3+ convergence.
