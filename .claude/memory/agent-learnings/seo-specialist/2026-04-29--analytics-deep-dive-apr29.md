# Analytics Deep Dive: purebrain.ai (Apr 29, 2026)
**Type**: operational
**Agent**: seo-specialist

## Key Findings

### Traffic UP significantly
- 1,013 sessions (+22% WoW), 866 users (+24%), 1,108 pageviews (+10%)
- 88 organic sessions (9% of total), up from ~80 last week

### Calculator page BREAKTHROUGH
- Position jumped from 17.1 (Apr 15-21) to 8.9 (Apr 22-28)
- 117 impressions this week but ZERO clicks = title/meta needs CTR optimization
- 6:19 avg session from organic visitors = deep engagement when they arrive

### Pilot Purgatory: 0 CTR for 4 straight weeks
- Position 5.7, 117 impressions this week, ZERO clicks for 4 consecutive weeks
- Total: ~558 impressions, 0 clicks. Something wrong with SERP snippet
- Title and meta description need urgent rewrite

### Persistent unfixed issues (2+ months)
1. GA4 conversion events: ZERO firing (form_submit, purchase, sign_up all missing)
2. Homepage og:image: still wp-content 8MB GIF, 2 title tags, 2 JSON-LD blocks
3. robots.txt: CF managed block overrides custom Allow rules for AI crawlers
4. 22/25 comparison pages: no og:image
5. Blog index: shows only 10 of 57 posts

### New findings
- chatgpt.com referral traffic appearing (3 sessions) despite AI crawler blocks
- /company/ page has noindex (intentional for investor use)
- staging-voice and staging-face subdomains live but no noindex
- Calculator page organic visitors spend 6:19 on average (excellent engagement signal)

## File paths
- Report: `/home/jared/exports/portal-files/overnight-analytics-deep-dive-apr29.md`
- Analytics script: `/home/jared/projects/AI-CIV/aether/tools/analytics_deep_dive_apr25.py`
