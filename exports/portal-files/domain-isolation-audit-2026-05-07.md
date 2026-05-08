# Domain Isolation Audit — Constitutional Review
**Date:** 2026-05-07
**Auditor:** architect-agent (read-only, no code changes)
**Trigger:** Jared's constitutional rule: each product is its own project, own D1, own Workers. No shared databases, no cross-domain writes without an explicit bridge API.
**Reference:** `.claude/memory/feedback_project_domain_isolation_constitutional.md`

---

## Track 1: Worker → D1 Binding Map

All D1 IDs found in codebase:
- `purebrain-social` = `625dde70-0a60-45e7-bf81-e18e5ac4d854`
- `purebrain-referrals` = `cdd9a522-f947-42a6-b9a3-c30534e02c3f`
- `ara-index` = `42163262-1849-4375-b10d-97a504f5d220`

| Worker | D1 Binding | Database Name | Worker's Domain | Violation? |
|--------|-----------|---------------|-----------------|------------|
| `social-api` | `DB` | `purebrain-social` | Social platform | CLEAN — correct |
| `admin-api` | `DB` | `purebrain-social` | Claimed "admin dashboard" | VIOLATION — see V-1 |
| `paypal-webhook` | `DB` | `purebrain-social` | Payments domain | VIOLATION — see V-2 |
| `agentmail-webhook` | `DB` | `purebrain-social` | Onboarding/email pipeline | AMBIGUOUS — see V-3 |
| `blog-publish-hook` | `DB` | `purebrain-social` | Blog/content domain | VIOLATION — see V-4 |
| `blog-publisher` | `DB` | `purebrain-social` | Blog/content domain | VIOLATION — see V-4b |
| `welcome-email-api` | `DB` | `purebrain-social` | Onboarding/email | AMBIGUOUS — see V-5 |
| `meetings-api` | `DB` | `purebrain-social` | Portal/meetings feature | AMBIGUOUS — see V-6 |
| `referrals-api` | `DB` | `purebrain-referrals` | Referrals domain | CLEAN — correct |
| `trio-comms` | `DB` | `purebrain-referrals` | Comms / trio product | VIOLATION — see V-7 |
| `ara-index` | `DB` | `ara-index` | ARA scoring product | CLEAN — dedicated DB |
| `777-sheets-api` | (none — Google Sheets only) | n/a | 777 dashboard | CLEAN — no D1 |
| `purebrain-portal-proxy` | (none — pure router) | n/a | Portal routing | ARCHITECTURAL — see V-8 |

**Summary of binding violations: 6 confirmed, 3 ambiguous (see details below)**

---

## Track 2: Worker → Worker Call Map

### Verified Cross-Worker HTTP Calls

| Calling Worker | Called Worker URL | Auth Method | Calling Domain | Called Domain | Violation? |
|----------------|-------------------|-------------|----------------|---------------|------------|
| `agentmail-webhook` | `welcome-email-api.in0v8.workers.dev` | None (no token) | Onboarding | Email/onboarding | CLEAN (same logical domain) |
| `social-api` | `trio-comms.in0v8.workers.dev` | Bearer token (`TRIO_COMMS_TOKEN`) | Social | Comms/trio | AMBIGUOUS — see V-9 |
| `blog-publish-hook` | `social-api.purebrain.ai` (POST `/api/content`) | Bearer `SOCIAL_API_SYSTEM_TOKEN` | Blog | Social | VIOLATION — see V-10 |
| `blog-publisher` | `social.purebrain.ai/media/{key}` (GET, fetch banner) | None | Blog | Social (R2 proxy) | VIOLATION — see V-10b |
| `purebrain-portal-proxy` | `social-api.in0v8.workers.dev` (POST `/api/login`) | None (passthrough) | Portal routing | Social | VIOLATION — see V-11 |
| `purebrain-portal-proxy` | `social-api.in0v8.workers.dev` (all `/api/admin/*`) | None (passthrough) | Portal routing | Social | VIOLATION — see V-11 |
| `purebrain-portal-proxy` | `referrals-api.in0v8.workers.dev` (referral paths) | Hardcoded token | Portal routing | Referrals | NEEDS BRIDGE CONTRACT |

### Auth Pattern Analysis

- `agentmail-webhook → welcome-email-api`: no token; caller and callee are in the same logical onboarding pipeline. No bridge contract defined.
- `social-api → trio-comms`: uses `TRIO_COMMS_TOKEN` Bearer. Token-auth exists but no explicit contract spec.
- `blog-publish-hook → social-api`: uses `SOCIAL_API_SYSTEM_TOKEN` Bearer. This is documented as intentional in the spec comments, but blog and social are conceptually different products.
- `portal-proxy → social-api (admin)`: no token injected for admin client calls (passes headers through unchanged, except referral paths which inject `purebrain-admin-2026` hardcoded).
- `portal-proxy → referrals-api`: injects hardcoded `X-Admin-Token: purebrain-admin-2026` (lines 183, 196 in proxy src).

---

## Track 3: Greedy Route Audit

| Route Pattern | Worker | Intended Subdomain | Problem Subdomains | Violation? |
|---------------|--------|--------------------|--------------------|------------|
| `*.purebrain.ai/*` | `purebrain-portal-proxy` | User portal containers (`{name}.purebrain.ai`) | `ce.purebrain.ai`, `777.purebrain.ai`, `legal.purebrain.ai`, any new product subdomain | VIOLATION — see V-8 |

**Detail on V-8 (greedy route):**

File: `workers/purebrain-portal-proxy/wrangler.toml` (comment, no explicit `[[routes]]` block — route is configured in CF dashboard)

The comment in `wrangler.toml` (lines 5-8) states:
> "Route is already configured on zone purebrain.ai: `*.purebrain.ai/*` → purebrain-portal-proxy"

The Worker code has a `SYSTEM_SUBDOMAINS` allowlist (lines 36-58 in `src/worker.js`) to exclude known system subdomains:
- `app`, `www`, `portal`, `api`, `video`, `cc`, `comms`, `mail`, `staging`, `blog`, `status`, `cdn`, `static`, `assets`, `media`, `social`, `social-api`, `voice`, `tts`, `keenjared`, `testariatest`

**Missing from SYSTEM_SUBDOMAINS (confirmed not in list):**
- `ce` — CE SME product (`ce.purebrain.ai`) — this was previously caught causing a 530; fix was applied to DNS/CF routing but the `SYSTEM_SUBDOMAINS` set was NOT updated to include `ce`
- `777` — 777 Command Center (`777.purebrain.ai`)
- `legal` — Legal product (`legal.purebrain.ai`)
- `referrals-api` — if that subdomain exists
- Any future product subdomain will silently fall through to container proxy and get a 502 "Portal unavailable"

**Risk:** Any new subdomain not explicitly added to `SYSTEM_SUBDOMAINS` will be proxied to a Witness container that doesn't exist, returning a 502. This is a latent operational risk for every product launch.

---

## Track 4: Domain Ownership Inventory

| Subdomain / Route | Worker(s) Handling | D1 Database | Git Repo | Status |
|-------------------|--------------------|-------------|----------|--------|
| `social.purebrain.ai` | `social-api` | `purebrain-social` | This repo (`workers/social-api`) | CLEAN domain |
| `social-api.purebrain.ai` | `social-api` | `purebrain-social` | This repo | CLEAN |
| `portal.purebrain.ai/admin/clients` | `portal-proxy` → `social-api` | `purebrain-social` (WRONG) | This repo | VIOLATION — clients data in social DB |
| `portal.purebrain.ai/api/referral/*` | `portal-proxy` → `referrals-api` | `purebrain-referrals` | This repo | CORRECT routing |
| `portal.purebrain.ai/api/login` | `portal-proxy` → `social-api` | `purebrain-social` | This repo | AMBIGUOUS — login belongs to auth domain |
| `app.purebrain.ai` | SYSTEM_SUBDOMAIN (falls to cloudflared tunnel → `portal_server.py`) | SQLite on VPS | VPS / separate | CORRECT |
| `ce.purebrain.ai` | SHOULD be SYSTEM_SUBDOMAIN but missing from list → 530 risk | CE SME D1 | Separate repo (off-machine) | V-8 applies |
| `777.purebrain.ai` | SHOULD be SYSTEM_SUBDOMAIN but missing from list | (none — CF Pages) | This repo? | V-8 applies |
| `voice.purebrain.ai` | `portal-proxy` (has explicit handler, lines 222-256) | (none) | This repo | CLEAN routing |
| `legal.purebrain.ai` | Missing from SYSTEM_SUBDOMAINS → 502 risk | Hancock Law D1 | Separate repo off-machine | V-8 applies |
| `referrals-api.purebrain.ai` | `referrals-api` Worker | `purebrain-referrals` | This repo | CLEAN |
| `paypal-webhook.purebrain.ai` | `paypal-webhook` Worker | `purebrain-social` (WRONG) | This repo | VIOLATION |
| `agentmail-webhook.purebrain.ai` | `agentmail-webhook` Worker | `purebrain-social` (PARTIAL VIOLATION) | This repo | V-3 |
| (internal) `welcome-email-api` | `welcome-email-api` Worker | `purebrain-social` (PARTIAL VIOLATION) | This repo | V-5 |
| (internal) `meetings-api` | `meetings-api` Worker | `purebrain-social` (PARTIAL VIOLATION) | This repo | V-6 |
| (internal) `trio-comms` | `trio-comms` Worker | `purebrain-referrals` (VIOLATION) | This repo | V-7 |
| `ara-index.purebrain.ai` or internal | `ara-index` Worker | `ara-index` (dedicated) | This repo | CLEAN |
| `777-sheets-api.in0v8.workers.dev` | `777-sheets-api` Worker | (none) | This repo | CLEAN |

---

## Track 5: Bridge API Inventory

### Existing Cross-Worker Calls That Need Bridge Contracts

| From | To | Current State | Bridge Contract Exists? | Recommended Action |
|------|----|---------------|-------------------------|--------------------|
| `agentmail-webhook` | `welcome-email-api` | Direct HTTP `POST /send-welcome`, no token | No formal contract | Promote to bridge: define endpoint spec, add shared secret |
| `blog-publish-hook` | `social-api` | HTTP `POST /api/content` with `SOCIAL_API_SYSTEM_TOKEN` | Informal (token exists but no contract doc) | Promote to bridge with documented schema |
| `blog-publisher` | `social-api` (media proxy via `social.purebrain.ai/media/`) | HTTP GET, no token | No contract | Promote to bridge: create `/api/media/{key}` bridge endpoint on social-api with token |
| `social-api` | `trio-comms` | HTTP with `TRIO_COMMS_TOKEN` | Informal token | Promote to bridge contract |
| `purebrain-portal-proxy` | `referrals-api` | HTTP with hardcoded `purebrain-admin-2026` token | No contract | Bridge: define referrals read-API contract; remove hardcoded token |
| `purebrain-portal-proxy` | `social-api (admin)` | HTTP, passthrough headers | No contract | Must be eliminated, not bridged — client data must leave social domain |
| `paypal-webhook` | (should be) `referrals-api` | MISSING — currently writes to `purebrain-social` directly | No bridge | Bridge needed: `payments → referrals` subscription event bridge |

### Bridge APIs Needed for v1 Referral Sprint

1. **Subscription-Event Bridge** (`paypal-webhook` → `referrals-api`): When `BILLING.SUBSCRIPTION.ACTIVATED` fires, paypal-webhook should call `POST /referrals/complete` or a new `POST /subscriptions/activated` endpoint on `referrals-api` to record the client as referred. Currently missing — paypal-webhook writes to `purebrain-social` D1 only and referrals-api has no way to know a subscriber converted via referral.

2. **Client-Registry Bridge** (new domain needed): The `clients` table is currently in `purebrain-social`. It needs to move to its own domain DB (e.g., `purebrain-clients` D1). Workers that need to look up client data should call a dedicated `clients-api` Worker bridge endpoint, not query the social DB directly.

3. **Auth/Session Bridge**: `portal.purebrain.ai/api/login` currently routes to `social-api`. Login/auth is a cross-cutting concern that arguably belongs in its own auth domain. For now, this is the lowest-risk violation (auth session tokens are in `purebrain-social`), but it should be tracked.

---

## Numbered Violation Register

### V-1: admin-api binds purebrain-social (ARCHITECTURAL)
**File:** `workers/admin-api/wrangler.toml` line 6-8
**Nature:** `admin-api` is described as the "PureBrain admin dashboard backend" and queries the `clients` table — but clients are not a social domain entity. The Worker and its D1 binding both need to move to a dedicated `clients` domain.
**Severity:** HIGH — admin dashboard exposes client business data through social DB
**Tables touched:** `clients`, `sessions`, `users`, `team_invites`
**Cleanup:** Extract `clients` table to `purebrain-clients` D1, redeploy `admin-api` against new DB.

### V-2: paypal-webhook binds purebrain-social (ARCHITECTURAL — CRITICAL)
**File:** `workers/paypal-webhook/wrangler.toml` lines 5-8; `src/worker.js` lines 91-116 (`upsertClient()`), lines 131-138 (`updateClientStatus()`), lines 141-158 (`incrementTotalPaid()`), lines 234-251 (`recordTransmission()`)
**Nature:** Payments domain Worker directly writes client status (`INSERT INTO clients`, `UPDATE clients`) and idempotency log (`paypal_webhook_log`) to the social DB. This is the canonical violation from Jared's discovery.
**Severity:** CRITICAL — payments writing to social DB with production data (64 rows of live clients)
**Cleanup:** 
1. Create `purebrain-payments` D1 for `paypal_webhook_log` 
2. Create `purebrain-clients` D1 and move `clients` table there
3. paypal-webhook should upsert via `POST /clients/upsert` bridge on a new `clients-api` Worker

### V-3: agentmail-webhook binds purebrain-social (ARCHITECTURAL)
**File:** `workers/agentmail-webhook/wrangler.toml` lines 5-8; `src/worker.js` lines 195-229 (`storeMagicLink()` → `magic_links` table), lines 238-257 (`lookupPaypalEmail()` → queries `clients` table), lines 260-275 (`updateClientRecord()` → updates `clients` table)
**Nature:** Onboarding Worker (a) reads PayPal email from `clients` in social DB, and (b) writes magic links to `magic_links` table in social DB, and (c) writes `ai_name` + `magic_link` back to `clients`. The magic_links table arguably belongs to the onboarding/auth domain; reading/writing clients belongs to the clients domain.
**Severity:** HIGH — cross-domain data coupling: onboarding reads and writes client records
**Cleanup:**
1. `magic_links` table → move to `purebrain-onboarding` D1 (new)
2. `lookupPaypalEmail()` → call `clients-api` bridge endpoint
3. `updateClientRecord()` → call `clients-api` bridge endpoint

### V-4: blog-publish-hook binds purebrain-social (ARCHITECTURAL)
**File:** `workers/blog-publish-hook/wrangler.toml` lines 21-24 (and staging env lines 47-50); `src/worker.js` lines 194-229 (D1 reads/writes to `published_blog_posts`, `worker_metadata`)
**Nature:** Blog Worker stores its state (`published_blog_posts`, `worker_metadata`) in the social DB. Additionally, it calls `social-api POST /api/content` to queue kanban items (cross-domain HTTP).
**Severity:** MEDIUM — blog state in social DB; cross-domain call to social-api lacks bridge contract
**Cleanup:**
1. Create `purebrain-blog` D1, move `published_blog_posts` + `worker_metadata` there
2. Rebind `blog-publish-hook` to `purebrain-blog` D1
3. Formalize the `blog-publish-hook → social-api` content queue call as bridge API

### V-4b: blog-publisher binds purebrain-social (ARCHITECTURAL + IMPL)
**File:** `workers/blog-publisher/wrangler.toml` lines 5-8; `src/worker.js` lines 680-688 (updates `content` status via D1), line 443-447 (fetches banner from `social.purebrain.ai/media/`)
**Nature:** Blog publisher (a) updates content status in social DB, and (b) fetches media via `social.purebrain.ai/media/` without a token (direct R2 proxy call, no bridge contract).
**Severity:** MEDIUM — blog publisher reading from and writing to social DB and R2
**Cleanup:**
1. Content tracking (`content` table status updates) → social-api bridge endpoint `PATCH /api/content/{id}/status`
2. Media fetch → use `social-api` bridge endpoint with auth token instead of unauthenticated media proxy

### V-5: welcome-email-api binds purebrain-social (ARCHITECTURAL)
**File:** `workers/welcome-email-api/wrangler.toml` lines 5-8; `src/worker.js` lines 395-413 (`logDelivery()` → writes to `email_delivery_log`), lines 446-449 (reads `email_templates`)
**Nature:** Email/communications Worker stores delivery logs and email templates in the social DB.
**Severity:** MEDIUM — email infra data belongs to a communications or onboarding domain, not social
**Cleanup:** Create `purebrain-comms` D1 (or `purebrain-onboarding`), move `email_templates` + `email_delivery_log` there.

### V-6: meetings-api binds purebrain-social (ARCHITECTURAL)
**File:** `workers/meetings-api/wrangler.toml` lines 5-8; `src/worker.js` lines 91-99 (reads `sessions`/`users` for auth), lines 154-217 (reads/writes `meeting_assignments`, `custom_meetings`, `meeting_form_responses`)
**Nature:** Meetings product stores data in the social DB and shares auth tables (`sessions`, `users`) with social-api. Meetings is a portal/product feature, not a social platform feature.
**Severity:** MEDIUM — meetings data co-located with social data; shared auth tables across domains
**Cleanup:** Create `purebrain-portal` D1 for meetings data; auth sessions should come from an auth-api bridge.

### V-7: trio-comms binds purebrain-referrals (ARCHITECTURAL)
**File:** `workers/trio-comms/wrangler.toml` lines 5-8; `src/worker.js` writes to `trio_messages` table in `purebrain-referrals`
**Nature:** Trio Comms (Jared + Aether + Chy + Morphe messaging system) stores its messages in the referrals DB. These are completely unrelated domains. Trio is an internal communications product; referrals is a client referral business product.
**Severity:** HIGH — two unrelated domains sharing a D1 (messages and referral business data)
**Cleanup:** Create `purebrain-comms` D1, move `trio_messages` there; rebind `trio-comms`.

### V-8: portal-proxy greedy *.purebrain.ai/* route (OPERATIONAL)
**File:** `workers/purebrain-portal-proxy/wrangler.toml` (comment lines 5-8); `src/worker.js` lines 36-58 (`SYSTEM_SUBDOMAINS` set)
**Nature:** The `*.purebrain.ai/*` route catches all subdomains. The `SYSTEM_SUBDOMAINS` allowlist is incomplete — missing `ce`, `777`, `legal`, and any future product subdomains. Any unlisted subdomain silently falls through to container-proxy and returns a 502.
**Severity:** MEDIUM-HIGH — operational availability risk for all new product subdomains; `ce.purebrain.ai` was already broken by this (fixed in DNS but code list not updated)
**Cleanup:** Add `ce`, `777`, `legal`, and document the rule: every new product subdomain MUST be added to `SYSTEM_SUBDOMAINS` before its DNS record goes live.

### V-9: social-api proxies to trio-comms (IMPLEMENTATION)
**File:** `workers/social-api/src/worker.js` lines 4801-4812, 4834-4845
**Nature:** `social-api` routes `/api/trios/*/messages` and `/api/trios/*/message` to `trio-comms.in0v8.workers.dev` with a Bearer token. Trio Comms is a separate Worker/domain; social-api acting as proxy to it conflates social and comms domains.
**Severity:** LOW-MEDIUM — implementation concern; token exists so there is some access control, but no formal bridge contract
**Cleanup:** Promote to explicit bridge contract; or expose trio-comms directly without social-api as intermediary.

### V-10: blog-publish-hook calls social-api /api/content (IMPLEMENTATION)
**File:** `workers/blog-publish-hook/src/worker.js` lines 151-188 (`postToSocialApi()`)
**Nature:** Blog Worker calls social-api to queue Bluesky drafts. Cross-domain HTTP with token (`SOCIAL_API_SYSTEM_TOKEN`). Token auth exists but no formal contract document.
**Severity:** LOW — functional cross-domain call with authentication; needs contract formalization
**Cleanup:** Document as bridge API; create `bridge-contracts/blog-to-social.md` spec.

### V-10b: blog-publisher fetches from social.purebrain.ai/media/ (IMPLEMENTATION)
**File:** `workers/blog-publisher/src/worker.js` lines 443-447 (`fetchBannerAsBase64()`)
**Nature:** Blog publisher fetches banner images from `social.purebrain.ai/media/{key}` with no auth token. The social-api media proxy is unauthenticated (by design for public images), but the caller is treating social-api as an asset CDN.
**Severity:** LOW — no auth concern since media is public; architectural concern about coupling
**Cleanup:** Direct R2 access via R2 binding on `purebrain-uploads`, or a dedicated media-api bridge endpoint.

### V-11: portal-proxy routes portal.purebrain.ai/api/admin/* to social-api (ARCHITECTURAL — CRITICAL)
**File:** `workers/purebrain-portal-proxy/src/worker.js` lines 206-217
**Nature:** The proxy routes ALL `/api/admin/*` requests (catch-all) to `social-api.in0v8.workers.dev`. This is the path `portal.purebrain.ai/api/admin/clients` takes to reach the `clients` table in the social DB — the full violation chain. The admin token is also hardcoded in the proxy source at lines 183 and 196 (`'purebrain-admin-2026'`) for referral paths.
**Severity:** CRITICAL — this is the client data access path going through the wrong domain; hardcoded admin token is also a security concern
**Cleanup:**
1. Admin client data must migrate to `clients-api` Worker + `purebrain-clients` D1
2. Portal proxy routes `/api/admin/clients` to `clients-api`, not `social-api`
3. Rotate/remove hardcoded `purebrain-admin-2026` token from source; use a secret

---

## Top 10 Violations by Criticality + Cleanup Cost

| Rank | Violation | Severity | Cleanup Cost | Why Critical |
|------|-----------|----------|--------------|--------------|
| 1 | **V-2: paypal-webhook → purebrain-social D1** | CRITICAL | HIGH | Payments domain writing 64 live client rows to social DB; any social D1 change risks payments data loss |
| 2 | **V-11: portal-proxy routes /admin/clients to social-api** | CRITICAL | HIGH | Client management UI reads/writes client data through the social Worker — full domain violation chain in production |
| 3 | **V-1: admin-api binds purebrain-social** | HIGH | HIGH | Admin Worker that manages client records is entirely in the wrong domain; blocks clean extraction |
| 4 | **V-7: trio-comms binds purebrain-referrals** | HIGH | MEDIUM | Two unrelated products (comms and referrals) share a D1; risk of query interference, schema conflicts |
| 5 | **V-3: agentmail-webhook reads/writes clients in social DB** | HIGH | MEDIUM | Onboarding pipeline reads PayPal email and writes AI names back to clients in social DB; tightly couples onboarding to social |
| 6 | **V-8: portal-proxy greedy route missing ce/777/legal** | MEDIUM-HIGH | LOW | Any new product subdomain without an entry in SYSTEM_SUBDOMAINS will 502; `ce` was already a victim |
| 7 | **V-4: blog-publish-hook binds purebrain-social** | MEDIUM | MEDIUM | Blog tracking state in social DB; cross-domain HTTP to social-api lacks formal bridge contract |
| 8 | **V-6: meetings-api binds purebrain-social** | MEDIUM | MEDIUM | Meetings product shares DB and session/auth tables with social platform |
| 9 | **V-5: welcome-email-api binds purebrain-social** | MEDIUM | LOW-MEDIUM | Email delivery infra (templates, logs) stored in social DB instead of comms/onboarding domain |
| 10 | **V-4b / V-10 / V-9: blog-publisher/blog-hook/social-api implementation-level cross calls** | LOW-MEDIUM | LOW | Cross-Worker HTTP calls with auth tokens but no formal bridge contracts; functional but undocumented |

---

## Recommended Cleanup Sequence

### Phase 0: Immediate (before referral v1 sprint starts)
1. Add `ce`, `777`, `legal` to `SYSTEM_SUBDOMAINS` in portal-proxy — 10 min change, prevents 502s on next deploy (V-8)
2. Remove hardcoded `purebrain-admin-2026` token from portal-proxy source; move to a `wrangler secret put` (V-11 security sub-issue)

### Phase 1: Database Extraction (requires data migration + Jared decision)
1. Create `purebrain-clients` D1. Extract `clients` + `team_invites` tables from `purebrain-social`.
2. Create `purebrain-payments` D1. Extract `paypal_webhook_log` from `purebrain-social`.
3. Create `purebrain-comms` D1. Move `trio_messages` from `purebrain-referrals`; move `email_templates` + `email_delivery_log` from `purebrain-social`.
4. Create `purebrain-blog` D1. Move `published_blog_posts` + `worker_metadata` from `purebrain-social`.

### Phase 2: Worker Rebinding
1. Rebind `paypal-webhook` → `purebrain-payments` D1; client upsert via `clients-api` bridge.
2. Rebind `admin-api` + `agentmail-webhook` → `purebrain-clients` D1.
3. Rebind `trio-comms` → `purebrain-comms` D1.
4. Rebind `welcome-email-api` → `purebrain-comms` D1.
5. Rebind `blog-publish-hook` + `blog-publisher` → `purebrain-blog` D1.

### Phase 3: Bridge API Formalization
1. Create `clients-api` Worker with bridge endpoints: `POST /clients/upsert`, `GET /clients/:email`, `PATCH /clients/:email`.
2. Document `paypal-webhook → referrals-api` subscription-event bridge (needed for referral attribution).
3. Formalize `blog-publish-hook → social-api` bridge with contract doc.
4. Update portal-proxy: route `/api/admin/clients` to `clients-api`, not `social-api`.

---

## Files Audited (Read-Only)

- `workers/*/wrangler.toml` (all 13 Workers)
- `workers/social-api/src/worker.js`
- `workers/admin-api/src/worker.js`
- `workers/paypal-webhook/src/worker.js`
- `workers/referrals-api/src/worker.js`
- `workers/agentmail-webhook/src/worker.js`
- `workers/welcome-email-api/src/worker.js`
- `workers/meetings-api/src/worker.js`
- `workers/trio-comms/src/worker.js`
- `workers/blog-publish-hook/src/worker.js`
- `workers/blog-publisher/src/worker.js`
- `workers/ara-index/src/worker.js` (grep only — file too large for full read)
- `workers/777-sheets-api/src/worker.js`
- `workers/purebrain-portal-proxy/src/worker.js`
- `.claude/memory/feedback_project_domain_isolation_constitutional.md`
