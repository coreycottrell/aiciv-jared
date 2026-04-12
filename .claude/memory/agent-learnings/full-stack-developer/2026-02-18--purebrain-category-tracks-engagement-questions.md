# WordPress Category Tracks + Engagement Questions

**Date**: 2026-02-18
**Type**: operational
**Topic**: Adding audience category navigation and engagement questions to purebrain.ai blog

---

## Task Summary

Two sub-tasks completed for purebrain.ai:
1. Created "For Individuals" / "For Teams" category tracks with filter nav on blog page
2. Added topic-specific engagement questions to all 5 posts, positioned before existing CTA blocks

## What Was Done

### Sub-Task A: Category Tracks

**Categories Created** (via `POST /wp-json/wp/v2/categories`):
- `for-individuals` (ID: 3) - "AI partnership insights for individual professionals and solopreneurs"
- `for-teams` (ID: 4) - "AI transformation strategy for teams and enterprise organizations"

**Post Assignments:**
| Post ID | Title | Categories |
|---------|-------|------------|
| 381 | CEO Sees AI Differently | for-teams (4) |
| 316 | Why AI Memory Changes Everything | for-individuals (3) + for-teams (4) |
| 373 | Most AI Agents Break... | for-teams (4) |
| 172 | What I Actually Do All Day | for-individuals (3) |
| 98  | How My Human Named Me | for-individuals (3) |

**Blog Page Navigation** (Page ID 319):
- Added `<div class="blog-category-nav">` with 3 pill links prepended to page content
- Links: /category/for-individuals/ (blue), /category/for-teams/ (orange), /blog/ (white/neutral)

### Sub-Task B: Engagement Questions

All 5 posts received a `<div class="blog-engagement-question">` block:
- Post 381: "What's the biggest gap between how leadership and your team talk about AI at your company?"
- Post 316: "How much time do you spend re-explaining context to your AI tools every week?"
- Post 373: "What question kills AI demos at your company?"
- Post 172: "If your AI could autonomously handle one thing while you sleep, what would it be?"
- Post 98: "If you named your AI partner, what would you call it — and why?"

## Key Patterns

### Idempotency Check Pattern
Always check before modifying:
```python
if "blog-engagement-question" in content:
    # skip - already done
```

### Insert Before CTA Pattern
```python
if "blog-cta-block" in content:
    idx = content.find('class="blog-cta-block"')
    div_start = content.rfind("<div", 0, idx)
    updated = content[:div_start] + new_block + "\n" + content[div_start:]
```

### Concurrent Agent Awareness
When other agents may be editing same posts (CTA standardization agent was active),
wait 30 seconds and always fetch fresh content before modifying.

### Category "term_exists" Error
If `POST /categories` returns 400 with `term_exists`, fetch existing ID via:
```python
cats_resp = requests.get(f"{base}/categories?slug={slug}", auth=auth)
existing_id = cats_resp.json()[0]["id"]
```

## Verification Results

All 13 verification checks passed:
- Both categories exist with correct IDs
- All 5 posts have correct category assignments
- Blog page has all 5 category nav elements
- All 5 posts have engagement questions positioned BEFORE CTA blocks

## Site Details

- Site: https://purebrain.ai
- Blog page: ID 319
- Auth: ("Aether", "FlFr2VOtlHiHaJWjzW96OHUJ")
- Rate: 3 seconds between API calls
