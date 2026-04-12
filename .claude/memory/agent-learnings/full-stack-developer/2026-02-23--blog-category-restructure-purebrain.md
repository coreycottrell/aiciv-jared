# Blog Category Structure Restructure - purebrain.ai

**Date**: 2026-02-23
**Agent**: full-stack-developer
**Type**: teaching
**Topic**: How to restructure WordPress category/tag taxonomy via REST API, remove dual-categorization, and add fresh content sections

---

## What Was Done

5 tasks completed for purebrain.ai blog category restructure:

1. **Category cleanup**: Removed all dual-categorization across 10 posts. Each post now has exactly ONE primary category.
2. **Tag system created**: 8 new topic tags created (Memory, Trust, AI Pilots, Partnership, Leadership, Security, Strategy, Identity). All posts tagged with 2-4 relevant topic tags.
3. **AI Strategy consolidation**: Moved post 631 (AI Trust Gap) from AI Strategy → AI Insights. AI Strategy category now empty (kept for future).
4. **404 gap check**: IDs 173-315 all return 404 - these are deleted/draft posts with no public URLs needing redirects.
5. **Fresh content**: Added 1-2 paragraph fresh sections to posts 98 and 172 before the CTA block.

## Category Structure After

| Category ID | Name | Count |
|-------------|------|-------|
| 3 | For Individuals | 3 (98, 172, 696) |
| 4 | For Teams | 3 (316, 373, 381) |
| 2 | AI Insights | 4 (480, 565, 606, 631) |
| 5 | AI Strategy | 0 (empty, kept) |
| 14 | AI Partnership | 0 (empty, kept) |
| 15 | Origin Story | 0 (empty, kept) |

## Tag IDs Created

| Tag | ID |
|-----|----|
| Memory | 16 |
| Trust | 17 |
| AI Pilots | 18 |
| Partnership | 19 |
| Leadership | 20 |
| Security | 21 |
| Strategy | 22 |
| Identity | 23 |

## Key Learnings

### 1. WP REST API - Updating categories/tags is a simple PATCH

```python
requests.post(
    '/wp-json/wp/v2/posts/{id}',
    auth=('Aether', APP_PASSWORD),
    json={'categories': [3], 'tags': [16, 19]}  # arrays of IDs
)
```

Setting `categories` to a list with ONE item removes all previous assignments and sets exactly that one. No need to explicitly remove old ones.

### 2. Creating tags - Handle 'term_exists' gracefully

If a tag already exists, the API returns 400 with `term_exists`. Check by slug:
```python
r = requests.get(f'{BASE}/wp-json/wp/v2/tags?slug={slug}', auth=AUTH).json()
```

### 3. Fresh content insertion point

For purebrain.ai blog posts structure:
- Content → FAQ sections → `<div class="blog-cta-block">` → newsletter subscribe div

Best insertion point for fresh sections: **before the `<div class="blog-cta-block">`** so fresh content appears before the CTA.

For posts with internal links section: insert before `<p><!-- Internal Links:`.

### 4. 404 Gap Investigation

The gap between post IDs 172 and 316 (IDs 173-315) all return HTTP 404. These are deleted/draft posts. Since none have been publicly linked (no LinkedIn/social posts pointing to them in that range), no redirects needed. Document the finding and move on.

### 5. Category Strategy Logic

- **For Individuals**: Personal/origin stories, AI day-in-the-life, founder perspective
- **For Teams**: Security, memory for orgs, CEO vs team dynamics, inter-org AI
- **AI Insights**: Broad strategic insights, pilot statistics, conceptual thought leadership

---

**End of Memory**
