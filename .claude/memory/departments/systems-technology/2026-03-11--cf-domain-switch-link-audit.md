# CF Domain Switch Link Audit — Patterns & Findings
**Date**: 2026-03-11
**Type**: architecture pattern + gotcha
**Task**: Pre-switch link audit for purebrain.ai → Cloudflare Pages migration

## Key Finding: WordPress vs CF Blog Permalink Structure

WordPress serves blog posts at ROOT path: `/blog-slug/`
CF Pages serves blog posts under: `/blog/blog-slug/`

This means EVERY blog cross-link and every nav link to a blog post will 404 after domain switch
UNLESS a `_redirects` file handles the mapping.

**Solution**: `_redirects` file in the public root catches `/slug/*` and 301s to `/blog/slug/`

## Cloudflare Pages _redirects Format

```
/old-path/* /new-path/:splat 301
/category/* /blog/ 301
```

The `:splat` captures anything after the path (including query strings, sub-paths).
File must be at the ROOT of the deployed site — `purebrain-site/public/_redirects`

## WordPress Artifacts in Exported HTML

When WordPress pages are exported as static HTML, they embed:
1. `<link rel="alternate" type="application/rss+xml" href="...slug/feed/">` — RSS artifacts, low severity
2. Category and tag archive links: `/category/ai-strategy/` — taxonomy pages WP generates automatically
3. WP admin links baked into page source (`/wp-admin/...`) — not user-visible, ignore
4. Protocol-relative URLs: `//fonts.googleapis.com` — external, not internal links

**Filter rule for audit scripts**: skip `/wp-admin`, `/wp-content`, `/feed`, `//` protocol-relative external, `.php` extensions.

## Audit Script Location

`/tmp/link_audit_v2.py` — Python script that:
- Walks both `exports/cf-pages-deploy/` and `purebrain-site/public/`
- Extracts all hrefs matching purebrain domains or relative paths
- Cross-references against existing pages (by slug)
- Groups RED items by destination, shows which source pages link there

## Files Created

- `purebrain-site/public/_redirects` — Deploy-ready redirects file (Cloudflare Pages)
- `exports/cf-pages-deploy/_redirects` — Same, in the deploy export copy
- `exports/departments/systems-technology/2026-03-11--cf-link-audit-domain-switch.md` — Full audit report

## Stats

- 128 HTML pages on Cloudflare Pages
- 1,076 unique internal links scanned
- 907 GREEN (84%)
- 169 RED before fixes (16%)
- After `_redirects` is deployed: estimate <10 RED remain (only the 4 truly missing product pages)

## Missing Pages Needing Decision

These are genuinely missing — not just permalink mismatches:
- `/audit/` — linked from 3 blog CTAs, HIGH priority
- `/start/` — linked from enso comparison pages
- `/how-it-works/` — linked from billiereview comparison pages
- `/ai-agent-tools-calculator/` — may be slug rename of existing calculator, needs check
- `/your-ai-resets-to-zero-every-morning/` — blog post exists in WP but not deployed to CF
