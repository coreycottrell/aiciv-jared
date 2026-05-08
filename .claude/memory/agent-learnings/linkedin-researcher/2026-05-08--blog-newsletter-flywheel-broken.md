# Linkedin-Researcher Learning: Blog/Newsletter Flywheel Broken

**Date**: 2026-05-08
**Type**: operational + teaching
**Topic**: PureBrain blog + LinkedIn newsletter audit

## Headline Findings

1. **jareddsanborn.com dark since Mar 20** — 49-day publishing gap as of 2026-05-08
2. **LinkedIn newsletter publishing daily** through Apr 30 (most recent visible)
3. **purebrain.ai/blog/ returns 403** — dual-site claim is single-site reality
4. **March 20 standard not deployed** — even on the Mar 20 namesake post, no 60% opacity bg, no BG video, no collapsible FAQs, no daily recap, no audio embed
5. **3 duplicate Mar 17 URLs** for "AI That Knows You Before You Even Speak" (`-2/`, `-3/`, base) = SEO penalty
6. **42% of posts (13/31) tagged Uncategorized**

## Engagement Pattern Found

LinkedIn newsletter top performer (Apr 30 "Day 1 vs Month 6") got 8 comments — 4-8x baseline. Pattern: contrarian framing ("Nobody talks about X", "I Fired Myself") drives engagement. Process/architecture posts (32 Agents, 3 AM Test) underperform.

## The Flywheel Problem

Per `content-creation-sop`: blog → newsletter → LI promo → Bluesky. Current state: only newsletter is live. Blog is dark, purebrain.ai/blog/ is 403, blog-to-newsletter automation doesn't exist. The newsletter ships first; blog never follows. SEO domain authority is being handed to LinkedIn.

## Quick-Win Pattern

When client has X days of silence on Channel A while Channel B is daily, the fastest recovery is: **backfill Channel B's proven-engagement piece to Channel A first**. It (1) breaks silence with a winner, (2) forces deploy pipeline reuse, (3) recovers SEO compounding. For this case: backfill Apr 30 newsletter to blog as the first move.

## Method Notes (Reusable)

- WebFetch on `purebrain.ai/blog` returned 403 — try `www.` variant + WebSearch `site:` query for indexed paths
- LinkedIn newsletter URL `linkedin.com/newsletters/{slug}-{entityUrn}` is publicly fetchable for index, individual articles via `linkedin.com/pulse/{slug}` may 404
- `linkedin.com/in/{handle}/recent-activity/articles/` returns HTTP 999 (LinkedIn anti-scrape) — don't waste time
- Compare claimed standard (memory) vs deployed reality (live URL fetch) — gap is the highest-impact finding most of the time

## Related Memory

- `feedback_blog_locked_in_march20.md` (canonical March 20 standard)
- `feedback_linkedin_blog_post_not_separate.md` (one-action rule)
- `feedback_newsletter_banner_is_linkedin_image.md` (1200x630 spec)
- `.claude/skills/content-creation-sop/SKILL.md` (full pipeline)
- `agent-learnings/blogger/2026-03-21--ai-runs-while-you-sleep-content-package.md` (proves Mar 21 package staged but never shipped — clue that approval gate stalled the pipeline)

## Status

Analysis delivered to `exports/portal-files/overnight-task2-blog-newsletter-analysis-2026-05-08.md`. Read-only research; no posting, no editing.
