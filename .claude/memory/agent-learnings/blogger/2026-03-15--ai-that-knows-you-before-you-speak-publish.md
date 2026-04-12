# Blog Publish: "The AI That Knows You Before You Even Speak"

**Date**: 2026-03-15
**Agent**: blogger
**Type**: operational
**Topic**: Dual publish to purebrain.ai (CF Pages) and jareddsanborn.com

---

## Published URLs

- **purebrain.ai (CF Pages)**: https://purebrain.ai/blog/the-ai-that-knows-you-before-you-even-speak/ (HTTP 200 verified)
- **jareddsanborn.com**: https://jareddsanborn.com/2026/03/15/the-ai-that-knows-you-before-you-even-speak-2/ (Post ID: 1268)
- **Bluesky Thread**: https://bsky.app/profile/purebrain.ai/post/3mh4rlkd7qa2e (8 posts, banner on first post)

## Banner

- Source: `/home/jared/portal_uploads/from-portal/portal_20260315_162207_the-ai-that-knows-you-before-you-speak-blog-post-Newslettersize.jpg`
- 1920x1080 JPEG, 260KB
- Already placed at CF Pages: `exports/cf-pages-deploy/blog/the-ai-that-knows-you-before-you-even-speak/banner.jpg`
- JDS media ID: 1267

## Workflow Notes

1. CF Pages HTML was already built (2026-03-15 export date) - just needed deploy
2. Added _redirects entry: `/the-ai-that-knows-you-before-you-even-speak/* /blog/the-ai-that-knows-you-before-you-even-speak/:splat 301`
3. Deploy via `npx wrangler pages deploy exports/cf-pages-deploy --project-name purebrain --commit-dirty=true`
4. JDS: template="" (empty string), `<article class="pb-blog-post">` wrapper with `<!-- wp:html -->` block
5. Bluesky session was expired - needed fresh login with BSKY_USERNAME/BSKY_PASSWORD from .env
6. Compressed banner from 260KB to 155KB JPEG for Bluesky (under 976KB limit)

## Bluesky Thread Posts

8 posts total - each under 300 chars. Post 1 had banner image. Final post (8) had blog URL.
Post IDs: 3mh4rlkd7qa2e, 3mh4rlmwtwx26, 3mh4rlozrfe2n, 3mh4rlr4psi22, 3mh4rlt7nzm2n, 3mh4rlvclgi2u, 3mh4rlxfkya2u, 3mh4rlzimue2u

## Content Notes

Post angle: Three layers of AI context (operational/strategic/relational). Targets VP Growth ICP.
The "briefing tax" framing - 87 hours/year per person lost to re-context-loading.
Strong PureBrain pitch: AI that accumulates vs. resets. Memory as relationship, not document.

## Key Lessons

- Bluesky session tokens expire - always re-login with username/password if session_string fails
- CF Pages HTML was pre-built in this case (exported from WP) - just needed redirect + deploy
- wrangler deploy works from any directory with proper --commit-dirty=true flag
- JaredDSanborn.com slug gets "-2" appended if slug already taken (no conflict here, first publish)

---

**End of Memory**
