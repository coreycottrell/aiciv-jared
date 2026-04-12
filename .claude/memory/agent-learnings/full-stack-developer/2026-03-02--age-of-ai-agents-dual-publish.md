# WordPress Dual Publish: "The Age of AI Agents"

**Date**: 2026-03-02
**Agent**: full-stack-developer
**Type**: operational
**Topic**: Dual blog post publication to purebrain.ai + jareddsanborn.com

---

## Task

Published "The Age of AI Agents: Why Your Business Needs a Team of AIs, Not Just One" to both WordPress sites as status=publish with banner uploaded from Telegram delivery.

## Published URLs

- **purebrain.ai**: https://purebrain.ai/the-age-of-ai-agents/ (Post ID: 1189)
- **jareddsanborn.com**: https://jareddsanborn.com/2026/03/02/the-age-of-ai-agents/ (Post ID: 1220)

## Media IDs

- purebrain.ai: Media ID 1188 (the-age-of-ai-agents-banner.png)
- jareddsanborn.com: Media ID 1219

## Category IDs Used

- purebrain.ai: Category 24 = "Agentic AI" (created fresh this session)
- jareddsanborn.com: Category 13 = "AI Strategy" (existed)

## Author IDs

- purebrain.ai: Author 3 (Aether)
- jareddsanborn.com: Author 4 (AetherPureBrain.ai)

## Banner Source

- File: `docs/from-telegram/the-age-of-ai-agents - blog-post- Newsletter size.png`
- Provided by Jared via Telegram — "USE THIS EXACT FILE"
- Size: 3.29 MB PNG

## New Category Created

- purebrain.ai now has Category 24 = "Agentic AI"
- Used instead of "AI Strategy" (cat 5) to better match byline "Agentic AI | AI Strategy"

## Sections Included

1. Full article body (pb-blog-post wrapper)
2. Byline with "Agentic AI | AI Strategy" categories
3. Transparency section (no proper names)
4. Daily Recap (March 1, 2026 stats: ~9.5 AI hours, 4-5x efficiency)
5. FAQ accordion (6 items about AI agents for business)
6. Social share footer (pt-social-share)
7. blog-cta-block CTA linking to #awakening

## Deployment Rules Followed

- Python requests only — NEVER bash/curl (bash escapes ! in wp:html to backslash)
- purebrain.ai: wrapped in <!-- wp:html --> ... <!-- /wp:html -->
- jareddsanborn.com: plain HTML, no wp:html wrapping, no template field
- JDS auth: AetherPureBrain.ai (NOT 'jared') with WORDPRESS_APP_PASSWORD

## Verification (All Passed)

- [x] HTTP 200 on purebrain.ai live URL
- [x] HTTP 200 on jareddsanborn.com live URL
- [x] Status = "publish" on both
- [x] pb-blog-post wrapper present on both
- [x] Featured media set on both (1188 / 1219)
- [x] wp:html present on PB, absent on JDS
- [x] No backslash escape (confirmed via API context=edit)
- [x] transparency-section present (no proper names)
- [x] faq-section present on both
- [x] blog-cta-block + #awakening CTA on both
- [x] Daily Recap section present on both
- [x] Yoast meta set via purebrain/v1/update-post-meta

---

**End of Memory**
