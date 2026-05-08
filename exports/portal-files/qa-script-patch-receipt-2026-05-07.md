# QA Script Patch Receipt — SIGPIPE-141 Fix

**Date**: 2026-05-07
**Patcher**: PTT (full-stack-developer / Systems-Technology)
**Authority**: Jared (CEO) greenlit
**Severity**: Low risk (test script, no production impact)

---

## Branch + Commit

- **Branch**: `main`
- **Worktree**: `/tmp/aether-main-wt` (main repo `/home/jared/projects/AI-CIV/aether` was on `referral-v1`; main is checked out at the worktree)
- **Commit hash**: `99e668e249cc6bf7f49c9860b7e1d450ddf5a72b`
- **Subject**: `fix(qa-script): patch SIGPIPE-141 false-negative in verify-payment-pages-pbsessionuuid.sh`
- **Pre-commit hooks**: Run (not skipped)
- **Position**: 21 commits ahead of `origin/main` (held by GH Push Protection — separate Sendinblue key issue at upstream commit 107019b)

## Lines Patched

File: `tools/verify-payment-pages-pbsessionuuid.sh`

| Line | Before | After |
|------|--------|-------|
| 95 | `if echo "$body" \| grep -q -- "$2"; then` | `if grep -q -- "$2" <<< "$body"; then` |
| 140 | `if curl ... \| grep -q "..."; then` | Captures `js_body="$(curl ... \|\| true)"`, then `grep -q -- "..." <<< "$js_body"` |

**Why**: `set -euo pipefail` + `echo "$body" \| grep -q "$pattern"` produces SIGPIPE-141 false-negatives on bodies >50KB because grep closes its stdin on first match, while the upstream `echo`/`curl` is still writing — pipefail then propagates SIGPIPE as a script failure, falsely reading "pattern not found" or aborting silently. The here-string form (`<<<`) feeds the variable as a single read without invoking a pipe subshell, eliminating the race entirely.

## Test Results

**Static mode** (no network):
```
Passed:  14
Failed:  0
STATUS: GREEN — safe to deploy
EXIT_CODE=0
```

**--live mode against production** (`LIVE_BASE=https://purebrain.ai`):
```
Passed:  14
Failed:  0
STATUS: GREEN — safe to deploy
```

Live-mode pass against real >50KB bodies confirms the heredoc form does NOT regress and the SIGPIPE-141 path is closed. (--live against `staging.purebrain.ai` returns 14/14 fail by design — staging hasn't been deployed with the MED-003 changes yet; this is correct behavior, not a script defect.)

## Status

**PATCHED-COMMITTED-NOT-PUSHED**

- Commit `99e668e` lives on local `main` only
- Will go upstream when the GH Push Protection block on Sendinblue key in commit 107019b clears
- No production impact — test script only

---

End of receipt.
