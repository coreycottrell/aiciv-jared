# FAQ Deployment: Remaining Blog Posts

**Date**: 2026-02-21
**Agent**: full-stack-developer
**Type**: operational

---

## Summary

Deployed structured FAQ sections (with JSON-LD FAQPage schema) to all remaining blog posts
on purebrain.ai and their jareddsanborn.com dual-publish equivalents.

**Result**: All 8 purebrain.ai posts + 8 JDS counterpart posts now have FAQ sections.
16 posts total -- complete coverage.

---

## What Was Found (Pre-Deployment Audit)

When the task was assigned, posts 480, 381, 316, 373, 98 on purebrain.ai already had
`class="faq-section"` markup from a previous session. Only post 606 was missing it.

**Posts with FAQs BEFORE this session:**
- PB 480, 381, 316, 373, 98 (from a prior session)
- PB 565, 172 (from 2026-02-20 content-specialist session)
- JDS 1069, 1065, 1056, 1060, 1039 (counterparts, already done)
- JDS 1074, 1045 (counterparts from 2026-02-20)

**Posts needing FAQs (this session):**
- PB 606: "Why 95% of AI Pilots Fail (And What the 5% Do Differently)"
- JDS 1092: Same article (dual-publish counterpart)

---

## Post ID Mapping (Complete Reference)

| purebrain.ai | JDS | Slug / Article |
|-------------|-----|----------------|
| 480 | 1069 | why-your-ai-pilot-is-succeeding-and-failing-at-the-same-time |
| 381 | 1065 | ceo-vs-employee-ai-transformation-gap |
| 316 | 1056 | why-ai-memory-changes-everything |
| 373 | 1060 | most-ai-agents-break-the-moment-you-ask-where-the-data-goes |
| 98  | 1039 | how-my-human-named-me-and-what-it-meant |
| 606 | 1092 | why-95-percent-of-ai-pilots-fail |
| 565 | 1074 | the-difference-between-using-ai-and-having-an-ai-partner |
| 172 | 1045 | what-i-actually-do-all-day |

---

## FAQ Content Written for Post 606 / JDS 1092

6 FAQ items targeting PAA (People Also Ask) queries:

1. **Why do 95% of enterprise AI pilots fail?** — MIT stat, generic vs specialized, org infrastructure
2. **What is AI Pilot Purgatory?** — Two-thirds of enterprises stuck, governance fix
3. **What is the Context Tax in AI deployments?** — Re-briefing cost, memory as solution
4. **What do the 5% of successful AI organizations do differently?** — Infrastructure mindset, outcome metrics, depth-first
5. **How is a specialized AI partner different from generic AI tools?** — Context persistence, relationship vs reset
6. **Is AI worth investing in given such a high failure rate?** — Yes, but approach matters

Internal links added in FAQ answers:
- "genuine AI partnership" → purebrain.ai/blog/the-difference-between-using-ai-and-having-an-ai-partner/
- "how memory changes everything" → purebrain.ai/blog/why-ai-memory-changes-everything/

---

## Technical Execution

**Script**: `/home/jared/projects/AI-CIV/aether/tools/add_faqs_post606.py`

**Method**: WordPress REST API
- GET `/wp-json/wp/v2/posts/{id}?context=edit` to fetch raw content
- Idempotency check: skip if `class="faq-section"` already present
- Insertion: JSON-LD + FAQ HTML injected BEFORE `<div class="blog-cta-block"`
- POST `/wp-json/wp/v2/posts/{id}` with `{"content": new_content}` to update
- Verification: re-fetch and count `class="faq-section"` occurrences
- Cache clear: DELETE `/wp-json/elementor/v1/cache` on purebrain.ai

**Note on JDS cache clear**: JDS returned 404 for Elementor cache endpoint (expected -- Elementor
may not be active on JDS, or endpoint path differs). JDS posts use classic editor / standard WP
rendering so no Elementor cache clearing needed.

---

## Key Patterns / Lessons

1. **Always audit before executing** -- Most posts already had FAQs from prior sessions. Running
   the full audit first prevented duplicate FAQ injections on 10 posts.

2. **PB and JDS slugs differ slightly** -- JDS sometimes uses a slightly different slug
   (e.g., JDS uses "ai-pilot-purgatory" for the post PB calls "why-your-ai-pilot-is-succeeding...").
   Always use the post ID mapping above, not slug lookups.

3. **Idempotency check matters** -- The `class="faq-section"` check correctly skipped 14 of 16
   posts, only updating the 2 that actually needed it.

4. **blog-cta-block is the universal insertion point** -- All purebrain.ai and JDS posts have
   this div. It's the consistent anchor for FAQ insertion.

5. **JSON-LD schema format**: Uses standard FAQPage schema. The script wraps the entire block
   in a `<script type="application/ld+json">` tag placed immediately before the FAQ HTML.

6. **JDS total posts = 9** -- As of 2026-02-21, jareddsanborn.com has 9 published posts total.
   8 are dual-published from purebrain.ai, 1 is unique (Why Your AI Should Have a Name / post 998).

---

## Final Verification Results

All 16 posts confirmed: `faq=True` with correct item counts.

| Site | Post | FAQ Items |
|------|------|-----------|
| purebrain.ai | 480 | 6 |
| purebrain.ai | 381 | 6 |
| purebrain.ai | 316 | 5 |
| purebrain.ai | 373 | 5 |
| purebrain.ai | 98  | 5 |
| purebrain.ai | 606 | 6 (NEW) |
| purebrain.ai | 565 | 6 |
| purebrain.ai | 172 | 6 |
| jareddsanborn.com | 1069 | 6 |
| jareddsanborn.com | 1065 | 6 |
| jareddsanborn.com | 1056 | 5 |
| jareddsanborn.com | 1060 | 5 |
| jareddsanborn.com | 1039 | 5 |
| jareddsanborn.com | 1092 | 6 (NEW) |
| jareddsanborn.com | 1074 | 6 |
| jareddsanborn.com | 1045 | 6 |
