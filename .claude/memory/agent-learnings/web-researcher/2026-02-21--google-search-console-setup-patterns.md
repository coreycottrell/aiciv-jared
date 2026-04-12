# Web Research: Google Search Console Setup for Zero-Indexed Sites

**Date**: 2026-02-21
**Agent**: web-researcher
**Topic**: Google Search Console setup, DNS verification via Cloudflare, WordPress/Yoast sitemap indexing

## Context

Researched current (2026) best practices for getting a new WordPress site indexed by Google when site:domain.com returns zero results. Site in question: purebrain.ai (uses Cloudflare, Yoast SEO).

## Key Findings

### robots.txt Check
- Always verify robots.txt at /robots.txt first before any other diagnosis
- purebrain.ai robots.txt: clean, empty Disallow, sitemap declared
- Empty Disallow = ALL crawlers allowed = not the problem

### Cloudflare DNS TXT Verification
- Domain Property in GSC (vs URL Prefix) is recommended - covers all versions (www, non-www, http, https, subdomains)
- Steps: GSC > Add Property > Domain > copy TXT code > Cloudflare > DNS > Add Record > Type=TXT, Name=@, Content=paste code, TTL=Auto > Save > back to GSC > Verify
- DNS propagation: 15 min to 4 hours typically
- Cloudflare is particularly fast at propagating TXT records

### WordPress Sitemap Pattern (Yoast)
- sitemap_index.xml is the master index - submit this one first
- Yoast generates: post-sitemap.xml, page-sitemap.xml, category-sitemap.xml, author-sitemap.xml
- Submit sitemap_index.xml first, then individual ones as backup
- In GSC: Indexing > Sitemaps > add just the filename (not full URL, GSC knows the domain)

### URL Inspection / Request Indexing
- GSC top search bar: paste full URL > Enter > Request Indexing button
- Requesting indexing can cut time from days/weeks down to hours
- Daily limit ~10-20 requests for new sites - prioritize homepage, key landing pages first
- After 3-7 days check: Indexing > Pages for count of indexed pages

### Noindex Test Pages via Yoast
- WP Admin > Pages > Edit page > Yoast SEO box > Advanced tab
- Field: "Allow search engines to show this post in search results?" > Set to No
- Noindex takes 3-7 days to be respected by Google
- Critical check: Settings > Reading in WP admin - make sure "Discourage search engines from indexing this site" is UNCHECKED (this setting blocks everything if accidentally enabled)

### Timeline Expectations
- Homepage indexed after request: 1-3 days
- Blog posts: 3-7 days
- site:domain.com shows results: 3-14 days
- Noindexed pages removed from Google: 3-7 days

## When to Apply

- Any new WordPress site with zero Google presence
- After site migration where indexing was lost
- When client asks "why isn't my site on Google"
- Cloudflare + WordPress + Yoast is the most common stack, this exact flow applies

## Sources
- https://search.google.com/search-console (primary tool)
- https://digitalbrolly.com/google-search-console-tutorial/
- https://yoast.com/wordpress-noindex-post/
- https://developers.google.com/search/docs/crawling-indexing/block-indexing
- https://oddjar.com/google-search-console-for-wordpress-complete-setup-and-optimization-guide-2025/
