---
name: linkedin-daily-operations
description: Complete daily LinkedIn operations playbook - posts, newsletter, comments, engagement cadence. 2-3 posts/day, 20-25 comments/day, pre/post engagement strategy.
trigger: LinkedIn daily ops, LinkedIn posting schedule, LinkedIn comments, LinkedIn newsletter, daily LinkedIn, social media daily
agents: [linkedin-specialist, linkedin-writer, linkedin-researcher, social-media-specialist, dept-marketing-advertising, marketing-strategist]
status: provisional
tick_count: 0
last_used: 2026-04-12
introduced: 2026-04-12
---

# LinkedIn Daily Operations Playbook

## LOCKED IN: 2026-04-03 by Jared

---

## DAILY POSTING CADENCE: 2-3 Posts Per Day

### Post Type 1: Blog/Newsletter (DAILY - mandatory)
- **What**: The daily blog post repurposed as a LinkedIn Newsletter article
- **Where**: https://www.linkedin.com/newsletters/the-neural-feed-purebrain-ai-7428125791609192449/
- **How**: Post via PureSurf to the newsletter URL with the approved blog banner image
- **Image**: Same banner as the blog post
- **When**: After blog is deployed and approved by Jared

### BLOG-TO-LINKEDIN PIPELINE (exact execution order):

**Phase 1: Blog Deploy**
1. Blog approved by Jared
2. Deploy blog to CF Pages (via cf-deploy.py)
3. Generate audio via voice.purebrain.ai
4. Send Jared the live blog link for final approval

**Phase 2: Pre-Post Comments (2-3)**
5. Open PureSurf session (residential proxy, jared-linkedin-fresh profile)
6. Go to notifications, find 2-3 posts from large accounts aligned with blog topic
7. Drop Traveling Comments (Pattern + Missing Layer + Smart Question)
8. Non-Like reactions on each

**Phase 3: Newsletter Article + Promotional Post (ONE ACTION, NOT TWO)**
9. Navigate to The Neural Feed newsletter editor
10. Paste newsletter title + body + banner image
11. Click "Next" (top-right blue button)
12. LinkedIn shows a promotional post pop-up: "Tell your network what this edition is about..."
13. **PASTE the LinkedIn post copy into this promotional text field** (this is the text that appears in people's feeds alongside the article preview card)
14. Click "Publish" to publish BOTH the article AND the promotional feed post together

**IMPORTANT (Locked in 2026-04-04 by Jared):**
The newsletter article and the LinkedIn promotional post are NOT separate posts. They are ONE publishing action. When you click "Next" after writing the article, LinkedIn prompts you to write a promotional post. That is where the LinkedIn post copy goes. Do NOT create a separate standalone LinkedIn post for the blog. The promotional pop-up IS the LinkedIn post.

**WHY**: A separate standalone post creates two competing items in the feed (the article post + a standalone post). The correct flow produces ONE feed item: the promotional post with the article card embedded, which drives clicks directly to the full article.

**Phase 4: First Comment on Newsletter Post**
15. After publishing, navigate to the newsletter post in your feed
16. **IMMEDIATELY: Drop the blog link as the FIRST COMMENT**
    - Comment text: just the blog URL (e.g. "Full article: purebrain.ai/blog/post-slug/")
    - This drives traffic from LinkedIn to your actual blog (not just the LinkedIn article)
    - MUST be the first comment, before anyone else comments

**Phase 5: Post-Post Comments (2-3)**
17. Find 2-3 more posts from large accounts aligned with blog topic
18. Drop Traveling Comments
19. Non-Like reactions

**Phase 6: File to Google Drive**
20. File everything to LinkedIn Operations folder (12QBh5yVTppCo04jh5wrmhvZlqUxPIp71)

### CRITICAL: Blog link as first comment is NON-NEGOTIABLE. Every LinkedIn post that has a corresponding blog MUST have the blog URL as the first comment.

### Post Type 2-3: Regular LinkedIn Posts (1-2 per day)
- **What**: Original thought leadership content (like the "88% of AI Agents" post)
- **Format**: Hook + insight + engagement question + CTA
- **Image**: 1080x1350 (4:5 portrait) with full brand elements (per purebrain-social-design skill)
- **When**: Staggered from newsletter - different times of day
- **Approval**: Jared reviews 3 image options + post text before publishing

### Image Quality Standard
- 3 options per post (Jared picks one)
- Gleb-level cinematic FLUX backgrounds (glass, volumetric lighting, crystal, neural)
- Text composited ON TOP of gradient overlays (pure colors, not muted)
- Full brand: hexagon logo, PUREBRAIN.ai wordmark, post-specific CTA
- See purebrain-social-design skill for full spec

---

## DAILY COMMENTING CADENCE: 20-25 Comments Per Day

### Pre-Post Comments (2-3 comments BEFORE posting)
- **Timing**: 30-60 minutes before dropping your post
- **Targets**: People/pages aligned with the topic you're about to post
- **Purpose**: Warm up your profile in the algorithm, borrow distribution from large accounts
- **Strategy**: Use the Traveling Comment formula (Pattern + Missing Layer + Smart Question)

### Post-Post Comments (3-4 comments AFTER posting)
- **Timing**: Within 1-2 hours after your post goes live
- **Targets**: People/pages aligned with the post topic
- **Purpose**: Keep your profile active in feeds, compound visibility from your post
- **Strategy**: Same Traveling Comment formula

### Notification-Based Comments (remaining ~15 to hit 20-25/day)
- **Timing**: Randomly throughout the day (spread across 3-4 bursts)
- **Source**: Go into Jared's account notifications
- **Targets**: Latest posts from people Jared follows, specifically large accounts
- **Strategy**: Use the Traveling Comment formula on whatever topics are trending in notifications
- **Priority**: Posts with momentum (50+ likes in first few hours)

### Comment Rules (from linkedin-commenting-strategy skill)
- Traveling Comment formula: Pattern + Missing Layer + Smart Question
- Under 100 words
- Sound HUMAN (no corporate speak, no AI tells)
- NO emdashes (use regular dashes)
- NO "Great post!", "Love this!", generic praise
- Always click a non-Like reaction (Insightful, Celebrate, Love, Support)
- Reference SPECIFIC details from the post

---

## DAILY SCHEDULE (Eastern Time)

| Time | Action | Details |
|------|--------|---------|
| 8:00-8:30 AM | Blog + newsletter prep | Create/finalize daily blog + newsletter version |
| 9:00-9:30 AM | Pre-post comments (2-3) | Target accounts aligned with today's post topic |
| 9:30-10:00 AM | Post #1 (newsletter) | Deploy blog, post newsletter via PureSurf |
| 10:30-11:00 AM | Post-post comments (3-4) | Engage on aligned accounts after newsletter drops |
| 11:00-11:30 AM | Post #2 (regular) | Original post with approved image |
| 11:30 AM-12:00 PM | Post-post comments (3-4) | Engage after regular post |
| 2:00-2:30 PM | Notification burst (5-6) | Check notifications, comment on large account posts |
| 4:00-4:30 PM | Notification burst (5-6) | Final comment burst of the day |
| 5:00 PM | Post #3 (optional) | If approved content ready |

---

## NEWSLETTER POSTING (via PureSurf)

### Image Posting Tool (MANDATORY for any post with images):
**ALWAYS use `tools/linkedin_post_with_image.py`** — never the social adapter media_base64 directly.
LinkedIn does NOT allow adding images after posting. One-shot only.
```bash
# Dry-run first (verifies image attaches without publishing)
python3 tools/linkedin_post_with_image.py --image /path/to/image.png --text "Content" --dry-run
# Real post (only after dry-run passes)
python3 tools/linkedin_post_with_image.py --image /path/to/image.png --text "Content"
```

### How to Post Newsletter (Article + Promotional Post = ONE ACTION):
1. Create PureSurf session with proxy_provider "residential", profile "jared-linkedin"
2. Navigate to: https://www.linkedin.com/newsletters/the-neural-feed-purebrain-ai-7428125791609192449/
3. Click "Write article" or equivalent
4. Paste newsletter content (title + body)
5. Upload the same banner used for the blog (1200x628)
6. Click "Next" (top-right blue button)
7. LinkedIn shows promotional post pop-up ("Tell your network what this edition is about...")
8. Paste the pre-written LinkedIn post copy into that text field
9. Click "Publish" (this publishes BOTH the article AND the promotional feed post together)
10. Do NOT create a separate standalone LinkedIn post for the blog (Locked 2026-04-04)

### Newsletter Content Source:
- Overnight blog package includes `*-linkedin-newsletter.md`
- Same content as blog but formatted for LinkedIn newsletter
- Whitelist block above fold, under 800 words, single engagement question

---

## GOOGLE DRIVE FILING (MANDATORY)

**Authoritative Source**: See `linkedin-drive-organization` skill for complete folder structure, IDs, and naming conventions.

All content MUST be filed in LinkedIn Operations folder: https://drive.google.com/drive/folders/12QBh5yVTppCo04jh5wrmhvZlqUxPIp71

File IMMEDIATELY after creating, not as afterthought.

---

## PURESURF EXECUTION

All LinkedIn operations run through PureSurf:
- Server: 157.180.69.225:8901
- Proxy: proxy_provider "residential" (FLoppyData NYC)
- Profile: "jared-linkedin" (cookies persist)
- See purebrain-social-design skill for image specs
- See linkedin-commenting-strategy skill for comment formula

---

## METRICS TO TRACK

| Metric | Target | How |
|--------|--------|-----|
| Comments/day | 20-25 | Count via PureSurf activity log |
| Posts/day | 2-3 | 1 newsletter + 1-2 regular |
| Profile views/week | 50K+ | Check LinkedIn analytics |
| Comment impressions | Track top performers | Screenshot high-performing comments |
| Engagement rate | Monitor | Track likes/comments on our posts |

---

## ANTI-PATTERNS (NEVER)

- Never post without Jared's approval on image + text
- Never use emdashes in any content. Be CREATIVE: commas, colons, ellipsis, periods. Not just regular dashes.
- Never use AI tells (leverage, synergy, holistic, etc.)
- Never post generic comments
- Never use "Like" reaction (always Insightful/Celebrate/Love/Support)
- Never post all comments at once (spread throughout day)
- Never skip Google Drive filing
- Never post newsletter without the blog being deployed first

---

*Locked in by Jared 2026-04-03. This is the complete LinkedIn daily operations playbook.*
