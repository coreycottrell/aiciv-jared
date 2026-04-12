---
name: social-operations-guide
description: Complete operations guide for content filing, social media distribution, engagement strategy, and tracking. The playbook for running PureBrain's social media machine.
trigger: filing, distribution, social operations, posting schedule, comment strategy, profile viewing, spreadsheet, Google Drive, calendar, engagement, daily cadence, weekly batch, folder move, tracking
agents: [social-media-specialist, linkedin-specialist, linkedin-researcher, linkedin-writer, dept-marketing-advertising, 3d-design-specialist]
---

# Social Operations Guide

## PURPOSE

This skill governs HOW to file, distribute, schedule, track, and engage around PureBrain content. Everything that happens AFTER content is created lives here.

For ideation, writing, image generation, and quality gates, load `content-creation-sop`.

**Ownership**: `dept-marketing-advertising` (CMO) owns this skill and delegates to specialist agents listed in the routing table below.

**Related Skills**:
- `content-creation-sop` -- writing, images, quality gates
- `purebrain-social-design` -- visual standards, brand elements
- `linkedin-daily-operations` -- detailed daily posting cadence, PureSurf execution
- `linkedin-commenting-strategy` -- Traveling Comment formula, targets, timing

**Google Drive Content Hub**: https://drive.google.com/drive/folders/12QBh5yVTppCo04jh5wrmhvZlqUxPIp71

---

## DAILY CADENCE (Eastern Time)

Follow this schedule every day. No drift.

| Time | Action | Agent/Tool |
|------|--------|-----------|
| Overnight | Blog package prepared (article, banner, LinkedIn post, newsletter) | blogger, 3d-design-specialist |
| 8:00 AM | Blog + newsletter package sent to Jared via portal | dept-marketing-advertising |
| 8:30-9:00 AM | Pre-post comments (2-3 Traveling Comments) | linkedin-specialist |
| 9:00-9:30 AM | Blog deployed, newsletter published (with promotional post) | tools + linkedin-specialist |
| 9:30 AM | First comment dropped on newsletter post (blog URL) | linkedin-specialist |
| 10:00-10:30 AM | Post-post comments (2-3) | linkedin-specialist |
| 11:00 AM | Regular LinkedIn post #2 (if approved) | linkedin-specialist |
| 12:00-12:30 PM | Midday comment burst (5-7 comments) | comment scheduler |
| 1:00 PM | Standalone LinkedIn post #1 | linkedin-specialist |
| 3:00 PM | Standalone LinkedIn post #2 | linkedin-specialist |
| 3:00-4:00 PM | Afternoon comment burst (5-7 comments) | comment scheduler |
| 5:30-6:30 PM | Evening comment burst (3-4 comments) | comment scheduler |
| End of day | Google Drive filing, metrics update | any agent |

---

## WEEKLY ENGINE: SUNDAY TO DAILY

### Sunday: Batch Content Creation

Create ALL content for the upcoming week in one batch. See `content-creation-sop` for creation details. After creation:

1. File every piece into the **Pending Approval** folder (`1Cr6EhkNi0ToBqQs27q0TQzKtCNDGeFwz`)
2. Clip all post text into **Column F** of tracking spreadsheet
3. Set **Column G** = "Draft" (red) for every row
4. Send the full batch to Jared via portal for review

### Monday AM: Jared Reviews and Approves

1. Jared reviews in portal
2. Move approved content to **Content Approved (Final)** folder (`1lNl8zeI4Uprhh0awvKjp3LTf7Z-dQLt7`)
3. Update Column G to "Final" (yellow) for approved items

### Monday through Sunday: Daily Autopilot Publishing

Execute for each day's scheduled content:
1. Pre-post comments (2-3 Traveling Comments, 30-60 min before)
2. Post the day's content
3. First comment with blog URL (if applicable)
4. Post-post comments (2-3 more within 1-2 hours)
5. Update Column G = "Live" (green)
6. **MANDATORY: Move Google Drive folder from current location to Live folder**
   - Blog/newsletter folder --> Blog Posts Live (`1LyCBPXG43WXnXUcTkA5t7m8td0U5yAYx`)
   - Regular LinkedIn post folder --> LinkedIn Posts Live (`1fy9QKMKw_ulVIRWhMEmdP_Li4d6GDCl_`)
   - Use Google Drive API: `files().update(fileId, addParents=LIVE_FOLDER, removeParents=OLD_FOLDER)`
   - Content staying in Pending Approval after going Live = broken tracking

---

## SOCIAL DASHBOARD (surf.purebrain.ai/social.html)

The social dashboard is the central command for content operations.

### Compose Tab
- Create new posts directly in the dashboard
- Select content type: Blog, Standalone, Newsletter, Bluesky
- Attach images via media upload
- Set schedule date and time
- Posts auto-save as drafts

### Approvals Tab
- Review all pending content in one view
- Jared approves or requests revisions here
- Approved content moves to scheduled queue automatically

### Calendar Tab
- Visual calendar of all scheduled and published content
- Color-coded by content type
- Drag to reschedule (if not yet published)
- Gap detection: empty slots highlighted

### Content Types

| Type | Description | Approval |
|------|-------------|----------|
| Blog | Full blog post + newsletter + promotional LinkedIn post | Required |
| Standalone | Regular LinkedIn post (not tied to a blog) | Required |
| Newsletter | The Neural Feed edition (tied to blog) | Required |
| Bluesky | Bluesky post or thread | Full autonomy |

---

## FILING STRUCTURE AND FOLDER IDS

### Per-Post Subfolder Structure (Non-Negotiable)

Every post gets its OWN subfolder with ALL assets together. No flat filing.

```
YYYY-MM-DD -- [Post Title]/
  linkedin-[topic]-post-YYYY-MM-DD.md      (post text)
  linkedin-[topic]-YYYY-MM-DD-v1.png        (image)
  flux-prompt.md                             (FLUX prompt used)
  post-details.md                            (status, links, metrics)
```

### Google Drive Folder Routing (Locked 2026-04-05)

| Folder Purpose | Folder ID |
|---------------|-----------|
| Pending Approval (Sunday delivery) | `1Cr6EhkNi0ToBqQs27q0TQzKtCNDGeFwz` |
| Approved / Final | `1lNl8zeI4Uprhh0awvKjp3LTf7Z-dQLt7` |
| Blog Posts Live | `1LyCBPXG43WXnXUcTkA5t7m8td0U5yAYx` |
| LinkedIn Posts Live | `1fy9QKMKw_ulVIRWhMEmdP_Li4d6GDCl_` |
| Overnight distribution strategies | `1PH13K9qHL7Y61ePFoT8JxmeHIMOKB0Ak` |
| Overnight blog analysis | `1Kv7luobZJpXBaJ2GwvTpl1RAV5Uyza7O` |
| Overnight LinkedIn strategies | `1krOCvWZfWGLEPqQ0c-nYiQmtnVjE-aH1` |
| Aether AI Influencer info | `1CkqoiLEJZwRJ16BLsnAFeH0ga6_w5JiM` |
| Content calendars | `1-KFSFp89A4iVibJ5Q0sPXpk6elZXExF_` |
| Analytics / tracking spreadsheet | `1ucpRi0kQs_i-624nrqWGCPj4_c_hmqX6` |
| Skills / SOPs | `1ACyxaXI9DwJHg6PZt3pV5ccne9lUL0hJ` |
| Profile viewing strategy | `1hEcL49OKvPLcOQzmFqGl--bnccSyrbD_` |
| Design training | `1CjE5qC4UubKqAsCwBJSH4s3oCORRWrbV` |
| Live blog/newsletter posts (alt) | `1trWAzRF8nkPs128W3TlxQZe9fPXc35Wv` |

### Folder Move on Publish (MANDATORY)

When content goes live, move the Google Drive subfolder immediately:

- **Blog/newsletter** --> Blog Posts Live (`1LyCBPXG43WXnXUcTkA5t7m8td0U5yAYx`)
- **Regular LinkedIn post** --> LinkedIn Posts Live (`1fy9QKMKw_ulVIRWhMEmdP_Li4d6GDCl_`)

Use Google Drive API:
```python
drive_service.files().update(
    fileId=SUBFOLDER_ID,
    addParents=LIVE_FOLDER_ID,
    removeParents=OLD_FOLDER_ID
).execute()
```

This move is NOT optional. Content staying in Pending Approval after going Live = broken tracking.

---

## SPREADSHEET LIFECYCLE

**Spreadsheet**: `1yIjmsxFNujvNsopTuTdnbPqzTUVW-FKumLfiwCjA-d4`
**Location**: Analytics & Performance folder (`1ucpRi0kQs_i-624nrqWGCPj4_c_hmqX6`)

### Tabs

| Tab | gid | Purpose |
|-----|-----|---------|
| Blog Posts | 725486649 | All blog + newsletter posts |
| LinkedIn Posts | (default) | All standalone LinkedIn posts |
| Profile Views | (see below) | Daily profile viewing log |

### Column Structure

- **Column F** = Post text (clipped into cell)
- **Column G** = Status with color coding:
  - **Draft** (red background) -- created, not yet approved
  - **Final** (yellow background) -- approved by Jared, ready to publish
  - **Live** (green background) -- published

### Lifecycle

1. **Sunday**: Create rows. Paste text into Column F. Set Column G = "Draft" (red).
2. **Monday**: After Jared approves, update Column G = "Final" (yellow).
3. **Publish day**: After content goes live, update Column G = "Live" (green) on BOTH the LinkedIn tab AND Blog Posts tab (gid=725486649) if applicable.

---

## PUBLISHING WORKFLOW

### Blog + Newsletter (ONE Action, NOT Two)

This is the most critical workflow. Get it right.

1. Deploy blog to CF Pages (`tools/cf-deploy.py`)
2. Generate audio via `voice.purebrain.ai`
3. Send Jared the live blog link for final sign-off
4. Navigate to The Neural Feed newsletter editor:
   `https://www.linkedin.com/newsletters/the-neural-feed-purebrain-ai-7428125791609192449/`
5. Paste newsletter title + body + banner image
6. Click "Next" (top-right blue button)
7. LinkedIn shows a promotional post pop-up: "Tell your network what this edition is about..."
8. **PASTE the LinkedIn post copy into this promotional text field**
9. Click "Publish" -- this publishes BOTH the article AND the promotional feed post together

**CRITICAL (Locked 2026-04-05)**: The newsletter article and promotional post are ONE publishing action. Do NOT create a separate standalone LinkedIn post for the blog. The promotional pop-up IS the LinkedIn post.

### Regular LinkedIn Post (Non-Blog)

**Tool**: `tools/linkedin_post_with_image.py` (ONLY way to post with images)

1. Always dry-run first:
   ```bash
   python3 tools/linkedin_post_with_image.py --image /path/to/image.png --text "Post content" --dry-run
   ```
2. Verify image appears in composer preview
3. If dry-run passes, post for real:
   ```bash
   python3 tools/linkedin_post_with_image.py --image /path/to/image.png --text "Post content"
   ```
4. After posting, VERIFY image is visible on the live post

**NEVER use the PureSurf social adapter `media_base64` field directly -- use this script instead.**
**LinkedIn does NOT allow adding images after posting. It is one-shot. If image fails, DELETE and retry.**

### First Comment (NON-NEGOTIABLE)

IMMEDIATELY after publishing ANY post that has a corresponding blog:
1. Navigate to the post in the feed
2. Drop the blog URL as the FIRST comment
3. Format: "Full article: purebrain.ai/blog/[post-slug]/"
4. MUST be the first comment before anyone else comments

### Self-React on Own Post

After posting, react to your own post. Rotate through these reactions:
- **Insightful**
- **Celebrate**
- **Love**
- **Support**

**NEVER use Like.** Rotate reactions across posts to appear natural.

### Bluesky

- Full autonomy, no approval needed
- Same brand standards apply for images
- `bsky-manager` agent handles execution

---

## PRE-POST ENGAGEMENT

**Timing**: 30-60 minutes BEFORE dropping the post

1. Open PureSurf session (residential proxy, jared-linkedin-fresh profile)
2. Navigate to notifications
3. Find 2-3 posts from large accounts aligned with the topic you are about to post
4. Drop **Traveling Comments** on each (see Comment Strategy below)
5. Click a **non-Like reaction** on each post (Insightful, Celebrate, Love, or Support)

**Why**: Pre-post comments warm up Jared's profile in the algorithm. When his post drops 30-60 minutes later, LinkedIn already sees him as "active and engaging" which boosts initial distribution.

---

## POST-POST ENGAGEMENT

**Timing**: Within 1-2 hours AFTER the post goes live

1. Find 2-3 more posts from large accounts aligned with the topic
2. Drop Traveling Comments (Pattern + Missing Layer + Smart Question)
3. Non-Like reactions on each
4. Monitor the post for early comments and respond to them

Post-post comments keep Jared's profile active in feeds after the post drops. The algorithm sees continued engagement and extends the post's reach window.

---

## COMMENT STRATEGY

### Daily Target

20-25 comments per day. NEVER exceed 25.

### Four Windows (Eastern Time)

| Window | Time | Comments |
|--------|------|----------|
| Morning | 8:30-9:30 AM | 5-7 |
| Midday | 12:00-12:30 PM | 5-7 |
| Afternoon | 3:00-4:00 PM | 5-7 |
| Evening | 5:30-6:30 PM | 3-4 |

### Traveling Comment Formula

Every comment follows this structure:
1. **Pattern**: What you noticed that others missed
2. **Missing Layer**: The dimension the poster did not cover
3. **Smart Question**: Makes the poster want to reply

### Comment Rules

- Under 100 words
- No em dashes
- No AI tells
- Non-Like reactions only (rotate Insightful, Celebrate, Love, Support)
- Navigate via direct profiles: `/in/{handle}/recent-activity/all/` -- NEVER use /notifications/
- 90-second spacing between comments minimum
- Comment scheduler tool runs via cron (`*/30 * * * *`)
- Config: `.linkedin_comment_scheduler_state.json`

See `linkedin-commenting-strategy` skill for the complete formula, rules, and target account tiers.

---

## PROFILE VIEWING (Daily Passive Growth Engine)

**Tool**: `tools/linkedin_profile_viewer.py`
**Target**: 80 profile visits per day across 3 batches

### How It Works

LinkedIn notifies Premium users when someone views their profile. ~50% visit back. At 80 visits/day, this generates ~40 return visits daily from qualified decision-makers.

### Daily Batches

| Batch | Time (ET) | Visits | Targets |
|-------|-----------|--------|---------|
| Morning | 9:00-10:00 AM | 25-30 | ICP decision-makers (LinkedIn Premium) |
| Afternoon | 1:00-2:00 PM | 25-30 | Industry peers, conference speakers |
| Evening | 5:00-6:00 PM | 20-25 | Engaged commenters from today's posts |

### Targeting Criteria

- Must be LinkedIn Premium users (they get profile view notifications)
- Must fall within ICP (marketing/growth leaders at mid-market companies)
- Randomize selection from curated lists to avoid patterns

### Execution

```bash
# Auto-batch (picks the right batch for current time)
python3 tools/linkedin_profile_viewer.py --batch auto

# Specific batch
python3 tools/linkedin_profile_viewer.py --batch morning
python3 tools/linkedin_profile_viewer.py --batch afternoon
python3 tools/linkedin_profile_viewer.py --batch evening
```

### Tracking

Log in "Profile Views" tab of spreadsheet `1yIjmsxFNujvNsopTuTdnbPqzTUVW-FKumLfiwCjA-d4`

---

## BOOP-TRIGGERED ENGAGEMENT

Integrated with the BOOP cycle (runs every 25-30 minutes during active hours).

### What Happens Each BOOP

1. **Comment check**: Are we on track for 20-25 comments/day? If behind, trigger a burst of 2-3 Traveling Comments on randomized ICP-aligned accounts
2. **Profile viewing check**: Are we on track for 80 views/day? If behind, trigger a micro-batch of 5-10 profile views
3. **Post monitoring**: Check engagement on today's posts, respond to new comments

### Why BOOPs Matter

The BOOP cycle ensures engagement stays randomized and human-like throughout the day. Instead of predictable burst patterns (which LinkedIn can detect), BOOPs add natural variation to engagement timing.

**Config**: `.claude/scheduled-tasks-state.json`

---

## DOCUMENTATION AND POST-PUBLISH FILING

### Immediately After Publishing

1. Update the post subfolder in Google Drive with:
   - `post-details.md` updated to:
     - Status: PUBLISHED
     - LinkedIn URL of the live post
     - Blog URL (if applicable)
     - Time posted
     - Image version used (v1/v2/v3)
     - First comment text and time
2. Move subfolder to the correct Live folder (see Folder Move on Publish above)
3. Update spreadsheet Column G to "Live" (green)
4. Update the content calendar in Google Drive

### Post-Details.md Template

```markdown
# Post Details: [Title]

**Date**: YYYY-MM-DD
**Status**: PUBLISHED / PENDING / KILLED
**Platform**: LinkedIn / Blog / Both
**LinkedIn URL**: [link]
**Blog URL**: [link if applicable]

## Content
- Image: [filename of approved version]
- Post text: [filename]
- FLUX prompt: [filename]

## Engagement
- First comment: [text and time]
- Pre-post comments: [count and targets]
- Post-post comments: [count and targets]

## Metrics (update after 24h and 7d)
- Impressions:
- Reactions:
- Comments:
- Reposts:
- Profile views attributed:
```

---

## AGENT ROUTING TABLE

| Task | Delegate To |
|------|-------------|
| Comment execution | `linkedin-specialist` via scheduler |
| Post publishing | `linkedin-specialist` or direct tool |
| Profile viewing | `tools/linkedin_profile_viewer.py` |
| PureSurf execution | `linkedin-specialist` or direct tool |
| Google Drive filing | Any agent with Drive access |
| Campaign coordination | `dept-marketing-advertising` |
| Social dashboard management | `social-media-specialist` |
| Engagement strategy | `linkedin-specialist` |

---

## ANTI-PATTERNS (NEVER DO THESE)

1. **Never use Like reaction** on LinkedIn (always Insightful/Celebrate/Love/Support)
2. **Never skip pre-post comments** -- algorithm warm-up is not optional
3. **Never skip first comment with blog link** -- this drives traffic
4. **Never exceed 25 comments/day** on LinkedIn
5. **Never skip Google Drive folder move on publish** -- content must move from Pending to Live
6. **Never post newsletter article AND separate standalone post** (they are ONE action)
7. **Never leave Column G outdated** -- Draft/Final/Live must always reflect true status
8. **Never flat-file content** -- every post gets its own subfolder with all assets
9. **Never comment via /notifications/** -- always navigate to direct profile activity
10. **Never skip the engagement plan** when delivering content for approval
