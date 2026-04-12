# Google Indexing Diagnostic: purebrain.ai
**Date**: 2026-02-24
**Agent**: full-stack-developer
**Type**: teaching + operational
**Topic**: Zero Google indexing investigation for new domain — all checks, root cause, fix path

---

## Context

Investigated why `site:purebrain.ai` returns zero results in Google. Ran all standard SEO technical checks.

---

## Complete Findings

### All Technical Checks Passed

| Check | Command | Result |
|-------|---------|--------|
| robots.txt | `curl -s "https://purebrain.ai/robots.txt"` | Empty Disallow, Sitemap declared — PASS |
| Sitemap | `curl -s "https://purebrain.ai/sitemap_index.xml"` | 5 child sitemaps, 34 URLs — PASS |
| noindex meta | `curl -s URL | grep -i "noindex"` | None found on any page — PASS |
| X-Robots-Tag header | `curl -sI URL | grep -i "x-robots"` | Not present — PASS |
| Canonical tags | `curl -s URL | grep -i "canonical"` | All point to production URLs — PASS |
| HTTP status codes | `curl -o /dev/null -s -w "%{http_code}" URL` | All 200 — PASS |
| WordPress blog_public | WP REST `/wp-json/wp/v2/settings` | `"blog_public": true` — PASS |
| Cloudflare blocking | Googlebot UA test | Full HTML returned — PASS |
| Schema markup | `grep -o '"@type":"[^"]*"'` | Organization, WebPage, WebSite — PASS |
| www redirect | `curl -sI "https://www.purebrain.ai/"` | 301 to apex — PASS |

### Root Cause: New Domain Age

purebrain.ai first published: **2026-02-11** (13 days before investigation)

Zero `site:domain.com` results is **completely normal** for a 13-day-old domain with:
- No established backlinks
- No GSC verification/sitemap submission confirmed
- Limited external link discovery paths

### The GSC Gap (Cannot Verify Externally)

GSC verification meta tag IS present:
```html
<meta name="google-site-verification" content="S4BWw-zZDnPzo2x3U7iPvdUTxqnUkqGlW1S9fb024O0" />
```

But we cannot verify from outside whether:
1. The property is actually verified in GSC
2. The sitemap has been submitted
3. URL Inspection + "Request Indexing" has been used

This is the highest-impact gap. Jared must confirm.

---

## Key Patterns for Future Diagnostics

### New Domain Zero-Index Checklist (in order)

```bash
# 1. robots.txt
curl -s "https://DOMAIN/robots.txt"

# 2. Sitemap exists
curl -s "https://DOMAIN/sitemap_index.xml" | head -20

# 3. noindex in HTML
curl -s "https://DOMAIN/" | grep -i "noindex"

# 4. X-Robots-Tag header
curl -sI "https://DOMAIN/" | grep -i "x-robots"

# 5. Status codes
for url in "/" "/blog/" "/key-page/"; do
  echo "$(curl -o /dev/null -s -w "%{http_code}" "https://DOMAIN${url}")  ${url}"
done

# 6. WordPress "discourage search engines" (blog_public)
curl -s "https://DOMAIN/wp-json/wp/v2/settings" -u "USER:PASS" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('blog_public'))"

# 7. Googlebot challenge check
curl -sI "https://DOMAIN/" -H "User-Agent: Googlebot/2.1 (+http://www.google.com/bot.html)" | head -5

# 8. GSC meta tag
curl -s "https://DOMAIN/" | grep -i "google-site-verification"

# 9. Yoast robots API
curl -s "https://DOMAIN/wp-json/yoast/v1/get_head?url=https%3A%2F%2FDOMAIN%2F" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('json',{}).get('robots',{}))"

# 10. Schema types
curl -s "https://DOMAIN/" | grep -o '"@type":"[^"]*"' | sort -u
```

### Schema Enhancement Opportunity

Organization schema missing `sameAs` links. Adding these helps Google confirm entity trust:
```php
add_filter('wpseo_schema_organization', function($data) {
    $data['sameAs'] = [
        'https://www.linkedin.com/company/purebrain-ai/',
        'https://bsky.app/profile/purebrain.bsky.social',
    ];
    return $data;
});
```

### Timeline Expectations for New Domains

| Action | Time to First `site:` Results |
|--------|-------------------------------|
| No GSC, no action | 4-8 weeks |
| GSC verified + sitemap submitted | 3-7 days |
| GSC + URL Inspection (manual request) | 1-3 days |
| GSC + backlinks from indexed domain | 24-48 hours |

### Cloudflare Cache-Control Note

`max-age=2678400` (31 days) on all pages. This does NOT block Google crawling — Google schedules its own crawl frequency and ignores Cache-Control for that purpose. However, it means pages may be stale in Cloudflare's edge cache. Reducing to 4 hours improves freshness for human visitors.

---

## What Was Verified as CLEAN

- No noindex tags anywhere (all pages index, follow)
- No X-Robots-Tag blocking headers
- All canonical URLs point to production (not staging)
- www redirects to apex correctly
- robots.txt allows all crawlers
- WordPress blog_public = true
- Cloudflare serves full HTML to Googlebot (no challenge)
- GSC meta tag present (verification status unknown)

---

## Output File

Full diagnostic report: `to-jared/overnight/google-indexing-diagnostic-2026-02-24.md`

---

**End of Memory**
