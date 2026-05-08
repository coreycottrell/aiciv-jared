# SEO Technical Audit -- purebrain.ai
**Date**: 2026-04-17
**Auditor**: SEO Specialist (Aether)
**Scope**: robots.txt, sitemap.xml, meta tags, schema markup, og:image, /llms.txt, blog CF Pages

---

## 1. robots.txt -- STATUS: GOOD (AI Crawlers ALLOWED)

**File**: `/exports/cf-pages-deploy/robots.txt`
**Live URL**: https://purebrain.ai/robots.txt

**Previous concern was that AI crawlers were blocked. This has been FIXED.**

Current state:
- `User-agent: *` --> `Allow: /` (default open)
- GPTBot, ClaudeBot, Google-Extended, anthropic-ai, cohere-ai, PerplexityBot, Amazonbot, CCBot, Bytespider, YouBot, FacebookBot, Applebot all have explicit `Allow: /blog/` and `Allow: /` directives
- 100+ internal/test/draft paths correctly blocked via `Disallow:`
- Sitemap declaration present: `Sitemap: https://purebrain.ai/sitemap.xml`

**Verdict**: No action needed. robots.txt is correctly configured for both SEO and AEO.

---

## 2. sitemap.xml -- STATUS: NEEDS FIXES

**File**: `/exports/cf-pages-deploy/sitemap.xml`
**Total URLs**: 107
- Blog posts: 46 (including /blog/ index)
- Comparison pages (purebrain-vs-*): 25
- Core pages: ~36

### Issues Found

**ISSUE 2A: 3 blog posts deployed but MISSING from sitemap**
- `first-ai-to-ai-transaction`
- `the-40-percent-problem-why-ai-agents-keep-dying`
- `when-your-ai-agent-goes-rogue`

These directories exist in `/exports/cf-pages-deploy/blog/` with `index.html` files but are not listed in sitemap.xml. Google cannot discover them via sitemap.

**ISSUE 2B: No sitemap index / sub-sitemaps**
With 107 URLs this is fine for now. Once you cross 200+ URLs, split into sitemap-blog.xml, sitemap-pages.xml, sitemap-compare.xml with a sitemap index.

**ISSUE 2C: llms.txt and llms-full.txt not in sitemap**
Not required by spec, but adding them signals to search engines that these files exist.

### Fix for 2A -- Add missing blog posts to sitemap.xml

Add these 3 entries before the closing `</urlset>` tag:

```xml
  <url>
    <loc>https://purebrain.ai/blog/first-ai-to-ai-transaction/</loc>
    <lastmod>2026-04-14</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.7</priority>
  </url>
  <url>
    <loc>https://purebrain.ai/blog/the-40-percent-problem-why-ai-agents-keep-dying/</loc>
    <lastmod>2026-04-14</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.7</priority>
  </url>
  <url>
    <loc>https://purebrain.ai/blog/when-your-ai-agent-goes-rogue/</loc>
    <lastmod>2026-04-14</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.7</priority>
  </url>
```

---

## 3. Homepage Meta Tags -- STATUS: CRITICAL ISSUES

**File**: `/exports/cf-pages-deploy/index.html`

### Issues Found

**ISSUE 3A (CRITICAL): DUPLICATE title tags**
The homepage has TWO `<title>` tags:
- Line 2652: `PURE BRAIN - Your Brain. Your AI. Actual Intelligence! - Agentic AI`
- Line 4823: `PURE BRAIN - Your Personal AI Awakens`

Google will likely use the first one. Two title tags is invalid HTML and confuses parsers.

**ISSUE 3B (CRITICAL): og:image points to wp-content GIF**
```
og:image: https://purebrain.ai/wp-content/uploads/2026/02/Pure-Brain-Vid-3.gif
```
This is:
1. A WordPress path -- the site is on CF Pages, this file may not exist or be served correctly
2. An animated GIF -- social platforms (LinkedIn, Twitter, Facebook) do NOT animate GIF previews, they grab one frame which is often bad
3. Likely undersized -- reported as 480x270 which is far below the 1200x630 minimum for good social cards

**ISSUE 3C: Brand inconsistency in title**
Title says "PURE BRAIN" (two words, all caps). The brand is "PureBrain" (one word, camel case). This hurts brand signal consistency for Google.

**ISSUE 3D: No twitter:image on homepage**
The `twitter:image` also points to the same wp-content GIF.

### Fix for 3A+3C -- Single, branded title tag

Remove the second title tag entirely. Update the first to:
```html
<title>PureBrain - Your Brain. Your AI. Actual Intelligence. | Agentic AI Partner</title>
```

### Fix for 3B+3D -- New og:image

Create a static 1200x630 PNG at `/assets/og-homepage.png` and update:
```html
<meta property="og:image" content="https://purebrain.ai/assets/og-homepage.png" />
<meta property="og:image:width" content="1200" />
<meta property="og:image:height" content="630" />
<meta property="og:image:type" content="image/png" />
<meta name="twitter:image" content="https://purebrain.ai/assets/og-homepage.png" />
```

---

## 4. /llms.txt -- STATUS: GOOD

**File**: `/exports/cf-pages-deploy/llms.txt` (exists, 55 lines)
**File**: `/exports/cf-pages-deploy/llms-full.txt` (exists, 5.4KB)

Both files exist and are well-structured. The homepage already has `<link rel="alternate">` tags pointing to them. This is ahead of most competitors for AEO.

**Minor improvement**: Add 2-3 more recent blog post URLs to llms.txt as new content publishes. Currently lists 7 articles from April 2026.

---

## 5. Schema Markup -- STATUS: MIXED

### Homepage Schema (GOOD)
The homepage has a well-structured `@graph` with:
- `Organization` (PureBrain / Pure Technology, with founder, sameAs)
- `WebSite` (with publisher reference)
- `WebPage` (with SpeakableSpecification -- excellent for voice/AEO)

### Blog Index Schema (GOOD)
- `CollectionPage` with `ItemList` of blog posts
- Publisher Organization reference

### Blog Post Schema (MOSTLY GOOD, needs fixes)

All 46 blog posts have `BlogPosting` schema EXCEPT:
- **`who-do-you-learn-from-when-youre-ahead`** -- MISSING BlogPosting schema entirely

Most blog posts also have `FAQPage` schema (confirmed on multiple posts) -- this is excellent for featured snippets.

**ISSUE 5A: Author is Organization, not Person**
Blog post author schema currently shows:
```json
"author": {
  "@type": "Organization",
  "name": "Pure Technology",
  "url": "https://purebrain.ai"
}
```
Google's documentation strongly recommends `@type: Person` for blog posts. Since Jared Sanborn is the author, this should be:
```json
"author": {
  "@type": "Person",
  "name": "Jared Sanborn",
  "url": "https://purebrain.ai/about-aether/",
  "jobTitle": "Founder & CEO",
  "worksFor": {
    "@type": "Organization",
    "name": "Pure Technology"
  }
}
```
This enables Google's author knowledge panel and E-E-A-T signals.

### Comparison Page Schema (NEEDS UPGRADE)
Comparison pages (purebrain-vs-chatgpt etc.) use basic `WebPage` schema. They should use:
- `FAQPage` (if they contain Q&A sections)
- `SoftwareApplication` (for PureBrain product listing)
- Consider adding `Review` or `ComparisonPage` structured data

**ISSUE 5B: Comparison pages have NO og:image**
The purebrain-vs-chatgpt page has no `og:image` meta tag at all. When shared on social, it will show a blank or random image.

---

## 6. TOP 5 TECHNICAL SEO FIXES (This Week)

Ranked by impact and urgency:

### FIX 1 (CRITICAL) -- Homepage og:image replacement
**Impact**: Every social share of purebrain.ai shows a bad/broken image
**Action**: Create 1200x630 static PNG, deploy to `/assets/og-homepage.png`, update meta tags
**Time**: 30 minutes (design) + 10 minutes (deploy)

### FIX 2 (CRITICAL) -- Duplicate homepage title tag
**Impact**: Google may index the wrong title; invalid HTML signals low quality
**Action**: Remove second `<title>` tag at line 4823, normalize first to "PureBrain" (not "PURE BRAIN")
**Time**: 5 minutes

### FIX 3 (HIGH) -- Blog author schema: Organization to Person
**Impact**: Missing E-E-A-T author signals across all 46 blog posts
**Action**: Bulk update all blog post JSON-LD to use `@type: Person` with Jared Sanborn's details
**Time**: 30 minutes (scripted find-replace)

### FIX 4 (HIGH) -- Add 3 missing blog posts to sitemap
**Impact**: 3 posts invisible to Google via sitemap discovery
**Action**: Add XML entries (code above in section 2)
**Time**: 5 minutes

### FIX 5 (MEDIUM) -- Comparison page og:image + schema upgrade
**Impact**: 25 comparison pages with no social preview image, weak schema
**Action**: Create a generic comparison og:image template, add FAQPage schema where Q&A exists
**Time**: 1-2 hours

---

## 7. Additional Action Items (Week 2-4)

| Priority | Item | Notes |
|----------|------|-------|
| HIGH | Google Search Console verification | Cannot track rankings or indexing without it |
| HIGH | Submit sitemap to GSC | After verification, submit https://purebrain.ai/sitemap.xml |
| MEDIUM | Add `SoftwareApplication` schema to product/pricing pages | Required per 90-day strategy |
| MEDIUM | Add `DefinedTerm` schema for coined terms (context tax, memory moat, BOOPs) | AEO advantage |
| MEDIUM | Create `/blog/category/ai-partnership/` and `/blog/category/ai-agents-business/` hub pages | Topical cluster architecture |
| LOW | Add `BreadcrumbList` schema to blog posts | Helps Google understand site hierarchy |
| LOW | Add hreflang if targeting international | Not needed yet |

---

## 8. What Is Working Well

- robots.txt is clean and AI-crawler-friendly
- llms.txt and llms-full.txt exist with `<link rel="alternate">` on homepage (ahead of competitors)
- Blog posts have BlogPosting + FAQPage schema (strong snippet potential)
- Homepage has Organization + WebSite + WebPage graph with SpeakableSpecification
- Sitemap covers 107 URLs with proper lastmod dates
- Canonical URLs set correctly on all checked pages
- OG tags on blog posts use absolute URLs to `/blog/[slug]/banner.png` (correct pattern)
- GTM and Clarity tracking in place

---

## Files Referenced

- `/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/robots.txt`
- `/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/sitemap.xml`
- `/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/index.html` (homepage)
- `/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/blog/index.html` (blog index)
- `/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/blog/the-context-tax/index.html` (sample post)
- `/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/purebrain-vs-chatgpt/index.html` (sample comparison)
- `/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/llms.txt`
- `/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/llms-full.txt`
