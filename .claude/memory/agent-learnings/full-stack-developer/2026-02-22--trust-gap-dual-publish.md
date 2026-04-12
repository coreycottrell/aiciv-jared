# WordPress Dual Publish: "The AI Trust Gap Is the Real Problem"

**Date**: 2026-02-22
**Agent**: full-stack-developer
**Type**: operational
**Topic**: Dual blog post publication to purebrain.ai + jareddsanborn.com

---

## Task

Published blog post "The AI Trust Gap Is the Real Problem (Not the Technology)" to both WordPress sites.

## Published URLs

- **purebrain.ai**: https://purebrain.ai/the-ai-trust-gap/ (Post ID: 631)
- **jareddsanborn.com**: https://jareddsanborn.com/2026/02/22/the-ai-trust-gap/ (Post ID: 1122)

## Media IDs

- purebrain.ai: Media ID 630 (trust-gap-blog-banner.png)
- jareddsanborn.com: Media ID 1121

## Category IDs Used

- purebrain.ai: Category 5 = "AI Strategy" (created fresh this session)
- jareddsanborn.com: Category 13 = "AI Strategy" (created fresh this session)

## Author IDs

- purebrain.ai: Author 3 (Aether PureBrain.ai - also current user)
- jareddsanborn.com: Author 2 (Jared - determined from existing posts)

## Tags Created

- purebrain.ai: [6, 7, 8, 9, 10] = AI adoption, enterprise AI, AI trust, AI partnership, digital transformation
- jareddsanborn.com: [14, 15, 16, 17, 18] = same names

## Interlink Handling

- purebrain.ai version: used `https://purebrain.ai/why-95-percent-of-ai-pilots-fail/`
- jareddsanborn.com version: used `https://jareddsanborn.com/2026/02/21/why-95-percent-of-ai-pilots-fail/`
- Confirmed JDS post exists (ID: 1092) before using the URL

## Category Discovery Pattern

- PureBrain only had: AI Insights (2), For Individuals (3), For Teams (4)
- JDS only had: AI Insights (9), Leadership (12), Marketing (10), Technology (11), Uncategorized (1)
- "AI Strategy" did NOT exist on either site - had to create it (POST /wp-json/wp/v2/categories)

## Workflow That Worked

1. Check existing categories and users first (GET /wp-json/wp/v2/categories, /wp-json/wp/v2/users/me)
2. Create "AI Strategy" category on both sites
3. Upload banner via POST /wp-json/wp/v2/media with Content-Disposition header
4. Build HTML manually from markdown (no pandoc)
5. Create tags via get-or-create pattern (search first, create if not found)
6. POST to /wp-json/wp/v2/posts with all fields
7. Verify with API GET + live HTTP 200 check

## Verification (All Passed)

- [x] Status = "publish" on both sites
- [x] Featured media ID set on both posts
- [x] #awakening CTA link present in both
- [x] pt-social-share social icons present in both
- [x] blog-cta-block CTA block present in both
- [x] Site-specific interlinks used correctly
- [x] HTTP 200 on both live URLs
- [x] No test page links in either post

---

**End of Memory**
