# Blog Complete Rebuild — Google Drive Approved Banners

**Date**: 2026-03-20
**Type**: operational / teaching
**Agent**: dept-systems-technology

## What Was Done

Full blog rebuild:
1. Pulled approved banners from Google Drive blog bundles folder `1trWAzRF8nkPs128W3TlxQZe9fPXc35Wv`
2. Fixed banner file extension references in blog/index.html and blog-neural-feed-memories/index.html
3. Fixed individual post index.html files to match actual banner file extensions
4. Deployed to purebrain-staging (CF Pages)

## Drive Folder Mapping

Drive folders matched to CF Pages slugs. When multiple folders exist for same slug, priority:
- Largest newsletter-size image (~2-3MB PNG) over small banner thumbnails
- Most recent date folder over older

## Banner Extension Fixes

Several slugs had Drive-approved .png banners but index files still referenced .jpg:
- teach-your-ai-something-no-one-else-can: fixed jpg->png (2.8MB newsletter size)
- the-ai-that-knows-you-before-you-even-speak: fixed jpg->png (2.9MB)
- the-context-tax: fixed jpg->png (50KB)
- the-ai-trust-gap: fixed jpg->png (3.1MB)
- your-ai-has-no-memory-mine-does: fixed jpg->png (61KB)

## Files Fixed (3 layers each)

1. exports/cf-pages-deploy/blog/index.html
2. exports/cf-pages-deploy/blog-neural-feed-memories/index.html
3. exports/cf-pages-deploy/blog/{slug}/index.html (individual posts)

## Fonts Verified

Both blog pages already have Oswald loaded correctly.

## Post Count

Both pages have 31 blog posts, newest-first order.

## Deployment

Deployed to purebrain-staging. 11 new files uploaded.
CF Pages token lacks zone scope - cannot API-purge cache.
