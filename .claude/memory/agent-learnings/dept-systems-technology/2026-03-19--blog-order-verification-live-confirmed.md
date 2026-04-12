# Blog Order: Live Site Verification Confirmed

**Date**: 2026-03-19
**Type**: operational + teaching
**Topic**: Blog order already correct on live site — earlier session fixed it, this session verified

## What Happened

Jared reported blog order still wrong. This session:
1. Inspected both local files — already correct (newest first, 31 posts each)
2. Confirmed via curl to live URLs — both pages already serving correct order
3. Previous fix from earlier today was already deployed and working
4. Ran fresh deploy anyway as belt-and-suspenders: wrangler pages deploy -> success

## Live Verification Results

**https://purebrain.ai/blog/**
- 31 posts
- Post 1: March 19, 2026 -- Your AI Has No Idea Who You Are
- Post 31: February 13, 2026 -- Why Your AI Should Have a Name
- Order: correct, newest first

**https://purebrain.ai/blog-neural-feed-memories/**
- 31 posts
- Post 1: March 19, 2026 -- Your AI Has No Idea Who You Are
- Post 31: February 13, 2026 -- Why Your AI Should Have a Name
- Order: correct, newest first

## Key Learnings

Lesson 1: Verify live before rebuilding
Always curl the live URL first when a "fix didn't work" report comes in.
It may have already worked -- CF cache can take time to clear, or Jared may be seeing browser cache.

Lesson 2: CF_PAGES_TOKEN cannot flush zone cache
The CF_PAGES_TOKEN in .env only has Pages:Edit scope. It cannot call zones/{id}/purge_cache.
Zone ID is 49400cad1527af716705f6cb8c22bb65 but requires a token with Cache Purge scope.
CF_ZONE_ID is NOT in .env (as of March 2026). Manual flush via CF Dashboard > Caching > Purge Everything.

Lesson 3: If live is already correct, tell Jared to hard-refresh
Ctrl+Shift+R (Chrome) or Cmd+Shift+R (Mac) bypasses browser cache.
Mobile: clear browser cache or open in incognito.

## Files Checked
- exports/cf-pages-deploy/blog/index.html -- correct, no changes needed
- exports/cf-pages-deploy/blog-neural-feed-memories/index.html -- correct, no changes needed
