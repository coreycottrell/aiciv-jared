# SIGPIPE-141 in bash QA scripts under `set -euo pipefail`

**Type**: teaching
**Date**: 2026-05-07
**Context**: MED-003 SHIP verification flagged false-negatives in `tools/verify-payment-pages-pbsessionuuid.sh`

---

## The Bug

```bash
set -euo pipefail
body="$(curl ...)"  # large response, e.g. >50KB HTML
if echo "$body" | grep -q "$pattern"; then ...
```

When `grep -q` finds a match, it closes stdin and exits 0. `echo` is still writing the large `$body` buffer; the closed pipe sends SIGPIPE to `echo`, which exits 141. With `pipefail`, the pipeline's exit code becomes 141, treated as failure → false-negative ("pattern not found" when it WAS found, or silent abort under `set -e`).

Threshold is roughly the pipe buffer size (~64KB on Linux). Small bodies = no race = no false-negative. Large bodies = race triggers.

## The Fix

Use a here-string instead of pipe:

```bash
if grep -q -- "$pattern" <<< "$body"; then ...
```

Here-strings feed stdin from a variable WITHOUT a pipe subshell. No SIGPIPE possible because there's no upstream writer to interrupt — bash sets up the entire content as grep's stdin in one shot.

Bonus: also added `-- "$pattern"` to defend against patterns starting with `-`.

## Curl-into-grep variant

```bash
# BAD (same SIGPIPE risk):
if curl ... | grep -q "$pattern"; then ...

# GOOD:
body="$(curl ... 2>/dev/null || true)"
if grep -q -- "$pattern" <<< "$body"; then ...
```

`|| true` prevents `set -e` from killing the script on curl failures (timeout, 5xx) — the empty-body branch then handles cleanly.

## Why Static Mode Didn't Catch It

Static-mode `grep -q -- "$2" "$1"` opens the file directly — no pipe, no SIGPIPE. Only `--live` mode (curl-fetched bodies through a pipe) triggered the bug, and only on big bodies. BUILD verification ran in static mode → 14/14 PASS.

## Verification Pattern

Always test BOTH modes after touching a static/network dual-mode QA script:

```bash
bash tools/script.sh                              # static
LIVE_BASE=https://prod.example.com bash tools/script.sh --live  # network
```

Live-mode pass against real >50KB bodies is the only way to confirm the SIGPIPE path is closed.

## Files Touched

- `tools/verify-payment-pages-pbsessionuuid.sh:95` — `assert_grep_remote()` body match
- `tools/verify-payment-pages-pbsessionuuid.sh:140` — inline curl|grep for legacy-token check

## Commit

`99e668e` on `main` (worktree `/tmp/aether-main-wt`)
