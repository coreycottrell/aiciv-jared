# PureBrain Funnel Telemetry Service ("PureFunnel")

**Department**: Product Development
**Date**: 2026-04-30
**Prepared by**: dept-product-development
**Product**: PureBrain.ai (cross-property — purebrain.ai, social.purebrain.ai, surf.purebrain.ai, voice.purebrain.ai, 777.purebrain.ai, /insiders/, /refer/, future client portals)

**Origin Signal**: SEO/Analytics Audit 2026-04-15 — *"No `form_submit`, `purchase`, `sign_up` events firing — flying blind on funnel"* + chronic "form tracking" issue (14+ self-analysis flags) + payment guard recently caught `/insiders/awakened/` rotted to wrong tier with no detection (Apr 29).

---

## Problem

We are flying blind on the funnel. GA4 shows 2,902 sessions in 30 days but **zero conversion events** because form submits, magic-link clicks, payment-page CTAs, and signup completions aren't wired to a single source of truth. When `/insiders/awakened/` silently rotted to a wrong-tier homepage clone for an unknown number of days, no telemetry alerted us — we found it only when the nightly onboarding-spec guard caught the constitutional violation. Every PT property fires its own ad-hoc fetch, payment pages have inconsistent tracking, and there is no D1-backed event log we own. Marketing can't measure CTR-to-signup, Sales can't attribute revenue to source, Product can't see drop-off, and we can't prove ROI to investors. This is the foundational data plane every other dashboard depends on.

---

## Pre-Build Checklist Answers

1. **Software / AI Automation / Both?** → **SOFTWARE.** This is a deterministic event collector + storage + query layer. AI may consume the data later (e.g., cohort summaries) but the core service must run with zero LLM calls.
2. **Must run without AI active?** → **YES.** Customers convert at 3am whether Aether is awake or not. Worker + D1 must serve every request.
3. **Internal or customer-facing?** → **BOTH.** Customer-facing (invisible JS beacon on every page), internal (admin dashboard reading the data). Customer side must be sub-50ms, GDPR-friendly, no PII leak.
4. **One-time or recurring?** → **RECURRING.** Every page view, form submit, payment intent, magic-link click — thousands per day at scale.
5. **Real-time or periodic?** → **REAL-TIME.** Events ingested synchronously (<100ms p95). Aggregations run periodically (hourly cron Worker).
6. **Persistence/tracking needs?** → **YES — D1 primary store** (`telemetry_events`, `telemetry_sessions`, `telemetry_conversions`), R2 for raw archive after 90 days.
7. **Human configurable?** → **YES.** Admin UI to define new event types, configure conversion goals, and tag campaigns without code deploys.

---

## User Stories

1. **As Jared (CEO)**, I want to see a single dashboard of "signups today / paid conversions today / revenue by source" so I can answer the investor question "what's working?" in one screen.
2. **As MA# (Marketing)**, I want to attribute every paid customer to their first-touch UTM source and last-touch CTA so I know which LinkedIn post / blog / referrer drives revenue.
3. **As OP# (Ops/QA)**, I want a real-time alert when a payment page's "Buy" button stops firing the `payment_intent_created` event so silent rot like the `/insiders/awakened/` incident is caught in <5 minutes, not 14 days.
4. **As SD# (Sales)**, I want to query "all leads from `agentmail` tier in the last 7 days who didn't complete onboarding" so I can hand them to Chy for re-engagement.
5. **As a future client tenant** (when we white-label PureBrain), I want my own isolated funnel data scoped by `tenant_id` so my numbers never mix with PT or other clients.

---

## Functional Requirements

- Single JS beacon (`<script src="https://telemetry.purebrain.ai/p.js">`) auto-loaded on every CF Pages site.
- Beacon emits: `page_view`, `form_submit`, `cta_click`, `payment_intent_created`, `payment_completed`, `magic_link_clicked`, `signup_completed`, `custom`.
- Auto-captures: UTM params, referrer, anonymized IP (truncated to /24), session ID (cookie, 30d), tenant_id (default `pt`, overridable per page), page URL, event type, custom payload (max 4KB).
- Worker ingest endpoint: validates schema, writes to D1, mirrors to GA4 via Measurement Protocol (server-side, bypasses ad blockers).
- Multi-tenant from day one: `tenant_id` is required column on every table, every query filters by it, admin UI gated by tenant.
- Admin dashboard at `https://admin.purebrain.ai/funnel/` (auth via existing magic-link flow): live event stream, daily/weekly conversion funnel, source attribution, alert config.
- Anomaly detection: hourly cron Worker compares last hour's event volume per `(tenant_id, event_type, page)` against trailing 7-day baseline; alerts to Telegram if drop >70%.
- Backfill API: one-time script to ingest historical PayPal payment logs (`logs/purebrain_payments.jsonl`) into D1 so we have continuity.

---

## Architecture

- **CF Pages**: Beacon JS file (`/p.js`) hosted at `telemetry.purebrain.ai`, ~3KB minified, no dependencies.
- **CF Workers**:
  - `funnel-ingest` — POST `/event` (and POST `/batch` for bundling) → validates → writes D1 → forwards to GA4.
  - `funnel-admin-api` — read API for dashboard (GET `/events`, `/funnels`, `/sources`, `/alerts`).
  - `funnel-cron-anomaly` — runs hourly, queries D1, checks deltas, sends Telegram alerts via existing `tg_send.sh` webhook.
- **D1**: `purebrain-funnel` database, 3 tables (schema below).
- **R2**: `pt-telemetry-archive` bucket, raw events older than 90d gzipped per-day.
- **Integrations**: GA4 Measurement Protocol (existing `GA4_API_SECRET` env var), PayPal webhook receiver writes to same D1 via `funnel-ingest` `/event` endpoint with shared HMAC secret, magic-link Worker writes `magic_link_clicked` events.

---

## Data Model

```sql
CREATE TABLE telemetry_events (
  id              TEXT PRIMARY KEY,            -- ULID
  tenant_id       TEXT NOT NULL DEFAULT 'pt',
  session_id      TEXT NOT NULL,
  event_type      TEXT NOT NULL,               -- page_view | form_submit | cta_click | etc.
  page_url        TEXT NOT NULL,
  referrer        TEXT,
  utm_source      TEXT, utm_medium TEXT, utm_campaign TEXT, utm_content TEXT, utm_term TEXT,
  ip_truncated    TEXT,                         -- /24 only
  user_agent      TEXT,
  payload_json    TEXT,                         -- max 4KB, custom event data
  email_hash      TEXT,                         -- SHA-256 of email if known (no PII stored)
  ts              INTEGER NOT NULL              -- unix ms
);
CREATE INDEX idx_events_tenant_ts ON telemetry_events(tenant_id, ts DESC);
CREATE INDEX idx_events_session ON telemetry_events(session_id);
CREATE INDEX idx_events_type_page ON telemetry_events(tenant_id, event_type, page_url, ts DESC);

CREATE TABLE telemetry_sessions (
  session_id      TEXT PRIMARY KEY,
  tenant_id       TEXT NOT NULL DEFAULT 'pt',
  first_seen_ts   INTEGER NOT NULL,
  last_seen_ts    INTEGER NOT NULL,
  first_utm_source TEXT, first_utm_campaign TEXT,
  landing_page    TEXT,
  email_hash      TEXT,
  converted       INTEGER DEFAULT 0             -- 0|1
);

CREATE TABLE telemetry_conversion_goals (
  id              TEXT PRIMARY KEY,
  tenant_id       TEXT NOT NULL,
  name            TEXT NOT NULL,                -- "Awakened Signup", "Paid Conversion"
  match_event     TEXT NOT NULL,
  match_payload   TEXT,                         -- JSON path query, e.g. $.tier == 'awakened'
  value_usd       REAL,
  active          INTEGER DEFAULT 1
);
```

---

## API Surface

| Method | Path | Auth | Body / Response |
|---|---|---|---|
| POST | `/event` | HMAC + origin allowlist | `{tenant_id, event_type, page_url, payload?, session_id}` → `{id, ok:true}` |
| POST | `/batch` | HMAC | `{events: [...]}` (max 50) → `{accepted, rejected}` |
| GET | `/admin/events` | Magic-link cookie | Query: `?tenant=pt&type=form_submit&from=ts&to=ts` → paginated list |
| GET | `/admin/funnel` | Magic-link cookie | Query: `?tenant=pt&goal_id=X&window=7d` → step-by-step drop-off counts |
| GET | `/admin/sources` | Magic-link cookie | Source attribution table (first/last touch) |
| POST | `/admin/goals` | Magic-link cookie | Create/edit conversion goal |
| GET | `/admin/alerts` | Magic-link cookie | List anomalies in last 24h |

All `/admin/*` calls require `X-Tenant-Id` header matching the user's tenant scope.

---

## UI Sketch

**Admin Dashboard** (`admin.purebrain.ai/funnel/`):

- **Header**: tenant switcher (Jared sees all PT tenants; future clients see only theirs), date-range picker, refresh.
- **Top row — 4 KPI tiles**: Sessions (24h), Form Submits, Paid Conversions, Revenue. Each shows delta vs prior period.
- **Middle — Funnel chart**: horizontal bar showing Visit -> CTA Click -> Form Submit -> Payment Intent -> Paid, with drop-off % between each step.
- **Left side — Source attribution table**: rows = utm_source, columns = sessions, conversions, conversion %, revenue.
- **Right side — Live event stream**: last 50 events, auto-scrolling, color-coded by type.
- **Bottom — Anomaly feed**: ongoing alerts from cron Worker (red = drop >70%, yellow = drop 40-70%).
- **Settings tab**: define conversion goals, manage alert thresholds, view beacon snippet to install on new pages.

---

## Success Metrics

1. **Coverage**: 100% of PT customer-facing pages emit `page_view` within 2 weeks of ship; 100% of payment pages emit `payment_intent_created`.
2. **Detection speed**: A simulated `/insiders/*` page rot is detected by anomaly cron within 60 minutes (vs 14 days for the Apr 29 incident).
3. **Attribution coverage**: ≥80% of paid conversions in month 1 have a known first-touch `utm_source` (currently effectively 0%).

---

## Out of Scope (v1)

- AI-driven cohort summaries / LLM-written insights — that's v2.
- Per-user identity stitching across devices (we use session cookie only).
- Public API for third-party tenants — internal PT only at launch.
- Replacing GA4 — we mirror to GA4, not replace.
- Heatmaps / session replay (Clarity already covers this).

---

## Risks

1. **Privacy/GDPR**: Storing event data with IP could trigger compliance issues. **Mitigation**: truncate IP to /24, hash all emails, no raw PII in payloads, document in privacy policy, give users a `?notrack=1` opt-out.
2. **Worker cost runaway**: 10K events/day at scale could blow CF Workers free tier. **Mitigation**: batch endpoint (50 events/req), D1 batch writes, monitor weekly, budget alert at $20/mo.
3. **Beacon breaks pages**: A bug in `p.js` could break every PT property simultaneously. **Mitigation**: try/catch wrapping all beacon code, async load with `defer`, automated smoke test on staging before any beacon deploy, version pinning per property.

---

## Implementation Estimate (ST# — BUILD → SECURITY → QA → SHIP)

- **BUILD** (full-stack-developer): 4 days — D1 schema, 3 Workers, beacon JS, admin dashboard skeleton.
- **SECURITY** (security-engineer-tech): 1 day — HMAC validation, origin allowlist, rate limit, PII audit, opt-out test.
- **QA** (qa-engineer): 1.5 days — beacon smoke test on all 10 payment pages + 20 content pages, anomaly cron simulation, multi-tenant isolation test.
- **SHIP** (devops-engineer): 0.5 day — CF Pages deploy via git (NEVER local), DNS for `telemetry.purebrain.ai` and `admin.purebrain.ai`, GA4 Measurement Protocol secret rotation, Telegram alert webhook wired.

**Total: 7 working days** end-to-end, parallelizable to ~5 calendar days with overlap.

## Decision / Recommendation

Build PureFunnel as the next ST# sprint after current /refer/ stabilization wraps. It is the foundation every other dashboard (CEO, MA#, SD#, investor) depends on, closes the chronic "form tracking" wound, and would have caught the Apr 29 `/insiders/awakened/` rot in under an hour.

## Files
- Spec: `/home/jared/projects/AI-CIV/aether/exports/portal-files/2026-04-30-pd-feature-spec-funnel-telemetry-service.md`
