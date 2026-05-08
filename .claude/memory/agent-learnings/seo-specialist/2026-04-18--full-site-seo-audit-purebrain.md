# 2026-04-18 -- Full Site SEO Audit: purebrain.ai

**Type**: teaching (operational + synthesis)

## Top Findings

1. **Homepage og:image STILL points to wp-content GIF** -- blocked by robots.txt. This is the #1 social sharing issue.
2. **Homepage has duplicate head sections** -- two title tags, two og blocks. Legacy WP export artifact.
3. **43/43 blog posts have ghost related-post links** (2 URLs that 404). Template-level issue.
4. **22/25 comparison pages lack og:image entirely** -- social shares show blank preview.
5. **38 pages total reference wp-content paths in og:image** -- all blocked by robots.txt.
6. **Calculator + assessment pages lack canonical tags and JSON-LD schema** -- missed structured data opportunity.
7. **Zero internal links from blog -> comparison pages** -- huge missed cross-linking opportunity.
8. **Homepage is 16,362 lines** -- performance concern, duplicate sections inflating size.
9. **No /pricing/ page exists** -- guaranteed branded search query target missing.

## Sitemap State
- 107 URLs total (47 blog, 25 compare, 35 core)
- `your-customers-will-tell-you-everything` in sitemap but is orphaned (no HTML)
- `/blog-neural-feed-memories/` blocked in robots.txt but linked from blog index

## What Works Well
- robots.txt is comprehensive and well-structured
- AI crawler allowances (GPTBot, ClaudeBot, PerplexityBot) properly configured
- llms.txt exists and is well-written
- Homepage has Organization + WebSite + WebPage + SoftwareApplication schema
- Blog posts have BlogPosting + FAQPage schema (where applicable)
- 25 comparison pages all in sitemap

## Techniques
- CF Pages returns 403 to direct WebFetch -- must audit from local deploy files
- `grep -l 'og:image.*wp-content'` across deploy dir is fast way to find affected pages
- Prior audit data (2026-04-16 blog audit, 2026-02-22 CRO analysis) provided valuable baseline -- memory-first approach saved significant re-analysis time

## Files
- Report: `/home/jared/exports/portal-files/OVERNIGHT-WEBSITE-ANALYSIS-2026-04-18.md`
- Prior blog audit: `2026-04-16--blog-newsletter-deep-audit.md`
