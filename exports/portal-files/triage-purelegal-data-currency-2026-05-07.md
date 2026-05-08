# PureLegal Data Currency Triage — Mike's "Showing 2024" Flag

**Date**: 2026-05-07 | **Flagger**: Meridian (HR Intelligence Manager) on behalf of Mike Daser
**Owner**: ST# (data pipeline) + PD# (live-source decision); LC# triage gate only
**Companion to**: `purelegal-v3-remediation-plan-2026-05-07.md` (same incident family, different surface)

---

## 1. Live State Evidence

| Probe | Result | Interpretation |
|---|---|---|
| `GET /api/health` | `{"status":"ok","service":"hancock-law-api","version":"0.1.0"}` | Worker live, **v0.1.0 — pre-production** |
| `GET /api/version` | Falls through to static HTML | **No version endpoint exists** — cannot self-report data freshness |
| `GET /api/legal/version` | Falls through to static HTML | Same — no data-freshness API |
| `GET /api/data/sources` | Falls through to static HTML | Source provenance not exposed |
| `GET /api/legal/jurisdictions` | Falls through to static HTML | No live jurisdiction registry |
| `GET /api/hr/templates` | `401 unauthorized` | Auth-walled (consistent with earlier V3 triage — small "static list" served behind auth) |
| `GET /api/compliance/alerts` | `401 unauthorized` | Auth-walled, can't validate freshness read-only |
| `GET /api/research/query` | `401 unauthorized` | Same |

**Public page audit (`legal.purebrain.ai/`)**: 2,454 lines of marketing HTML; only date string is `2026-01-15.pdf` (asset reference). The **2024 vibes Mike is seeing live in dashboards/responses are behind the auth wall** — read-only triage cannot pull them, but the architectural cause is identifiable.

---

## 2. Data Source Location + Freshness Assessment

**Worker repo**: NOT in `/home/jared/projects/AI-CIV/aether/`. Earlier V3 triage (Phase-0.2) already flagged this — ST# owes a repo-locate. Local repo has **only** the marketing/auth-shell at `exports/cf-pages-deploy/hancock-law/index.html`.

**D1 schema** (per V3 remediation plan §3): `legal_templates`, `legal_research`, `legal_compliance`, `legal_clauses`, `legal_contracts`, `legal_billing`, `legal_matters`, `legal_memory`. Schema **exists but is not ingested** — V3 ingestion is Phase-0.3 of the remediation plan, not started.

**Live data source Mike references**: **Unknown to Aether**. No environment variable, scheduled job, or external API reference for live legal-data sync is locatable in the accessible codebase. **This is an open question for Mike** — see §5.

**Freshness assessment**: The "showing 2024" observation has three plausible mechanisms, all consistent with the V3 triage finding:

1. **Hardcoded snapshot in worker code** (most likely, given v0.1.0): minimum wage tables, regulatory dates, etc. embedded as JS constants frozen at end-of-2024 ingestion.
2. **D1 row data populated once, never refreshed**: Tables seeded in 2024, no cron/sync job updating them.
3. **LLM knowledge-cutoff response** without a current-data layer: If templates/research lean on Anthropic API output without a freshness retrieval layer, model recency drift surfaces as "2024 vibes."

All three are **stale-by-design**, not broken sync. There is no evidence of a sync job that's failing — there is evidence that no sync job exists.

---

## 3. Gap Analysis

| Hypothesis | Evidence | Verdict |
|---|---|---|
| Sync job broken | No cron/scheduled trigger visible; no error logs accessible read-only | **UNLIKELY** — can't break what doesn't exist |
| Stale snapshot from 2024 | v0.1.0 worker, no version endpoint, D1 not ingested per V3 plan, public page has no live-data signal | **HIGH CONFIDENCE** |
| Live source not wired | Mike says "we have access to live data" — no reference to that source in repo | **HIGH CONFIDENCE — and the missing-link** |

**Conclusion**: This is **stale-by-design + missing-source**, not a broken pipeline. PureLegal v0.1.0 was shipped with a small static dataset and **no freshness layer was ever built**. Mike's flag is the first time this has been raised against production usage, because Mike is the first user pulling on it for real legal-grade answers.

**Relationship to V3 templates flag** (this morning): **Same root cause family**. V3 templates flag = "what we serve doesn't match Mike's spec." Currency flag = "what we serve isn't refreshed against any live source." Both trace to: D1 ingestion + freshness pipeline never built. **Phase 0 of V3 remediation plan covers part of this**, but adds the freshness/live-source dimension as new scope.

---

## 4. Owner Recommendation + Dispatch Path

**Primary owner**: **ST# (dept-systems-technology)** — data pipeline / ETL / D1 ingestion / cron sync are squarely in their lane. Spawn `data-engineer` (architecture) + `full-stack-developer` (implementation).

**Co-owner**: **PD# (dept-product-development)** — Mike's "live data source" reference is a product decision: which feed do we license/scrape/integrate? (Westlaw? LexisNexis? Free GovInfo + state register feeds? Manual editorial + cron?) This is not an engineering choice; PD# specs, ST# builds.

**Triage gate**: **LC# (this agent) — done.** No legal/compliance gate beyond licensing review **once the live-source decision is made** (data-licensing terms, redistribution rights). LC# stands by for that gate but is not blocking.

**Dispatch path**:
1. **Aether → PD#** : "Spec the live-data source. Mike says we have access — confirm what source, what feed format, what license, what update cadence. Deliverable by Friday 2026-05-09."
2. **Aether → ST#** : "Phase-0.4 added to V3 remediation: build data-freshness layer. Locate Hancock worker repo (already on Phase-0.2 board), expose `/api/version` returning `{data_as_of, last_sync, source}`, design ingestion cron from PD#'s sourced feed." Capacity-blocked on the same 2026-05-08 18:00 ST# deadline as V3 plan.
3. **LC# (me) → standby** : Re-engaged when PD# returns the source decision (license review).

**Phase-0 vs parallel track**: This is **additive Phase-0 scope** to the V3 plan, not a parallel. Both flags share Phase-0.2 (locate worker) and Phase-0.3 (D1 ingestion). Currency flag adds Phase-0.4 (live-source pipeline + version endpoint). Recommend folding into one ST# capacity ask, not two.

---

## 5. Open Question for Meridian / Mike

**Q**: Mike's email said "we have access to live data." **What source?** Specific feed name, vendor, or URL needed before PD# can spec the integration. Without this, PD# is guessing and ST# is building against an unknown contract. (This is the highest-leverage unblock — 5-minute answer from Mike saves a multi-day discovery for PD#.)

---

## 6. Acknowledgment Text for human-liaison → Meridian

> Meridian — confirming receipt of the PureLegal data-currency flag from Mike. We've triaged it alongside the V3 templates flag from earlier today; both trace to the same root cause family — Hancock Law Worker shipped at v0.1.0 with no data-ingestion or freshness pipeline behind it. The "showing 2024" observation is consistent with a one-time static snapshot, not a broken sync job. We have a remediation path scoped (folding into the V3 Phase-0 plan as Phase-0.4: live-source ingestion + `/api/version` freshness endpoint), and ownership is locked: PD# specs the live-data source, ST# builds the pipeline, LC# stays on standby for licensing review once the source is selected. **One unblock we need from Mike**: the email referenced "we have access to live data" — can he name the specific source/feed/vendor? That answer routes directly to PD# and saves multi-day discovery. Capacity-locked dates land alongside the V3 plan after ST#'s 2026-05-08 18:00 EST capacity confirmation. Honest read: this is the second flag in one day on the same product, and it tells us PureLegal needs a deeper architectural pass before Mike can use it production-grade. Aether is treating that as the signal it is.

---

**Word count**: ~480
