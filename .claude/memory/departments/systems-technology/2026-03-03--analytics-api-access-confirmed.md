# Analytics API Access Confirmed — Full Diagnosis Complete
**Date**: 2026-03-03
**Type**: pattern + data-state + gotcha
**Topic**: GA4 and Search Console fully working via service account; Clarity needs Jared action; SEMRush has browser automation

---

## Access Status (Permanent Reference)

| Platform | Access Method | Status |
|----------|--------------|--------|
| GA4 | Service account (SA) via analyticsdata.googleapis.com | WORKING |
| Search Console | Service account via webmasters/v3 | WORKING |
| Microsoft Clarity | Microsoft Azure AD OAuth required | BLOCKED — needs Jared |
| SEMRush | Browser automation (Playwright) | WORKING headlessly |
| SEMRush API | Needs API key from account settings | NOT YET CONFIGURED |

## Key IDs (Lock These In)
- GA4 Account ID: `384811174` (display: PureBrain.ai)
- GA4 Property ID: `525007539` (display: purebrain.ai)
- GA4 Measurement ID: `G-86325WBT3P` (NOT the property ID — different thing)
- GSC Site URL: `sc-domain:purebrain.ai`
- Clarity Project: `viy9bnc56x`
- GTM Container: `GTM-WTDXL4VJ`

## Reusable Analytics Module
`/home/jared/projects/AI-CIV/aether/tools/analytics_api.py`

Functions:
- `ga4_report(dimensions, metrics, date_range, ...)` — any GA4 report
- `ga4_realtime()` — live active users
- `ga4_parse_rows(response)` — parse to list of dicts
- `get_ga4_summary(days=30)` — quick overview
- `gsc_query(dimensions, days=28, ...)` — Search Console data
- `gsc_list_sitemaps()` — sitemap indexing status
- `get_gsc_summary(days=28)` — quick overview
- `health_check()` — verify both APIs work

Health check confirmed working 2026-03-03.

## Real Traffic Data (30 days to 2026-03-03)
- Total sessions: ~633
- Total users: ~492
- Channels: Direct 474, Organic Social 62, Referral 50, Search 18
- Germany anomaly: 147 sessions, 147 users (likely bot/VPN)
- Real organic US traffic: ~250 sessions
- LinkedIn driving 20 homepage visits
- Microsoft Teams referral: 15 visits to /why-purebrain/ (B2B signal)

## GSC Indexing Status
- 73 pages submitted via sitemap
- GSC shows 0 indexed in sitemap report
- BUT homepage has 19 clicks from GSC = homepage IS indexed
- GSC sitemap reports lag 2-4 weeks for new domains — this is normal
- Sitemaps last downloaded by Google: 2026-03-03 (active crawling)

## Events Currently in GA4
Auto-tracked: page_view, session_start, first_visit, scroll, user_engagement
Auto-tracked by Enhanced Measurement: form_start (148), form_submit (67)
Missing: chatbox_opened, name_captured, email_captured, onboarding_complete, pricing_page_view

## Critical GA4 Fact
- Measurement ID (G-86325WBT3P) is NOT the Property ID
- Property ID is numeric: 525007539
- Always use property ID for Data API calls
- Measurement ID is only for JS tag configuration

## Jared Actions Needed
1. Clarity: add purebrain@puremarketing.ai as Admin in clarity.microsoft.com settings
2. GTM write access: add purebrain@puremarketing.ai with Edit role in tagmanager.google.com
3. GA4 conversions: mark events as conversions after GTM events are live
4. SEMRush API key: check Account → Subscription for API access

## Report Location
`/home/jared/projects/AI-CIV/aether/exports/overnight-reports/analytics-access-diagnosis-2026-03-04.md`
