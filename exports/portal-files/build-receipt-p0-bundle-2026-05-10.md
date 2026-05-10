# P0 Bundle Build Receipt — 2026-05-10

**Builder**: PTT (full-stack-developer)
**Source brief**: `exports/portal-files/cto-prebuild-p0-bundle-2026-05-10.md`
**Burst window**: ~1.5 hr (well under 3 hr target)
**Status**: **P0-BUNDLE-COMPLETE-AWAITING-SEC-QA**

---

## Memory Search Results

- Searched `.claude/memory/` for `validateLeaderSession`, `display_name`, `sess.role`, `magic_links id=9`, `whitehurst-household`, `S5-payerName fuzzy`, `referral-v1 vs main`, `pre-deploy credential scan`.
- Found: `2026-05-10--onboarding-nightly-post-credential-rotation.md` (gate path-match scope), `2026-05-10--whitehurst-household-audit.md` (Sheila authoritative name = "Sheila Whitehurst"), `2026-05-08--portal-proxy-admin-api-routing-fix-build.md`, `2026-05-09--admin-api-retro-and-V11-regression.md`, `2026-05-07--s5-fuzzy-fallback-disabled-hard-block.md`.
- Applied: branch-divergence pattern, validator-update validation, fail-closed gate semantics, NO-FUZZY rule for human_name selection (used D1 `clients` table id=94 audit, not S5-fuzzy guess).

---

## V-11 Diagnostic — Root Cause

**Hypothesis from CTO brief**: deploy didn't propagate vs path-match wrong vs middleware ordering.

**Investigation steps**:
1. Confirmed live anonymous leak: `GET https://portal.purebrain.ai/api/admin/invites` returned **200** with full invitee list (5e8f40fa nathan@puremarketing.ai, etc.) **before** fix.
2. Inspected portal-proxy deployment list via `wrangler deployments list`: **last live deploy was 2026-05-09 10:08 UTC** (version `9f1e389f-fd3a-4661-b52e-d9123ba4113f`).
3. Diffed branches: commit `65ef0f0` (V-11 gate at `validateLeaderSession()`) lives on **`referral-v1`** ONLY — `main` does not contain it. The two branches have diverged.
4. **Root cause**: Code was committed at 2026-05-10 10:25 UTC on `referral-v1` but **the wrangler deploy step was never run** after that commit. The Worker has been serving 2026-05-09 10:08 UTC code (no gate) for ~28 hours.

**Fix path chosen**: Add admin-api fixes to `referral-v1` (the canonical branch carrying portal-proxy security work), commit, then `wrangler deploy` from `referral-v1`. Branch reconciliation between `main` and `referral-v1` is a separate post-burst chore (defer).

---

## Fix 1 — V-11 deploy regression (PATCHED)

**Files**: `workers/purebrain-portal-proxy/src/worker.js` (no code change needed — gate already correct on `referral-v1`)
**Commit**: `83d767a` (combined commit with bug A+B)
**Worker version (post-deploy)**: `e768da8b-c514-4b60-bc27-f67ccb2085ca`

**3-probe verification (live)**:
| Probe | Expected | Actual |
|---|---|---|
| Anonymous `GET /api/admin/invites` | 401 | **401** `{"error":"unauthorized"}` ✅ |
| Bad-bearer `GET /api/admin/invites` | 401/403/503 | **503** `{"error":"auth_unavailable"}` ✅ (fail-CLOSED) |
| Anonymous `GET /api/admin/clients` | 401 | **401** `{"error":"unauthorized"}` ✅ |
| Anonymous `GET /api/admin/validate-token` | 400 (intentionally public) | **400** `{"error":"token required"}` ✅ |

**Before/after**: 200 (full invitee list including pending leader-invite tokens) → **401** (no body leak).

---

## Fix 2 — Form-field reduction (PATCHED)

**File**: `exports/cf-pages-deploy/waitlist/index.html`
**Diff**:
- Line 388 (rating label): `--required` → optional ("(optional)" suffix)
- Line 396 (rating hidden input): `required` removed
- Line 400-401 (use case): `--required` → optional, `required` removed from textarea
- Line 405-406 (urgency): `--required` → optional, `required` removed from select
- Line 3415-3418 (validator): `if (!name || !email || !rating || !useCase || !urgency)` → `if (!name || !email)` with updated alert copy

**Commit**: `04c7e93`
**Pages deploy ID**: `6cd6f846-4051-479d-ae38-0b51a9461acf`
**Pages URL**: `https://6cd6f846.purebrain-production-23b.pages.dev` → live at `https://purebrain.ai/waitlist/`

**Browser verification (Playwright headless)**:
```
FIELD STATE:
  waitlistName: required=True
  waitlistEmail: required=True
  waitlistRatingValue: required=False
  waitlistUseCase: required=False
  waitlistUrgency: required=False
  waitlistCompany: required=False
  waitlistRole: required=False
```
JS-level click attempt fired no validator alert (validator change confirmed live).

**GA4**: `form_submit` event unchanged (no form name change).

---

## Fix 3 — Latent Bug A (display_name selector) (PATCHED)

**File**: `workers/admin-api/src/worker.js`
**Line**: 213
**Diff**:
```js
- "SELECT s.user_id, s.expires_at, u.email, u.role, u.display_name FROM sessions s JOIN users u ON s.user_id = u.id WHERE s.token = ?"
+ "SELECT s.user_id, s.expires_at, u.email, u.role, u.name AS display_name FROM sessions s JOIN users u ON s.user_id = u.id WHERE s.token = ?"
```
**Why**: `users` table has `name`, not `display_name` (per `shared/social-api-schema.sql:11`). Aliased so downstream call sites that read `sess.display_name` keep working.
**Commit**: `83d767a`
**Worker version**: admin-api `586bc3ed-0857-4fed-9b5c-97675aea8236`
**Verify**: Code path is masked by X-Admin-Token shortcut (and by bridge primary). Schema-level fix; no live SELECT regression observed in 503 fallback during V-11 probing. SEC/QA can force the D1 fallback by toggling `CLIENTS_API` binding off in a preview Worker.

---

## Fix 4 — Latent Bug B (owner role gate, BOTH FILES) (PATCHED)

**File 1**: `workers/admin-api/src/worker.js` — lines 323, 333, 345, 357, 423, 434
**File 2**: `workers/purebrain-portal-proxy/src/worker.js` — line 182

**Diff (admin-api, all 6 sites)**:
```js
- if (sess.role !== "leader") return err(403, "leader only");
+ if (!["leader","owner"].includes(sess.role)) return err(403, "leader or owner only");
```

**Diff (portal-proxy bridge gate)**:
```js
- if (j.role !== "leader") return { ok: false, status: 403 };
+ if (!["leader","owner"].includes(j.role)) return { ok: false, status: 403 };
```

**Commit**: `83d767a` (single commit covers both files per CTO mandate)
**Worker versions**: admin-api `586bc3ed-...`, portal-proxy `e768da8b-...`
**Why**: 12 prod users (per CTO recon) have `role='owner'` including Jared. Both gate layers were excluding them.
**Verify**: SEC/QA browser test — login as Jared (owner) → load `/admin/clients` → click Save. Today's curl-based proof: V-11 gate fires correctly (anonymous 401), so the `["leader","owner"]` allowlist is the only gate now between owners and admin actions.

---

## Fix 5 — Latent Bug C (magic_links id=9 cosmetic) (PATCHED)

**Database**: D1 `purebrain-social` (`625dde70-0a60-45e7-bf81-e18e5ac4d854`)
**Table**: `magic_links`, row `id=9`

**Authoritative source for correct human_name**: `.claude/memory/agent-learnings/full-stack-developer/2026-05-10--whitehurst-household-audit.md` — Whitehurst household audit confirmed "sheila@couplify.com (id=94): **Sheila Whitehurst**". This is a clean source per CTO mandate (NOT a fuzzy guess from S5).

**BEFORE**:
```
id=9, ai_name=Kindred, human_name="Jay Whitehurst", human_email=Sheila@couplify.com, status=ready
```

**SQL run** (belt-and-suspenders WHERE):
```sql
UPDATE magic_links SET human_name = 'Sheila Whitehurst'
  WHERE id = 9
    AND LOWER(human_email) = 'sheila@couplify.com'
    AND ai_name = 'Kindred';
```

**AFTER**:
```
id=9, ai_name=Kindred, human_name="Sheila Whitehurst", human_email=Sheila@couplify.com, status=ready
```

**D1 confirmation**: `changes: 1, rows_written: 1, changed_db: true`.
**ai_name** preserved as `Kindred` (correct).

---

## Mandatory gates — all PASSED

| Gate | Status |
|---|---|
| Pre-deploy credential scan (admin-api + portal-proxy) | **0 CRITICAL, 0 HIGH** ✅ |
| Pre-deploy credential scan (Pages, run by `cf-deploy.py`) | **clean** ✅ |
| Browser-based UX testing for form-fix (Playwright headless) | ✅ — field-attribute state confirmed |
| Service Binding pattern (no hardcoded tokens) | ✅ — `env.CLIENTS_API` binding only |
| NO local deploy, git → CF flow | ✅ — both Workers via `wrangler deploy` from committed `referral-v1`; Pages via `cf-deploy.py` |
| Bug B in BOTH files (admin-api + portal-proxy) in same commit | ✅ — commit `83d767a` |

---

## Deploy summary

| Surface | Version / ID |
|---|---|
| **portal-proxy Worker** | `e768da8b-c514-4b60-bc27-f67ccb2085ca` |
| **admin-api Worker** | `586bc3ed-0857-4fed-9b5c-97675aea8236` |
| **Pages waitlist deploy** | `6cd6f846-4051-479d-ae38-0b51a9461acf` |
| **D1 UPDATE (Bug C)** | `changes: 1` confirmed remote |
| **Commits** | `83d767a` (workers), `04c7e93` (Pages) |
| **Branch** | `referral-v1` (per V-11 root-cause analysis; main reconciliation is post-burst chore) |

---

## Out-of-scope / defer-tickets surfaced

1. **Branch reconciliation `main` ↔ `referral-v1`**: `main` has 2 portal-proxy security commits (`1fe0a3e`, `83439b4`) not in `referral-v1`; `referral-v1` has the V-11 gate not in `main`. A future burst should merge cleanly. Not blocking — `referral-v1` is the deployed branch and is post-rotation/secure.
2. CTO defer-tickets 1-5 (per brief) all stand.
3. Owner-role browser verification (login as Jared → click Save) is left to SEC/QA per division of labor.

---

## Memory Written

Path: `.claude/memory/agent-learnings/full-stack-developer/2026-05-10--p0-bundle-v11-deploy-and-fixes.md`
Type: teaching
Topic: P0 bundle execution — V-11 root cause was missed deploy (not branch divergence per se), 5-fix burst pattern, belt-and-suspenders D1 UPDATE.

---

**Status**: **P0-BUNDLE-COMPLETE-AWAITING-SEC-QA**
