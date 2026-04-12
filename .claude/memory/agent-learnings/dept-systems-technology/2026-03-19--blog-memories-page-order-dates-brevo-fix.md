# Blog Neural Feed Memories: Order + Date Fix + Brevo Key

**Date**: 2026-03-19
**Type**: operational
**Topic**: Fixed neural feed memories card order, wrong dates, and Brevo API key in CF Pages

## What Was Done

### FIX 1 - Blog Index Order
- /blog/index.html was already correct (newest first, March 19 at top)
- No changes needed

### FIX 2 - Neural Feed Memories Page
- File: exports/cf-pages-deploy/blog-neural-feed-memories/index.html
- The page had 30 cards but in WRONG order with WRONG dates
- Used Python to replace entire grid section (lines 310-688)
- Old order was scrambled (e.g., "Prompting Is Dead" labeled March 17 when it is March 13)
- New order matches blog index datetime attributes exactly
- Added missing newer posts at top (Mar 19, 18, 17, 16, 15, 14)
- Corrected all dates to match authoritative source

### FIX 3 - Brevo API Key
- Command: npx wrangler pages secret put BREVO_API_KEY --project-name purebrain-staging
- Result: Success - Uploaded secret BREVO_API_KEY
- Env var name: BREVO_API_KEY

## Key Learnings

Pattern: Neural Feed Memories Page Is Manual
The /blog-neural-feed-memories/ page is a static HTML file that must be manually updated when:
1. New blog posts are published
2. Post order changes
3. Banner images are updated

The authoritative source of truth for dates is the datetime= attribute in /blog/index.html.

Pattern: CF Cache Flush
- Only CF_PAGES_TOKEN is in .env - no Zone ID
- Cache flush via API requires Zone ID
- Manual flush needed via CF dashboard if pages look stale after deploy

Pattern: Banner File Naming
Several posts have both banner.png and banner_OLD_BACKUP.png - current file is always banner.png.
Exception: why-95-percent-of-ai-pilots-fail has both banner_new.png and banner.png.

## Files Modified
- exports/cf-pages-deploy/blog-neural-feed-memories/index.html - grid section rewritten with correct order and dates
- CF Pages secret BREVO_API_KEY set via wrangler
