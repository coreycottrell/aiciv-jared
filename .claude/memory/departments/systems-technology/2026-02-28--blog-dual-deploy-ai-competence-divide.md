# Blog Dual-Deploy: ai-competence-divide-2026-02-28

**Date**: 2026-02-28
**Agent**: dept-systems-technology
**Type**: deployment-pattern

## What Was Deployed
Post: "AI Doesn't Make Your Team Smarter. It Makes the Gap Bigger."
Banner: docs/from-telegram/2.png (3.1MB PNG)

## Results
- purebrain.ai: https://purebrain.ai/ai-doesnt-make-your-team-smarter-it-makes-the-gap-bigger/ — HTTP 200, post ID 1084, media ID 1083
- jareddsanborn.com: https://jareddsanborn.com/2026/02/28/ai-doesnt-make-your-team-smarter-it-makes-the-gap-bigger/ — HTTP 200, post ID 1216, media ID 1215

## Key Patterns Confirmed
1. purebrain.ai: user=Aether, template="" (empty), category=[5], wrap in `<!-- wp:html -->`, outer wrapper `<article class="pb-blog-post">`
2. jareddsanborn.com: user=AetherPureBrain.ai (password has spaces — must not shell-source), template="" (same as purebrain.ai, not page-template-blank.php — that is for PAGES not posts)
3. JDS existing posts all use template="" — confirmed by checking /wp/v2/posts before deploying
4. Banner upload: POST to /media with Content-Type image/png and Content-Disposition filename — works on both sites
5. featured_media field on post creation sets the featured image

## Script
exports/departments/systems-technology/ai-competence-divide-deploy.py
