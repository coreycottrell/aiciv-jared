# Viral Content Repurposing Flow - Cross-Platform to LinkedIn

**Date**: 2026-02-20
**Type**: synthesis
**Agent**: marketing-strategist
**Confidence**: high
**Topic**: Complete daily flow for trending content discovery and LinkedIn repurposing for PureBrain / PureMarketing / PureTechnology

---

## Context

Jared requested a full system for discovering trending content on TikTok, Reddit, Instagram, Twitter/X, and YouTube Shorts, filtering it for AI/marketing/business relevance, and repurposing it as LinkedIn posts that ride viral attention waves for the Pure brand accounts.

## What Was Produced

Full deliverable: `/home/jared/projects/AI-CIV/aether/to-jared/viral-content-repurposing-flow.md`

Covers:
- Daily automation flow (6 AM scan -> 7 AM brief delivery to Jared)
- Repurposability Index scoring framework (5 criteria, 6.5+ threshold)
- Platform-specific research methods with API details (Reddit PRAW, YouTube Data API v3)
- 5 repurposing templates (TikTok->Carousel, Reddit->Story, Video->Text, Trend->Opinion, Meme->Insight)
- Automation pipeline (what Aether handles vs. what requires human review)
- Content calendar (posting cadence, times, mix per account)
- Brand voice guidelines for Jared, Nathan, John, and all 3 company pages
- Success metrics and weekly review cadence
- Full sample daily brief with 5 scored opportunities + 1 complete ready-to-publish post

## Key Strategic Decisions Made

### 1. Aether Automates Discovery, Humans Approve Voice

The critical distinction: Aether can score, filter, draft, and brief. But the voice authenticity check for opinion posts must stay human. Posts that sound like AI-generated takes on a trending topic are worse than no post.

### 2. Company Pages Are Legitimacy Anchors, Not Growth Engines

Company page reach: 1-2%. Personal profiles: 8-15%. Posting equally to both wastes effort. Company pages should amplify personal posts and add legitimacy, not originate content.

### 3. The Translation Rule

TikTok/Reddit/Instagram = emotion and virality. LinkedIn = insight and authority. The transformation is: keep the hook, swap the format. Never repost raw. Always translate.

### 4. Rising Posts > Hot Posts

When monitoring Reddit, "rising" posts (gaining velocity in first 2 hours) are more valuable than "hot" posts (already peaked). A post with 200 upvotes in 1 hour beats 5,000 upvotes at 24 hours for content opportunity.

### 5. External Link Penalty Is Real

Every post with an external link loses approximately 60% of its organic reach. All links go in the first comment after posting. This applies to trending content attribution too.

## Platform API Notes

| Platform | API | Cost | Key Detail |
|----------|-----|------|-----------|
| Reddit | PRAW (official) | Free | 60 requests/min, needs app creation at reddit.com/prefs/apps |
| YouTube | Data API v3 | Free (10K units/day) | Already have GOOGLE_API_KEY, may need YouTube scope |
| TikTok | Creative Center (no API) | Free | Web fetch trends.tiktok.com |
| Twitter/X | Public trending page | Free | No API needed for trending data |
| Instagram | Public profile fetch | Free | No official API for read-only monitoring |

## Brand Voice Positioning (Locked In)

- Jared: Visionary + practitioner. Speaks from lived experience building PureBrain. Never sounds like generic AI content.
- Nathan: Marketing practitioner who shows his work. "Here's what I tested" is his reliable opener.
- John: Relationship and strategic thinking. Uses "I was talking to someone who..." to bring in real conversations.
- Company pages: Professional, bold, data-driven. Legitimacy anchors, not content engines.

## Content Topic Routing

- AI partnership, human-AI collaboration, AI adoption stories -> PureBrain.ai / Jared
- Marketing tactics, campaign results, what's working now -> PureMarketing.ai / Nathan
- Tech innovation, digital transformation, automation -> PureTechnology.ai
- BD, partnerships, network building -> John

## When to Apply

- Any future content strategy work for Pure brands
- When planning automation for social media monitoring
- When designing cross-platform content repurposing for any brand
- When setting up Reddit API access for content discovery

---

*marketing-strategist | viral content repurposing flow | 2026-02-20*
