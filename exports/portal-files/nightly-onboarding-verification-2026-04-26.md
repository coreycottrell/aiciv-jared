# Nightly Onboarding Pipeline Verification
**Date**: 2026-04-26 06:16 UTC
**Scope**: 8 payment pages + backend services + today's fixes

---

## 1. HTTP Status (All Pages)

| Page | Status |
|------|--------|
| `/` (homepage) | 200 OK |
| `/insiders/` | 200 OK |
| `/awakened/` | 200 OK |
| `/partnered/` | 200 OK |
| `/unified/` | 200 OK |
| `/home-test/` | 200 OK |
| `/home-test-sandbox/` | 200 OK |
| `/home-test-live-1/` | 200 OK |

**Result**: PASS -- all 8 pages responding.

---

## 2. PayPal SDK + Plan IDs

**Canonical plan IDs from ONBOARDING-SPEC**: P-2SA65600MT088594TNGLTFKY, P-3VH43554A66001716NGLTFKY, P-43A28944XN5237411NGLTFLA

| Page | Plan IDs Present | Match Spec |
|------|-----------------|------------|
| `/` | P-2SA, P-3VH, P-43A (3 live plans) | YES |
| `/insiders/` | P-3VH, P-43A, P-8AU (incl. insiders-specific) | YES |
| `/awakened/` | P-2SA, P-3VH, P-43A | YES |
| `/partnered/` | P-2SA, P-3VH, P-43A | YES |
| `/unified/` | P-2SA, P-3VH, P-43A | YES |
| `/home-test/` | P-2SA, P-3VH, P-43A | YES |
| `/home-test-sandbox/` | 6 plans (3 live + 3 sandbox P-6DU/P-6JY/P-9KA) | YES (dual-mode) |
| `/home-test-live-1/` | EMPTY (all plan IDs = '') | WARNING -- capture-only by design |

**Result**: PASS (7/8). home-test-live-1 is intentionally capture-only.

---

## 3. Seed Flow Guards

| Guard | Homepage | insiders | awakened | partnered | unified | home-test | sandbox | live-1 |
|-------|----------|----------|----------|-----------|---------|-----------|---------|--------|
| `fireSeed` | 6 | 6 | 6 | 6 | 6 | 6 | 6 | 6 |
| `_seedFired` | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 |
| `_addendumFired` | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 |

**Result**: PASS -- double-fire protection intact on all 8 pages.

---

## 4. Pre-Payment State Export

| Feature | Present |
|---------|---------|
| `window._pbState` on homepage | YES (8 refs) |
| `_pbState` on tier-specific pages | NOT present (expected -- simpler flow) |

**Result**: PASS.

---

## 5. Performance Optimizations

| Check | Result |
|-------|--------|
| `preconnect` to PayPal | 3 preconnect hints on homepage |
| GoDaddy references | ZERO |

**Result**: PASS.

---

## 6. Backend Endpoints

| Endpoint | Method | Status |
|----------|--------|--------|
| `api.purebrain.ai/api/verify-payment` | OPTIONS | 204 (CORS OK) |
| `api.purebrain.ai/api/send-seed` | OPTIONS | 204 (CORS OK) |

NOTE: Yesterday's report checked `app.purebrain.ai` (wrong subdomain). The actual endpoints live on `api.purebrain.ai` as referenced in the page source. Both return proper CORS 204.

**Result**: PASS.

---

## 7. Thank-You Page + Magic Link Polling

- `/thank-you/` returns 200
- 9 magic link references in page source (polling active)

**Result**: PASS.

---

## 8. AgentMail Monitors

- `agentmail_monitor.py` (PID 1203627): RUNNING (since Apr 24)
- `agentmail_general_monitor.py` (PID 1203609): RUNNING (since Apr 24)

**Result**: PASS.

---

## 9. Domain Rewrite (.ai-civ.com -> .app.purebrain.ai)

- Line 367 in agentmail_monitor.py: regex rewrites `.ai-civ.com` to `.app.purebrain.ai`
- Line 470: documented in code comments

**Result**: PASS.

---

## 10. TODAY'S FIXES VERIFICATION

### 10a. SEO: 404.html for Invalid URLs

- `curl https://purebrain.ai/this-does-not-exist-test/` returns HTTP 404
- Page title: "Page Not Found | PureBrain"
- Branded page with PureBrain logo, "404" heading, and "Back to PureBrain" link

**Result**: PASS -- custom 404.html is serving correctly for invalid URLs.

### 10b. og:image on Homepage + Pricing Pages

| Page | og:image |
|------|----------|
| `/` | `https://purebrain.ai/blog/your-ai-has-a-memory-problem/banner.jpg` |
| `/awakened/` | Same |
| `/partnered/` | Same |
| `/unified/` | Same |
| `/insiders/` | Same |

- Image URL resolves: HTTP 200

**Result**: PASS -- og:image present and resolving on all 5 checked pages.

### 10c. meetings-api Login (display_name Bug Fix)

- `meetings-api.purebrain.ai/health` returns HTTP 530 (CF Error 1016 -- Origin DNS error)
- CNAME still points to `meetings-api.ai-civ.com` which cannot resolve
- Worker also not reachable at `meetings-api.purebrain.workers.dev` (404)
- Local source (workers/meetings-api/src/worker.js) shows login handler returns `{ id, email, name, role }` -- the `name` field is populated from D1 users table

**Result**: FAIL -- CANNOT VERIFY LIVE. The display_name fix exists in source code (worker.js line 146-149), but the worker is unreachable due to DNS Error 1016. Same issue as yesterday. This DNS problem persists from at least April 25.

### 10d. ContentRouter /api/content/ready (Should Be 404)

- `purebrain.ai/api/content/ready` returns 404
- `social.purebrain.ai/api/content/ready` returns 404

**Result**: PASS -- endpoint correctly removed.

### 10e. All 3 Workers Health

| Worker | Status |
|--------|--------|
| `social.purebrain.ai` | 200 OK (frontend loads) |
| `meetings-api.purebrain.ai/health` | **FAIL** -- HTTP 530, CF Error 1016 (Origin DNS error) |
| `admin-api.purebrain.ai/health` | **FAIL** -- HTTP 530, CF Error 1016 (Origin DNS error) |

**Result**: 1/3 PASS. meetings-api and admin-api still have DNS resolution failures (persisting since at least April 25).

---

## SUMMARY

| Category | Status |
|----------|--------|
| All 8 pages HTTP 200 | PASS |
| PayPal plan IDs correct | PASS (7/8; home-test-live-1 capture-only by design) |
| fireSeed + _seedFired guard | PASS (all 8) |
| _addendumFired guard | PASS (all 8) |
| verify-payment CORS | PASS (api.purebrain.ai) |
| send-seed CORS | PASS (api.purebrain.ai) |
| Magic link polling | PASS |
| AgentMail monitors | PASS (both running) |
| Domain rewrite | PASS |
| Preconnect optimization | PASS |
| No GoDaddy | PASS |
| **NEW: 404.html for invalid URLs** | **PASS** |
| **NEW: og:image on homepage + pricing** | **PASS** (all 5 pages, image resolves) |
| **NEW: ContentRouter removed** | **PASS** |
| social.purebrain.ai | PASS |
| meetings-api health | **FAIL** (DNS Error 1016 -- Day 2) |
| admin-api health | **FAIL** (DNS Error 1016 -- Day 2) |
| meetings-api login fix | **CANNOT VERIFY** (worker unreachable) |

### Critical Issues (Persisting)
1. **meetings-api.purebrain.ai** -- CF Error 1016 (Origin DNS error). CNAME -> `meetings-api.ai-civ.com` cannot resolve. Day 2 of this failure.
2. **admin-api.purebrain.ai** -- CF Error 1016 (Origin DNS error). CNAME -> `admin-api.ai-civ.com` cannot resolve. Day 2 of this failure.

### Action Required
- Fix DNS CNAMEs for meetings-api and admin-api in Cloudflare dashboard. Either point them to valid origins or deploy as CF Workers with direct routes.
- Once DNS is fixed, verify Mireille can log in to meetings-api (display_name bug fix).

---
*Generated by Payment Flow QA Engineer -- READ-ONLY analysis, no code modified.*
