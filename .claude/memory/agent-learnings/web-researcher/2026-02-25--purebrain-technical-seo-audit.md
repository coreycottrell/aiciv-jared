# Scientific Inquiry: Technical SEO Audit - purebrain.ai

**Date**: 2026-02-25
**Question**: What are the critical technical SEO issues on purebrain.ai that are suppressing organic search visibility?
**Conclusion**: 4 critical issues found: low Google indexing, 404 on key page, missing Twitter cards site-wide, missing FAQPage JSON-LD despite visual accordions
**Confidence**: 4 (Strong) - direct crawl evidence, Google index check, schema extraction from multiple pages

---

## Key Findings

### Site Architecture (Verified)
- Sitemap index at /sitemap_index.xml (Yoast SEO generated)
- 5 sub-sitemaps: 11 blog posts, 25 pages, 4 categories, 12 tags, 1 author
- Total 53 URLs in sitemaps
- robots.txt: fully open, all bots allowed, correct sitemap reference

### Critical Issues Confirmed
1. **Only 1 page indexed by Google** (site:purebrain.ai returned 1 result) - domain is new (Feb 2026)
2. **/ai-adoption-assessment returns 404** - correct URLs are /ai-partnership-assessment/ and /ai-readiness-assessment/
3. **Twitter card meta tags ABSENT on all pages** - confirmed on homepage, blog, calculator, assessment, all blog posts checked
4. **FAQPage JSON-LD missing** - visual FAQ accordions (`.faq-section`, `.pb-faq-item` CSS) exist on blog posts but no FAQPage JSON-LD schema. FAQPage schema enables Google rich results (expandable Q&A in SERPs).

### Meta Tag Quality
- Blog og:image on /blog/: 512x512 favicon PNG (should be 1200x630 blog banner)
- /ai-partnership-assessment/ og:image: 480x270 GIF (should be static 1200x630 PNG)
- Blog posts: all have Article schema with word count, author "Aether (AI) at PureBrain.ai", published/modified dates
- Calculator page: best optimized - good title, description, dedicated OG image at 1456x816

### Good Foundation
- Yoast SEO generating proper Article schema on blog posts
- Canonical URLs consistent, non-www HTTPS
- Blog post word counts solid (avg ~2,000 words)
- Meta descriptions generally good (one missing on /your-next-direct-report-wont-be-human/)
- BreadcrumbList schema present
- Organization schema present (needs sameAs social profiles added)

---

## SEO Research Patterns Learned

### JavaScript-Heavy Site Limitation
Elementor WordPress sites render content via JS. WebFetch extracts CSS/scripts not rendered DOM. Cannot verify H1 tags, image alt text, or certain meta tags from raw HTML extraction. Use Google Search Console URL Inspection for verification.

### FAQ Schema Gap Pattern
Sites built with custom CSS FAQ accordions (visual only) frequently miss the corresponding FAQPage JSON-LD schema. This is a quick win - the content exists, just needs JSON-LD wrapping.

### GIF as OG Image
Using .gif files as og:image is a common mistake - many platforms (LinkedIn, iMessage, Slack) don't render animated GIFs in link previews, and the small size (480x270) is below minimum recommended (1200x630).

### Twitter Cards = Separate from OG Tags
Platforms route og: tags to Facebook/LinkedIn and twitter: tags to X/Twitter. Yoast SEO has a Twitter Settings tab that auto-generates twitter: tags from og: tags. Enable it globally - takes 5 minutes.

---

## Sources
- https://purebrain.ai/robots.txt (direct crawl)
- https://purebrain.ai/sitemap_index.xml (direct crawl)
- https://purebrain.ai/post-sitemap.xml (direct crawl)
- https://purebrain.ai/page-sitemap.xml (direct crawl)
- https://purebrain.ai/why-95-percent-of-ai-pilots-fail/ (schema extraction)
- https://purebrain.ai/the-ai-trust-gap/ (schema extraction)
- Google search: site:purebrain.ai (1 result returned)

## Limitations
- Cannot verify HTTP redirect chain (tool follows redirects automatically)
- Cannot verify image alt text on JS-rendered pages
- Cannot confirm gzip/brotli compression
- Google indexing status could improve rapidly as site ages

## Deliverable
Full report at: `/home/jared/projects/AI-CIV/aether/exports/analytics-report/technical-seo-audit.md`
