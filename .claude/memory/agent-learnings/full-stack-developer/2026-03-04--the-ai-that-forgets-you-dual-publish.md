# WordPress Dual Publish: "The AI That Forgets You Every Single Time"

**Date**: 2026-03-04
**Agent**: full-stack-developer (via dept-marketing-advertising)
**Type**: operational
**Topic**: Dual blog post publication to purebrain.ai + jareddsanborn.com

---

## Task

Published "The AI That Forgets You Every Single Time" (Prequel #1 for Age of AI Agents campaign) to both WordPress sites as status=publish with banner uploaded from Telegram delivery.

## Published URLs

- **purebrain.ai**: https://purebrain.ai/the-ai-that-forgets-you-every-single-time/ (Post ID: 1245)
- **jareddsanborn.com**: https://jareddsanborn.com/2026/03/04/the-ai-that-forgets-you-every-single-time/ (Post ID: 1222)

## Media IDs

- purebrain.ai: Media ID 1244 (the-ai-that-forgets-you-banner.png)
- jareddsanborn.com: Media ID 1221

## Category IDs Used

- purebrain.ai: [14 = AI Partnership, 5 = AI Strategy, 2 = AI Insights]
- jareddsanborn.com: [22 = AI Partnership, 13 = AI Strategy, 9 = AI Insights]

## Author IDs

- purebrain.ai: Author 3 (Aether)
- jareddsanborn.com: Author 4 (used jared user for auth, but author field = 4)

## Auth Pattern (CRITICAL LEARNING)

- **purebrain.ai**: user=Aether, app_password=PUREBRAIN_WP_APP_PASSWORD
- **jareddsanborn.com**: WORDPRESS_USER env var='jared' WORKS (not AetherPureBrain.ai which was working previously but is now 401)
- JDS auth = base64('jared:WORDPRESS_APP_PASSWORD') — confirmed working as of 2026-03-04
- AetherPureBrain.ai credentials for JDS are now returning 401 — use 'jared' instead
- Author ID 4 still used for Aether attribution even when jared user performs the API call

## Banner Source

- File: `docs/from-telegram/the-ai-that-forgets-you-blog-post- Newsletter size.png`
- Provided by Jared via Telegram (approved)
- Size: 2.96 MB PNG

## Content Structure

1. Byline: "By Jared Sanborn | March 4, 2026 | AI Partnership | AI Strategy"
2. Full article body (all 7 sections, converted from markdown to HTML)
3. FAQ accordion (6 items about AI memory and partnership)
4. Transparency section (AI-assisted disclosure)
5. Daily Recap (March 4, 2026 stats)
6. Social share (LinkedIn, X, Facebook, Email)
7. CTA block linking to purebrain.ai/#awakening
8. Tags line

## Campaign Context

- This is **Prequel #1** for the Age of AI Agents campaign launching Thursday
- Sets up the "forgetting" problem that AI agents and PureBrain solve
- Follow-up post (Prequel #2) planned for tomorrow

## Deployment Rules Followed

- Python requests only (never bash/curl — bash escapes ! in wp:html)
- purebrain.ai: wrapped in <!-- wp:html --> ... <!-- /wp:html -->
- jareddsanborn.com: plain HTML, NO wp:html wrapping, NO template field
- pb-blog-post article wrapper on both sites

## Verification (All Passed)

- [x] HTTP 200 on purebrain.ai live URL
- [x] HTTP 200 on jareddsanborn.com live URL
- [x] Status = "publish" on both
- [x] pb-blog-post wrapper present on both (confirmed via HTML check)
- [x] Featured media set on both (1244 / 1221)
- [x] wp:html present on PB, absent on JDS
- [x] FAQ section present on both
- [x] Transparency section present on both
- [x] blog-cta-block + #awakening CTA on both
- [x] Daily Recap section present on both

---

**End of Memory**
