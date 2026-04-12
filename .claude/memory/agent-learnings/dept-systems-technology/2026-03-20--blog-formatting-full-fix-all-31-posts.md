# Blog Post Formatting: Full Fix Applied to All 31 Posts

**Date**: 2026-03-20
**Type**: operational
**Topic**: Fixing all 31 CF Pages blog posts to match prompting-is-dead reference template

## What Was Fixed

30 of 31 blog posts had formatting issues. Only `prompting-is-dead` was the correct reference.

### Issues Found

1. Microsoft Clarity script missing - 26 posts
2. pb-audio-player missing - ALL 30 posts
3. purebrain-subscribe-fix missing - 6 posts
4. Old/minimal CSS (< 10K chars) - 3 oldest posts had CSS from ~8K, missing nav + styles
5. CSS missing extra sections (13220 to 15976 chars) - 24 posts

### Daily Recap Structure
Two valid implementations exist - both correct:
- pb-transparency-block: reference post and a few newer posts
- pb-recap-wrapper: most older posts (two-tier frozen+live design)

## Fix Script
/home/jared/projects/AI-CIV/aether/tools/fix_blog_formatting.py
Idempotent - safe to re-run.

## Audio Player Placement
Placed after banner image (pb-post-banner class or banner img tag).
Uses relative path: audio.mp3

## Deployment
30 files uploaded to purebrain-staging CF Pages.
CF cache purged after deploy.
