# PureBrain.ai Website Analysis — March 11, 2026

**Department**: Systems & Technology
**Agent**: dept-systems-technology
**Date**: 2026-03-11 00:32 UTC
**Scope**: Full site audit — SEO, performance, UX, conversion, technical debt
**Method**: WP REST API + live URL analysis + HTML inspection
**Previous analyses built on**: March 6, March 9, March 10 audits

---

## Executive Summary

The site is functionally sound: zero 404s on published content, Cloudflare caching active, Brotli compression working, dark background enforced site-wide. However, three categories of issues remain open and compounding: (1) SEO gaps on blog posts, (2) a bloated and duplicated homepage HTML payload, and (3) 13 internal/test pages published and indexable.

---

## 1. PERFORMANCE

### Homepage Load Times (as of this audit)
| Page | TTFB | Total Transfer | HTML Size |
|------|------|---------------|-----------|
| Homepage | 0.16s | 0.25s | 808KB (raw) |
| Blog | 0.16s | 0.20s | 192KB |
| Invitation | 0.68s | 0.71s | 118KB |
| Compare hub | 0.51s | 0.55s | 196KB |
| Developers | 0.54s | 0.57s | 144KB |

**Cloudflare**: Homepage returns `cf-cache-status: HIT` and `content-encoding: br` (Brotli). The 808KB raw homepage compresses well in transit.

**Invitation page TTFB (0.68s)**: Notably higher than homepage. Likely a cache miss or heavier server-side render. Worth investigating if Cloudflare Page Rule covers it.

### Critical: jQuery Loaded 3x on Homepage
- `jquery.min.js` loads 3 separate times
- `jquery-migrate.min.js` loads 3 separate times
- This is dead weight — two extra jQuery instances per page load
- **Root cause**: WP plugin queue + Elementor + theme each registering jQuery without deduplication

### Duplicate CSS Injection — Still Active
From March 10 audit this was flagged. As of March 11:
- `#pb-aether-footer` appears **110 times** in homepage HTML (4 actual DOM elements, 103+ CSS references)
- `"purebrain-blog-cta-hover"` style block injected 4x
- `"pb-aether-footer"` style block injected 4x
- `"alt-text-description"` element appears 4x
- Total: **48 duplicate element IDs** detected on homepage
- **Impact**: Bloated HTML (808KB), browser style recalculation overhead, confusing DOM

### Inline Resource Count (Homepage)
| Resource Type | Count |
|--------------|-------|
| External JS files | 123 |
| External CSS files | 49 |
| Inline `<script>` blocks | 93 |
| Inline `<style>` blocks | 35 |
| Total inline JS | 283,415 chars |
| Total inline CSS | 350,613 chars |

**Assessment**: This is Elementor's output combined with plugin CSS injection. The 808KB HTML is mostly inline CSS/JS that belongs in enqueued files. This is a known Elementor pattern but it is at an extreme end.

### Image Optimization
- **0 of 28 homepage images use WebP format** — all PNG/JPG
- **24 of 28 images have no `loading="lazy"` attribute** — all load immediately
- **0 images have `fetchpriority="high"`** — no LCP optimization hint
- **0 preload hints** in `<head>` for hero image or video poster
- Gravatar images (2x) load without alt text
- All WP-uploaded images are served from `purebrain.ai/wp-content/uploads/` — no CDN for images

**LCP risk**: The hero video autoplay tag exists but no poster image is preloaded. Browser must guess what to preload for LCP.

---

## 2. SEO

### Sitemap
- Sitemap index at `/sitemap_index.xml` — 5 sitemaps (posts, pages, categories, tags, author)
- Page sitemap has **57 entries**
- **11 internal/test pages are in the page sitemap** — actively being indexed by Google:
  - `/video-test/` — dev page
  - `/homepage-clone-v2/` — dev page
  - `/homepage-clone-test/` — dev page
  - `/elementor-1502/` — orphan Elementor draft page
  - `/pay-test-5/` and `/pay-test-sandbox-5/` — live payment test pages
  - `/refer/` — duplicate of `/refer-and-earn/`
  - `/hunden-proposal/` — client proposal page (confidential)
  - `/brainiac-mastermind-training/` and sub-page — internal training portal
  - `/training/` — redirect stub

### Robots.txt
Current state:
```
User-agent: *
Disallow:
Sitemap: https://purebrain.ai/sitemap_index.xml
```
**Status: STILL UNFIXED from March 6 audit.** `/wp-admin/` and `/wp-login.php` are not blocked. All pages are crawlable including test and internal pages. This was flagged on March 6 — it has not been addressed.

### Blog Posts Missing Meta Descriptions — 7 Posts
These 7 published blog posts have NO meta description. They will show unpredictable Google-generated snippets in search results:

| Post ID | Slug |
|---------|------|
| 1441 | `/your-ai-resets-to-zero-every-morning/` |
| 1423 | `/teach-your-ai-something-no-one-else-can/` |
| 1378 | `/52-billion-ai-agents-market-is-not-the-story/` |
| 1307 | `/age-of-ai-agents-next-18-months/` |
| 1281 | `/something-big-already-happened-you-just-werent-invited-yet/` |
| 1245 | `/the-ai-that-forgets-you-every-single-time/` |
| 1228 | `/the-context-tax/` |

**Note**: OG title is present for all — so social shares work. Only the search snippet is missing.

### Blog Post Missing OG Image — 1 Post
- Post 1441 (`/your-ai-resets-to-zero-every-morning/`) has a featured image (ID 1440, PNG exists at WP uploads) but Yoast is not picking it up as OG image. The image may not be set correctly in Yoast SEO settings or the PNG has an issue.

### Pages Missing Meta Descriptions — 44 of 92 Pages
Many are internal/test pages (expected), but several public-facing pages lack meta:
- `/developers/` — public-facing developer page, no meta
- `/refer-and-earn/` — referral program page, no meta
- `/openclaw/`, `/enso/`, `/supercool/`, `/billiereview/`, `/boardy/` — 5 new compare pages, no meta
- `/unified-how-this-levels-you-up/` and `/partnered-how-this-levels-you-up/` — tier detail pages, no meta

### Pages Missing OG Images — 48 of 92 Pages
Same pattern — new pages built without Yoast OG setup. The 5 new compare pages (openclaw, enso, supercool, billiereview, boardy) have no OG image for social sharing.

### Template Audit — 5 New Compare Pages Still Wrong Template
Pages built in the March 9–10 sprint with `slug` set to their name but deployed under `/compare/` parent:

| Page ID | Slug | Actual URL | Template |
|---------|------|-----------|---------|
| 1463 | boardy | `/compare/boardy/` | `""` (default, not elementor_canvas) |
| 1462 | billiereview | `/compare/billiereview/` | `""` |
| 1461 | supercool | `/compare/supercool/` | `""` |
| 1460 | enso | `/compare/enso/` | `""` |
| 1459 | openclaw | `/compare/openclaw/` | `""` |

Also:
- `[174] /purebrain-2-0/` uses `elementor_header_footer` — wrong template (not canvas, not default)
- `/refer/` — uses default template (not canvas), and `/refer/` vs `/refer-and-earn/` are two separate live pages with no redirect between them

### Dead /pricing/ URL — 404 Cached by Cloudflare
`https://purebrain.ai/pricing/` returns HTTP 404 with Cloudflare caching headers showing `cache-control: max-age=2678400` (31 days). The 404 is being cached for 31 days. If any external site links to `/pricing/`, those visitors hit a cached 404 and cannot reach the actual pricing page at `/invitation/`.

**Fix**: Either create a WP page at `/pricing/` that redirects to `/invitation/`, or add a Cloudflare Page Rule to redirect `/pricing/*` → `/invitation/`.

### Structured Data
Present schema types: `ListItem`, `Organization`, `WebPage`, `ImageObject`, `EntryPoint`, `WebSite`, `ReadAction`, `BreadcrumbList`, `SearchAction`, `PropertyValueSpecification`.

**Missing**: `FAQPage` schema on blog posts with accordion/FAQ sections. This was flagged in the March 9 audit and remains unimplemented.

---

## 3. UX / CONVERSION

### Pricing Visibility on Homepage
The homepage DOES show pricing: `$79`, `$149`, `$499`, `$999` all appear in the chatbox pricing section. This is an improvement vs March 6. However, pricing is only visible after chatbox interaction — not in the above-the-fold content.

### Social Proof
Positive finding: The homepage now has 48 "testimonial" mentions in HTML and 31 "review" mentions. Social proof exists. This addresses the critical gap from the March 6/9 audits.

### /pricing/ → 404
Any user typing "purebrain.ai/pricing" hits a dead end. This is a meaningful conversion leak. See SEO section above.

### Dual /refer/ Pages
- `/refer/` (ID 1310) — published, no meta, default template
- `/refer-and-earn/` (ID 1298) — published, no meta, default template
Both live simultaneously. Referral program link equity and SEO value is split between two URLs. Should 301 redirect `/refer/` to `/refer-and-earn/`.

### New Compare Pages (301 Redirect Pattern)
Accessing `/openclaw/` → 301 → `/compare/openclaw/`. The redirect works but:
1. Any external links to the short URL pass through an extra redirect hop before reaching the page
2. The canonical URL is `/compare/openclaw/` which is correct

---

## 4. TECHNICAL DEBT

### 13 Internal Pages Publicly Published
These pages are live, indexable, and accessible to anyone:

| ID | Slug | Risk |
|----|------|------|
| 1528 | `/pay-test-sandbox-5/` | Live payment test |
| 1527 | `/pay-test-5/` | Live payment test |
| 1508 | `/homepage-clone-test/` | Dev artifact |
| 1502 | `/elementor-1502/` | Orphan Elementor draft |
| 1496 | `/homepage-clone-v2/` | Dev artifact |
| 1394 | `/hunden-proposal/` | Client confidential content |
| 1326 | `/bloomberg-bpipe-demo/` | Client proposal |
| 1128 | `/homepage-backup/` | Backup page |
| 1118 | `/video-test/` | Dev page |
| 383 | `/purebrain-4/` | Old site version |
| 338 | `/purebrain-3/` | Old site version |
| 174 | `/purebrain-2-0/` | Old site version (wrong template too) |
| 95 | `/blog-old/` | Old blog archive |

**Recommended action**: Set all to `private` status via WP REST API. Except hunden-proposal which should be password-protected (not just private).

### Homepage HTML Bloat — Root Cause
The 808KB homepage HTML is driven by:
1. Elementor rendering CSS inline for every section
2. Plugin CSS injected 3–4x due to extract-from-page + original-still-in-Elementor pattern
3. 123 external JS files — most are WordPress core, theme, and plugin scripts
4. 93 inline script blocks, many duplicate or redundant

This cannot be fully fixed without either (a) migrating off Elementor or (b) aggressively consolidating plugins and extracting inline CSS to enqueued files.

**Short-term wins**: Remove duplicate CSS blocks (#pb-aether-footer CSS appearing 103x), dequeue duplicate jQuery registrations.

---

## 5. A/B TEST OPPORTUNITIES

1. **Homepage CTA above the fold**: Current — no pricing visible without scrolling or chatbox interaction. Test: Add "Plans from $149/mo — See All Options" anchor link in hero section.

2. **Blog meta descriptions**: 7 posts without meta. Write compelling 150-char meta for each and measure CTR change in Google Search Console over 30 days.

3. **/invitation/ page headline test**: "By Invitation Only" framing may reduce intent-driven traffic. Test variant: "PureBrain Plans — Choose Your Tier" with direct pricing grid visible without scroll.

4. **LCP improvement test**: Add `fetchpriority="high"` to hero video poster image and measure Core Web Vitals improvement.

5. **Comparison page OG images**: The 5 new compare pages have no OG image. Adding custom OG images (e.g., PureBrain logo vs competitor logo split-screen) before sharing could improve social CTR.

---

## 6. PRIORITIZED ACTION LIST

### Tier 1 — Fix Now (Security + Broken Conversions)
1. **Set 13 internal/test pages to private** — stops indexing, prevents client content exposure
2. **Fix /pricing/ → /invitation/ redirect** — stops conversion leak from dead URL (cached 31 days by Cloudflare)
3. **Update robots.txt** — add `Disallow: /wp-admin/` and `Disallow: /wp-login.php` (flagged March 6, still open)
4. **Remove /refer/ page or redirect to /refer-and-earn/** — consolidate referral page SEO

### Tier 2 — SEO Fixes (High Impact, Low Effort)
5. **Set elementor_canvas on 5 new compare pages** (IDs 1459–1463) — one API call each
6. **Write meta descriptions for 7 blog posts** — direct search CTR improvement
7. **Fix OG image for post 1441** (`your-ai-resets-to-zero-every-morning`) — featured image exists but Yoast not reading it
8. **Write meta descriptions for key public pages**: `/developers/`, `/refer-and-earn/`, new compare pages

### Tier 3 — Performance (Medium Effort, Measurable Gain)
9. **Eliminate duplicate jQuery** — dequeue redundant registrations (saves ~2 extra HTTP requests per page load)
10. **Remove duplicate CSS blocks** — especially the `#pb-aether-footer` CSS appearing 103x
11. **Add `fetchpriority="high"` to hero LCP element** — homepage Core Web Vitals improvement
12. **Add lazy loading to non-hero images** — 24 images load eagerly, most should be lazy

### Tier 4 — Architectural (Higher Effort, Long-Term Health)
13. **FAQPage schema on top 5 blog posts** — enables rich results in Google
14. **Image CDN / WebP conversion** — currently 0 WebP images; all PNG/JPG served from WP uploads
15. **Plugin consolidation** — 34 total plugins (22 active) with duplicate CSS injection pattern
16. **Investigate invitation page TTFB** — 0.68s TTFB vs homepage 0.16s; check if Cloudflare page rule excludes it

---

## 7. STATUS OF PREVIOUSLY FLAGGED ISSUES

| Issue | First Flagged | Status |
|-------|--------------|--------|
| robots.txt missing wp-admin block | March 6 | STILL OPEN |
| Social proof on homepage | March 6, 9 | FIXED — testimonials now present |
| Pricing not visible on homepage | March 6 | PARTIALLY FIXED — visible in chatbox, not above fold |
| GIF background video | March 9 | FIXED — now using mp4 |
| 13 test pages publicly published | March 10 | STILL OPEN |
| 5 new compare pages missing elementor_canvas | March 10 | STILL OPEN |
| Duplicate CSS injection (pb-aether-footer) | March 10 | STILL OPEN |
| jQuery loading 3x | This audit | NEW FINDING |
| /pricing/ 404 cached by Cloudflare | This audit | NEW FINDING |
| 7 blog posts missing meta descriptions | This audit | NEW FINDING |
| No LCP optimization hints | This audit | NEW FINDING |

---

## 8. QUICK WINS — IMPLEMENT TONIGHT

These can be done via WP REST API without Jared's review:

### A. Set 5 new compare pages to elementor_canvas
```
PUT /wp/v2/pages/1459  { "template": "elementor_canvas" }
PUT /wp/v2/pages/1460  { "template": "elementor_canvas" }
PUT /wp/v2/pages/1461  { "template": "elementor_canvas" }
PUT /wp/v2/pages/1462  { "template": "elementor_canvas" }
PUT /wp/v2/pages/1463  { "template": "elementor_canvas" }
```

### B. Set internal/test pages to private
```
PUT /wp/v2/pages/1508  { "status": "private" }  -- homepage-clone-test
PUT /wp/v2/pages/1502  { "status": "private" }  -- elementor-1502
PUT /wp/v2/pages/1496  { "status": "private" }  -- homepage-clone-v2
PUT /wp/v2/pages/1118  { "status": "private" }  -- video-test
PUT /wp/v2/pages/383   { "status": "private" }  -- purebrain-4
PUT /wp/v2/pages/338   { "status": "private" }  -- purebrain-3
PUT /wp/v2/pages/174   { "status": "private" }  -- purebrain-2-0
PUT /wp/v2/pages/95    { "status": "private" }  -- blog-old
PUT /wp/v2/pages/1128  { "status": "private" }  -- homepage-backup
```
(Leave pay-test pages and hunden pages for Jared to decide — they may be actively in use)

### C. Add /pricing/ redirect
Create WP page with slug `pricing` that has a meta redirect to `/invitation/`, OR add Cloudflare redirect rule (preferred — no WP page needed).

---

*Report generated by dept-systems-technology | 2026-03-11*
