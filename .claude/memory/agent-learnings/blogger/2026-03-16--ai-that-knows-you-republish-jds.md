# Blog Republish: "The AI That Knows You Before You Even Speak" → jaredsanborn.com

**Date**: 2026-03-16
**Agent**: blogger
**Type**: operational
**Topic**: Republish to jaredsanborn.com after previous publish (ID 1268) was 404

---

## Published URL

- **jaredsanborn.com**: https://jareddsanborn.com/2026/03/16/the-ai-that-knows-you-before-you-even-speak-2/ (Post ID: 1271, HTTP 200 verified)

## Banner

- Source: `/home/jared/portal_uploads/from-portal/portal_20260315_162207_the-ai-that-knows-you-before-you-speak-blog-post-Newslettersize.jpg`
- JDS media ID: 1270

## Workflow Notes

1. Previous publish attempt (2026-03-15, Post ID 1268) was returning 404 — not showing in post list
2. Connection tested: WordPress API connected as Jared Sanborn
3. `markdown` Python module not available — wrote manual MD-to-HTML converter in Python using re
4. HTML conversion preserved: h1/h2/h3 headers, paragraphs, bold/italic, links, hr, lists
5. Removed internal note footer (`*[Internal note:...]`) before publishing
6. The title in HTML was H1 — WordPress adds its own title display, so this is fine
7. Slug got "-2" appended because slug "the-ai-that-knows-you-before-you-even-speak" may already exist in DB
8. Categories: "AI", "Business Strategy" | Tags: ai-memory, ai-partnership, context, purebrain, business-ai

## Key Lessons

- When `markdown` module unavailable, write a simple regex-based MD-to-HTML converter — it handles the common cases
- Previous post IDs that return 404 are silently deleted/missing — just republish fresh
- WordPress appends "-2" to slug when exact slug already exists in DB (even if that post is deleted)
- Always verify HTTP 200 after publish — connection test doesn't mean post is visible

---

**End of Memory**
