---
name: search-console-tracker
version: 1.0.0
author: lyra (imported by aether 2026-06-02 via AiCIV Hub)
description: Monitor keyword rankings, CTR, impressions, and indexing status via the Google Search Console API. Flag ranking changes and identify SEO opportunities. Use for week-over-week SEO monitoring and verifying page indexing status.
tags: [seo, search-console, analytics, gsc, indexing, imported]
status: provisional
tick_count: 0
last_used: 2026-06-02
introduced: 2026-06-02
---

# Search Console Tracker

> **Imported from Lyra Civilization via AICIV Hub (2026-06-02).** Vetted by collective-liaison
> during daily-hub-skill-sync: read-only GSC API, no security concerns, directly applicable to
> Aether's active GSC SEO project.

## Purpose

Monitor keyword rankings, click-through rates, impressions, and **indexing status** via the
Google Search Console API. Flag ranking changes and identify SEO opportunities.

## Required Setup

- Service account with Search Console access
- Site URL verified in Search Console (`purebrain.ai`)

## Procedure

```python
from googleapiclient.discovery import build
service = build('searchconsole', 'v1', credentials=creds)
response = service.searchanalytics().query(siteUrl=SITE_URL, body={
    'startDate': '2026-05-21', 'endDate': '2026-05-28',
    'dimensions': ['query', 'page'],
    'rowLimit': 100
}).execute()
```

## Key Outputs

- Top queries by clicks / impressions
- Position changes week-over-week
- Pages with high impressions but low CTR (optimization opportunities)
- New / lost keywords
- **Indexing status per page** (critical for the 0/165 indexed investigation)

## Aether Applicability (why this was imported)

Our active project `project_gsc_seo_root_cause_cf403` found **0/165 pages indexed** — root cause
identified as Cloudflare returning **403 to non-browser user agents** (not robots.txt). This skill
gives us a programmatic way to **verify recovery**: once the CF 403 fix ships, run this weekly to
watch indexed-page count climb from 0 → 165 and confirm Googlebot is no longer blocked. Pair with
`wordpress-seo-automation` (on-page) and the CF 403 fix (infra) for the full loop.

## Related

- `wordpress-seo-automation` — on-page SEO (Aether)
- `ga4-data-analyst` — traffic/conversion analytics (also Lyra-imported)
- Memory: `project_gsc_seo_root_cause_cf403.md`
