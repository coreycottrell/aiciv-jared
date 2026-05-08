# SEO Audit V2 Findings - purebrain.ai
**Date**: 2026-04-19
**Type**: operational
**Agent**: SEO Specialist (ptt-fullstack)

## Key Findings

### Still Broken (from Apr 6 audit)
- Homepage og:image still uses wp-content GIF path (480x270, not 1200x630 PNG)
- Homepage has duplicate title/og:title/description tags (WP layer + custom inject)
- `/live/` payment page still blocked by `Disallow: /live*/` in robots.txt
- 22/22 comparison pages (`purebrain-vs-*`) have ZERO og:image tag
- Google Search Console verification still commented out in HTML

### Fixed Since Last Audit
- Blog post og:images are correct: absolute URLs at `/blog/[slug]/banner.png`, all return 200
- Sitemap has 97 URLs (was unverified last time)
- Custom JSON-LD Organization schema added to homepage

### New Issues Found
- 8 blog posts deployed but missing from sitemap.xml
- 4 of those 8 appear on blog index but not sitemap (crawlers can't find them)
- Blog index only shows 12 of 49 posts (WP latest-posts block limit)
- /pricing/ /features/ /faq/ /contact/ return 200 but serve WP homepage fallback (canonical = `/`, not real pages)
- robots.txt is 296 lines with duplicate CF-managed blocks and conflicting directives
- Duplicate JSON-LD: custom Organization schema + Yoast schema graph compete
- Homepage is 643KB / 16,339 lines -- likely poor mobile LCP

### Techniques
- WebFetch gets 403 on purebrain.ai (CF bot protection) -- must use curl with browser UA
- PageSpeed Insights API quota exceeded -- need manual test at pagespeed.web.dev
- Blog index post detection: grep for `wp-block-latest-posts__post-title` class

## File Reference
- Report: `/home/jared/exports/portal-files/OVERNIGHT-WEBSITE-V2-2026-04-19.md`
- Previous report: `/home/jared/exports/portal-files/overnight-analytics-seo-report.md`
