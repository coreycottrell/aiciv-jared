# First 90 Days Blog Post: Dual Publish

**Date**: 2026-02-26
**Agent**: full-stack-developer
**Type**: operational
**Topic**: Dual blog post publication to purebrain.ai + jareddsanborn.com

---

## Task

Published "The First 90 Days of an AI Partnership (And Why Most Get It Backwards)" blog post to both WordPress sites.

## Published URLs

- **purebrain.ai**: https://purebrain.ai/the-first-90-days-of-an-ai-partnership/ (Post ID: 966)
- **jareddsanborn.com**: https://jareddsanborn.com/2026/02/26/the-first-90-days-of-an-ai-partnership/ (Post ID: 1210)

## Media IDs

- purebrain.ai: Media ID 965 (banner PNG)
- jareddsanborn.com: Media ID 1209 (banner PNG)

## Category IDs Used

- purebrain.ai: Category 5 = "AI Strategy"
- jareddsanborn.com: Category 13 = "AI Strategy"

## Critical Pattern: JDS Credentials

- **WRONG user**: 'jared' with WORDPRESS_APP_PASSWORD → 401
- **CORRECT user**: WORDPRESS_USER env var = 'AetherPureBrain.ai' with WORDPRESS_APP_PASSWORD → 200
- Always use `os.environ['WORDPRESS_USER']` for jareddsanborn.com, NOT hardcoded 'jared'

## Critical Pattern: JDS Template Field

- DO NOT include 'template' field in post_data for jareddsanborn.com posts
- It returns 400 "template is not one of" error
- purebrain.ai accepts 'elementor_canvas' template; JDS posts use default

## wp:html Wrapping

- purebrain.ai: ALWAYS wrap full HTML content in `<!-- wp:html -->` ... `<!-- /wp:html -->`
- jareddsanborn.com: No wrapping needed — plain HTML works fine

## Yoast SEO

- Meta description set via custom endpoint POST purebrain/v1/update-post-meta on both sites
- Both returned 200

## Footer Template

- Location: `.claude/skills/wordpress-publishing/blog-footer-template.html`
- Replace `{slug}` with actual post slug for UTM links
- Contains: pt-social-share (LinkedIn, X, Facebook, Email) + blog-cta-block with #awakening CTA

## Verification (All Passed)

- [x] HTTP 200 on purebrain.ai live URL
- [x] HTTP 200 on jareddsanborn.com live URL
- [x] Title present in page content on both
- [x] #awakening CTA link present on both
- [x] pt-social-share footer present on both
- [x] Featured banner image uploaded and set on both
- [x] Yoast SEO meta set on both
- [x] No test page links in either post
- [x] Transparency section (no proper names) included

---

**End of Memory**
