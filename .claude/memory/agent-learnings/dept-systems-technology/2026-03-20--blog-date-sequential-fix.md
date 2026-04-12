# Blog Post Date Sequential Fix

**Date**: 2026-03-20
**Type**: operational
**Topic**: Fixing non-sequential blog post dates across blog index, memories archive, and individual post pages

## Problem
Blog posts were in the right ORDER but dates displayed were non-sequential (jumbled).
Example: Post #2 showed March 13 when it should be March 19.

## Files Modified
1. `/exports/cf-pages-deploy/blog/index.html` - Main blog index, 11 posts
2. `/exports/cf-pages-deploy/blog-neural-feed-memories/index.html` - Archive page, 31 posts
3. Individual post pages with hardcoded dates:
   - `the-meeting-your-ai-should-already-know-about/index.html` (byline + recap header)
   - `prompting-is-dead/index.html` (byline + transparency span)
   - `the-ai-that-gets-smarter-when-you-push-back/index.html` (byline + transparency span)
   - `your-ai-has-no-idea-who-you-are/index.html` (transparency span)
   - `what-i-named-my-ai/index.html` (time element)
   - `why-enterprises-are-betting-on-agentic-ai/index.html` (time element)
   - `why-your-ai-should-have-a-name/index.html` (time element)

## Date Assignment Strategy
- Newest post at top = March 20, 2026 (today)
- Each subsequent post = 1 day earlier
- Blog index: March 20 down to March 10 (11 posts)
- Memories archive: March 19 down to February 17 (31 posts)

## Technique
Used Python regex to find post slugs then fix adjacent date elements.
Pattern: `href="/blog/{slug}/...">title</a><time datetime="...">date</time>`
For memories page: `href="/blog/{slug}/..." ... <div class="nfm-card-date">date</div>`

## Key Gotcha
The blog index and memories page may show the same post at different sequential positions (and thus different dates). This is unavoidable when one page shows top 11 and the other shows all 31.

## Deployed
CF Pages purebrain-staging - deployment ID dabca90d
