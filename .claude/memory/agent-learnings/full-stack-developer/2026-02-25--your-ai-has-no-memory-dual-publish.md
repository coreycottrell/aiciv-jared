# WordPress Dual Publish: "Your AI Has No Memory. Mine Does."

**Date**: 2026-02-25
**Agent**: full-stack-developer
**Type**: operational
**Topic**: Dual blog post publication to purebrain.ai + jareddsanborn.com

---

## Task

Published blog post "Your AI Has No Memory. Mine Does. Here's Why That Changes Everything." to both WordPress sites as DRAFT.

## Draft URLs

- **purebrain.ai**: https://purebrain.ai/?p=950 (Post ID: 950)
  - Admin: https://purebrain.ai/wp-admin/post.php?post=950&action=edit
- **jareddsanborn.com**: https://jareddsanborn.com/?p=1207 (Post ID: 1207)
  - Admin: https://jareddsanborn.com/wp-admin/post.php?post=1207&action=edit

## Media IDs

- purebrain.ai: Media ID 949 (photo_20260225_120301.jpg)
- jareddsanborn.com: Media ID 1206 (same banner)

## Category IDs Used

- purebrain.ai: Category 5 = "AI Strategy"
- jareddsanborn.com: Category 13 = "AI Strategy"

## Author IDs

- purebrain.ai: Author 3 (Aether (AI) at PureBrain.ai)
- jareddsanborn.com: Author 4 (Aether PureBrain.ai) — note: this is the Aether account on JDS, NOT jared (2)

## Internal Links Used

- Trust Gap: PB = /the-ai-trust-gap/ | JDS = /2026/02/22/the-ai-trust-gap/
- AI Tool vs Partner: PB = /the-difference-between-using-ai-and-having-an-ai-partner/ | JDS = /2026/02/20/...
- Agent Manager: PB = /your-next-direct-report-wont-be-human/ | JDS = /2026/02/24/...
- AI Partnership Audit: Both → https://purebrain.ai/#awakening (with UTM params)

## Critical Auth Fix (LEARNED THIS SESSION)

- JDS env var WORDPRESS_USER = "AetherPureBrain.ai" (NOT "jared")
- auth = base64.b64encode(f'AetherPureBrain.ai:{WORDPRESS_APP_PASSWORD}'.encode()).decode()
- Using 'jared' as username gives 401 rest_not_logged_in
- Jared (author ID 2) is a different account from Aether (author ID 4)
- Recent JDS posts (1195, 1180) use author_id=4 (Aether), older ones (1122) use author_id=2 (Jared)

## SEO Fields Set

- Yoast _yoast_wpseo_title: "Your AI Has No Memory. Mine Does. Here's Why That Matters"
- Yoast _yoast_wpseo_metadesc: "Most AI tools reset after every conversation. Permanent AI memory creates compounding intelligence competitors can't copy."
- Yoast _yoast_wpseo_focuskw: "permanent AI memory"
- Yoast OG + Twitter image: set to media ID

## Verification (All Passed)

- [x] Status = "draft" on both sites
- [x] Featured media ID set on both posts (949 / 1206)
- [x] #awakening CTA link present in both
- [x] pt-social-share social icons present in both
- [x] blog-cta-block CTA block present in both
- [x] Site-specific interlinks used correctly
- [x] Transparency section preserved
- [x] Wrapped in <!-- wp:html --> block (WordPress wpautop protection)

---

**End of Memory**
