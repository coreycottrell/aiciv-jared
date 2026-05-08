# Analytics Deep Dive + SEO Audit — April 28, 2026

**Date**: 2026-04-28
**Type**: operational
**Topic**: Fresh GA4 + GSC pull, comprehensive SEO audit, conversion tracking gap analysis

## Key Data Points (April 28)
- 901 sessions / 768 users / 984 pageviews (7d)
- Sessions up +6% WoW, users +10%, but pageviews -8% (engagement declining)
- 80 organic sessions/week (only 9% of traffic)
- GSC: 45 clicks in 28 days, nearly ALL branded ("purebrain")
- Non-branded organic traffic is essentially zero

## Persistent Issues (Still Unfixed)
1. GA4 conversion events NOT wired (2+ months) -- GTM Custom Event tags missing
2. Homepage og:image = WP 8MB GIF (og-image.png exists but not referenced)
3. Homepage: 2 title tags, 2 JSON-LD blocks, 8 og:image tags
4. robots.txt AI crawler contradiction (CF blocks then custom allows)
5. 22/25 comparison pages missing og:image
6. `/age-of-ai-agents-next-18-months/` root path returns 404 but gets 66 GSC impressions
7. 1 blog post deployed but missing from sitemap

## New Findings This Session
- `/ai-tool-stack-calculator/` = 334 impressions at position 12.1 (biggest non-branded opportunity)
- `/mission-vision-values/` = 109 impressions at position 4.8 with 0.9% CTR
- `/purebrain-vs-atomicbot/` = 60 impressions at position 5.7 with 1.7% CTR
- Pages/session = 1.09 (very low; SaaS avg 2.5-4.0)
- Homepage = 630KB / 16,357 lines (CWV risk)
- Blog index shows only 12 of 54 posts
- form_start fires 17/week but form_submit is invisible

## File Paths
- Report: `/home/jared/exports/portal-files/overnight-analytics-deep-dive.md`
- Analytics script: `/home/jared/projects/AI-CIV/aether/tools/analytics_deep_dive_apr25.py`
- Sitemap: `/home/jared/purebrain-site/sitemap.xml` (108 URLs, 53 blog posts)
- robots.txt: `/home/jared/purebrain-site/robots.txt` (237 lines)
