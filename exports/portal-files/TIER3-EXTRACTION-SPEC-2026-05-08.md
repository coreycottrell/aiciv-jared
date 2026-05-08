# Tier 3 Extraction Sprint — Clients-API + Payments-API
**Date**: 2026-05-08 | **Author**: Aether (Co-CEO/Conductor) | **Status**: Pre-Dispatch

**Locked decisions**:
- Tier 3 production-grade extraction (full architectural fix, not Tier 1 minimal)
- Option B for payments (own domain, not folded into clients)
- Per CTO pre-build review (`cto-prebuild-review-clients-extraction-2026-05-08.md`) + Jared's payments-as-domain decision

---

## 1. Goal

Satisfy the constitutional Project Domain Isolation rule (`feedback_project_domain_isolation_constitutional.md`, May 7) by extracting `clients` and `payments` data + code from `purebrain-social` into their own first-class projects, each with own git repo + own D1 + own Worker. Eliminate drift permanently. Preserve 100% of current functionality and UI — no user-facing changes.

## 2. Non-goals

- ❌ NO functional changes to admin/clients UI
- ❌ NO change to PayPal subscription billing logic
- ❌ NO UX changes for admin users
- ❌ NO forced re-login (sessions migrate intact)
- ❌ NO cutover-day mass emails (24h verify window first)

## 3. Architecture target

```
TODAY (drift):
  social-api Worker → purebrain-social D1 (clients + posts + scheduled + analytics + sessions + ...)
  admin-api Worker → purebrain-social D1 (mostly clients-related)
  paypal-webhook Worker → purebrain-social D1 (paypal_events + writes to clients)
  agentmail-webhook Worker → purebrain-social D1 (writes magic_link + ai_name to clients)
  meetings-api + blog-publisher → purebrain-social D1 (read users/sessions)

TARGET (constitutional):
  clients-api (NEW repo: puretechnyc/clients-api):
    Worker: clients-api
    D1: purebrain-clients
    Tables: clients, users, sessions, team_invites
    Routes: /api/login, /api/admin/clients/*, /api/me, /api/forgot-password, /api/reset-password, /api/team-invites/*
    Folds in admin-api (same domain, redundant Worker)
    
  payments-api (NEW repo: puretechnyc/payments-api):
    Worker: payments-api  
    D1: purebrain-payments
    Tables: paypal_events, subscriptions, payments, refunds
    Routes: paypal webhook receiver + bridge API outbound to subscribers
    Folds in paypal-webhook (same domain, was wrong-bound)
    
  social-api (CLEANED):
    Worker: social-api (existing)
    D1: purebrain-social (existing — clients/users/sessions/team_invites/paypal_events DROPPED)
    Tables: posts, scheduled_posts, platforms, platform_tokens, analytics, content_calendar, approval_queue, team_members
    
  Bridge API contracts:
    payments-api → clients-api: "subscription state changed for customer X"
    payments-api → hancock-law-api: "subscription state changed for firm X"  
    agentmail-webhook → clients-api: "magic link arrived for session X"
    Service Bindings between OUR Workers (per cf-service-binding-pattern skill)
```

## 4. Migration phases (CTO sequencing)

### Phase 0 — Gate-zero: schemas to git (0.5 ed)
- `wrangler d1 execute purebrain-social --command=".schema clients"` → land in repo as `shared/clients-schema.sql`
- Same for `users`, `sessions`, `team_invites`, `paypal_events`
- This was missing in Apr 21-23 sprint (per CTO finding)

### Phase 1 — Stand up clients-api project (2 ed)
- Create git repo `puretechnyc/clients-api` (pattern: Hancock Law repo)
- Initialize wrangler.toml
- Create D1 `purebrain-clients`
- Apply schema migrations (CREATE TABLE statements from Phase 0)
- Skeleton routes (login, /me)

### Phase 2 — Stand up payments-api project (2 ed, parallel with Phase 1)
- Create git repo `puretechnyc/payments-api`
- Initialize wrangler.toml
- Create D1 `purebrain-payments`
- Apply schema migrations
- Skeleton paypal webhook receiver

### Phase 3 — Migrate clients/users/sessions code into clients-api (2.5 ed)
- Copy clients-related routes from `social-api/src/worker.js` → `clients-api/src/worker.js`
- Copy `admin-api/src/worker.js` routes (folds in)
- Verify hash functions match (PBKDF2-SHA256 100k iter)
- Add new `/api/forgot-password` + `/api/reset-password` endpoints (NEW functionality)

### Phase 4 — Migrate paypal-webhook code into payments-api (1.5 ed)
- Copy paypal-webhook code → `payments-api/src/worker.js`
- Add bridge API outbound calls to clients-api when subscription changes
- Add bridge API outbound calls to hancock-law-api when firm subscription changes

### Phase 5 — Bridge API contracts + Service Bindings (1.5 ed)
- Define bridge endpoints + request/response shapes
- Update `agentmail-webhook` to call clients-api bridge instead of writing to purebrain-social D1
- Update `meetings-api` + `blog-publisher` session validation to call clients-api `/api/validate-session` bridge endpoint
- Service Bindings in wrangler.toml for inter-Worker calls (no hardcoded tokens)

### Phase 6 — Data migration (1 ed)
- Export clients/users/sessions/team_invites from purebrain-social D1
- Import into purebrain-clients D1
- Export paypal_events from purebrain-social D1
- Import into purebrain-payments D1
- Verify row counts match exactly

### Phase 7 — Header-gated routing flip in portal-proxy (0.5 ed)
- Add `X-Use-Clients-API: 1` header check in portal-proxy
- When header present → route /api/admin/clients/* to clients-api
- When header absent → route to social-api (legacy)
- Initially set on a small % of admin requests for canary

### Phase 8 — Cutover + 24h verify window (1 ed + 24h)
- Flip header to ON for 100% of traffic
- Operations-analyst (independent verifier per `feedback_verifier_independence_audit_separation.md`) monitors:
  - Admin login success rate
  - Admin/clients page load time
  - Error rate on /api/admin/clients/*
  - PayPal webhook → clients-api bridge call success rate
- 24h window must pass before any cleanup

### Phase 9 — Cleanup (1 ed)
- Drop `clients`, `users`, `sessions`, `team_invites`, `paypal_events` from purebrain-social D1
- Remove client routes from social-api Worker
- Remove admin-api Worker entirely (folded into clients-api)
- Remove paypal-webhook Worker entirely (folded into payments-api)
- Update SYSTEM_SUBDOMAINS allowlist if needed

### Phase 10 — Bulk credentials resend (after Phase 8 verify)
- For all team_invites users: send "your dashboard URL has been migrated, password unchanged" email
- For users with MAGIC_LINK populated: confirm link still works
- 11 users flagged by Lyra-PMG with missing magic-links: resync from Brevo

**Total: ~14 ed / 8-10 calendar days with 3-engineer parallelism**

## 5. Engineering flow per phase

Every phase passes: SPEC → CTO REVIEW (already done at sprint level) → BUILD → SECURITY → QA → SHIP. Specialists in parallel where dependencies allow.

## 6. Rollback plan

- Header-gated flip (Phase 7-8) means rollback = remove `X-Use-Clients-API` header. Single line in portal-proxy.
- 7-day escape hatch: `?force_legacy=1` query param routes back to social-api during transition window.
- Data migration is COPY (not MOVE) — original data stays in purebrain-social until Phase 9 cleanup. Until Phase 9, can revert by flipping header.
- After Phase 9 cleanup, rollback requires data restore from purebrain-social-staging (which we maintain a snapshot of pre-Phase 9).

## 7. Constitutional compliance

- ✅ Project Domain Isolation: each domain own git, own D1, own Worker
- ✅ NO local deploys: all via cf-deploy.py + wrangler deploy
- ✅ NEVER --hard reset, --force-push, --no-verify
- ✅ Pre-deploy credential scan: every deploy
- ✅ Service Bindings replace cross-Worker hardcoded tokens (per cf-service-binding-pattern skill)
- ✅ No data loss (COPY not MOVE; cleanup gated on 24h verify)

## 8. Specialist dispatch plan

Aether dispatches **dept-systems-technology** with this SPEC as the brief. Dept manager spawns:
- **wtt-fullstack** — Phase 1 + 3 (clients-api setup + clients code migration)
- **coder** OR another wtt-fullstack — Phase 2 + 4 (payments-api setup + paypal code migration)
- **ptt-fullstack** — Phase 5 (bridge APIs + portal-proxy update + agentmail-webhook rebind)
- **coder** — Phase 0 (schemas) + Phase 6 (data migration) + Phase 7 (header gating)
- **security-auditor** — SECURITY gate per phase
- **qa-engineer** — QA gate per phase
- **operations-analyst** — Phase 8 24h verify (independent of cutover engineer)

Per memory `feedback_subagents_cannot_spawn_subagents.md`: Aether ALSO spawns specialists DIRECTLY in parallel (not waiting on dept manager). Dept manager synthesizes.

## 9. Status reporting cadence

- After each phase completes: receipt to portal + task list update
- Daily progress summary in portal at end of work session
- 24h verify window: hourly status checks
- Customer-facing changes: ZERO. No notifications to admin users until Phase 10.

## 10. Open questions (none — all resolved by CTO + Jared decisions)

All scope locked. Ready to dispatch.
