# Analytics Deep Dive — purebrain.ai March 15 Data
**Date**: 2026-03-15
**Agent**: browser-vision-tester
**Type**: operational + teaching

---

## Context

Overnight analytics run. Same pattern as 2026-03-11 session. GA4 + GSC via API, Clarity still blocked (interactive OAuth wall).

---

## Key Data Points (2026-03-15)

**Traffic**: 337 sessions in last 7d, UP 26% vs monthly avg of ~267/week
**Organic Search**: 14 sessions this week, UP 65% from avg — growing fastest
**Live users**: 2 at time of report
**Homepage CTR in GSC**: 15.2% (strong for branded queries)

## New Findings vs 2026-03-11

1. **/age-of-ai-agents/ CTR crisis still ongoing** — 234 impressions 90d, only 1 click (0.4% CTR). Position 5.5. This page had 123 impressions in just the last 7 days. The title/meta is clearly not matching search intent or is non-compelling.

2. **"Position 3-5 with 0 clicks" pattern identified** — Multiple pages ranking in top 5 on Google (positions 3-5) getting literally 0 clicks over 90 days. Pages: /ai-partnership-guide/ (3.1), /the-ai-that-forgets-you/ (3.7), /invitation/ (4.8), /ai-website-analysis/ (4.8), /ai-readiness-assessment/ (5.4). This is a systemic meta description quality issue.

3. **Germany anomaly confirmed persistent** — 150 sessions in 28d from 150 different German users (1 session each). Almost certainly automated traffic. Not genuine audience.

4. **Microsoft Teams referral (71 sessions)** = internal demo/sales traffic from statics.teams.cdn.office.net. Not acquisition — Jared sharing site in calls.

5. **Form funnel**: 97 users start forms, 60-68 complete = 38% abandonment after starting. Consistent finding.

6. **blog/ engagement (79%)** — persistent star performer.

7. **Sitemap errors** — 3 sitemaps still showing errors in GSC (category, post, sitemap_index). page-sitemap.xml hasn't been re-crawled since 2026-02-24.

---

## API Pattern (Confirmed Working)

All same as 2026-03-11 patterns. No changes needed. `ga4_realtime()`, `ga4_report()`, `ga4_parse_rows()`, `gsc_query()`, `gsc_parse_rows()`, `gsc_list_sitemaps()` — all stable.

---

## Tags

`analytics`, `ga4`, `gsc`, `purebrain`, `seo`, `ctr-crisis`, `indexing`, `meta-descriptions`, `form-conversion`
