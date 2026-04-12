# PureBrain.ai Combined Analysis + Analytics - April 11, 2026
**Date**: 2026-04-11
**Type**: operational
**Agent**: dept-systems-technology

## Key Findings

### Bot Traffic Discovery
- 46% of sessions (1,304/2,809) come from 800x600 resolution -- classic bot fingerprint
- Real traffic is approximately 1,500 sessions/30d (still +2x MoM)
- Singapore: 62 unique sessions from 62 unique users (all new) -- likely bot farm
- Midnight-5am EST peak hours are suspicious

### Traffic Growth (Real)
- ~1,500 real sessions/30d, up from ~769 prior period
- Organic search +76% WoW, social +72% WoW
- Microsoft Teams referral = #3 source (91 sessions) -- B2B signal
- LinkedIn total: 72 sessions (43 UTM + 29 organic)

### Conversion Tracking Still Broken
- Only 92 form_start + 46 click events in 30 days
- GTM container GTM-WTDXL4VJ missing click triggers for CTAs
- No scroll depth, video play, or purchase tracking
- No e-commerce tracking for PayPal Smart Buttons

### GSC: Pages Ranking but Not Clicking
- /ai-tool-stack-calculator/: 464 impressions, 1 click, position 15.3 -- close to page 1
- /blog/pilot-purgatory/: 301 impressions, 0 clicks, position 5.8 -- ON page 1, not clicking
- Duplicate URL cannibalization: /age-of-ai-agents/ exists at root AND /blog/ paths
- Still 0/109 sitemap URLs indexed (21 warnings)

### Security Headers FIXED (since Apr 7)
- HSTS, X-Frame-Options, X-Content-Type-Options, XSS-Protection all present now
- Only CSP still missing

### Still Not Fixed from March
- HTML caching: max-age=0 (should be 900s minimum)
- Font loading: 40+ variants loaded, only 6 used
- OG image: still a GIF
- Duplicate meta tags on homepage (3 viewport, 2 title, 2 description)
- HTML size: 640KB (Elementor bloat)

## Report Location
/home/jared/exports/portal-files/purebrain-analysis-analytics-2026-04-11.md

## Tags
analytics, ga4, gsc, purebrain, bot-traffic, conversion-tracking, seo, security-headers
