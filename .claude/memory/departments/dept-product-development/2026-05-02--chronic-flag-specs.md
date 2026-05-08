# PD# Chronic-Flag-to-Spec — 2026-05-02

**Department**: Product Development
**Date**: 2026-05-02
**Prepared by**: dept-product-development
**Trigger**: Aether BOOP — break the flag-without-spec cycle on 3 chronic 14+ flag issues
**Type**: PRD bundle (3 specs) + routing dispatches

---

## Executive Summary

Three issues have been flagged 14+ times in self-analysis cycles without ever crossing the line from "flag" to "shipped fix." This BOOP converts each into a buildable spec with a routing target, then dispatches each spec to the responsible department manager TODAY. No more analysis theater. Per `feedback_analysis_theater_anti_pattern.md` and `feedback_self_analysis_commitments_need_delegation.md`.

**The three specs:**

| # | Issue | Routing | Effort | Priority |
|---|-------|---------|--------|----------|
| 1 | Email welcome sequence (post-seed nurture) | MA# (with ST# webhook handoff) | M | P0 |
| 2 | birth_completions D1 writer + reconciliation | ST# | S-M | P0 |
| 3 | LinkedIn cookie refresh workflow | ST# (Plan A) → MA# adoption | S | P1 |

**Constitutional checks applied (per `pre-build-checklist`):**
- Spec 1: SOFTWARE (Brevo workflow + webhook), NOT AI automation. Recurring, customer-facing, persistence required → D1.
- Spec 2: SOFTWARE (D1 schema + writer worker). Persistence required, source of truth for revenue ops → D1.
- Spec 3: SOFTWARE (refresh workflow + Telegram one-tap page). Real-time when expiry hits, human-configurable.
- All specs comply with: NEVER deploy to containers, ALL APIs → CF Workers, ALL data → D1, NEVER local deploy.

---

## SPEC 1 — Email Welcome Sequence (Post-Seed Nurture)

### Problem statement
New PureBrain customers receive their seed email and magic link to the portal, then go silent. There is no automated 5-7 email nurture sequence to drive activation, surface Brainiac Training, reinforce the AI-partnership relationship, or set up upgrade conversations. The 2026-04-14 spec (`to-jared/email-welcome-sequence-fix-2026-04-14.md`) routed a v1 sequence to MA# with an ETA of 2026-04-20. That deadline passed. As of 2026-05-02 the sequence is not verifiably live in production. This is the flag-without-verification anti-pattern (`feedback_routed_items_need_verification_boop.md`). Without this sequence, new customers experience a cliff after seed delivery — measurably hurts activation, retention, and tier-upgrade conversion.

### Proposed solution
Re-activate the 2026-04-14 spec with two upgrades:
1. **Tier segmentation v1 (not v2)** — three parallel tracks branching from the same trigger:
   - **Awakened ($149)**: 5 emails, lighter cadence, focused on activation + Brainiac Module 1 + soft upgrade ask at Day 30.
   - **Insider ($499)**: 6 emails, adds Module 2 unlock at Day 21 + Neural Feed positioning + community signal.
   - **Founder ($999)**: 7 emails, adds white-glove "founder office hours" booking link at Day 14 + custom case-study collaboration ask at Day 30.
2. **Trigger source = D1 `birth_completions` row** (NOT seed-send timestamp). This forces the dependency on Spec 2 — we don't fire nurture until the customer has actually entered their portal at least once. Prevents emailing customers who paid but never completed.

**Architecture**: Brevo workflow with three lists (one per tier). CF Worker `birth-completion-handler` (already exists per 2026-03-13 doc) writes to D1 (Spec 2) AND fires Brevo `addToList` API. Brevo handles cadence and merge fields. Suppression rules (pause on portal login or reply) handled by webhook from log server back to Brevo.

**Merge fields required**: `{AI_NAME}`, `{CUSTOMER_FIRST_NAME}`, `{PORTAL_MAGIC_LINK}`, `{TIER}`, `{BRAINIAC_MODULE_URL}`.

**Out of scope**: Voice-narrated emails (future), behavioral re-engagement (future), referral nudges (handled separately).

### Acceptance criteria
1. Test seed → birth completion → tier-correct email #1 lands within 1 hour, all 3 tiers verified end-to-end with internal addresses (jared@puretechnology.nyc + purebrain@puremarketing.ai).
2. All emails populate `{AI_NAME}` and `{CUSTOMER_FIRST_NAME}` correctly with no `{{ }}` artifacts (tested across all 3 tiers).
3. Suppression works: portal login within 48hrs of an email pauses next nudge by 48hrs, verified in Brevo logs.
4. MA# delivers a reconciliation report showing every birth_completions row from the last 7 days received its tier-correct sequence with no drops (cross-checked against Brevo send log).
5. Status report posted to Aether portal daily until ship, then weekly send-volume + open-rate + activation-rate dashboard added to social.purebrain.ai or 777 command center.

### Routing target
**MA# (dept-marketing-advertising)** owns copy, segmentation, Brevo workflow, suppression rules, and reporting.
**Cross-dept handoff to ST# (dept-systems-technology)** for: Brevo webhook trigger from CF Worker `birth-completion-handler`, magic link merge field exposure, log server portal-login → Brevo suppression API call.

### Effort estimate
**M** (medium) — copy is ~80% drafted in the 2026-04-14 doc, needs tier-specific variants. Brevo workflow build + webhook integration is ~2-3 dev days. Reconciliation tooling adds ~1 day.

### Priority
**P0** — every day this isn't live, every new customer churns silently. Direct revenue impact via tier-upgrade conversion.

### Dependencies
- Spec 2 (D1 birth_completions) MUST ship first or in parallel — this sequence triggers off that table.
- Brevo template IDs already exist (template 30 per 2026-03-13 doc) — verify and extend.

---

## SPEC 2 — birth_completions D1 Writer + Reconciliation

### Problem statement
The current "source of truth" for who actually completed onboarding is a JSONL file: `birth_completions.jsonl` written by the CF Worker `/api/birth/webhook` (per 2026-03-13 doc). This violates `feedback_nothing_in_containers_ever.md` ("ALL data → D1") and `feedback_never_deploy_to_container.md`. Worse, it means we have NO queryable source of truth for the question "who is actually a customer?" — we only have:
- PayPal webhooks (paid)
- Seed email forwards (questionnaire complete)
- A flat JSONL file (Witness sent magic link)

There is no reconciliation between "paid in PayPal" and "actually completed birth." This is a foundational gap — every downstream system (welcome sequence, tier reporting, churn analysis, financial close, refund eligibility) depends on knowing who actually onboarded.

### Proposed solution

**D1 schema** (database: `purebrain-customers`, table: `birth_completions`):

```sql
CREATE TABLE birth_completions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  uuid TEXT NOT NULL UNIQUE,           -- session UUID from seed
  customer_email TEXT NOT NULL,
  customer_first_name TEXT,
  ai_name TEXT NOT NULL,
  tier TEXT NOT NULL,                  -- 'awakened' | 'insider' | 'founder'
  paypal_subscription_id TEXT,         -- nullable; reconciled later
  paypal_payer_email TEXT,             -- nullable; reconciled later
  magic_link_url TEXT NOT NULL,        -- the .app.purebrain.ai URL Witness sent
  container_name TEXT NOT NULL,        -- e.g. 'aetherjared'
  birth_completed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  first_portal_login_at TIMESTAMP,     -- nullable; updated by log server
  last_portal_login_at TIMESTAMP,      -- nullable; updated by log server
  reconciliation_status TEXT NOT NULL DEFAULT 'pending',  -- 'pending' | 'matched' | 'orphan_birth' | 'orphan_payment'
  reconciliation_at TIMESTAMP,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_birth_completions_email ON birth_completions(customer_email);
CREATE INDEX idx_birth_completions_uuid ON birth_completions(uuid);
CREATE INDEX idx_birth_completions_tier ON birth_completions(tier);
CREATE INDEX idx_birth_completions_recon ON birth_completions(reconciliation_status);
```

**Write path** (CF Worker — modify existing `/api/birth/webhook` handler):
1. Receive Witness webhook.
2. INSERT into D1 `birth_completions` (idempotent ON CONFLICT (uuid) UPDATE).
3. Continue existing JSONL write for 30 days (parallel run for safety).
4. Fire Brevo `addToList` API call with tier-correct list ID (Spec 1 trigger).
5. Fire Telegram notification (existing `_notify_jared_birth_complete` behavior).

**Reconciliation worker** (new CF Worker scheduled cron, every 15 min):
1. Pull `birth_completions` WHERE `reconciliation_status='pending'`.
2. Pull recent PayPal subscriptions from PayPal API or D1 `paypal_subscriptions` table (if exists).
3. Match on `customer_email` (case-insensitive). If matched → UPDATE `reconciliation_status='matched'`, fill `paypal_subscription_id` + `paypal_payer_email`.
4. After 24hrs unmatched → flag as `orphan_birth` (got a birth but no payment found) → alert Aether on Telegram for review.
5. Reverse check: PayPal payments older than 24hrs with no `birth_completions` row → flag as `orphan_payment` (paid but never onboarded) → alert.

**Portal login tracking** (modify log server `/api/birth/portal-status/{container}` handler):
- On confirmed login event, UPDATE `birth_completions SET first_portal_login_at = CURRENT_TIMESTAMP WHERE first_portal_login_at IS NULL AND container_name = ?`, then `last_portal_login_at = CURRENT_TIMESTAMP`.
- Fire Brevo suppression webhook (Spec 1 dependency).

### Acceptance criteria
1. D1 schema deployed to `purebrain-customers` database, verified with `wrangler d1 execute --remote` showing all indexes.
2. CF Worker writes to D1 on every birth webhook AND continues JSONL parallel-write for 30-day safety period; verified by inserting a test birth and reading both sources.
3. Reconciliation worker runs every 15 min via cron trigger; backfill the last 30 days of JSONL into D1 as part of cutover (one-time migration script).
4. Orphan detection alerts Aether via Telegram within 24hrs (verified by deliberately creating an orphan via test).
5. Aether (or Jared) can run `wrangler d1 execute purebrain-customers --command "SELECT tier, COUNT(*) FROM birth_completions WHERE birth_completed_at > date('now','-7 day') GROUP BY tier"` and get accurate counts matching PayPal records.
6. Portal login tracking populates `first_portal_login_at` within 60 seconds of a real customer login event.

### Routing target
**ST# (dept-systems-technology)** — owns CF Worker, D1 schema, reconciliation worker, and log server modifications. No MA# work needed for this spec (MA# consumes the data via Spec 1 webhook).

### Effort estimate
**S-M** — D1 schema + writer is ~1 day. Reconciliation worker is ~1 day. JSONL backfill migration script is ~0.5 day. Portal login tracking modification is ~0.5 day. Testing + cutover ~1 day. Total: 3-4 dev days.

### Priority
**P0** — this is the foundational table. Spec 1 cannot ship reliably without it. Every financial close question, refund discussion, churn metric, and growth report needs this.

### Dependencies
- D1 database `purebrain-customers` exists (verify; create if not).
- PayPal subscription data accessible (either D1 table already, or PayPal API available with stored credentials).
- CF Worker deployment via `cf-deploy.py` ONLY (`wrangler pages deploy` is BANNED per constitutional rule).

---

## SPEC 3 — LinkedIn Cookie Refresh Workflow

### Problem statement
LinkedIn automation (icp-commenter, post scheduler, comment scheduler) periodically loses authentication when `li_at` cookies expire or get destroyed. Per ST# 2026-05-01 fix (`2026-05-01--linkedin-puresurf-session-idempotency-fix.md`), the destruction LOOP is now patched — sessions no longer overwrite cookies.json with login-page state. But cookies still expire naturally (~30 days), and Jared currently has to manually open `surf.purebrain.ai`, select profile `aether-linkedin`, and re-log into LinkedIn whenever this happens. There is no automated ping when cookies are about to expire, no one-tap refresh page, and no clear ownership of the recurring task.

### Proposed solution — DECISION: Plan A first, Plan B as future evolution

**Plan A (ship now, Telegram one-tap refresh)** — chosen because Plan B requires LinkedIn Developer App approval which is multi-week and not in our control. Plan A unblocks operations today.

**Components:**

1. **Cookie expiry monitor** (CF Worker scheduled cron, daily at 09:00 UTC):
   - For each LinkedIn profile in PureSurf (`aether-linkedin` and any future ones), call `GET /api/v1/profiles/{profile}/cookies`.
   - Find `li_at` cookie, parse expiry. If expiry is <7 days away OR cookie is missing → fire alert.
   - Also fire alert if any pre-flight check in `linkedin_icp_commenter.py` logs the "PRE-FLIGHT FAIL" line in the last 24hrs (tail the log).

2. **Telegram one-tap refresh flow**:
   - Alert fires to Jared via Telegram with a short message + a button-link to `https://refresh.purebrain.ai/linkedin?profile=aether-linkedin&token={one_time_token}`.
   - The refresh page (CF Pages, served from a `purebrain-tools` deployment):
     - Validates the token (single-use, 1hr TTL, stored in D1 `refresh_tokens` table).
     - Renders a single-page UI: "Click here to open PureSurf and refresh LinkedIn cookies." Button opens `https://surf.purebrain.ai` in new tab pre-set to the right profile.
     - Includes a 3-step checklist: (a) log into LinkedIn manually, (b) wait for cookie save, (c) click "Verify" button which pings the cookie monitor and confirms `li_at` is fresh.
     - On verify success, marks the token consumed and sends confirmation back to Aether's Telegram.

3. **Plan B path (not now, but documented)**:
   - The Plan-B independent OAuth path (`feedback_plan_b_oauth_means_independent.md`) means the team member running their own LinkedIn Developer App self-hosts. We do NOT collect their codes, Client IDs, or tokens — that defeats the point. Plan B is for OTHER team members operating their own LinkedIn presence, NOT for Pure Tech's `aether-linkedin` automation account.
   - For Pure Tech's own automation account, Plan A (cookie + manual periodic refresh) is the ONLY viable path until LinkedIn approves a developer app for our domain — which is a separate multi-week R&D track owned by PR# (dept-pure-research).

### Acceptance criteria
1. Cookie expiry monitor runs daily and successfully identifies a deliberately-expired test cookie within one cron cycle.
2. Telegram alert fires to Jared with a clickable refresh link when expiry < 7 days OR cookie missing.
3. Refresh page loads, validates one-time token, renders correctly on mobile (Jared often refreshes from phone).
4. After Jared completes manual login + verify click, cookie monitor confirms fresh `li_at`, sends confirmation to Telegram, and any blocked LinkedIn workflows (`linkedin_icp_commenter.py --discover`) succeed on next scheduled run.
5. Reduce "manual cookie refresh requests in Telegram" to zero unprompted asks per month — every refresh is initiated by the monitor, not by Jared discovering posts didn't go out.

### Routing target
**ST# (dept-systems-technology)** — owns the monitor (CF Worker cron), refresh page (CF Pages), D1 token table, and integration with PureSurf cookie API.
**Handoff to MA# (dept-marketing-advertising)** for adoption: MA# updates LinkedIn weekly engine SOP to include "check cookie monitor status" pre-flight, and confirms the new flow replaces ad-hoc Telegram requests.

### Effort estimate
**S** (small) — Monitor worker is ~0.5 day. Refresh page is ~0.5 day. D1 tokens table + Telegram integration is ~0.5 day. Testing + Jared walkthrough ~0.5 day. Total: 2 dev days.

### Priority
**P1** — high value, low effort. Currently blocking ~30% of LinkedIn operations (per recurring MA# blocker memos). Below P0 only because the destruction loop is already fixed (per ST# 2026-05-01 ship), so we're now in "natural expiry" mode rather than "constantly broken" mode.

### Dependencies
- ST# 2026-05-01 cookie destruction fix (already shipped).
- PureSurf cookie API available (already exists).
- Telegram bot infrastructure (already running per CLAUDE.md Step 0.5).
- One-time human re-login still required to seed initial cookies (residual blocker from 2026-05-01 fix — this is the FIRST refresh, then the monitor catches all subsequent expiries).

---

## Routing Dispatch Status

| Spec | Routing | Dispatch method | Dispatch sent |
|------|---------|-----------------|---------------|
| 1 — Email welcome | MA# (with ST# webhook) | Memo at `.claude/memory/departments/dept-marketing-advertising/2026-05-02--PD-spec-1-email-welcome-sequence.md` | YES |
| 2 — birth_completions D1 | ST# | Memo at `.claude/memory/departments/systems-technology/2026-05-02--PD-spec-2-birth-completions-d1.md` | YES |
| 3 — Cookie refresh | ST# (then MA# adopt) | Memo at `.claude/memory/departments/systems-technology/2026-05-02--PD-spec-3-linkedin-cookie-refresh.md` | YES |

Each dispatch memo includes the full spec, acceptance criteria, effort estimate, and a 24hr response request to Aether confirming pickup. Per `feedback_routed_items_need_verification_boop.md`, paired verification BOOPs are recommended at 48hrs against `operations-analyst` (OP#) for independent audit.

---

## Memory Written
Path: `.claude/memory/departments/dept-product-development/2026-05-02--chronic-flag-specs.md`
Type: teaching + operational
Topic: Three chronic 14+ flag issues converted to buildable PRDs and dispatched to routing departments. Breaks the analysis-theater pattern by attaching every flag to acceptance criteria + an owner + a deadline path.

## Files
- This spec: `/home/jared/projects/AI-CIV/aether/.claude/memory/departments/dept-product-development/2026-05-02--chronic-flag-specs.md`
- MA# dispatch (Spec 1): `/home/jared/projects/AI-CIV/aether/.claude/memory/departments/dept-marketing-advertising/2026-05-02--PD-spec-1-email-welcome-sequence.md`
- ST# dispatch (Spec 2): `/home/jared/projects/AI-CIV/aether/.claude/memory/departments/systems-technology/2026-05-02--PD-spec-2-birth-completions-d1.md`
- ST# dispatch (Spec 3): `/home/jared/projects/AI-CIV/aether/.claude/memory/departments/systems-technology/2026-05-02--PD-spec-3-linkedin-cookie-refresh.md`
