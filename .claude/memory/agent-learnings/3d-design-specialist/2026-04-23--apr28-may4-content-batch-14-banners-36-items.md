# Apr 28 - May 4 Content Batch: 14 Standalone Banners + 36 Social API Items

**Date**: 2026-04-23
**Type**: operational
**Agent**: 3d-design-specialist

## Context
Generated 14 v4.2 standalone LinkedIn banners (1080x1350) for the Apr 28 - May 4 content batch, uploaded all to R2, and submitted all 36 content items to social.purebrain.ai API. 36/36 created, 0 failed.

## Pipeline (identical to Apr 24-27 batch)
1. FLUX Pro 1.1 via Replicate (1080x1080 square backgrounds, 14 unique)
2. PIL v4.2 overlay: top bar (140px with 80px hex icon + 46pt wordmark), 2px blue accent, FLUX bg with centered title (62pt Oswald Bold with 4px dark stroke + gradient backing), 2px blue accent, bottom bar (90px with brand wordmark left + orange CTA right)
3. Upload to R2 via POST /api/uploads
4. Create content items via POST /api/content with social_account_id

## Content Breakdown (36 items)
- 14 standalones (with images, content_type="standalone")
- 7 text posts (no images, content_type="post")
- 5 blogs (no images, content_type="blog") - Apr 30 through May 4 only
- 5 newsletters (no images, content_type="newsletter")
- 5 newsletter promos (no images, content_type="newsletter_promo")
- Skipped Apr 28-29 blogs (already existed as drafts)

## Key Parameters
- social_account_id: a325193d-4a8e-40ba-ab20-c86b5a72f0b7
- All body text uses \n\n between paragraphs for WYSIWYG formatting
- All items status="draft", platform="linkedin"
- FLUX rate limit: 15s between calls (no 429 errors)

## Files
- Generation script: /home/jared/projects/AI-CIV/aether/exports/content-batch-images-week2/generate_banners.py
- Submission script: /home/jared/projects/AI-CIV/aether/exports/content-batch-images-week2/submit_content.py
- Raw FLUX: /home/jared/projects/AI-CIV/aether/exports/content-batch-images-week2/flux-raw/ (14 files)
- Final banners: /home/jared/projects/AI-CIV/aether/exports/content-batch-images-week2/*-standalone.jpg (14 files)

## R2 Keys
- purebrain-vs-va-math: f15527f5-.../1777241796383-f999f0dc-purebrain-vs-va-math-standalone.jpg
- ai-remembers-client-birthday: f15527f5-.../1777241785396-1906255e-ai-remembers-client-birthday-standalone.jpg
- stopped-writing-linkedin-posts: f15527f5-.../1777241799350-94a0d4d7-stopped-writing-linkedin-posts-standalone.jpg
- 32-ai-agents-not-tech-company: f15527f5-.../1777241779300-e9785dce-32-ai-agents-not-tech-company-standalone.jpg
- ai-doesnt-need-better-model: f15527f5-.../1777241783665-abd98030-ai-doesnt-need-better-model-standalone.jpg
- day1-skepticism-month6-indispensable: f15527f5-.../1777241790274-9f1ea48e-day1-skepticism-month6-indispensable-standalone.jpg
- ai-texts-midnight-security: f15527f5-.../1777241786881-e38b1455-ai-texts-midnight-security-standalone.jpg
- most-ai-glorified-autocomplete: f15527f5-.../1777241791828-fffe0de7-most-ai-glorified-autocomplete-standalone.jpg
- ai-caught-billing-error: f15527f5-.../1777241782273-9c96ce8a-ai-caught-billing-error-standalone.jpg
- stop-evaluating-ai-by-capabilities: f15527f5-.../1777241797838-3ce7ffd7-stop-evaluating-ai-by-capabilities-standalone.jpg
- next-hire-no-resume: f15527f5-.../1777241794715-cbec25ff-next-hire-no-resume-standalone.jpg
- 36-businesses-named-their-ai: f15527f5-.../1777241780748-00a46290-36-businesses-named-their-ai-standalone.jpg
- company-runs-32-agents: f15527f5-.../1777241788708-3b829360-company-runs-32-agents-standalone.jpg
- next-hire-naming-ceremony: f15527f5-.../1777241793225-f1add647-next-hire-naming-ceremony-standalone.jpg
