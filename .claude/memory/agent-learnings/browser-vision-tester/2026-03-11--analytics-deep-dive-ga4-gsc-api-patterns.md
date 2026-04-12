# Analytics Deep Dive - GA4 + GSC API Patterns

**Date**: 2026-03-11
**Agent**: browser-vision-tester
**Type**: operational + technique

---

## Context

Overnight Task 9 - full analytics deep dive for purebrain.ai across GA4, GSC, and Clarity.

---

## What Worked

**GA4 API via service account** - full programmatic access works perfectly:
- Tool: `tools/analytics_api.py`
- Service account: `aether-drive-access@aether-integration.iam.gserviceaccount.com`
- Key: `.credentials/google-drive-service-account.json`
- Property ID: `525007539`
- Functions: `get_ga4_summary(30)`, `ga4_realtime()`, `ga4_report(dims, metrics, date_range)`
- Returns full channel breakdowns, top pages, events, countries, devices

**GSC API** - also fully programmatic:
- Function: `gsc_query(['query'], days=28)`, `gsc_query(['page'], days=90)`
- Returns: clicks, impressions, CTR, position per query/page
- `gsc_list_sitemaps()` returns indexing status
- Key insight: `get_gsc_summary()` had a KeyError bug — use raw `gsc_query()` + `gsc_parse_rows()` directly

**Clarity** - auth wall, requires interactive OAuth (Microsoft, Facebook, or Google). No programmatic API available. Project ID: viy9bnc56x.

---

## Key Findings for purebrain.ai (2026-03-11)

- **GA4 only has ~30 days of data** — site tracking is recent
- **0 of 100 submitted pages indexed** in GSC — new domain, indexing in progress (3-6 months typical)
- **74% direct traffic** — strong brand, weak discovery
- **/age-of-ai-agents/ gets 160 impressions at pos 5.3 but ZERO clicks** — title/meta needs urgent fix
- **/ai-tool-stack-calculator/ gets 140 impressions at pos 10.9** — needs to break top 5
- **Germany = 20% of sessions** — anomalous spike, needs investigation
- **Blog page engagement rate 79%** — highest of any high-traffic page

---

## Reusable Pattern for Future Analytics Audits

```python
import sys
sys.path.insert(0, 'tools')
from analytics_api import ga4_report, ga4_parse_rows, ga4_realtime, gsc_query, gsc_parse_rows, gsc_list_sitemaps

# Realtime
rt = ga4_realtime()

# 30-day summary
channels = ga4_parse_rows(ga4_report(['sessionDefaultChannelGroup'], ['sessions','totalUsers','newUsers','screenPageViews','bounceRate','averageSessionDuration'], '30daysAgo', order_by_metric='sessions'))
top_pages = ga4_parse_rows(ga4_report(['pagePath'], ['sessions','totalUsers','screenPageViews','bounceRate'], '30daysAgo', order_by_metric='sessions', limit=25))
devices = ga4_parse_rows(ga4_report(['deviceCategory'], ['sessions','totalUsers','bounceRate','averageSessionDuration'], '30daysAgo', order_by_metric='sessions'))
countries = ga4_parse_rows(ga4_report(['country'], ['sessions','totalUsers'], '30daysAgo', order_by_metric='sessions', limit=10))
sources = ga4_parse_rows(ga4_report(['sessionSource','sessionMedium'], ['sessions','totalUsers'], '30daysAgo', order_by_metric='sessions', limit=15))
landing_pages = ga4_parse_rows(ga4_report(['landingPage'], ['sessions','totalUsers','bounceRate'], '30daysAgo', order_by_metric='sessions', limit=10))
engagement = ga4_parse_rows(ga4_report(['pagePath'], ['userEngagementDuration','engagementRate','sessions'], '30daysAgo', order_by_metric='userEngagementDuration', limit=10))

# GSC
queries = sorted(gsc_parse_rows(gsc_query(['query'], days=90, limit=50)), key=lambda x: x['impressions'], reverse=True)
pages = sorted(gsc_parse_rows(gsc_query(['page'], days=90, limit=50)), key=lambda x: x['impressions'], reverse=True)
sitemaps = gsc_list_sitemaps()
```

---

## Tags

`analytics`, `ga4`, `gsc`, `purebrain`, `api`, `search-console`, `clarity-auth-wall`, `seo`
