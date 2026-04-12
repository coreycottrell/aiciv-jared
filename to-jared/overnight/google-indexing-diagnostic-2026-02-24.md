# Google Indexing Diagnostic: purebrain.ai
**Date**: 2026-02-24
**Investigator**: full-stack-developer
**Status**: INVESTIGATION COMPLETE

---

## VERDICT: No Hard Technical Blocks Found — Timeline Issue

The good news: **nothing is technically preventing Google from indexing purebrain.ai**. Every SEO technical signal passes. The zero results in `site:purebrain.ai` is expected for a site this young.

---

## 1. robots.txt — PASS

```
User-agent: *
Disallow:

Sitemap: https://purebrain.ai/sitemap_index.xml
```

- Googlebot is fully allowed
- All user-agents are allowed (empty Disallow)
- Sitemap is declared correctly
- **No issues**

---

## 2. XML Sitemap — PASS

**Sitemap index**: `https://purebrain.ai/sitemap_index.xml` — Live, Yoast-generated

**5 child sitemaps** all working:
- `post-sitemap.xml` — 10 blog posts (all dated 2026-02-23)
- `page-sitemap.xml` — 24 pages
- `category-sitemap.xml` — Live
- `post_tag-sitemap.xml` — Live
- `author-sitemap.xml` — Live

**Total URLs declared**: 34+ public pages

**No issues** — sitemap is comprehensive and valid.

---

## 3. noindex Tags — PASS

Checked all key pages. Every page shows `index, follow`:

| Page | robots meta | noindex? |
|------|-------------|----------|
| Homepage `/` | `index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1` | NO |
| `/blog/` | `index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1` | NO |
| `/compare/` | `index, follow` | NO |
| `/ai-partnership-assessment/` | `index, follow` | NO |
| `/purebrain-vs-chatgpt/` | `index, follow` | NO |
| `/ai-adoption-review/` | `index, follow` | NO |

WordPress `blog_public` setting: `true` (Search engine visibility is ON — not discouraged)

Yoast API confirmed `index: index` for homepage and compare page.

**No noindex issues anywhere.**

---

## 4. Canonical URLs — PASS

All canonical tags point to clean production URLs:

- Homepage: `<link rel="canonical" href="https://purebrain.ai/" />`
- Blog: `<link rel="canonical" href="https://purebrain.ai/blog/" />`
- Compare: `<link rel="canonical" href="https://purebrain.ai/compare/" />`

`www.purebrain.ai` correctly 301-redirects to `purebrain.ai` — no canonicalization conflict.

**No issues.**

---

## 5. Cloudflare — PASS (with one note)

**Googlebot is NOT being challenged or blocked.** Verified:
- Googlebot request returns `HTTP/2 200` with full HTML content
- No `cf-challenge` or Turnstile challenge pages
- No `X-Robots-Tag: noindex` headers from Cloudflare
- Content is properly served to crawler user-agents

**One note — long cache TTL:**
`cache-control: public, max-age=2678400` (31 days)

This means Cloudflare caches pages for 31 days. Google ignores Cache-Control for its own crawl scheduling, so this does NOT block indexing. However, it means Googlebot may see a cached version when it does crawl. This is worth monitoring but is not the cause of zero indexing.

---

## 6. WordPress/Yoast Search Engine Setting — PASS

`blog_public: true` — WordPress is NOT set to discourage search engines.

Yoast v27 is correctly generating:
- Robots meta tags
- Sitemap
- Schema markup
- Canonical tags

---

## 7. HTTP Status Codes — ALL PASS

| URL | Status |
|-----|--------|
| `https://purebrain.ai/` | 200 |
| `https://purebrain.ai/blog/` | 200 |
| `https://purebrain.ai/compare/` | 200 |
| `https://purebrain.ai/ai-partnership-assessment/` | 200 |
| `https://purebrain.ai/ai-partnership-guide/` | 200 |
| `https://purebrain.ai/ai-adoption-review/` | 200 |

---

## 8. Schema / Structured Data — PRESENT BUT IMPROVABLE

Homepage has valid schema:
- `WebSite` — with SearchAction
- `WebPage` — with datePublished, dateModified, description
- `Organization` — with name, url, logo
- `BreadcrumbList`

**What's missing (opportunity, not blocking)**:
- Organization schema lacks `sameAs` links (LinkedIn, Bluesky URLs help Google trust the entity)
- Organization schema lacks `contactPoint`
- No `LocalBusiness` schema (not critical for SaaS)

---

## 9. Google Search Console Verification — NEEDS VERIFICATION

GSC meta tag is present on the homepage:
```html
<meta name="google-site-verification" content="S4BWw-zZDnPzo2x3U7iPvdUTxqnUkqGlW1S9fb024O0" />
```

**Critical questions only Jared can answer:**
1. Is this property actually verified in GSC? (Meta tag presence ≠ verified)
2. Has the sitemap `https://purebrain.ai/sitemap_index.xml` been submitted in GSC?
3. Has anyone used the URL Inspection tool to request indexing for key pages?

**If GSC is not verified, Google has no direct feedback channel and no sitemap submission.**

---

## 10. Site Age — THE REAL REASON FOR ZERO INDEXING

**purebrain.ai was first published: 2026-02-11** (13 days ago)

This is the primary explanation for zero indexing:

- Google discovers new domains gradually
- **New domains with zero backlinks from established sites** take 2-6 weeks minimum
- Even with GSC and sitemap submission, first crawl can take 7-14 days
- `site:domain.com` showing zero results is completely normal for a 13-day-old domain

**The site is indexable. Google just hasn't gotten there yet.**

---

## What Jared Needs to Do Manually (Requires Your Login)

### PRIORITY 1: Verify GSC and Submit Sitemap (Highest Impact)
1. Log into Google Search Console: https://search.google.com/search-console/
2. Verify ownership of `https://purebrain.ai` (the meta tag is there — click Verify)
3. Go to **Sitemaps** → Submit `https://purebrain.ai/sitemap_index.xml`
4. Go to **URL Inspection** → Paste `https://purebrain.ai/` → Click "Request Indexing"
5. Repeat URL Inspection for 5-10 key pages (limit: ~10-12/day):
   - `https://purebrain.ai/blog/`
   - `https://purebrain.ai/the-ai-trust-gap/`
   - `https://purebrain.ai/why-95-percent-of-ai-pilots-fail/`
   - `https://purebrain.ai/compare/`
   - `https://purebrain.ai/ai-partnership-assessment/`

**Time to first results after this**: 24-72 hours

---

## What Can Be Fixed Autonomously Right Now

### Fix 1: Add sameAs to Organization Schema (Impact: MEDIUM)

Helps Google confirm purebrain.ai is a real, established entity.

I can add LinkedIn + Bluesky profile URLs to the Organization schema in the Yoast plugin. This requires a PHP filter in the WordPress plugin. I can deploy this now.

### Fix 2: Ensure jareddsanborn.com posts link directly to purebrain.ai posts

Checked jareddsanborn.com — it has a menu link "PureBrain.AI Blog" but the blog posts themselves (the duplicated content) may not cross-link. Cross-links from jareddsanborn.com (which IS indexed) would create a crawl path into purebrain.ai.

**Action**: Add footer cross-links from each jareddsanborn.com post to the corresponding purebrain.ai post.

### Fix 3: Cloudflare Cache TTL Reduction (Impact: LOW-MEDIUM)

31-day cache is aggressive. Reducing to 1-4 hours would ensure Google sees fresh content on every crawl. This is a Cloudflare dashboard change (not WP).

---

## Priority Action List (Ranked by Impact)

| Priority | Action | Who | Time | Impact |
|----------|--------|-----|------|--------|
| 1 | Verify GSC + submit sitemap | JARED (requires login) | 10 min | CRITICAL |
| 2 | Request indexing via URL Inspection (10 pages) | JARED (requires login) | 15 min | HIGH |
| 3 | Add sameAs links to Organization schema | Autonomous (Aether) | 30 min | MEDIUM |
| 4 | Add cross-links from jareddsanborn.com posts to purebrain.ai posts | Autonomous (Aether) | 45 min | MEDIUM |
| 5 | Share purebrain.ai blog URLs on LinkedIn + Bluesky (already doing this) | Ongoing | Ongoing | MEDIUM |
| 6 | Reduce Cloudflare cache TTL from 31 days to 4 hours | JARED (CF dashboard) | 5 min | LOW-MEDIUM |

---

## Summary

**No technical SEO blocks exist.** The site is perfectly configured for indexing:
- robots.txt: Open
- Sitemap: Live with 34 URLs
- noindex: None found anywhere
- Canonical: All clean
- Status codes: All 200
- Schema: Present (Organization, WebPage, WebSite)
- Cloudflare: Not blocking Googlebot

**The only things that could be holding it back:**

1. **GSC may not be verified/sitemap submitted** — this is the highest-impact gap we can't verify from outside
2. **Site is only 13 days old** — new domain with minimal external backlinks (natural delay)
3. **No established sites linking in** — jareddsanborn.com links help but Google has to discover it first

**Timeline with GSC verified + sitemap submitted**:
- First `site:purebrain.ai` results: 3-7 days
- Blog posts appearing in searches: 7-14 days
- Brand queries working: 14-21 days

**Without GSC/sitemap submission**: 4-8 weeks (Google discovers it eventually, just slower)

---

*Diagnostic generated: 2026-02-24*
*All curl tests run against live production URLs*
