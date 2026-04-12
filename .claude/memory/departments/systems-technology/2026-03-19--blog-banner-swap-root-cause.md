---
date: 2026-03-19
agent: dept-systems-technology
type: operational
topic: Blog banner images replaced by script - root cause and fix
---

# Blog Banner Swap Root Cause (March 19, 2026)

## Problem
Jared reported blog banners were "wrong" after multiple fix attempts. Banners were PERFECT when "Prompting Is Dead" was posted (~March 17-18).

## Root Cause
A script ran on March 18 at approximately 23:41 that renamed original approved banner files to banner_OLD_BACKUP.* and replaced them with wrong/different banner images.

This was NOT a git rollback issue. The OLD_BACKUP files contained the original approved images.

## Affected Posts (8 total)
- prompting-is-dead/banner.png (2.5MB original, had been replaced with 1.4MB wrong image)
- your-ai-has-no-idea-who-you-are/banner.png (3.1MB original)
- age-of-ai-agents-next-18-months/banner.png (2.8MB original)
- why-ai-memory-changes-everything/banner.png (3.5MB original)
- the-context-tax/banner.jpg (50KB original)
- teach-your-ai-something-no-one-else-can/banner.jpg (106KB original)
- 52-billion-ai-agents-market-is-not-the-story/banner.jpg (198KB original)
- the-meeting-your-ai-should-already-know-about/banner.png (59KB original)

## Fix
Moved wrong banners to banner_WRONG_BACKUP.*, restored banner_OLD_BACKUP.* to banner.png/jpg, deployed to CF Pages.

## Key Learnings
- Git rollback was not the solution - the issue was file content swapped outside git
- Detection command: find . -name "banner_OLD_BACKUP*"
- CF Pages content-addressing: original files already stored, deploy = instant restore
- Add CF_ACCOUNT_ID to .env to avoid wrangler auth dependency on cache
- Clearing wrangler cache (.wrangler/cache/) breaks wrangler deploy auth without CF_ACCOUNT_ID
