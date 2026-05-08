# cto: Pre-Build Architectural Review — Clients Extraction

**Agent**: cto
**Domain**: Technology Strategy & Vision
**Date**: 2026-05-08
**Mode**: READ-ONLY architectural review (no code changes)
**Constitutional reference**: `feedback_project_domain_isolation_constitutional.md` (locked 2026-05-07)

---

## Verdict (TL;DR)

**GO-WITH-EDITS.** The extraction is the constitutionally correct fix and should ship. However the scope as briefed is **incomplete by ~50%** — there are 6 Workers bound to `purebrain-social` D1 today, not just `social-api`. Three of them (`admin-api`, `agentmail-webhook`, `paypal-webhook`) are the actual writers/heavy readers of the `clients` table. Cutover that only re-points `social-api` would leave these three as silent dual-writers and re-create drift on day 1.

The edits below convert this from a 1-Worker port to a 4-Worker rebind sprint. With those edits, ship.

---

## 1. Architecture Soundness

The proposed split is correct and matches the Hancock Law / PureLegal pattern referenced in `reference_hancock_law_repo_clean.md` (own repo, own Worker, own D1). Tables to extract are correctly identified: `clients`, `users`, `team_invites`, `sessions`.

**What's missing from the brief — current cross-domain consumers** (verified in code today):

| Worker | wrangler.toml line | Touches `clients`? | Action required |
|---|---|---|---|
| `social-api` | `workers/social-api/wrangler.toml:7` | YES — read-only listing at `worker.js:6201-6207` | Remove route; drop `clients` from social D1 after cutover |
| `admin-api` | `workers/admin-api/wrangler.toml:7` | YES — primary admin CRUD (`worker.js:135,181,233,270`) | **Rebind to `purebrain-clients` D1 OR fold this Worker into `clients-api`** |
| `agentmail-webhook` | `workers/agentmail-webhook/wrangler.toml:7` | YES — reads + writes ai_name + magic_link (`worker.js:243,265`) | Rebind to `purebrain-clients` D1 (or call clients-api via service binding) |
| `paypal-webhook` | `workers/paypal-webhook/wrangler.toml:7` | YES — INSERT new clients + UPDATE on payment (`worker.js:92,131,149,435,484,499`) | Rebind to `purebrain-clients` D1 |
| `meetings-api` | `workers/meetings-api/wrangler.toml:7` | reads `users`/`sessions` only | Needs decision — does meetings own its own users, or use bridge? |
| `blog-publisher` | `workers/blog-publisher/wrangler.toml:7` | reads `users`/`sessions` only | Same as meetings-api |

**Recommendation**: The cleanest pattern is to fold `admin-api` into `clients-api` — the two are functionally the same domain (admin CRUD over clients/users/team_invites). Today they only differ by route prefix. Don't ship two Workers that do the same job in one project.

For `meetings-api` and `blog-publisher`, the `sessions`/`users` dependency means they need a **bridge contract** to validate session tokens against `clients-api`. The simplest bridge: a `POST /api/auth/validate-token` endpoint on `clients-api` that returns `{user_id, role, team_id}` or 401. Both consumer Workers add a Service Binding to `clients-api` and call that one endpoint. This stays inside the constitutional rule (explicit bridge, defined contract).

**Bonus drift to flag (not blocking, but should track)**: `paypal-webhook` writing customer client records to a "social" D1 was the original drift incident that prompted the May 7 rule. This sprint correctly pulls it out.

---

## 2. D1 Migration Safety

**Recommended path**: SQL dump → import, NOT row-by-row INSERT, for these reasons:
1. 64 client rows is small; transaction integrity matters more than throughput.
2. SQL dump preserves schema exactly (indices, defaults, FKs).
3. Reproducible: same dump can populate staging, prod, and a recovery copy.

**Concrete steps:**
```bash
# Export from purebrain-social (source)
wrangler d1 export purebrain-social --output=clients-extract.sql \
  --table=clients --table=users --table=team_invites --table=sessions

# Create new D1
wrangler d1 create purebrain-clients

# Import into purebrain-clients
wrangler d1 execute purebrain-clients --file=clients-extract.sql
```

**Backup BEFORE**: full `purebrain-social` dump to R2 (pattern already established — see `backups/d1/purebrain-referrals-pre-0002a-20260507T155851Z.sql`).

**Schema source of truth**: `shared/social-api-schema.sql:7-19` (users), `shared/social-api-schema.sql:78-86` (sessions). Note the brief says `clients` table — confirm schema exists somewhere; current schema file does NOT include it (it was added ad-hoc during the Apr 21-23 sprint per `project_clients_extraction_drift_admitted.md`). **Step 0 of the sprint = QA captures the live `clients` schema via `wrangler d1 execute purebrain-social --command=".schema clients"` and lands it in version control.**

**Post-cutover dual-write verification window**: Run BOTH databases for 24h with reads going to new, writes mirrored to old. If old never diverges, drop. If divergence, you've found the hole.

---

## 3. Auth / Session Cutover

Sessions are stored in `sessions` table keyed by token (`shared/social-api-schema.sql:78`). Login issues a token at `worker.js:3751`, stored in localStorage by the portal frontend.

**Good news**: tokens are opaque random strings, not JWTs with embedded D1-binding info. If we copy the `sessions` rows over and the new `clients-api` reads from `purebrain-clients` D1 with the same token-lookup logic (`worker.js:3731`), **existing browser sessions remain valid through cutover**. No forced re-login.

**Gotcha**: cookies/localStorage are scoped per origin. If the new Worker is at a different origin than the old (e.g., `clients-api.in0v8.workers.dev` vs `social-api.in0v8.workers.dev`), tokens travel via Authorization header through portal-proxy, not cookies, so origin doesn't matter. Verified: `worker.js:1492` sends `fetch(API+"/api/login")` with the token from response stored in JS, not Set-Cookie. Safe.

**One required edit**: `requireAuth()` in `clients-api` must be byte-identical to social-api's. Don't rewrite.

---

## 4. Portal-Proxy Routing — Test in Staging Without Breaking Prod

`workers/purebrain-portal-proxy/src/worker.js:147-227` is the routing hub. It currently sends:
- `/api/login` → `social-api.in0v8.workers.dev` (line 157)
- `/api/admin/*` (except referrals/affiliates) → `social-api.in0v8.workers.dev` (line 217)

**Recommended test pattern** (no production disruption):
1. Deploy new `clients-api` to its own `*.in0v8.workers.dev` URL.
2. Add a **header-gated** routing branch in portal-proxy: if header `X-Use-Clients-API: 1` is present, route to new Worker; otherwise current path. Ship to prod.
3. Test by injecting that header from a staging admin page or via curl. Production users see no change.
4. Remove the header gate and flip the unconditional route on cutover day.
5. Keep a `?force_legacy=1` escape hatch for 7 days as rollback fuse.

**Alternative**: Use a dedicated subdomain like `clients-api.purebrain.ai` and only switch portal-proxy after independent end-to-end test on that subdomain. Slightly cleaner, slightly more setup.

---

## 5. Bridge API Needs

Per the constitutional rule, all cross-domain access requires explicit bridges. Audit:

- `social-api` → `clients` (current: direct read). After extraction: **DELETE this read entirely.** social-api has no business showing client lists; the route at `worker.js:6201-6208` was opportunistic admin reuse. The portal admin page can call `clients-api` directly.
- `paypal-webhook` → writes new clients on payment. After extraction: **bridge call** `POST clients-api/api/internal/clients` with shared secret. Better than D1 binding because it goes through the API surface that owns invariants (validation, magic_link generation).
- `agentmail-webhook` → updates `ai_name` + `magic_link`. After extraction: bridge call `PATCH clients-api/api/internal/clients/by-email/:email`. Same reasoning.
- `meetings-api` + `blog-publisher` → session validation. Bridge: `POST clients-api/api/auth/validate-token`.

This makes `clients-api` the only Worker bound to `purebrain-clients` D1. Five Workers consume it via HTTP/Service Binding. That IS the constitutional pattern.

---

## 6. Forgot-Password Design

**Token-based reset link** is correct. Specifics:

- Generate `password_reset_tokens` table: `(token TEXT PK, user_id, expires_at, used_at, created_at)`. Token = 32-byte URL-safe random.
- Endpoint flow: `POST /api/forgot-password { email }` → always returns 200 (don't leak existence). If user exists, insert token + send email. Token TTL = 1 hour.
- Reset link format: `https://portal.purebrain.ai/reset-password?token=XXX`
- `POST /api/reset-password { token, new_password }` → validate token unused + unexpired → bcrypt new password → mark token used → invalidate ALL existing sessions for that user (force re-login on all devices).

**Sender inbox**: do NOT use `aether-aiciv@agentmail.to` (that's onboarding, per memory rule). Use a new dedicated `clients@agentmail.to` OR reuse `purebrain@puremarketing.ai` via existing Gmail App Password path. Recommendation: **dedicated `clients@agentmail.to`** — cleaner audit trail, separate from onboarding/seed-flow, doesn't pollute the locked seed-flow inbox.

**Rate limit**: identical pattern to `LOGIN_FAILED_LIMIT` at `worker.js:3834` — 5 attempts per IP per hour for forgot-password requests.

---

## 7. Bulk Credentials Resend Timing

**Recommendation: AFTER 24h verification window. NOT at cutover.**

Why:
- Sending mass credential emails requires the new auth path to be 100% known-good. If you mass-send and the new path has a bug, you've blasted 64 customers with broken login links during peak confusion.
- The 24h watch lets you catch any edge case (CORS, cookie domain, session token format) before customers feel it.
- Current users have working sessions; they don't need a new credential to log in. Only invited-but-not-yet-logged-in users actually need the resend, and those can wait 24h.

**Sequence**: cutover day → monitor 24h → if green, send bulk resend → monitor email bounces → done.

**Bulk send mechanism**: existing `agentmail_general_monitor.py` whitelist + new `tools/bulk_credentials_resend.py` script. Send in batches of 10 with 30s spacing to avoid AgentMail rate limiting.

---

## 8. Timeline (Engineer-Days)

Assumes ST# specialists per `reference_hancock_law_repo_clean.md` capacity (Tier 1 ≈ 4 wks).

| Phase | Owner | Days |
|---|---|---|
| Schema capture + git repo + D1 create | ST1 | 0.5 |
| Port relevant Worker code from social-api → clients-api | ST1 | 1.5 |
| Add forgot-password + reset-password endpoints | ST1 | 1.0 |
| Fold admin-api into clients-api (or rebind) | ST2 | 1.0 |
| Rebind paypal-webhook to bridge calls | ST2 | 1.0 |
| Rebind agentmail-webhook to bridge calls | ST2 | 0.5 |
| Bridge endpoint for session validation (meetings/blog) | ST1 | 0.5 |
| Portal-proxy header-gated route | ST3 | 0.5 |
| Data migration + dry run on staging D1 | ST1 | 0.5 |
| Security review (security-engineer) | SE1 | 0.5 |
| QA + integration tests | QA1 | 1.5 |
| Cutover day + 24h monitoring | ST1 | 1.0 |
| Bulk credentials resend + monitoring | ST1 | 0.5 |
| Drop client tables from purebrain-social | ST1 | 0.5 |

**Total: ~10.5 engineer-days, parallelizable to ~6 calendar days** with 3 ST# in flight simultaneously after the schema capture lands.

---

## 9. Rollback Plan

**Three rollback layers, ordered cheapest first:**

1. **Header escape hatch (T+0 to T+7d)**: portal-proxy keeps `?force_legacy=1` query param that re-routes to social-api. Single-user rollback for stuck customers.
2. **Routing flip (T+0 to T+24h)**: portal-proxy revert to single-line change pointing back to social-api. social-api still has the old `clients` table because we don't drop it until T+24h verified.
3. **D1 restore (catastrophic)**: pre-cutover snapshot of `purebrain-social` to R2. Restore command pre-rehearsed on staging.

**Drop trigger** (point of no return): T+24h with zero P1/P2 reports → `wrangler d1 execute purebrain-social --command="DROP TABLE clients; DROP TABLE team_invites; ..."`. After this, rollback requires R2 restore + re-deploy of social-api with old routes. Document this as the gate moment.

---

## 10. Recommended Dispatch Plan

```
[BUILD-1 — schema + repo]   ST1 (now)        : Capture clients schema, create git repo + D1
[BUILD-2 — clients-api]     ST1 + ST2 (par)  : Port code + add forgot/reset endpoints
[BUILD-3 — webhook rebinds] ST2 (after BUILD-2 staging URL up)
[BUILD-4 — portal-proxy]    ST3 (par with BUILD-2)
[QA — integration]          QA1 (after BUILD-3 + BUILD-4)
[SEC — review]              SE1 (after QA1)
[CUT — cutover]              Aether owns runbook, ST1 hands-on
[VERIFY — 24h]               ops-analyst (independent verifier per memory rule)
[BULK — credentials resend] ST1 (after VERIFY green)
[CLEANUP — drop social tables] ST1 (after VERIFY green)
```

**Dependencies that must NOT slip**:
- Schema capture is gate-zero. Nothing else starts until `clients` table schema is in version control.
- Cutover requires SE1 sign-off on the new `forgot-password` flow. New auth surface = mandatory security review.
- 24h verify uses `operations-analyst` per `feedback_routed_items_need_verification_boop.md` — **NOT** the same engineer who built the cutover.

---

## Final Verdict Block

**Decision**: **GO-WITH-EDITS**

**Edits required before BUILD starts:**
1. Expand scope: `admin-api` folds into `clients-api` (or rebinds D1) — not just social-api.
2. Add `paypal-webhook` + `agentmail-webhook` rebind tasks to sprint scope.
3. Capture live `clients` table schema as gate-zero deliverable.
4. Confirm dedicated `clients@agentmail.to` inbox or override.
5. Use header-gated portal-proxy route, not big-bang flip.
6. Verifier (ops-analyst) is a different agent than the cutover engineer (memory rule).

**Critical-path concerns:**
- Schema not in version control today (gate-zero risk)
- 6 Workers currently bound to `purebrain-social` D1 — sprint must address all clients-touching ones (3) or drift returns
- Bulk credentials resend MUST wait for 24h verify window — do not send on cutover day

**Total engineer-day estimate: 10.5 days, 6 calendar days with 3-engineer parallelism.**

**Aligned with constitutional rule** (`feedback_project_domain_isolation_constitutional.md`): YES. This extraction is the canonical example of the rule — same pattern as Hancock Law (`reference_hancock_law_repo_clean.md`).

---

**END cto pre-build review**
