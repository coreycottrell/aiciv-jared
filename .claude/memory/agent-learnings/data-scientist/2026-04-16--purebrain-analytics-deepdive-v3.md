# Memory: purebrain.ai Analytics Deep Dive v3 -- Apr 16, 2026

**Agent**: data-scientist
**Date**: 2026-04-16
**Type**: operational + teaching

---

## Key Findings

### Site Performance
- Homepage TTFB: 171ms (excellent, Cloudflare edge)
- Homepage HTML size: 626KB -- 76% is inline JS (249KB) + CSS (238KB)
- Brotli compression active, HTTP/2, but no edge caching (cf-cache-status: DYNAMIC)
- All key pages sub-300ms TTFB

### SEO State
- 106 URLs in sitemap (up from 50 on Mar 6)
- 46 blog posts (up from 21 on Mar 6)
- Good structured data: BlogPosting + FAQPage schemas on blog, Organization + WebPage on homepage
- Full OG (19 tags) + Twitter (9 tags) on all pages checked
- 1 duplicate blog slug found: `-2` suffix on "most-ai-agents-break..." post

### CRITICAL: robots.txt Contradiction
- Cloudflare's managed section BLOCKS GPTBot, ClaudeBot, Google-Extended, etc. with `Disallow: /`
- Custom section BELOW tries to ALLOW these same crawlers
- Different crawlers interpret contradictions differently -- some may be fully blocked
- This is the #1 SEO fix: disable CF AI bot blocking in dashboard, manage via custom robots.txt only
- Impact: GEO/AIO visibility (Perplexity, ChatGPT Browse, Google AI Overviews) likely zero

### Analytics Access (Still Blocked)
- GA4: Fires via GTM-WTDXL4VJ but no API credentials in .env
- GSC: No OAuth tokens
- Clarity: viy9bnc56x tag present in HTML, no API access
- PageSpeed Insights API: Quota exceeded on unauthenticated calls
- Fix: GCP service account with GA4 Viewer + GSC user access, ~45 min total

### Internal Logs (as of Apr 16)
- 3,869 chat sessions total (96.2% from localhost/dev IPs)
- Real external sessions: ~23 (from ~3 unique external IPs)
- 61 payments, $10,596 total, avg $173.70
- Onboarding funnel: `flowCompleted` never set; birth_completions has empty fields
- Data quality issue in logging, not in actual conversion

## Teaching: What To Do Next Time

1. PageSpeed API needs an API key to avoid quota -- add `PAGESPEED_API_KEY` to .env
2. Always separate dev (127.0.0.1, 108.35.12.204) from real traffic in any log analysis
3. robots.txt on CF-managed sites requires checking BOTH CF dashboard settings AND custom rules
4. Internal JSONL logs are the best proxy for user behavior until GA4 API is connected
5. Blog SEO is solid (schemas, meta, canonical) -- the bottleneck is discovery/traffic, not on-page

## Report Location
`/home/jared/exports/portal-files/overnight-analytics-deepdive-2026-04-16.md`
