# Blog Publish: "Your AI Doesn't Work For You"

**Date**: 2026-03-01
**Agent**: blogger
**Type**: operational
**Topic**: Dual publish - "Your AI Doesn't Work For You" to PureBrain.ai and JaredDSanborn.com

---

## Published URLs

- **purebrain.ai**: https://purebrain.ai/your-ai-doesnt-work-for-you/ (Post ID: 1139)
- **jareddsanborn.com**: https://jareddsanborn.com/2026/03/01/your-ai-doesnt-work-for-you/ (Post ID: 1218)

## Banner

- Source: `/home/jared/projects/AI-CIV/aether/docs/from-telegram/your-ai-doesnt-work-for-you-blog-post.png`
- Jared-designed PNG with title text, subtitle, PureBrain.ai branding
- PB media ID: 1138 | JDS media ID: 1217

## Google Drive

- Subfolder: `your-ai-doesnt-work-for-you-2026-03-01`
- Subfolder ID: `1UFoB4O18S5gtBbcM03x5CsN_AQ6k3-K_`
- Files: blog-post.md, banner PNG

## Workflow That Worked

1. Banner came in as `your-ai-doesnt-work-for-you-blog-post.png` (NOT a photo_ file - check for named files)
2. PureBrain.ai: template='' (empty string), wrapper `<article class="pb-blog-post">`
3. JDS: template='' (empty string NOT 'page-template-blank.php' - that 400'd on posts endpoint)
4. Image upload: raw bytes via `data=f.read()` with `Content-Type: image/png`
5. Always use `requests` library (not urllib) for auth reliability

## Key Lessons

- JDS blog posts use template='' NOT 'page-template-blank.php' (page-template-blank.php works for PAGES not POSTS)
- Banner filename pattern: sometimes named files not photo_ pattern from Telegram
- Check telegram inbox tail to find actual filenames when path doesn't exist

## Content Notes

Post angle: CEO vs Employee inversion - you're working FOR your AI instead of the reverse. Strong PureBrain pitch. Category: AI Partnership | Leadership.

---

**End of Memory**
