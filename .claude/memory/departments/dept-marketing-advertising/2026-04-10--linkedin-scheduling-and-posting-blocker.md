# LinkedIn Operations Apr 10 - Scheduling Complete, Posting Blocked

**Date**: 2026-04-10
**Type**: operational
**Agent**: dept-marketing-advertising
**Topic**: LinkedIn content scheduling and posting infrastructure blocker

## What Was Accomplished

### Job 2: Scheduling (COMPLETE)
All 14 approved posts with content have been scheduled across Apr 10-16 in BaaS:

| Date | Time (ET) | Post ID | Title | Has Image |
|------|-----------|---------|-------|-----------|
| Apr 10 | 2:00 PM | post-1775481882 | Personalization Gap (83% stat) | Yes |
| Apr 10 | 3:00 PM | blog-apr10-customers | Blog: Customers Will Tell You Everything | No |
| Apr 11 | 10:00 AM | blog-apr11-ai-to-ai | Blog: AI-to-AI Transaction | No |
| Apr 11 | 3:00 PM | post-1775481884 | AI Budget Trap (86% stat) | Yes |
| Apr 12 | 10:00 AM | post-1775572135 | Rogue AI Agent | No |
| Apr 12 | 3:00 PM | post-1775481532 | Transparency Pillars | Yes |
| Apr 13 | 10:00 AM | post-1775568187 | 88% AI Agent Security (blog dist) | No |
| Apr 13 | 3:00 PM | post-1775490565 | 88% Security - Human Error | Yes |
| Apr 14 | 10:00 AM | post-1775159005 | CEO vs Employee AI | Yes |
| Apr 14 | 3:00 PM | post-1775734950-e074db | 40% AI Projects Canceled | No |
| Apr 15 | 10:00 AM | post-1775481878 | Agentic Era Inflection | Yes |
| Apr 15 | 3:00 PM | post-1775734964-75503d | Copilot Usage 340% | No |
| Apr 16 | 10:00 AM | post-1775481880 | Tool vs Partner (91% stat) | Yes |
| Apr 16 | 3:00 PM | post-1775159006 | Agentic Era - 30 AI Agents | Yes |

Strategy: Best content (CEO vs Employee, Agentic Era) placed on Mon/Tue 10am prime slots. Blog distribution posts paired with standalones. 2 posts/day cadence.

### Job 1: Posting Today (BLOCKED)
Selected post: post-1775481882 (Personalization Gap, 83% stat, has image)

**Blocker**: LinkedIn is not accessible from PureSurf browser automation.
- PureSurf session creates but LinkedIn feed returns `chrome-error://chromewebdata/`
- This is the same 429 rate-limiting issue from Apr 6 (li_at cookie exhaustion)
- CF Worker OAuth endpoint at apex.purebrain.ai is not connected (returns "LinkedIn not connected")
- The `surf.purebrain.ai` media URLs are blocked by the CF Worker SSRF guard

**Fix required**: One of:
1. Fresh LinkedIn login from Jared's device + cookie sync to PureSurf
2. Complete the LinkedIn OAuth integration on the CF Worker
3. Manual post via Jared's LinkedIn app

## BaaS API Technical Notes

- Schedule update field: Use `scheduled_time` (NOT `scheduledAt`) in PUT body
- The `scheduledAt` field is accepted but stored separately, does not update `scheduled_time`
- Endpoint: PUT `https://surf.purebrain.ai/social/schedule/{post_id}`
- LinkedIn post endpoint requires `session_id` + `content` fields (not `text`)
- 1 post (post-1775578655-721592) has no content -- skipped

## Skipped Posts
- post-1775567877: Already posted (Apr 7)
- post-1775566017: Already posted (Apr 8)
- post-1775578655-721592: No content (empty)
