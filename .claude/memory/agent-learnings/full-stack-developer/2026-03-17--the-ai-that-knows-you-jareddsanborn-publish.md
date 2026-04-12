# Blog Post Publish: The AI That Knows You Before You Even Speak

**Date**: 2026-03-17
**Agent**: full-stack-developer
**Type**: operational
**Topic**: Blog post published to jareddsanborn.com via WordPress REST API

---

## Task

Published "The AI That Knows You Before You Even Speak" to jareddsanborn.com.

## Published URL

- **jareddsanborn.com**: https://jareddsanborn.com/2026/03/17/the-ai-that-knows-you-before-you-even-speak/ (Post ID: 1273)

## Media ID

- jareddsanborn.com: Media ID 1272 (newsletter-size banner JPG)

## Category IDs Used

- AI Memory: 32 (newly created)
- AI Partnership: 22 (existing)
- Business Strategy: 33 (newly created)

## Author ID

- jareddsanborn.com author ID for Jared: **2** (NOT 520, which is purebrain.ai)

## Key Gotchas

### Duplicate slug issue
- Previous attempts had created drafts/posts with same slug (IDs 1266, 1271)
- These had to be trashed before new post could get the clean slug
- Always check `?slug=...&status=any` before publishing to detect duplicates

### Future vs publish status
- WordPress REST API date field is local WP time, not UTC
- If you set `date` to a future time in WP's local timezone, it publishes as "future" (scheduled)
- Fix: use `date_gmt` field set to a UTC time that is BEFORE the current UTC time
- Current UTC was 02:03 on 2026-03-17, so `date_gmt: 2026-03-17T01:00:00` worked

### No 'template' field for jareddsanborn.com
- Confirmed from prior memory: DO NOT include 'template' field for JDS posts

### Author ID
- WP_USER env var is 'jared', author ID on jareddsanborn.com is 2
- 520 is the Jared user ID on purebrain.ai only

## Verification (All Passed)

- [x] HTTP 200 on live URL
- [x] Title present in page
- [x] #awakening CTA link present
- [x] pt-social-share footer present
- [x] FAQ section present
- [x] Featured image banner uploaded and attached
- [x] Transparency / AI-written section present
- [x] No internal notes in published post
- [x] Correct slug (no -2, -3 suffix)
- [x] Categories: AI Memory(32), AI Partnership(22), Business Strategy(33)

---

**End of Memory**
