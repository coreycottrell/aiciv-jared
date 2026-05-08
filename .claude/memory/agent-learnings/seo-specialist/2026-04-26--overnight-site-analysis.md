# Overnight Site Analysis: purebrain.ai (Apr 26, 2026)
**Type**: operational
**Agent**: seo-specialist

## Key Findings

### Verified fixes from Apr 25
- 404.html now serving HTTP 404 (was HTTP 200 with homepage)
- ContentRouter removed (confirmed)
- og:image partially fixed on 5 pages (but homepage still broken)

### Still broken (persistent since Apr 24-25)
- Blog index: 14 of 52 posts listed (unchanged)
- Sitemap: 102 URLs, 10 blog posts still missing (unchanged)
- GA4 conversion events: ZERO firing (broken since March, #1 priority)
- Homepage og:image: still wp-content path

### New finding: CF robots.txt override
- Cloudflare prepends managed AI crawler blocks (Disallow: /) BEFORE our custom Allow rules
- GPTBot, ClaudeBot, Google-Extended, Amazonbot, Bytespider, CCBot all effectively BLOCKED
- Fix: disable "AI Crawlers" managed block in CF dashboard
- This is why PureBrain is invisible to AI-powered search

### Analytics WoW
- Sessions: 776 (down 14% from 900)
- Pageviews: 894 (down 23% from 1,166)
- Blog bounce: 80% (improved from 95.5%, was 22% in March)
- GSC: 35 clicks / 239 impressions / 14.6% CTR in 28 days
- 100% of GSC clicks are brand terms (purebrain, pure brain)

### GA4 conversion fix options
- Option A: GTM Event Tags (if GTM manages GA4)
- Option B: Replace dataLayer.push with direct gtag() calls (simplest)
- Option C: Measurement Protocol (server-side only)

## File paths
- Report: `/home/jared/exports/portal-files/overnight-site-analysis-2026-04-26.md`
- Analytics: `/home/jared/projects/AI-CIV/aether/exports/portal-files/analytics-report-2026-04-25.md`
- Sitemap: `/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/sitemap.xml`
- robots.txt: `/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/robots.txt`
- Blog index: `/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/blog/index.html`
