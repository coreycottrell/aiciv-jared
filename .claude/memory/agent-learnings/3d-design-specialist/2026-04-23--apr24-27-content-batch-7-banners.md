# Apr 24-27 Content Batch: 7 Standalone Banners + 13 Social API Items

**Date**: 2026-04-23
**Type**: operational
**Agent**: 3d-design-specialist

## Context
Generated 7 v4.2 standalone LinkedIn banners (1080x1350) for the Apr 24-27 content batch, uploaded to R2, and submitted all 13 content items to social.purebrain.ai API.

## Pipeline
1. FLUX Pro 1.1 via Replicate (1080x1080 square backgrounds, 7 unique)
2. PIL v4.2 overlay: top bar (140px with 80px hex icon + 46pt wordmark), 2px blue accent, FLUX bg with centered title (62pt Oswald Bold with 4px dark stroke + gradient backing), 2px blue accent, bottom bar (90px with brand wordmark left + orange CTA right)
3. Upload to R2 via POST /api/uploads
4. Create content items via POST /api/content with social_account_id

## Key Discovery
- Social API requires `social_account_id` field: `a325193d-4a8e-40ba-ab20-c86b5a72f0b7`
- API normalizes content_type values: "standalone" -> "post", "linkedin" -> "post"
- "blog", "newsletter", "newsletter_promo" content_types are preserved
- Title field doesn't display in list view but body is the primary content

## FLUX Rate Limiting
- 15s delay between calls sufficient at current balance
- All 7 images generated without hitting 429 errors

## Files
- Generation script: /home/jared/projects/AI-CIV/aether/exports/content-batch-images/generate_batch.py
- Submission script: /home/jared/projects/AI-CIV/aether/exports/content-batch-images/submit_content.py
- Raw FLUX: /home/jared/projects/AI-CIV/aether/exports/content-batch-images/flux-raw/ (7 files)
- Final banners: /home/jared/projects/AI-CIV/aether/exports/content-batch-images/*-standalone.jpg (7 files)

## R2 Keys
- purebrain-vs-va-cost: f15527f5-.../1776979004436-db525e20-purebrain-vs-va-cost-standalone.jpg
- 6-months-ai-partner: f15527f5-.../1776979005845-036cff0d-6-months-ai-partner-standalone.jpg
- 147k-question-ai: f15527f5-.../1776979007207-7649dbaa-147k-question-ai-standalone.jpg
- 35-businesses-named-ai: f15527f5-.../1776979008573-44e188b2-35-businesses-named-ai-standalone.jpg
- 10000-lines-ai-wrote: f15527f5-.../1776979009992-7732a8fe-10000-lines-ai-wrote-standalone.jpg
- day1-vs-month6-ai: f15527f5-.../1776979011430-f6bbe23d-day1-vs-month6-ai-standalone.jpg
- best-context-not-best-models: f15527f5-.../1776979012864-729d9b73-best-context-not-best-models-standalone.jpg
