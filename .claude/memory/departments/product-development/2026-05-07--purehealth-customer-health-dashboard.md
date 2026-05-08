# PureHealth — Customer Health Dashboard

**Department**: Product Development
**Date**: 2026-05-07
**Prepared by**: dept-product-development
**Product**: PureBrain.ai (admin surface; per-tenant slice for white-label clients)
**Related**: PureFunnel (2026-04-30 funnel telemetry spec) — *PureHealth is the retention layer to PureFunnel's acquisition layer.*

---

## Why This, Why Now

We sell PureBrain at $149 / $499 / $999 per month. That is recurring revenue at SMB price points where the math is brutal: a customer who churns at month 2 lost us money on acquisition. Yet right now, after a customer completes the constitutional birth pipeline (magic link → seed email → portal access → Brainiac modules), **we have zero per-customer visibility into whether they are getting value**. We see acquisition (PureFunnel) and we see infrastructure health (777, BOOP, Triangle), but we cannot answer the single most important question for a recurring product:

> "Which customers are about to churn, and why?"

Three signals make this Thursday's spec topic:

1. **Phil + Jared Tier 1/Tier 2 phased rollout strategy** (endorsed via 5/4 19:13 UTC email) names HR / Marketing / Ops / Sales / AI Advisory as Tier 1. Selling vertical pilots without a health surface is selling churn. Phil will ask "how do we know it's working for them?" and we will not have an answer.
2. **Brainiac Training has 3 modules shipped** with no completion telemetry exposed to admins. We literally do not know if anyone has finished module 1.
3. **The /insiders/awakened/ silent rot incident (Apr 29)** proved we don't notice when *acquisition* breaks. We have the same blind spot on *retention*: a customer could stop logging into their portal for 30 days and we would learn about it from a cancellation email, not a dashboard.

PureHealth is the surface that answers "is this customer going to renew?" before the customer themselves knows.

---

## Problem Statement

PureBrain is a recurring product. Recurring revenue depends on retention. Retention is measurable through engagement signals: portal logins, AI conversation volume, training completion, feature adoption, support touches, time-since-last-active. We capture none of these in a unified, query-able, alertable way. The data is scattered: portal access lives in the portal Worker, AI conversations live in customer containers, training progress lives in the Brainiac module state, payment status lives in PayPal logs. There is no single tenant-scoped record of "customer X is engaged at level Y, trending Z."

**Concrete consequences observed in the last 30 days**:
- We cannot tell Phil what % of Tier 1 pilot customers reached "first AI win" (whatever that is — undefined).
- We cannot trigger an automated check-in when a customer hasn't logged in for 14 days.
- We cannot tell Brainiac Training course-graders whether anyone is actually grading.
- We cannot calculate cohort retention by acquisition source (paid LinkedIn vs referral vs investor-gift code).
- We cannot give a white-label client (when the multi-tenant rollout lands) a view of *their* customers' health.

PureHealth is the unified retention data plane and the admin surface on top of it.

---

## Pre-Build Checklist Answers (Locked Apr 19 SOP)

1. **Software / AI Automation / Both?** → **SOFTWARE primary, AI secondary.** The data plane (collectors, schema, queries, alerts) is deterministic. AI is layered on top later for narrative summarization ("customer X looks at risk because…") but core service must run with zero LLM calls. AI add-on phases in v1.1.
2. **Must run without AI active?** → **YES.** Customer health signals must be collected and dashboards rendered whether Aether is online or compacted. Cron + Worker + D1, no Claude in the hot path.
3. **Internal or customer-facing?** → **BOTH.** Admin-facing first (PT + Aether + Chy + future white-label tenants). Customer-facing v1.2 — the customer themselves sees a "your AI partnership health" widget in their portal as a positive nudge.
4. **One-time or recurring?** → **RECURRING.** Continuous signal collection, daily aggregations, real-time score recomputation on event arrival.
5. **Real-time or periodic?** → **HYBRID.** Event ingest is real-time (<200ms). Health score recompute runs on event arrival (debounced 60s per customer). Cohort rollups run hourly. Churn-risk alerts fire within 5 minutes of threshold breach.
6. **Persistence/tracking needs?** → **YES — D1 primary.** New database `purebrain-health` with 4 tables (schema below). R2 archive for raw event log >180 days.
7. **Human configurable?** → **YES.** Admin UI lets ops define what "engagement" means per tenant (weights, thresholds, alert rules) without code deploy. Default profile ships with PT-tuned weights; tenants can override.

---

## Target Users

| User | Need | Frequency |
|---|---|---|
| **Jared (CEO)** | "Show me 5 customers most likely to churn this week, and why." | Weekly |
| **Aether (Co-CEO)** | Auto-trigger Chy outreach when health crosses red threshold. | Continuous |
| **SD# (Sales)** | Identify expansion-ready customers (high engagement → upsell candidates). | Weekly |
| **OP# (Ops/QA)** | Detect silent failure modes (e.g., portal up but customer hasn't logged in for 21d → maybe their magic link broke). | Daily |
| **MA# (Marketing)** | Cohort retention by acquisition source for ROI defense. | Monthly |
| **Phil / Tier 1 vertical leads** | Per-vertical health snapshots (HR pilots vs Marketing pilots) for case study selection. | Weekly |
| **Future white-label tenant admin** | View *their* customers' health in *their* portal, scoped to `tenant_id`. | Continuous |
| **The customer themselves (v1.2)** | "You've used your AI 14 times this week, completed 2 of 3 modules — your partnership is growing." | Weekly nudge |

---

## User Stories

1. **As Jared**, I want to open `admin.purebrain.ai/health/` and see a sortable table of all customers with their health score (0–100), trend arrow (last 14d), days-since-active, last-touch date, and tier — so I can answer "who needs attention?" in 30 seconds without grepping logs.

2. **As Aether (via cron)**, when a customer's health score drops below 40 OR drops 25+ points in 14 days, I want a Telegram alert with the customer name, their declining signals (e.g., "0 portal logins in 18d, 0 AI conversations, last touch: birth seed"), and a one-click "draft re-engagement message" link that pre-fills a Chy-tone email — so I can act on churn risk in <60 minutes, not learn about it at cancellation.

3. **As OP# verifier**, I want a daily "silent failure" report listing customers whose health score declined by >50% week-over-week with no obvious cause (active payment, no support ticket) — so I can route an investigation BOOP before the customer churns.

4. **As SD# (Chy/Aether)**, I want to filter the health table to "score 75+, on Foundation tier, 60+ days tenure" — so I can produce a weekly upsell candidate list without manual review.

5. **As Brainiac Training admin**, I want a per-customer view of module completion (M1 / M2 / M3 / certification earned), time-spent, and last-touched module — so I can see which modules drive activation and which fail to engage.

6. **As MA# (cohort analyst)**, I want to slice retention curves by acquisition source (UTM utm_source from PureFunnel: linkedin_post / referral / investor_code / agentmail / direct) — so I can defend marketing ROI and tell Jared which channels deliver retaining customers vs only acquiring them.

7. **As a white-label tenant admin (post-v1.0)**, I want my dashboard scoped to *only my customers*, with my own health weight profile, my own alert thresholds, and zero leakage of PT-internal customer data — so multi-tenant means tenant-isolated.

8. **As the customer themselves (v1.2)**, I want a "Partnership Health" widget in my portal showing my own engagement score with positive framing ("Your AI has learned 47 things about your business this month") — so the same data plane that protects PT also rewards the customer.

---

## Success Metrics

This is what "shipped right" looks like, measured 30 / 60 / 90 days after launch:

| Metric | Day 30 | Day 60 | Day 90 |
|---|---|---|---|
| Customers with computed health score | 100% of paid | 100% | 100% |
| Avg latency: event → score updated | <90s p95 | <60s p95 | <30s p95 |
| Churn-risk alerts fired in <5min of threshold breach | 95% | 99% | 99.5% |
| % of churn events preceded by ≥1 health alert | n/a (baseline) | 60% | 85% |
| Tenants using custom weight profile | 1 (PT) | 1 (PT) + 1 white-label test | 3+ |
| Re-engagement actions triggered from alerts → conversion | track baseline | 15% recovery | 25% recovery |
| Brainiac module completion visibility (% admins who can answer) | 100% | 100% | 100% |
| Customer-facing widget v1.2 NPS impact | n/a | +5 vs control | +10 vs control |

**The single number that proves leverage**: % of churn events preceded by ≥1 health alert. Goal: 85%+ at Day 90. If a customer churns and we had no warning, PureHealth failed for that customer.

---

## Functional Requirements

### Data collection (signal sources)
PureHealth ingests from existing PT systems via Worker endpoint `health-ingest`:
- **Portal Worker** — emits `portal_login`, `portal_session_duration` per customer, per session.
- **Birth pipeline** — emits `magic_link_opened`, `seed_email_received`, `first_portal_access`, `first_ai_conversation`.
- **AI conversation containers** (CF Worker layer, NOT container internals — see Constitutional Compliance below) — emits `ai_message_sent`, `ai_session_duration` aggregated per customer per day.
- **Brainiac Training state** — emits `module_started`, `module_completed`, `certification_earned`.
- **PayPal webhook receiver** (existing) — emits `payment_succeeded`, `payment_failed`, `subscription_canceled`.
- **Support inbox (AgentMail)** — emits `support_ticket_opened`, `support_ticket_resolved`.
- **Manual "human touch" log** — Chy/Aether/Jared can POST a `human_touch` event when they personally reach out, so the system knows who's been hand-held.

### Health score computation
Default PT weight profile (configurable per tenant):
```
score = 100 * weighted_sum([
  (recency_score, 0.25),       // days since last active, exponential decay
  (frequency_score, 0.20),     // portal logins / AI conversations per week
  (depth_score, 0.20),         // AI session duration, message count per session
  (training_score, 0.15),      // Brainiac module progression
  (payment_score, 0.10),       // payment in good standing
  (support_score, 0.10),       // open tickets / time-to-resolution
])
```
Score is recomputed on event arrival (debounced 60s per customer). Score history stored per-day for trend rendering.

### Trend & alert engine
- **Trend** — 14-day rolling delta surfaced in UI (▲ / ▼ / →) and machine-readable as `trend_14d_delta`.
- **Alert rules (configurable per tenant, defaults below)**:
  - 🔴 Score drops below 40 → immediate Telegram alert
  - 🔴 Score drops 25+ points in 14 days regardless of absolute level → immediate alert
  - 🟡 No portal login for 21 days → daily digest entry
  - 🟡 Brainiac module abandoned (started, no progress 14+ days) → weekly digest entry
  - 🟢 Score 75+ for 30+ days → upsell candidate weekly digest
  - 💀 Payment failed AND score <50 → P1 churn-imminent alert (Telegram + email Jared)

### Admin dashboard (`admin.purebrain.ai/health/`)
- **Overview tab**: tenant-scoped count of customers, distribution histogram of health scores, top 5 at-risk, top 5 expansion-ready, weekly trend.
- **Customer table**: sortable, filterable, exportable. Columns: name, email, tier, tenure, score, trend, days-since-active, last-touch, alert-status.
- **Customer detail page**: per-customer signal breakdown, score history sparkline, event timeline, "draft re-engagement" button (pre-fills Chy-tone outreach via existing email tooling).
- **Cohort tab**: retention curves by acquisition source, by tier, by tenure month.
- **Config tab**: alert rule editor, weight profile editor, integration status (which signals are flowing).
- **Auth**: existing magic-link admin flow; tenant scoping enforced at Worker level (every query parameterized by `tenant_id`).

### Customer-facing widget (v1.2 — phase 2, not v1.0)
Embedded in customer portal as "Partnership Health" card. Same data plane, positive framing, customer's own score only (never sees other customers, never sees PT-internal weights).

### API surface (read-only, for SD# / MA# automations)
- `GET /api/customers?tenant=X&min_score=Y&max_score=Z&trend=down`
- `GET /api/customer/{id}/signals` — signal breakdown
- `GET /api/cohorts/retention?source=linkedin_post&period=monthly`
- `POST /api/touch` — record a human touch event (Chy reached out, Jared called, etc.)

---

## Architecture (CF-native, constitutional)

- **CF Workers**:
  - `health-ingest` — POST `/event` from all signal sources, validates, writes D1, triggers debounced score recompute.
  - `health-scorer` — scheduled (every 60s) and event-triggered; recomputes scores for customers in dirty queue; writes `customer_health_scores` and `customer_health_history`.
  - `health-alert` — runs every 5 minutes; queries D1 for threshold breaches in last interval; sends alerts via existing `tg_send.sh` webhook + email via existing AgentMail.
  - `health-admin-api` — read API behind magic-link auth; serves dashboard.
  - `health-cohort-cron` — runs hourly; computes cohort rollups; writes `cohort_retention` materialized table.
- **CF Pages**:
  - Admin dashboard at `admin.purebrain.ai/health/` (static React/HTMX, fetches from `health-admin-api`).
- **D1**: Database `purebrain-health`, 4 tables (schema below).
- **R2**: `pt-health-archive` bucket; raw events older than 180d gzipped per-day per-tenant.
- **No containers**. All compute is CF Workers. **No customer container internals are read** — we read CF Worker layer aggregates only (per `feedback_nothing_in_containers_ever.md`).
- **Integrations**:
  - PureFunnel (4/30 spec) shares acquisition-source data via cross-D1 query or event stream (decision in build phase).
  - Magic link Worker emits to `health-ingest`.
  - PayPal webhook receiver emits to `health-ingest`.
  - Brainiac Training state Worker emits to `health-ingest`.
  - Existing TOS Dashboard sheet (`1bMshOr-Hf4PVh2fycj0t7U_rBxByzD-FyBdEoVRMgEs`) gets a daily auto-snapshot row (top 5 at-risk, top 5 expansion-ready) for Triangle visibility.

---

## Data Model

```sql
-- Raw event log (every signal, append-only)
CREATE TABLE health_events (
  id            TEXT PRIMARY KEY,           -- ULID
  tenant_id     TEXT NOT NULL,              -- 'pt' default; per white-label tenant
  customer_id   TEXT NOT NULL,              -- stable customer ID from birth pipeline
  event_type    TEXT NOT NULL,              -- portal_login | ai_message_sent | module_completed | etc.
  occurred_at   INTEGER NOT NULL,           -- unix ms
  source        TEXT NOT NULL,              -- which Worker / system emitted
  payload_json  TEXT,                       -- max 4KB
  created_at    INTEGER NOT NULL DEFAULT (unixepoch() * 1000)
);
CREATE INDEX idx_events_tenant_customer_time ON health_events(tenant_id, customer_id, occurred_at);
CREATE INDEX idx_events_tenant_type_time ON health_events(tenant_id, event_type, occurred_at);

-- Current health score per customer (single row per customer, updated on recompute)
CREATE TABLE customer_health_scores (
  tenant_id          TEXT NOT NULL,
  customer_id        TEXT NOT NULL,
  score              REAL NOT NULL,            -- 0-100
  recency_score      REAL, frequency_score REAL, depth_score REAL,
  training_score     REAL, payment_score REAL, support_score REAL,
  trend_14d_delta    REAL,                     -- score change over last 14d
  days_since_active  INTEGER,
  last_touch_at      INTEGER,                  -- last human touch event
  computed_at        INTEGER NOT NULL,
  alert_status       TEXT,                     -- ok | yellow | red | critical
  PRIMARY KEY (tenant_id, customer_id)
);
CREATE INDEX idx_scores_tenant_score ON customer_health_scores(tenant_id, score);

-- Daily score history (for trend rendering)
CREATE TABLE customer_health_history (
  tenant_id    TEXT NOT NULL,
  customer_id  TEXT NOT NULL,
  date         TEXT NOT NULL,                -- YYYY-MM-DD
  score        REAL NOT NULL,
  signals_json TEXT,                         -- snapshot of sub-scores
  PRIMARY KEY (tenant_id, customer_id, date)
);

-- Configurable alert rules and weight profiles (per tenant)
CREATE TABLE health_config (
  tenant_id          TEXT PRIMARY KEY,
  weights_json       TEXT NOT NULL,          -- {recency:0.25, frequency:0.20, ...}
  thresholds_json    TEXT NOT NULL,          -- {red:40, drop_14d:25, ...}
  alert_channels     TEXT NOT NULL,          -- ['telegram', 'email']
  updated_at         INTEGER NOT NULL,
  updated_by         TEXT
);
```

**Multi-tenant from day one**: every table has `tenant_id` as part of primary key or required indexed column. Every query parameterized by `tenant_id`. Worker auth resolves the caller's tenant scope; cross-tenant queries blocked at the Worker layer.

---

## Constitutional Compliance Check

| Rule | Compliance |
|---|---|
| Birth pipeline / magic link / seed flow / `/insiders/` FROZEN | **No changes.** PureHealth *consumes* events emitted by these systems via webhook, never modifies them. |
| `/insiders/awakened/` payment guard ALL 10 pages | N/A — admin surface, not customer payment page. |
| Pre-build 7 questions | Answered above. SOFTWARE-primary, runs without AI, both internal & customer-facing, recurring, real-time, D1 persistence, human-configurable. ✅ |
| NEVER local deploy | Build will use CF Pages git pipeline. Spec mandates `cf-deploy.py` only, no Wrangler Pages. ✅ |
| NEVER deploy to customer containers | We read CF Worker aggregates, never SSH into containers. ✅ |
| NOTHING IN CONTAINERS | All state in D1, all compute in Workers. ✅ |
| Multi-tenant always | `tenant_id` is required column on every table; every query scoped. ✅ |
| Voice via voice.purebrain.ai only | N/A — text dashboard. If voice readouts of health summary land later, they go through voice.purebrain.ai. |
| Wrangler ban (Pages) | Pages component shipped via cf-deploy.py. Workers shipped via `wrangler deploy`. ✅ |

---

## Risks & Mitigations

| Risk | Mitigation |
|---|---|
| **Health score becomes a vanity number** that doesn't predict churn | Day 60 success metric explicitly measures "% of churn preceded by alert." If <60%, recalibrate weights from observed churn data, not designer intuition. |
| **Alert fatigue** (too many yellows, ignored) | Default thresholds are conservative; tune from real data after 30 days. Weekly digest for non-urgent, immediate Telegram only for red/critical. |
| **Privacy leak across tenants** in white-label deployment | Worker auth resolves tenant_id; every query parameterized; integration test suite specifically attempts cross-tenant reads and expects rejection. CTO-mandated review before white-label launch. |
| **Container internal data desire** (engineers will want to read AI conversation contents for "depth" signal) | Spec **prohibits** this. Depth signal = aggregated metadata only (message count, session duration) emitted by Worker layer that brokers container access. Constitutional. |
| **Scope creep into "AI customer success agent"** in v1.0 | v1.0 is dashboard + alerts. AI narrative summaries ("here's why customer X is declining") is v1.1, requires separate spec. |
| **Customer-facing widget feels like surveillance** | v1.2 framing must be positive ("your AI has learned 47 things this month"), opt-in, with full transparency on what's measured. UX review required before v1.2 ship. |
| **Brainiac signal coupling** — if Brainiac state Worker doesn't emit reliably, training_score is broken | Build phase 1 includes Brainiac state-Worker emission upgrade as dependency, not assumption. |
| **Cohort cron at scale** could timeout on D1 | Hourly cron with materialized rollup table; full table scans avoided; CTO review of query plans before ship. |

---

## What NOT to Build (Scope Discipline)

- ❌ **AI-generated churn narrative in v1.0.** Numbers and signals only. Narrative is v1.1.
- ❌ **Predictive ML model** ("ML predicts customer X churns in 7 days"). Rules-based scoring first. ML candidacy revisited at Day 90 with real churn data.
- ❌ **Customer-facing widget in v1.0.** Admin dashboard first. Customer widget v1.2.
- ❌ **Reading customer container internals.** Constitutional. Worker-layer aggregates only.
- ❌ **Modifying birth pipeline or payment pages** to emit new events. They already emit enough via webhooks; if more is needed, that's a separate constitutional review.
- ❌ **Real-time streaming dashboard.** Polling at 30s is fine for v1.0.
- ❌ **Multi-product support** (PureSurf health, voice.purebrain.ai health) in v1.0. PureBrain core only. Other products can adopt the same data plane in v2.0.
- ❌ **Mobile app.** Responsive web is enough for v1.0.

---

## Build Phasing (so ST# can route)

**v1.0 (target: ~3 weeks of ST# capacity)**
- Phase 1 — Data plane: D1 schema, `health-ingest` Worker, signal source upgrades (portal Worker, magic link Worker, PayPal webhook, Brainiac state Worker emit events). Backfill from existing logs.
- Phase 2 — Score engine: `health-scorer` Worker, default PT weight profile, score history, trend computation.
- Phase 3 — Alerts: `health-alert` Worker, Telegram + email integration, threshold rules, daily digest.
- Phase 4 — Admin dashboard: CF Pages site, magic-link auth, customer table, customer detail, cohort tab.
- Phase 5 — Multi-tenant hardening: cross-tenant query block tests, white-label test profile, security audit.

**v1.1 (later)**
- AI narrative summaries on customer detail ("at risk because: signal A declined, signal B flat")
- Auto-draft re-engagement message generation
- Cohort dashboard expansions (retention curves with statistical confidence)

**v1.2 (later)**
- Customer-facing "Partnership Health" widget in customer portal
- Opt-in transparency UI

---

## Specialist Routing (for ST# when this gets dispatched)

- **CTO** — Pre-build architecture review (mandatory gate per `feedback_cto_pre_build_architectural_review.md`). Specifically: D1 schema sanity, cross-tenant isolation strategy, score recompute debouncing, container-data-access prohibition enforcement.
- **full-stack-developer** — Worker implementation (ingest, scorer, alert, admin-api), D1 migrations, dashboard frontend.
- **api-architect** — `health-admin-api` shape and pagination strategy.
- **security-engineer-tech** — Multi-tenant isolation audit, magic-link auth integration, integration tests that attempt cross-tenant reads (expect rejection).
- **qa-engineer** — Functional test suite, alert rule edge cases, score computation determinism.
- **test-architect** — Integration test patterns for event-sourced systems with eventual consistency.
- **feature-designer** — Admin dashboard UX flow, customer-detail information architecture, customer-facing widget framing (v1.2).
- **ui-ux-designer** — Visual design, brand consistency with admin tools, sparkline / trend rendering.

---

## Open Questions (need Jared / CTO input before build)

1. **Customer ID stability** — what is the canonical `customer_id` across portal Worker, PayPal, Brainiac, magic link? If it varies, PureHealth needs a customer-identity reconciliation layer first. (CTO question.)
2. **PureFunnel <-> PureHealth integration model** — shared D1, event stream, or independent reads? Funnel is acquisition, Health is retention; the customer ID join needs deciding. (CTO + 4/30 spec author.)
3. **Default churn-risk threshold** — score <40 is a guess. Should we run for 30 days collecting baseline before turning alerts on, or alert from day one with conservative defaults? (Jared call — risk preference.)
4. **White-label tenant onboarding** — when a Tier 1 vertical client (HR vertical, etc.) wants their own tenant slice, what is the provisioning flow? (Phil + Jared strategic input.)
5. **Brainiac certification visibility to customer** — does the customer see their own certification state? If yes, this affects v1.2 widget scope. (Product call.)

---

## Decision / Recommendation

**Build PureHealth v1.0 as the next major product surface after the LinkedIn pipeline situation is resolved.** This is the missing retention data plane underneath the recurring-revenue business model, and it's the answer to Phil's "how do we know it's working?" question for the Tier 1 phased rollout.

**Sequencing**:
- **Don't start while LinkedIn pipeline is in outage** — ST# capacity is committed there. PureHealth needs CTO + full-stack + security at full attention.
- **Pre-build CTO review the week LinkedIn is closed** — answer the 5 open questions above.
- **3-week build window** for v1.0 once CTO approves.
- **Day 30 / 60 / 90 success metric review** baked into spec.

**The single number that matters**: % of churn events preceded by ≥1 health alert. 85%+ at Day 90 = PureHealth shipped right.

---

## Files

- Saved to: `/home/jared/projects/AI-CIV/aether/exports/portal-files/2026-05-07-pd-feature-spec-purehealth-customer-health-dashboard.md`
- Memory copy: `/home/jared/projects/AI-CIV/aether/.claude/memory/departments/product-development/2026-05-07--purehealth-customer-health-dashboard.md`

---

## Memory Written

Path: `.claude/memory/departments/product-development/2026-05-07--purehealth-customer-health-dashboard.md`
Type: teaching (transferable PRD pattern: retention-layer companion to acquisition telemetry)
Topic: PureHealth — per-customer health score & churn-risk alerting; multi-tenant from day one; constitutional CF-only architecture; rules-based scoring before ML
