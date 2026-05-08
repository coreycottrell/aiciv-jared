# Security Review — MED-003 BUILD `250f5f5`

**Reviewer**: security-auditor
**Date**: 2026-05-07
**Commit**: `250f5f567314437cae2fe6248a91b6ebe43267bf` on `main`
**Worktree**: `/tmp/aether-main-wt`
**Mode**: READ-ONLY static analysis

---

## 1. MED-003 PII Preservation — PASS

**Intent**: April MED-003 removed `window.payTestData` / `window.logPayTestData` to prevent third-party scripts from reading PII (email, name, aiName).

**Verified scope** (`git show 250f5f5`):
- 8 files touched: 5 HTML pages (each +2 lines), 2 JS files (each ±2 lines), 1 new SHIP-gate script. **211 insertions / 4 deletions total** — surgical.
- Only one new global is exposed:
  `index.html:13451`, `awakened/index.html:5613`, `partnered/index.html:5682`, `unified/index.html:5630`, `insiders/index.html:5494`
  → `window.pbSessionUuid = payTestData.sessionUuid;`
- `payTestData.sessionUuid` is the output of `crypto.randomUUID()` (line 13449 et al.) — pure UUID v4, **no PII**.
- Confirmed no accidental re-exposure: `grep -n "window\.payTestData\|window\.logPayTestData"` across all 5 pages returns **zero hits** in code paths; only the MED-003 banner comments remain (e.g. `index.html:13377`, `awakened:5539`).
- `payTestData.email`, `.name`, `.aiName` remain inner-scope only.

**Verdict**: MED-003 intent preserved. UUID-only escape hatch is the minimum-privilege fix.

---

## 2. XSS / Injection Surface — PASS

`window.pbSessionUuid` is sourced exclusively from `crypto.randomUUID()` (with a polyfill that uses `Math.random()` charset `[0-9a-f-]`). No user input reaches the assignment. The polyfill regex `/[xy]/g` is operating on a hardcoded literal — not user-controlled.

No new HTML sinks introduced. No `innerHTML`, `document.write`, or `eval` paths added.

---

## 3. `custom_id` Construction — PASS

Pattern: `'PB-' + tier.toUpperCase() + '-' + (window.pbSessionUuid || '')`

- `tier`: function parameter of `renderSDKButtons(tier, container)` (e.g. `index.html:12880` JSDoc: `"Awakened" | "Partnered" | "Unified"`). Caller passes from internal config (`PRICES[tier]`, `PLAN_IDS[tier]`). **Not user-controllable**.
- `window.pbSessionUuid`: UUID v4 charset. No injection vector into PayPal's `custom_id` field.
- Worst-case fallback (`|| ''`) yields `'PB-AWAKENED-'` — a deterministic, safe degraded value.

---

## 4. Logger Migration Safety — PASS

`exports/cf-pages-deploy/js/homepage-payment.js:457, 552` and `exports/cf-pages-deploy/js/payment-background.js:414, 421`:

Diff inspection confirms **only the source of `sessionUuid` changed**. Endpoints unchanged:
- `payment-background.js:399` → `https://api.purebrain.ai/api/log-conversation` (untouched)
- `homepage-payment.js:463` → `VERIFY_ENDPOINT` constant (untouched)
- Headers, method (POST), payload shape, auth posture: identical.

No auth removed; no endpoint redirected. The sessionStorage fallback (`sessionStorage.getItem('pb_sessionUuid')`) is preserved in `homepage-payment.js:457` for cross-tab continuity.

---

## 5. S5 Disable / Dispatcher Hard-Block Untouched — PASS

`git diff 250f5f5~1 250f5f5 -- tools/purebrain_log_server.py` returns **empty**. Lines 1029–1164 (S5 commented-out block, S1–S4 priority chain, hard-block `BLOCKED-NO-MATCH` path with Telegram alert + `logs/blocked_seeds.jsonl` queue + early `return`) are byte-identical to the prior ship `775c840`. MED-003 fix is upstream of dispatcher; the Sheila-class collision guard remains active.

---

## 6. Race Conditions — PASS

The two relevant lines are sequential synchronous JS in a single inline `<script>` block:

```
payTestData.sessionUuid = (crypto.randomUUID ? crypto.randomUUID() : ...);  // line N
window.pbSessionUuid = payTestData.sessionUuid;                             // line N+1
```

Browser inline-script execution is single-threaded and synchronous; no event loop yield occurs between assignments. Any consumer (`window.pbSessionUuid` readers in `payment-background.js`, PayPal SDK `createSubscription`/`createOrder` callbacks) executes strictly **after** DOMContentLoaded or user button-click — both are downstream of full inline-script parse. No TOCTOU window.

---

## 7. Pre-Deploy Credential Scan — PASS

`git show 250f5f5 | grep -iE "password|secret|api_key|apikey|bearer|token=|sk_(live|test)|sk-[a-z0-9]{20}"` → **zero hits**.

Direct scan on touched JS files (`homepage-payment.js`, `payment-background.js`) → **zero hits**. Diff contains only UUID-handling edits and one inline comment per HTML file. SHIP gate script `tools/verify-payment-pages-pbsessionuuid.sh` (197 lines) contains no credentials, only grep assertions.

---

## Final Verdict: **PASS**

All 7 review items pass. MED-003 PII intent preserved (UUID-only window export). No new injection surface. `tier` is internal; `pbSessionUuid` is `crypto.randomUUID()`. Logger endpoints/auth unchanged. S5 hard-block intact on `main`. No race. No credentials in diff.

**No concerns. Ship-cleared from security gate.**
