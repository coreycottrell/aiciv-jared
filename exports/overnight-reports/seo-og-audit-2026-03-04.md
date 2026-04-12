# SEO Snippet + OG Image Audit & Fix Report
**Date**: 2026-03-03 (for 2026-03-04 delivery)
**Agent**: dept-systems-technology
**Site**: purebrain.ai
**SEO Plugin**: Yoast SEO v27.0

---

## Executive Summary

Full SEO audit completed across all 62 published pages and 16 published blog posts on purebrain.ai.

**Total items audited**: 78 (62 pages + 16 posts)
**Fixes applied**: 47 updates across pages and posts
**Result**: All public-facing pages and posts now have proper OG image and meta description set in Yoast

---

## What Was Fixed

### Pages: OG Image Added (10 pages)

These public pages had no Yoast OG image set. All now use the standard PureBrain OG image:
`https://purebrain.ai/wp-content/uploads/2026/02/purebrain-homepage-og.jpg` (media ID: 694)

| ID | Slug | OG Image | Meta Desc |
|----|------|----------|-----------|
| 1206 | hunden-partners | ADDED | ADDED |
| 1205 | investor-intelligence | ADDED | ADDED |
| 1200 | purebrain-for-danby-appliances | ADDED | ADDED |
| 1196 | purebrain-for-staycation-breaks | ADDED | ADDED |
| 1190 | purebrain-vs-glbgpt | ADDED | ADDED |
| 1156 | purebrain-for-graham-martin-responsible-gambling | ADDED | ADDED |
| 1155 | purebrain-for-graham-martin-virya-intelligence | ADDED | ADDED |
| 1154 | purebrain-for-graham-martin-chairman-intelligence | ADDED | ADDED |
| 1153 | purebrain-for-graham-martin-casino-ai | ADDED | ADDED |
| 1150 | purebrain-for-graham-martin | ADDED | ADDED |

### Pages: OG Image Added (already had meta desc)

| ID | Slug | Note |
|----|------|------|
| 1115 | training | OG image added |
| 1044 | purebrain-vs-sitegpt | OG image added |
| 541 | terms-of-service | OG image added |
| 3 | privacy-policy | OG image added |

### Blog Posts: Meta Description Set (16 posts)

ALL 16 published blog posts now have custom `_yoast_wpseo_metadesc` set:

| ID | Slug | Fix Applied |
|----|------|-------------|
| 1189 | the-age-of-ai-agents | metadesc + focuskw |
| 1139 | your-ai-doesnt-work-for-you | metadesc + excerpt + focuskw |
| 1084 | ai-doesnt-make-your-team-smarter | metadesc + focuskw |
| 966 | the-first-90-days-of-an-ai-partnership | metadesc + focuskw |
| 950 | your-ai-has-no-memory-mine-does | metadesc + focuskw |
| 879 | your-next-direct-report-wont-be-human | metadesc + focuskw |
| 696 | we-both-wrote-this-post | metadesc |
| 631 | the-ai-trust-gap | metadesc + focuskw |
| 606 | why-95-percent-of-ai-pilots-fail | metadesc + focuskw |
| 565 | the-difference-between-using-ai-and-having-an-ai-partner | metadesc + focuskw |
| 480 | why-your-ai-pilot-is-succeeding-and-failing-at-the-same-time | metadesc |
| 381 | ceo-vs-employee-ai-transformation-gap | metadesc |
| 316 | why-ai-memory-changes-everything | metadesc |
| 373 | most-ai-agents-break-the-moment-you-ask-where-the-data-goes-2 | metadesc |
| 172 | what-i-actually-do-all-day | metadesc |
| 98 | how-my-human-named-me-and-what-it-meant | metadesc |

**Special fix on post 1139**: The Yoast og:description was pulling from the post excerpt, which contained the author byline (`By Jared Sanborn...`). Fixed by setting the proper excerpt AND the `_yoast_wpseo_metadesc`.

---

## Pages Already OK (No Action Needed)

The following public pages already had correct Yoast OG image + meta description:

| ID | Slug |
|----|------|
| 1006 | portfolio |
| 1001 | pitch |
| 993 | your-ai-tim-cook |
| 987 | invitation |
| 929 | mission-vision-values |
| 923 | partners |
| 860 | ai-website-execution |
| 816 | ai-website-analysis |
| 800 | migrate |
| 794 | why-purebrain |
| 777 | ai-tool-stack-calculator |
| 760 | purebrain-vs-perplexity |
| 759 | purebrain-vs-jasper |
| 758 | purebrain-vs-gemini |
| 757 | purebrain-vs-deepseek |
| 756 | purebrain-vs-custom-gpts |
| 755 | purebrain-vs-copilot |
| 754 | purebrain-vs-claude |
| 753 | purebrain-vs-chatgpt |
| 752 | compare |
| 731 | about-aether |
| 700 | blog-neural-feed-memories |
| 620 | ai-partnership-audit |
| 577 | ai-adoption-review |
| 405 | ai-partnership-guide |
| 403 | ai-readiness-assessment |
| 319 | blog |
| 284 | ai-partnership-assessment |
| 11 | pure-brain-agentic-ai-partner (homepage) |

---

## Pages Skipped (Noindex or Internal)

These pages are correctly noindexed or are internal tools - no OG meta needed:

| ID | Slug | Reason |
|----|------|--------|
| 689 | pay-test-2 | noindex |
| 688 | pay-test-sandbox-2 | noindex |
| 1118 | video-test | internal |
| 439 | pay-test | noindex |
| 963 | demo-no-bs | noindex |
| 859 | client-report-duckdive | noindex |
| 855 | website-execution | noindex |
| 854 | duckdive-report | noindex |
| 843 | team-dashboard | noindex |
| 811 | ai-partnership-calculator | noindex (redirects) |
| 532 | living-avatar | noindex |
| 468 | pay-test-sandbox | noindex |
| 383 | purebrain-4 | noindex |
| 338 | purebrain-3 | noindex |
| 309 | thank-you | noindex |
| 174 | purebrain-2-0 | noindex |
| 95 | blog-old | noindex |
| 1128 | homepage-backup | internal backup |

---

## Technical Notes

### Yoast Meta Field Availability

- `_yoast_wpseo_opengraph-image` and `_yoast_wpseo_metadesc` are registered for **pages** via `register_meta` with `show_in_rest=true`
- For **posts**, these fields are NOT exposed via standard WP REST API
- Fix: Used the custom `purebrain/v1/update-post-meta` REST endpoint (authenticated admin-only)
- This endpoint uses `update_post_meta()` directly and bypasses the REST API registration requirement

### OG Image Verification Method

The authoritative source for live OG metadata is Yoast's head API:
```
GET /wp-json/yoast/v1/get_head?url=ENCODED_PAGE_URL
```

This returns the exact head HTML Yoast will output - including og:image, description, etc.
Social crawlers (LinkedIn, Facebook, Twitter) typically request this from origin, bypassing CDN cache.

### CDN Cache Note

Cloudflare CDN may serve stale HTML for up to TTL period after meta updates.
The Yoast head API (`/wp-json/yoast/v1/get_head`) always returns fresh data.
Social card scrapers typically bypass CDN and see fresh content.

### Default OG Image

- URL: `https://purebrain.ai/wp-content/uploads/2026/02/purebrain-homepage-og.jpg`
- Media ID: 694
- Dimensions: 1200x627 (optimal for Open Graph)
- Applied to: all pages that don't have a page-specific image

### Blog Post OG Images

All 16 blog posts use their individual banner images as OG images (auto-set by Yoast from featured image).
No override needed - each post has a unique, properly sized banner.

### Twitter Card

All posts and pages have `twitter:card: summary_large_image` set by Yoast.
No explicit `twitter:image` is set - Twitter/X falls back to `og:image` per their spec.
This is the correct behavior for a site that doesn't need platform-specific image variants.

---

## Focus Keywords Added (Blog Posts)

| ID | Post | Focus Keyword |
|----|------|---------------|
| 1189 | The Age of AI Agents | AI agents for business |
| 1139 | Your AI Doesn't Work For You | AI not working for your business |
| 1084 | AI Doesn't Make Your Team Smarter | AI competence gap |
| 966 | The First 90 Days of an AI Partnership | first 90 days AI partnership |
| 950 | Your AI Has No Memory, Mine Does | AI memory persistence |
| 879 | Your Next Direct Report Won't Be Human | AI direct reports |
| 631 | The AI Trust Gap | AI trust gap enterprise |
| 606 | Why 95 Percent of AI Pilots Fail | why AI pilots fail |
| 565 | The Difference Between Using AI and Having an AI Partner | AI partner vs AI tool |

---

## Verification Status

All fixes verified via:
1. WP REST API meta field read-back (pages)
2. Yoast head API response check (`/wp-json/yoast/v1/get_head?url=...`)
3. Direct curl to confirm API responses contain correct og:image and description

**All public pages**: OG image OK, meta description OK
**All blog posts**: OG image OK (featured image), meta description OK
**Post 1139**: Special fix - excerpt updated + metadesc set, verified description now correct

---

## Recommended Next Steps

1. **Homepage OG image review**: The homepage uses a GIF for LinkedIn (og:image) + static for Twitter (twitter:image). This special split is already configured correctly per the 2026-02-23 memory.

2. **New pages**: Any new page created should have OG image and meta description set before publishing. Consider adding this to the page creation checklist.

3. **Blog post excerpts**: Future blog posts should have a manually set excerpt (not auto-generated from content) to ensure proper Yoast description generation.

4. **Google Search Console**: After 2-3 days, check GSC for any description changes being indexed. Access requires adding purebrain@puremarketing.ai as a GSC owner.
