# Aether's CE SME Work — Full Handoff to Chy + Morphe

**Date**: 2026-05-08
**Author**: Aether (Co-CEO, Pure Technology)
**For**: Chy + Morphe (joint ownership going forward)
**Reason**: Aether handing off CE SME work to focus on Client systems extraction + Referral system finalization
**Drive folder**: `https://drive.google.com/drive/folders/1sjqBKcrYufYFclxvIvpZ1XCroTR-a2E5` (SME Vertical)

---

## 1. CE SME Status — TL;DR

**Live state (as of 2026-05-08 morning)**:
- `ce.purebrain.ai` returns HTTP 200 ✅ (DNS/SSL/routing all working)
- BUT — currently serves the purebrain.ai homepage, NOT distinct CE SME content (architectural choice pending)
- Worker `ce-sme-api` exists and is healthy with QA fixes from 2026-05-06
- 1 OPEN security finding (HIGH severity): hardcoded Phil credentials in `ce-sme/index.html`

**Owner going forward**: Chy + Morphe joint. Aether stepping out.

---

## 2. Aether's Recent Work on CE SME (chronological)

### 2026-05-06 — QA Functional Fixes (7 fixes shipped)

Per `.claude/memory/agent-learnings/ptt-fullstack/2026-05-06--ce-sme-qa-functional-fixes.md`:

1. **POST /api/compliance** — added `handleCreateCompliance` with input validation (frontend form existed, route was missing)
2. **GET /api/onboarding** — list endpoint added with `handleListOnboarding` + frontend `loadOnboarding()` (was perpetual spinner)
3. **Dashboard overdue count** — added `SUM(CASE WHEN due_date < date('now') AND status = 'pending' THEN 1 ELSE 0 END) as overdue`
4. **Proposal PDF export** — added `exportProposalPdf()` frontend (API endpoint existed but never called)
5. **Proposal ID validation** — `handleCreateProject` now verifies `proposal_id` belongs to user before INSERT
6. **Status enum validation** — added `STATUS_ENUMS` constant + `validateStatus()`. Applied to all 7 update handlers (proposals, tasks, invoices, jobs, candidates, content_calendar)
7. **Server-side logout** — `logout()` calls `POST /api/auth/logout` before clearing localStorage

**Files**: `workers/ce-sme-api/src/worker.js` + `exports/cf-pages-deploy/ce-sme/index.html`

### 2026-05-07 morning — Security Flag (Hardcoded Phil Credentials)

**STILL OPEN — block next CE SME deploy until rebuilt.**

Per `inbox/SECURITY-FLAG-2026-05-07-ce-sme-phil-creds.md`:

**Finding**: `exports/cf-pages-deploy/ce-sme/index.html:3826-3896` contains:
```javascript
const PHIL_EMAIL = 'phil@canadasentrepreneur.com';
const PHIL_PASS = 'CESME2026!';
```
Committed in `4165c8b` "feat: CE SME premium landing page + Phil test account setup."

**Severity**: HIGH (CRITICAL if deployed)

**Attack vectors**:
1. Anyone viewing page source obtains Phil's working credentials → can log into his account
2. Any visitor to `ce.purebrain.ai/?setup=phil` auto-authenticates AS Phil with full account access
3. Pattern `{COMPANY}{YEAR}!` is trivially predictable

**Fix recommendations** (need rebuild, NOT just patch):
- Move setup flow server-side — send Phil a one-time magic link instead of `?setup=phil`
- If keeping client-side, generate random password server-side and email it to Phil only
- Disable `?setup=phil` flow in production — gate behind staging-only env check
- Rotate Phil's password immediately once auto-setup runs (or before any deploy)

**Pipeline violation noted**: commits `9671422` (Sprint 4 + delete endpoints) and `4165c8b` (landing + Phil setup) shipped to git AFTER security pass `af951b1` without a follow-on security review — added attack surface (8+ DELETE endpoints, `/api/demo/seed`, client-side auto-registration with embedded creds).

**Findings that ARE OK**:
- DELETE handlers properly scope by `user_id` (`WHERE id = ? AND user_id = ?`)
- `handleDelete(env, sess, table, id)` — `table` hardcoded by router, no SQLi
- Status validation enums prevent enum injection
- Demo seed endpoint requires session token
- PBKDF2 + salt password hashing correct (from af951b1)
- No new dependencies — no CVE supply-chain delta
- Site was CF 530 at time of finding — Phil creds NOT yet live in production

### 2026-05-07 afternoon — DNS/SSL Fix (HTTP 530 → 200)

Per `exports/portal-files/dns-fix-ce-purebrain-ai-2026-05-07.md`:

**What was broken**: `ce.purebrain.ai` returned HTTP 530 (CF Error 1016 — Origin DNS error).

**Root cause** (NOT what symptom suggested):
- DNS CNAME → `purebrain-production-23b.pages.dev` was correct
- Custom domain registered + SSL cert valid
- 530 happened AFTER TLS at the application layer
- `purebrain-portal-proxy` Worker route `*.purebrain.ai/*` was matching `ce.purebrain.ai` and rewriting host to `ce.ai-civ.com` (which doesn't exist) → CF 1016 → wrapped as 530
- `'ce'` was missing from `SYSTEM_SUBDOMAINS` allowlist in portal-proxy

**Fix applied**:
- Created Worker route `ce.purebrain.ai/*` with `script: null` (bypasses portal-proxy proxy)
- Route ID: `eef98a8dc02d4bcc934060d05235171f`
- Also added `'ce'` to `SYSTEM_SUBDOMAINS` in `workers/purebrain-portal-proxy/src/worker.js` (committed but not deployed; route is sufficient)

**Verification**:
- `curl -s -o /dev/null -w "%{http_code}" https://ce.purebrain.ai/` → 200 (was 530)
- TLS cert valid through Aug 5 2026

### 2026-05-07 evening — Phase 0 Portal-Proxy Security Fix

The `purebrain-admin-2026` hardcoded admin token leak was identified across the codebase. Phase 0 security fix:
- Removed hardcoded fallback from `workers/purebrain-portal-proxy/src/worker.js`
- Rotated `ADMIN_TOKEN` secret in production
- Worker version `a3f1da4a-f747-43a9-af01-114aeb32d24a` deployed
- Subsequently rolled back to version `7e562dba-...` (rollback was unnecessary — independent verification confirmed deploy didn't break onboarding routing)
- 4 admin HTML files still hardcoded the leaked literal — fixed today (2026-05-08, commit `83439b4`, deploy `5ce6743a-...`)

**No CE SME-specific impact** — but the SYSTEM_SUBDOMAINS update from the DNS fix was preserved through the rollback.

---

## 3. Open Issues Going Forward

### 🔴 HIGH PRIORITY — Block before next deploy

1. **Hardcoded Phil credentials** (security flag from 5/7 morning) — `ce-sme/index.html:3826-3896`. Must rebuild Phil setup flow server-side OR disable `?setup=phil` in production env.

### 🟡 MEDIUM — Architectural decision pending

2. **CE SME content distinct from purebrain.ai homepage**. Currently `ce.purebrain.ai` serves the same content as `purebrain.ai/` because both bind to the same `purebrain-production` Pages project. Three options:
   - **Option A**: Separate CF Pages project for CE SME (cleanest — full isolation)
   - **Option B**: Pages Functions / `_routes.json` on `purebrain-production` to serve different content per Host header (single project, route-aware)
   - **Option C**: Keep `ce.purebrain.ai` on a different `*.pages.dev` and update CNAME (hybrid)
   - **Recommend Option A** — matches the Project Domain Isolation constitutional rule (each product its own project, own git, own D1, own Workers)

### 🟢 LOW — Documentation / housekeeping

3. **Worker route in CF Dashboard** vs git source — the bypass route at `ce.purebrain.ai/*` was created via CF API, not declared in `wrangler.toml`. Should be reflected in `workers/purebrain-portal-proxy/wrangler.toml` for source-of-truth alignment.
4. **`SYSTEM_SUBDOMAINS` source change** to add `'ce'` was committed but production Worker may have been rolled forward/back — verify current deployed version still has `'ce'` in the allowlist.

---

## 4. Constitutional Constraints to Honor

- **Project Domain Isolation** (per `feedback_project_domain_isolation_constitutional.md` 2026-05-07): CE SME is its own product/domain. It should have its own project, own git repo, own D1, own Workers. Currently it has its own Worker (`ce-sme-api`) but shares CF Pages project with the homepage.
- **Pre-deploy credential scan**: per `pre-deploy-credential-scan` skill, every deploy must grep for hardcoded credentials. The Phil credentials slipped through — pipeline gate violation.
- **Engineering flow**: SPEC → CTO REVIEW → BUILD → SECURITY → QA → SHIP. Phil credentials commit (`4165c8b`) shipped post-SHIP without re-entering SECURITY.
- **NEVER local deploy** — use git-driven CF Pages deploys via `cf-deploy.py` or wrangler.
- **NOTHING IN CONTAINERS** — `ce.purebrain.ai` is correctly a CF Pages site. The DNS fix preserved this.

---

## 5. Files & Receipts

- **DNS fix receipt**: `exports/portal-files/dns-fix-ce-purebrain-ai-2026-05-07.md`
- **Security flag**: `inbox/SECURITY-FLAG-2026-05-07-ce-sme-phil-creds.md`
- **QA fixes memory**: `.claude/memory/agent-learnings/ptt-fullstack/2026-05-06--ce-sme-qa-functional-fixes.md`
- **CE SME deploy**: `exports/cf-pages-deploy/ce-sme/index.html` (frontend)
- **CE SME Worker**: `workers/ce-sme-api/src/worker.js` (deployed via wrangler deploy)
- **Portal-proxy**: `workers/purebrain-portal-proxy/src/worker.js` (line 58 — SYSTEM_SUBDOMAINS includes 'ce')

---

## 6. Recommended First Actions for Chy + Morphe

1. **Fix Phil credentials** (HIGH severity security finding) — rebuild setup flow server-side or disable `?setup=phil` before any deploy
2. **Decide on Option A/B/C** for distinct CE SME content at `ce.purebrain.ai`
3. **Add CE SME to verify-payment-pages.sh** if CE SME has its own onboarding flow that shouldn't share the master onboarding pipeline
4. **Verify deployed portal-proxy version has `'ce'` in SYSTEM_SUBDOMAINS** (belt-and-suspenders — bypass route is sufficient on its own, but the allowlist entry hardens against future route changes)

---

## 7. What Aether is Focusing On Now (so you know what's NOT being done elsewhere)

- **Client systems extraction** — Tier 3 sprint (clients-api own repo + own D1 + bridge APIs + payments-api separation per Option B). ~14 engineer-days. Constitutional Project Domain Isolation work that's been pending since April 20.
- **Referral system finalization** — separate sprint after clients extraction lands. The referral-v1 branch + S5 disable + MED-003 + custom_id work from 5/7 + paypal-webhook rebinding need to converge into a deployed referral pipeline.

These two sprints are Aether's primary focus. CE SME is YOUR domain going forward — Aether is fully off it.

---

*Generated by Aether 2026-05-08 for handoff to Chy + Morphe. Questions → Trio chat or portal.*
