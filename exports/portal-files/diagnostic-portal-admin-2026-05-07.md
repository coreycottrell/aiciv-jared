# Diagnostic — portal.purebrain.ai/admin/referrals/ (commit b98235f follow-up)

**Date:** 2026-05-07
**Mode:** Read-only investigation. NO ship.
**Trigger:** Jared tested b98235f fixes; reported autocomplete missing names + Save Splits dead.

---

## CRITICAL META-FINDING — Read this first

**Commit b98235f has not been deployed to ANY live host.**

- 17 commits unpushed on `main` (`b98235f` is one of them).
- `https://portal.purebrain.ai/admin/referrals/` md5 = `3b74f111…` (1323 lines).
- `https://staging.purebrain.ai/admin/referrals/` md5 = `3a7d8eed…` (1286 lines).
- Local `exports/cf-pages-deploy/admin/referrals/index.html` md5 = `c91a4d7b…` (2159 lines).
- Live HTML (both hosts) contains **zero references** to `splits`, `btnSaveSplits`, `renderSplitRows`, or `/admin/partners/:id/splits`. There is no split UI live anywhere.

What Jared tested cannot have been the b98235f file. Either (a) he was on a CF Pages preview tied to an unmerged branch, (b) browser was loading a cached/sibling page, or (c) the "missing names" + "Save Splits dead" symptoms are from the OLD admin where splits were never wired. Need confirmation of exact URL Jared hit before any fix.

---

## Q1 — Names missing from autocomplete

**Root cause (in b98235f code, file `exports/cf-pages-deploy/admin/referrals/index.html`):**

- Line **1336**: `if (window.location.hostname !== 'portal.purebrain.ai' && state.clients.length === 0)` — the affiliates fallback is **gated to non-portal hosts**. On portal, if `admin-api` ever fails (5xx, timeout, expired token), there is NO fallback — `state.clients` stays empty, autocomplete shows nothing.
- Even when the fallback runs (staging path), `affiliates` (66 rows live) is the **wrong data set**. `affiliates` = users with referral codes; `admin-api/clients` = full client roster. Mismatch is by design.
- Confirmed `admin-api` CORS works for `https://portal.purebrain.ai` origin: preflight OPTIONS returns `access-control-allow-origin: https://portal.purebrain.ai`. So in production the primary path *should* succeed (if a valid Bearer token is sent via `portal_server` proxy). On staging, browser hits admin-api with `https://staging.purebrain.ai` origin → server replies `access-control-allow-origin: https://purebrain.ai` (mismatch) → CORS fail → fallback fires → wrong dataset.

**Connected to /admin/clients?** Yes — the *intended* primary source is admin-api `/api/admin/clients`. That is the correct full roster. The autocomplete will only show full names when that primary path succeeds.

**Proposed fix (frontend, single ST# work order):**
1. Remove host gate at line 1336 — let fallback run on any host.
2. Stop calling `affiliates` as a fallback. Add a real "all clients" endpoint, or have the fallback merge `affiliates ∪ partners` and label entries `(affiliate)` so the user knows it's a partial set.
3. Surface a UI hint when fallback is active ("Showing affiliates only — admin API unavailable").

**Better fix (Worker, needs SEC/QA):** add `https://staging.purebrain.ai` and `https://portal.purebrain.ai` to admin-api's CORS allowlist for `/api/admin/clients` so primary path works everywhere.

---

## Q3 — Save Splits does nothing

**Root cause #1 — UI never opens with existing splits, file `exports/cf-pages-deploy/admin/referrals/index.html`:**

- Line **1006**: `renderSplitRows(af.split_config || [])` — reads `split_config` from `state.affiliates`.
- `/admin/affiliates` Worker handler (`workers/referrals-api/src/worker.js:1775-1784`) **does not include `split_config` in its response shape**. Confirmed live: `curl /admin/affiliates` returns no `split_config` key on any of 66 rows.
- So opening any partner's edit modal renders zero rows — looks like "no splits" to user.
- Live D1 DOES have `split_config` (verified via `/admin/partners` — partner #11 has stored split config as JSON string).

**Root cause #2 — Save round-trip should work, but UI lies:**

- Frontend POSTs `PATCH /api/admin/partners/:id/splits` (line 1881). Worker handler at `worker.js:380-426` matches that route, validates, persists to D1, returns `{ok, partner}` with `split_config` as JSON string.
- Frontend handles string vs array correctly (line 1865: `typeof rawSplits === 'string' ? JSON.parse(rawSplits) : rawSplits`). Save itself is plumbed correctly.
- But **`btnSaveSplits` does not exist in the live HTML at all** — so on the live site, clicking the button (if any) is a no-op handler. This matches Jared's "does nothing" symptom exactly.

**Proposed fix:**

A. Worker side (`worker.js:1775-1784`) — add `split_config: r.split_config || '[]'` to the `affiliates` mapping so the modal can render existing splits. **This is a Worker code change → SEC/QA gate required.**

B. Frontend side — once b98235f is actually deployed, splits UI exists and works. Until then, no JS fix can produce the button.

---

## Scope & gates

| Fix | Layer | Gate |
|---|---|---|
| Deploy b98235f to portal+staging | Deploy only | NEVER without auth from Jared. Push 17 commits + verify CF Pages target. |
| Remove host gate line 1336 | Frontend (HTML) | Single ST# work order, no SEC/QA needed |
| Add `split_config` to `/admin/affiliates` response | Worker | SEC/QA gate (touches API contract; needs CTO pre-build review since persistence layer) |
| Add admin-api CORS allowlist for portal/staging | Worker | SEC/QA gate (security boundary change) |
| Real "all clients" fallback endpoint on referrals-api | Worker | SEC/QA gate + new endpoint design |

**Recommended sequence (DO NOT execute without Jared go):**
1. Confirm with Jared which URL he tested (rules out cache / preview-branch confusion).
2. Push the 17-commit backlog after CTO review (separate authorization — multi-feature push).
3. ST# work order: frontend host-gate removal + UI hint when fallback fires.
4. Separate ST# + CTO + SEC review: Worker `/admin/affiliates` response shape change.

**NOT shipping. Awaiting your call on sequence.**

---

## Memory Written
Path: `.claude/memory/agent-learnings/full-stack-developer/2026-05-07--admin-referrals-deploy-mismatch.md`
Type: operational + teaching
Topic: b98235f fix targets a file no production host serves; deploy chain to portal.purebrain.ai unverified.
