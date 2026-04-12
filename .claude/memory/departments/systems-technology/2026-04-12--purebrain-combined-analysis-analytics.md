# PureBrain.ai Combined Analysis + Analytics - April 12, 2026
**Date**: 2026-04-12
**Type**: operational
**Agent**: dept-systems-technology

## Key Findings

### Bot Traffic (800x600) - Stable at 45.4%
- 1,299 sessions from 1,300 unique users (1:1 ratio confirms bots)
- 98.4% hit homepage only, 98.5% classified as Direct
- 95% from United States, consistent 24/7 hourly pattern
- Singapore: still 62 unique = 62 new = bot farm pattern

### Traffic Growth (WoW)
- Total: +48% (996 vs 673)
- Organic Social: +308% (49 vs 12) -- biggest growth channel
- Organic Search: +41% (65 vs 46) -- steady growth
- Referral: +57% (108 vs 69) -- MS Teams strongest referral
- Monday is peak day (186 sessions Apr 7)

### Conversion Tracking STILL Broken
- 82 form_start + 45 click events in 30 days -- no purchase/CTA tracking
- GTM container GTM-WTDXL4VJ missing critical triggers
- Cannot measure ROI of any channel

### Security Header REGRESSION
- HSTS, X-Frame-Options, X-XSS-Protection NOT in headers today
- Were reportedly fixed on Apr 11 -- fix may have been reverted or deployed to wrong env
- Only X-Content-Type-Options: nosniff present
- CSP still missing

### GSC: Pilot Purgatory = 313 Impressions, 0 Clicks
- Position 5.9 (page 1!) but CTR = 0%
- Title/meta description not compelling enough to click
- Duplicate URL cannibalization still present for age-of-ai-agents
- Sitemap: 0/102 URLs indexed (down from 109, still 0 indexed)

### Page Engagement Leaders
- /why-purebrain/: 85% engagement rate (best on site)
- /invitation/: 75% engagement
- /investor-avatar/: 71.4% engagement, 12min avg session
- /compare/: 71.1% engagement
- Homepage: 33% engagement (worst for a key page)

### Returning vs New Users
- Returning: 8m 47s avg, 37.9% bounce, 2.0 pages/session
- New: 48s avg, 71.7% bounce, 1.1 pages/session
- 11x engagement gap validates relationship-first model

## Report Location
/home/jared/exports/portal-files/purebrain-analysis-analytics-2026-04-12.md

## Tags
analytics, ga4, gsc, purebrain, bot-traffic, conversion-tracking, seo, security-headers, ab-testing
