# MED-003 + createSubscription custom_id — SHIP RECEIPT

**Date**: 2026-05-07
**Greenlit**: Jared (CEO) — "greenlight so that nobody has any issues getting the right AI ever again"
**Commit**: `250f5f5` "fix: thread session_uuid through chat logger + PayPal custom_id (MED-003 + createSubscription)"
**Executor**: Aether (PTT — full-stack ship)

---

## Status

**SHIPPED-AND-VERIFIED on production CF Pages.** Push to origin/main BLOCKED by upstream secret in unrelated commit (see §6).

---

## 1. Pre-deploy state capture

| Field | Value |
|-------|-------|
| Worktree | `/tmp/aether-main-wt` (clean, on `main`) |
| Commit | `250f5f5` (HEAD) |
| `git status` | working tree clean, ahead of origin/main by 20 commits |
| LIVE pre-check | All 5 pages returned `pbSessionUuid=0` (correct — about to add this code) |
| **Pre-deploy CF Pages deployment ID** | `2d4e45cd-75e4-48a8-86bd-6b327ae81d50` |
| Pre-deploy created | 2026-05-07T11:14:57Z |
| Pre-deploy aliases | `https://ce.purebrain.ai`, `https://purebrain.ai` |

---

## 2. Deploy command + output

```bash
CF_PAGES_PROJECT=purebrain-production python3 tools/cf-deploy.py \
  --base-dir /tmp/aether-main-wt/exports/cf-pages-deploy \
  --message "MED-003 + createSubscription custom_id ship 250f5f5" \
  awakened/index.html index.html insiders/index.html partnered/index.html \
  unified/index.html js/homepage-payment.js js/payment-background.js
```

Output:
- 7 files CHANGED (matches commit diff stat exactly)
- 7 files uploaded to CF
- 1 protected file preserved (constitutional)
- Total deployment files: 1334

---

## 3. New CF Pages deployment ID (post-ship)

| Field | Value |
|-------|-------|
| **Deployment ID** | `ecade38e-b979-4f2b-a125-6c8f181209d9` |
| Preview URL | `https://ecade38e.purebrain-production-23b.pages.dev` |
| Production | `https://purebrain.ai` |

---

## 4. Live verification (5 pages × 2 markers + 2 JS × 2 markers)

After cache purge (CF zone `49400cad1527af716705f6cb8c22bb65` — needed because `/js/*.js` had `cache-control: max-age=604800` on stale edges):

| URL | pattern-A `window.pbSessionUuid = payTestData.sessionUuid` | pattern-B `createSubscription custom_id` |
|-----|---|---|
| `https://purebrain.ai/` | PASS | PASS |
| `https://purebrain.ai/awakened/` | PASS | PASS |
| `https://purebrain.ai/partnered/` | PASS | PASS |
| `https://purebrain.ai/unified/` | PASS | PASS |
| `https://purebrain.ai/insiders/` | PASS | PASS |

| JS file | reads `window.pbSessionUuid` | no legacy `payTestData.sessionUuid` cross-scope read |
|---|---|---|
| `/js/payment-background.js` | PASS | PASS |
| `/js/homepage-payment.js` | PASS | PASS |

**TOTAL: 14/14 PASS** (independent direct-curl verification).

Served sha matches worktree exactly: `5bc1cd8d69ca…` for `/js/payment-background.js`.

---

## 5. E2E assertion script (live mode)

```bash
LIVE_BASE=https://purebrain.ai bash tools/verify-payment-pages-pbsessionuuid.sh --live
```

Script reports `STATUS: BLOCKED — fix failed assertions before deploy` (3 pass / 11 fail).

**Diagnosis**: The script has a bash defect — `set -euo pipefail` + `echo "$body" | grep -q "$pattern"` returns SIGPIPE (exit 141) when body is large (~450KB). `grep -q` exits early on match, sends SIGPIPE to `echo`, `pipefail` surfaces 141, the `if` condition becomes false, and `fail()` is called despite the pattern being present. Verified by exit-code probe (`Final ec: 141`) and confirmed working when same body grepped via heredoc/tmpfile.

**Recommended script fix** (out of scope for this ship — file as ST# follow-up):
```bash
# Replace `echo "$body" | grep -q -- "$2"` with:
grep -q -- "$2" <<< "$body"   # heredoc avoids SIGPIPE
```

Independent 14-assertion verification (§4) **passed all 14**. Deploy is correct; the gate-script needs patch.

Sandbox/test pages (5 pages) — out of scope per QA flag, INFO-only in script output.

---

## 6. Push to origin/main result

```bash
cd /tmp/aether-main-wt && git push origin main
```

**Result: BLOCKED by GitHub Push Protection.**

```
remote: - GITHUB PUSH PROTECTION
remote:   —— Sendinblue API Key ——
remote:    locations:
remote:      - commit: 107019b95939d6660f18f3eaac8477a8c8ae73ba
remote:        path: exports/cf-pages-deploy/contact-us/index.html:700
```

- Offending commit: `107019b` "chore: Add all untracked CF Pages production content to git" (May 6, **UPSTREAM** of MED-003)
- This is a pre-existing source-control issue, NOT introduced by 250f5f5
- Refused to `--force-push` or `--no-verify` per constitutional rules
- **20 commits including 250f5f5 remain unpushed locally** until secret is rotated and history cleaned

**Action required (separate from this SHIP)**:
1. Rotate the leaked Sendinblue API key (security-auditor)
2. Either accept GitHub's unblock URL (creates audit trail) OR rewrite history to remove the secret
3. Re-attempt `git push origin main`

The CF Pages production deploy is independent of git push — production is LIVE with the fix regardless.

---

## 7. Final Status

| Gate | Result |
|------|--------|
| Pre-deploy capture | PASS |
| CF Pages deploy | PASS (`ecade38e-b979-4f2b-a125-6c8f181209d9`) |
| Cache purge | PASS (CF zone purge_cache → success) |
| Live verification (5 LIVE pages × 2 markers) | PASS 10/10 |
| Live verification (2 JS × 2 markers) | PASS 4/4 |
| E2E script (live mode) | FAIL — script defect, not deploy defect (see §5) |
| Push to origin/main | BLOCKED — upstream secret in `107019b` (see §6) |

**STATUS: SHIPPED-AND-VERIFIED on production.** Git push gate is a separate follow-up.

---

## Memory Written

Path: `.claude/memory/agent-learnings/full-stack-developer/2026-05-07--med003-ship-cf-cache-and-pipefail-gotcha.md`
Type: operational
Topic: CF Pages JS cache TTL behavior + bash pipefail+SIGPIPE false-negative in verify scripts
