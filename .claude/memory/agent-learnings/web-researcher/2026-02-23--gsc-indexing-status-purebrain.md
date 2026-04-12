# Web Research: GSC Verification + Indexing Status for purebrain.ai

**Date**: 2026-02-23
**Agent**: web-researcher
**Type**: operational
**Topic**: Google Search Console status check, sitemap verification, indexing acceleration methods

## Context

Verified Google Search Console setup status for purebrain.ai following addition of Shahbaz (ayeshah.zd@gmail.com) as GSC owner with backend access.

## Key Findings

### Infrastructure Status (All Green)
- robots.txt: Accessible, empty Disallow, sitemap declared correctly
- sitemap_index.xml: Live, Yoast-generated, auto-updating (last updated 2026-02-23)
- 5 child sitemaps: post, page, category, post_tag, author
- 19 public URLs declared (9 blog posts + 10 pages)
- No technical crawl blocks found

### Google Visibility Status
- site:purebrain.ai = 0 results
- "purebrain.ai" = 0 results in Google
- "pure brain ai" = 0 results
- NORMAL: Newest pages are only 1-4 days old, Google takes 7-21 days for new domains

### Fastest Indexing Methods (Priority Order)
1. URL Inspection Tool in GSC - request indexing manually (10-12/day limit), 24-72hr turnaround
2. Submit sitemap_index.xml in GSC - covers all 19 pages at once
3. External links (LinkedIn, Bluesky posts with purebrain.ai URLs) - Google follows these within hours
4. Internal linking - helps crawl depth after initial discovery
5. IndexNow (Yoast has this built in) - instant ping to Bing/Yandex

### Timeline Expectations with Active GSC
- First site:domain.com results: 3-7 days
- Blog posts in search: 7-14 days
- Brand name queries showing: 14-21 days

## When to Apply

- Any "is the site on Google yet" question for new sites
- New site launch GSC checklist
- Client sites needing indexing acceleration
- After content publication to determine crawl urgency

## Sources
- https://support.google.com/webmasters/answer/9012289?hl=en
- https://developers.google.com/search/docs/crawling-indexing/ask-google-to-recrawl
- https://rssautoindex.com/blog/en/articles/force-google-indexing-methods.html
- https://www.trysight.ai/blog/speed-up-google-indexing-process
