# IT# Analytics API Access Diagnosis — Clarity + GA4
**Date**: 2026-03-18
**Type**: diagnosis + pattern + resolution
**Topic**: Previous task incorrectly reported no access; GA4 fully working; Clarity has no server-side API

---

## Root Cause of False Report

A previous analytics task reported "cannot access Clarity or GA4." This was incorrect. The task likely:
1. Tried to curl `analytics.google.com` or `clarity.microsoft.com` directly (auth walls in browser UI)
2. Did not discover or use the existing `tools/analytics_api.py` module
3. Confused "dashboard login required" with "no API access"

---

## Actual Access Status (Verified 2026-03-18)

| Platform | Status | Method |
|----------|--------|--------|
| GA4 | WORKING — live data confirmed | Service account via Google Data API |
| Google Search Console | WORKING | Same service account |
| Microsoft Clarity | NO SERVER-SIDE API EXISTS | Client-side JS only — by design |

---

## GA4 — Fully Working

**Service account**: `aether-drive-access@aether-integration.iam.gserviceaccount.com`
**Key file**: `/home/jared/projects/AI-CIV/aether/.credentials/google-drive-service-account.json`
**Tool**: `/home/jared/projects/AI-CIV/aether/tools/analytics_api.py`
**Property ID**: `525007539`
**Measurement ID**: `G-86325WBT3P`

Health check run 2026-03-18: `{'ga4_token': True, 'ga4_data': True, 'gsc_token': True, 'gsc_data': True}`

Live data (last 7 days as of 2026-03-18):
- Total sessions: ~473 (Direct 372, Unassigned 28, Referral 26, Organic Search 24, Organic Social 23)
- Top pages: `/` (388 sessions), `/pay-test-sandbox-3/` (19), `/pay-test-awakened/` (18)
- Top countries: US 338, Canada 47, Pakistan 24, UK 11

---

## Microsoft Clarity — Architecture Reality

Clarity does NOT have a server-side REST API for data retrieval.

Per Microsoft's official documentation (clarity.microsoft.com):
- The "Clarity API" is a **client-side JavaScript API only** (`window.clarity(...)`)
- It is used to SET custom tags, events, identifiers FROM the browser
- It does NOT expose session recordings, heatmaps, or dashboard data via HTTP endpoints
- Dashboard access requires Microsoft OAuth login at clarity.microsoft.com

**This is by design. Clarity's data is only accessible via:**
1. The clarity.microsoft.com web dashboard (requires Jared to log in)
2. Clicking through recordings/heatmaps manually
3. CSV export from the dashboard

**The Clarity tag ID `viy9bnc56x` IS active and collecting data** — confirmed via GTM container `GTM-WTDXL4VJ`. Data exists in the dashboard. We just cannot pull it programmatically.

---

## What Jared Confirmed vs What Exists

Jared confirmed: "we have Clarity and GA4 access"
Reality:
- GA4: TRUE — service account gives full programmatic access
- Clarity: TRUE for dashboard access (Jared has it), but NO automated API exists

The previous task confused "no automated API" with "no access."

---

## Action Items (If Jared Wants Clarity Data)

1. Log into clarity.microsoft.com and grant purebrain@puremarketing.ai admin access
2. Export CSV data manually from the Clarity dashboard
3. OR accept that Clarity = dashboard-only and use GA4 for all programmatic reporting

---

## Key Files

- Analytics tool: `/home/jared/projects/AI-CIV/aether/tools/analytics_api.py`
- Service account: `/home/jared/projects/AI-CIV/aether/.credentials/google-drive-service-account.json`
- GA4 Measurement ID in .env: `GA4_MEASUREMENT_ID=G-86325WBT3P`
