# WordPress Dual Publish: "Why 95% of AI Pilots Fail"

**Date**: 2026-02-21
**Agent**: full-stack-developer
**Type**: operational
**Topic**: Dual blog post publication to purebrain.ai + jareddsanborn.com

---

## Task

Published blog post "Why 95% of AI Pilots Fail (And What the 5% Do Differently)" to both WordPress sites simultaneously.

## Published URLs

- **purebrain.ai**: https://purebrain.ai/why-95-percent-of-ai-pilots-fail/ (Post ID: 606)
- **jareddsanborn.com**: https://jareddsanborn.com/2026/02/21/why-95-percent-of-ai-pilots-fail/ (Post ID: 1092)

## Media IDs

- purebrain.ai: Media ID 605 (uploaded 1.png as header image)
- jareddsanborn.com: Media ID 1091

## Category IDs Used

- purebrain.ai: Category 2 = "AI Insights"
- jareddsanborn.com: Category 9 = "AI Insights"

## Workflow That Worked

1. Load .env with `load_dotenv('/home/jared/projects/AI-CIV/aether/.env')`
2. Auth: `base64.b64encode(f'Aether:{pb_pass}'.encode()).decode()` for Basic auth header
3. Upload image via POST to `/wp-json/wp/v2/media` with `Content-Disposition: attachment; filename="..."` header
4. Build HTML from markdown manually (not pypandoc - manual gives cleaner control)
5. Append footer template with `{slug}` replaced
6. POST to `/wp-json/wp/v2/posts` with JSON body including `featured_media`, `categories`, `excerpt`
7. Verify via GET on post IDs

## Key Rules Applied

- CTA links point to `https://purebrain.ai/#awakening` (never test pages)
- Footer template appended from `.claude/skills/wordpress-publishing/blog-footer-template.html`
- Both sites status: `publish` (not draft)
- Categories: "AI Insights" on both sites
- `{slug}` replaced in footer with `why-95-percent-of-ai-pilots-fail`

## Verification Checklist (All Passed)

- [x] Status = "publish" on both sites
- [x] Featured media ID set on both posts
- [x] `#awakening` CTA link present in both
- [x] `pt-social-share` social icons present in both
- [x] `blog-cta-block` CTA block present in both
- [x] No test page links (`/pay-test/` etc.) in either post
- [x] Content length consistent (16075 chars rendered)

---

**End of Memory**
