# MED-003 Ship — CF Pages JS Cache + Bash Pipefail Gotchas

**Date**: 2026-05-07
**Type**: operational
**Topic**: Two SHIP-day gotchas that will recur

---

## What was shipped
Commit `250f5f5` — `window.pbSessionUuid` exposure + createSubscription `custom_id` thread on 5 LIVE awakening pages. Fix for Sheila/Couplify household-payer routing. CF Pages prod deploy `ecade38e-b979-4f2b-a125-6c8f181209d9`. 14/14 live assertions passed.

---

## Gotcha 1 — CF Pages JS files have 7-day edge cache

**Symptom**: After `cf-deploy.py` succeeded and HTML pages were live with the new `window.pbSessionUuid` code, `/js/payment-background.js` was still serving the OLD content. SHA mismatch between worktree (`5bc1cd8d…`) and served (`c10d9c7f…`).

**Root cause**: CF Pages applies `cache-control: public, max-age=604800` (7 days) to static JS by default. HTML often has shorter TTLs that propagate fast, but JS edges hold the stale version. `cf-cache-status: HIT, age: 4756`.

**Fix**: Purge zone cache via API after deploy:
```bash
CF_ZONE_ID=$(grep '^CF_ZONE_ID=' .env | cut -d= -f2)
CF_API_TOKEN=$(grep '^CF_API_TOKEN=' .env | cut -d= -f2)
curl -X POST "https://api.cloudflare.com/client/v4/zones/$CF_ZONE_ID/purge_cache" \
  -H "Authorization: Bearer $CF_API_TOKEN" \
  -H "Content-Type: application/json" \
  --data '{"files":["https://purebrain.ai/js/payment-background.js", ...]}'
```

**Forward action**: cf-deploy.py should auto-purge the SPECIFIC URLs it deployed (not whole zone) when run against `purebrain-production`. Open ST# ticket.

**Verify post-purge**: compare served sha to worktree sha — they should match within ~5 seconds of purge confirmation.

---

## Gotcha 2 — Bash `set -euo pipefail` + `echo "$body" | grep -q` = SIGPIPE 141 false negative

**Symptom**: `tools/verify-payment-pages-pbsessionuuid.sh` reports FAIL on every live assertion despite the pattern being PRESENT in served HTML. Direct `curl | grep -c` finds the pattern. Script is wrong.

**Root cause**: When `body` is ~450KB and `grep -q` matches early, it exits 0 and closes the pipe. `echo "$body"` is still streaming → receives SIGPIPE → exits 141. Under `pipefail`, the pipeline's exit code is `max(0, 141) = 141`. Inside `if echo … | grep -q`, the if-condition evaluates to FALSE because the pipeline didn't exit 0. `fail()` is called.

**Reproduction**:
```bash
set -euo pipefail
body="$(curl -sS https://purebrain.ai/awakened/)"
echo "$body" | grep -q "window.pbSessionUuid"; echo $?  # → 141
```

**Fix patterns**:
```bash
# Use heredoc instead of echo-pipe:
grep -q -- "$2" <<< "$body"

# Or write to tmpfile:
tmp=$(mktemp); printf '%s' "$body" > "$tmp"; grep -q -- "$2" "$tmp"; rm "$tmp"

# Or disable pipefail just for this call:
set +o pipefail; echo "$body" | grep -q -- "$2"; rc=$?; set -o pipefail
```

**Forward action**: file ST# fix for `tools/verify-payment-pages-pbsessionuuid.sh` — replace `echo "$body" | grep -q -- "$2"` with heredoc form. The existing script will produce false BLOCKED status on every live run.

---

## Gotcha 3 — GitHub Push Protection blocks unrelated upstream commit

**Symptom**: `git push origin main` fails with `GH013` Push Protection due to a Sendinblue API key in commit `107019b` (May 6 "chore: Add all untracked CF Pages production content").

**Lesson**: Even if YOUR commit (`250f5f5`) is clean, ANY upstream commit between origin and HEAD with a secret will block the push. CF Pages deploy is independent of git push — production was already SHIPPED via cf-deploy.py before push attempted.

**Constitutional response**: Refuse `--force-push`, `--no-verify`, or to bypass via the GitHub unblock URL without security-auditor + Jared signoff. The secret needs ROTATION first. The `pre-deploy-credential-scan` skill (added 2026-05-07) would have caught this BEFORE the commit landed.

---

## Patterns for future ships

1. **Always cache-purge after JS/CSS deploys** — HTML propagates fast, static assets don't.
2. **Independent verification > script verification when they disagree** — direct curl + grep -c is the ground truth. If a script disagrees with raw curl-grep, suspect the script.
3. **Capture pre-deploy and post-deploy sha** — proves what changed.
4. **Push-protection blocks are SEPARATE from deploy success** — don't conflate "git push failed" with "ship failed". Production is what matters; git is the audit trail.
5. **Use cf-deploy.py with explicit file list** — passing the whole `exports/cf-pages-deploy/` dir doesn't work because the script expects paths relative to site root, not absolute base-dir prefixes.

---

## Files touched (for future archaeology)

- `/tmp/aether-main-wt` (worktree — not main repo at `/home/jared/projects/AI-CIV/aether`)
- 7 deployed: `awakened/index.html`, `index.html`, `insiders/index.html`, `partnered/index.html`, `unified/index.html`, `js/homepage-payment.js`, `js/payment-background.js`
- Receipt: `exports/portal-files/med003-ship-receipt-2026-05-07.md`
- Script needing fix: `tools/verify-payment-pages-pbsessionuuid.sh`
