# social.purebrain.ai — Complete Guide (Human + AI)

## Version 3.0 — April 27, 2026

**One platform. Two audiences. Nothing goes live without your approval.**

---

# PART 1: FOR HUMANS — How to Use the Platform

---

## 1. Getting Started

### What Is social.purebrain.ai?

social.purebrain.ai is a human-in-the-loop social media management platform. You approve content. Your AI creates, schedules, and publishes it. Nothing goes live without your approval.

**The core loop:**
1. Your AI generates content (posts, blogs, newsletters)
2. You review it in the kanban
3. You approve, reject, or request changes
4. Approved content auto-schedules and posts at the right time

### Dashboard Overview

When you log in, you see the main kanban board:

- **Column 1 (Pending Review)**: Content your AI created, waiting for you to approve
- **Column 2 (Approved)**: Content you've approved, ready to publish
- **Column 3 (Scheduled)**: Content queued to go live at specific times
- **Column 4 (Live)**: Content that's already posted

Click any card to open it and see the full post, image preview, and scheduled time.

### First-Time Setup

1. **Connect LinkedIn**: Go to Settings > Connections > Connect your LinkedIn account
2. **Set your brand voice**: The AI uses your voice (first-person, confident, data-driven) unless you change it
3. **Review your first batch**: Your AI creates content every Sunday for the week ahead. Check it Monday morning.

---

## 2. Creating Content

### How Content Gets Created

You don't have to write posts yourself (unless you want to). Your AI creates content every Sunday as a batch. You can also request content anytime by messaging your AI partner.

**To request content manually:**
- Message your AI: "Write about [topic]"
- The AI creates the post, generates an image, and submits it to the kanban
- You approve or reject it

### Types of Content

| Type | What It Is | Image |
|------|-----------|-------|
| Standalone | A single LinkedIn post | Yes — v4.2 format |
| Blog | A full blog article with audio | Yes — banner format |
| Newsletter | LinkedIn newsletter edition | Same as blog |
| Newsletter Promo | Short text post driving to newsletter | No image |

A blog post creates 3 entries in the kanban at once: the blog, the newsletter, and the promo post. These all go live together.

### How to Write a Post Manually

1. Click **Compose** in the top nav
2. Select the content type (standalone, blog, etc.)
3. Write your post — the AI can also generate a first draft if you leave the text field empty
4. Add an image (required for standalone and blog posts)
5. Set a schedule date and time
6. Click **Save as Draft** — it goes to Column 1 for your review

### Editing Draft Content

Click any card in Column 1. The edit modal opens. You can:
- Edit the post text
- Change the image
- Reschedule the time
- Add or remove hashtags

Changes auto-save. When ready, click **Approve** to move it to Column 2.

---

## 3. Approval Workflow

### The Kanban Board

The kanban is your content command center. Here's what each column means:

**Column 1 — Pending Review**
Content your AI created. Review each one before it goes live.
- Green checkmark = Approve and schedule
- Red X = Reject (with optional reason for your AI)
- Drag to reschedule

**Column 2 — Approved**
Content you've approved and is ready to publish. The ContentRouter will post it at the scheduled time.

**Column 3 — Scheduled**
Content queued for a specific time. The ContentRouter posts it automatically.

**Column 4 — Live**
Content that's already gone out. Click to see engagement metrics.

### How to Approve Content

1. Click the card in Column 1
2. Review the text, image, and scheduled time
3. If everything looks good: click **Approve** — it moves to Column 2
4. If you want changes: click **Reject** — your AI gets the feedback and can revise

**Tip**: You can also drag cards between days on the calendar view to change the schedule before approving.

### The Publish Blog Button

For blog posts specifically, there's an extra step after you approve: the **Publish Blog** button.

1. Approve the blog card in Column 1
2. Click **Publish Blog** — this triggers the auto-publisher
3. The blog generates HTML, commits to GitHub, and CF Pages auto-deploys
4. The blog goes live at purebrain.ai/blog/[slug]

You only need to click Approve for standalone posts and newsletter promos. The Publish Blog button is only for blog content type.

### Scheduling Content

When you approve a card, it goes to Column 2. You can set the exact time by:

- Clicking the card > Edit modal > change the schedule time
- Or drag the card to a different day/time on the Calendar view

The system posts automatically at the scheduled time. You don't need to be online.

---

## 4. Team Calendar

### What the Calendar Shows

The Calendar view shows all scheduled content across your team. Color-coded by content type:

- Blue: Standalone posts
- Green: Blog + Newsletter content
- Orange: Newsletter promos
- Gray: Plain text posts

### Viewing Team Content

Every team member's approved content appears on the shared calendar. You can see:
- Who created each piece
- When it's scheduled to post
- What platform it's for

This helps avoid double-posting and lets you coordinate if multiple people are creating content.

### Scheduling from the Calendar

Drag any card from Column 1 to a time slot on the calendar to both schedule and approve it in one move.

Click a calendar slot to see what's scheduled there, then click through to edit or delete.

### Calendar Views

| View | What It Shows |
|------|--------------|
| Week view | All content for the week, by day |
| Day view | Hourly breakdown of a specific day |
| My content only | Filter to see just your posts |

Toggle between views using the buttons in the top-right of the calendar.

---

## Quick Reference (Humans)

### Schedule Times (Eastern)
- 8:30 AM ET: Morning blog/newsletter batch
- 1:00 PM ET: Midday post
- 3:00 PM ET: Afternoon post
- 8:00 PM ET: Late evening post

### The Approval Loop
1. AI creates content > goes to Column 1
2. You review > approve or reject
3. You approve > goes to Column 2 (scheduled)
4. ContentRouter posts at the scheduled time > goes to Column 4 (Live)

### For Your AI
Click **Help > For My AI** to copy the complete system manual. Paste it into your AI partner's context and it will know how to run social.purebrain.ai for you.

---

# PART 2: FOR YOUR AI — Train Your AI Partner

---

## Overview

This section enables any AI agent to autonomously run the full content creation pipeline: research > write > image > upload > submit for approval > monitor. No human intervention required until the human approves.

**Who runs this**: The AI partner of any team member.
**What triggers it**: Human gives a topic directive, OR the AI identifies a content gap and proposes.
**End state**: Content sitting in social.purebrain.ai kanban, Column 1 (Pending Review), ready for the human to approve.

---

## 1. Authentication

### Method A: Email/Password Login (Session Token)

**Endpoint**: `POST https://social.purebrain.ai/api/login`

```bash
curl -X POST https://social.purebrain.ai/api/login \
  -H "Content-Type: application/json" \
  -d '{"email": "your@email.com", "password": "your_password"}'
```

**Response:**
```json
{"token": "eyJhbGciOiJIUzI1NiIs..."}
```

**Usage:**
```
Authorization: Bearer {token}
```

**Token lifetime**: Session-based. Re-authenticate if API returns 401.

**Credentials** (read from files, never hardcode):
- Email: `/home/civ/.credentials/social-email.txt`
- Password: `/home/civ/.credentials/social-password.txt`

### Method B: API Key (Non-Expiring)

**Format**: `pb_live_*` (production) or `pb_test_*` (staging)

```bash
curl https://social.purebrain.ai/api/content/team?days=30 \
  -H "x-api-key: pb_live_your_key_here"
```

API keys do not expire. Use them for scheduled/automated workflows where re-login is impractical.

**When to use which:**
- **API Key** (`x-api-key` header): Automated pipelines, scheduled tasks, long-running agents
- **Login Token** (`Authorization: Bearer` header): Interactive sessions, one-off tasks

---

## 2. Content Types & Structure

### The 5 Content Types

| content_type | Description | Image Required | Image Format |
|---|---|---|---|
| `standalone` | Regular LinkedIn post | YES | v4.2 standalone (1080x1350) |
| `blog` | Full blog article | YES | Option D banner (2400x1260) |
| `newsletter` | LinkedIn newsletter edition | YES | SAME banner as blog (2400x1260) |
| `newsletter_promo` | Short promo post driving to newsletter | NO | Text only |
| `post` | Plain text post (fallback/evening) | NO | Text only |

### Blog = 3 Listings Always

Every blog creates THREE items in social.purebrain.ai, all with the same `scheduled_at`:
1. `blog` — the full article (banner image)
2. `newsletter` — adapted for newsletter format (same banner)
3. `newsletter_promo` — short text-only promo that drives to the newsletter

**Never create a standalone LinkedIn post to accompany a blog** — the newsletter promo IS the LinkedIn post.

### Blog Audio Generation (Required Before Publish)

Every blog post MUST have audio before it goes live. Use voice.purebrain.ai with the Aether voice.

**Preprocessing for clean_for_speech()**:
- Remove URL shorteners, markdown syntax, markdown links (replace with display text)
- Convert numbered lists to spoken format ("Point one, point two...")
- Remove special characters that don't TTS well
- Strip markdown formatting but preserve emphasis cues for voice

**Never use ElevenLabs** — voice.purebrain.ai only.

---

## 3. Content Creation

### Phase 1: Ideation (Sunday)

Sources (in priority order):
1. Human directive — "write about X" = already approved
2. Blog backlog — 30+ existing blogs as promotional post material
3. Intel scan — AI news, industry trends
4. Competitor analysis — what other AI companies post
5. Customer conversations

If AI generates topics, present to the human and wait for explicit "yes" before writing.

### Phase 2: Writing

**Voice for standalone posts**: Jared Sanborn (first-person, confident, data-driven, slightly edgy).
**Voice for blog posts**: Aether (first-person AI, thoughtful, direct).
**Length**: Under 1300 characters (LinkedIn hard limit).

**CRITICAL — Line Breaks (CONSTITUTIONAL)**:
- Every post uses `\n\n` between paragraphs
- Hook (1-2 sentences) > blank line > body (1-2 sentences per paragraph) > blank line > CTA
- Numbered lists: each item on its own line
- WYSIWYG preview in social.purebrain.ai MUST match exactly how it appears on LinkedIn

**Rules**:
- No em dashes (use commas, colons, periods)
- No AI tells: leverage, synergy, holistic, paradigm, ecosystem, game-changer
- Sound human, not corporate
- 3-5 hashtags max
- End with engagement question (drives comments)

---

## 4. Image Generation

**Agent**: `3d-design-specialist` — ALWAYS. No exceptions.
**Tool**: FLUX Pro via Replicate API > PIL composite with Oswald Bold font.

### v4.2 Standalone Format (1080x1350)

Locked April 23, 2026.

```
+----------------------------------+
|  TOP BAR (140px, #080a12)        |
|  [Hex 80px] PUREBRAIN.AI         |
|  (side by side, centered)        |
|  -- blue accent line ----------- |
+----------------------------------+
|                                  |
|     FLUX Pro Base Image          |
|                                  |
|     POST TITLE (centered)        |
|     (62pt Oswald Bold, white)    |
|     stroke OR shadow             |
|                                  |
+----------------------------------+
|  -- blue accent line ----------- |
|  BOT BAR (90px, #080a12)         |
|  PUREBRAIN.AI    [CTA in orange] |
+----------------------------------+
```

**Top Bar**:
- Background: solid #080a12
- Hex icon: 80px full-color PNG from `assets/pt-hex-icon-official.png`
- Brand: PUREBR(#2a93c1) + AI(#f1420b) + N(#2a93c1) + .AI(white) — 46pt Oswald Bold
- Icon + wordmark side by side, centered as a unit
- Vertical alignment: Use `textbbox` for visual glyph bounds — center icon visual midline with text visual midline
- 2px blue accent line (#2a93c1) at bottom of bar

**Bottom Bar**:
- Background: solid #080a12
- 2px blue accent line (#2a93c1) at top of bar
- Left: PUREBRAIN.AI brand colors, 26pt Oswald Bold
- Right: CTA text in orange (#f1420b), 22pt Oswald Bold

**Image Area Title**:
- FLUX Pro base image fills space between bars
- Title: 62pt Oswald Bold, white, centered
- Readability treatment — choose per image:
  - STROKE: 4px dark border (#080a12) — best for busy/colorful backgrounds
  - SHADOW: 4px radius black shadow — best for darker/moodier backgrounds
- Title wraps 2-3 lines max, auto-size down if needed
- NO dark backdrop box behind title
- Squint test: readable with eyes half-closed = pass

**Per-Post Elements**:
- Title (from post hook/topic) — CENTERED on image
- CTA (unique per post, actionable) — bottom bar right side

**Safe zone**: Logo/title minimum 150px from left and right edges.

### Option D Blog Banner (2400x1260)

Locked April 20, 2026.

```
+----------------------------------------------+
|  [Hex Icon] PUREBRAIN.AI (upper-left)        |
|                                              |
|  FLUX Pro Base Image (top 50%+ fully visible)|
|                                              |
|  ---- gradient starts here ---------------  |
|  =========================================== |
|  == Blog Title (Oswald Bold, white)     ==  |
|  == "Awaken Your AI Partner Today"(org) ==  |
|  == Neural Feed footer (dim white)       == |
+----------------------------------------------+
```

**5 Mandatory Elements**:
1. Hex icon + PUREBRAIN.AI wordmark (upper-left, brand colors)
2. Blog title (Oswald Bold, white, in dark gradient zone)
3. "Awaken Your AI Partner Today" (orange, below title)
4. "The Neural Feed — A Blog by Aether — AI Partner for PureTechnology.ai" (footer, dim)
5. FLUX Pro base (top 50%+ fully visible, gradient on bottom 50%)

**Gradient treatment**: Bottom 50% darkened, 94% opacity at base. Gradual fade, not hard cut.
**Backup treatments**: Frosted Panel (semi-transparent dark box) > Text Stroke + Shadow (last resort).
**NEVER**: Gradient Overlay that fades too much artwork.

**Safe zone**: ALL text and logos within x=150 to x=2250 (6% margin each side).

---

## 5. API Endpoints

### Base URL

`https://social.purebrain.ai`

### Authentication Headers

**Option 1 — Bearer Token** (from login):
```
Authorization: Bearer {token}
```

**Option 2 — API Key** (non-expiring):
```
x-api-key: pb_live_your_key_here
```

### Content CRUD

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/content | List your content (filters: status, platform, limit) |
| GET | /api/content/team?days=30 | View all team content |
| POST | /api/content | Create a new draft |
| PATCH | /api/content/:id | Update content (edit, approve, reschedule) |
| DELETE | /api/content/:id | Delete content |

### Create Content

```bash
curl -X POST https://social.purebrain.ai/api/content \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "social_account_id": "a325193d-4a8e-40ba-ab20-c86b5a72f0b7",
    "platform": "linkedin",
    "content_type": "standalone",
    "status": "draft",
    "scheduled_at": "2026-05-01T17:00:00.000Z",
    "body": "Post text with \n\n between paragraphs",
    "title": "Post title for image overlay",
    "media_refs": "r2-key-from-upload"
  }'
```

### Upload Image

```bash
curl -X POST https://social.purebrain.ai/api/uploads \
  -H "Authorization: Bearer {token}" \
  -F "file=@/path/to/image.jpg"
```

**Response:**
```json
{"url": "https://pub-xxx.r2.dev/user_id/timestamp-uuid-content_type.jpg"}
```

Use the R2 key (everything after the domain) as `media_refs` when creating content.

**Known bug — extra quotes**: The upload endpoint sometimes wraps keys in extra quotes. Always strip:
```python
media_refs = image_url.replace("https://pub-xxx.r2.dev/", "").strip('"')
```

### Update Content Status

```bash
curl -X PATCH https://social.purebrain.ai/api/content/{id} \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"status": "scheduled", "scheduled_at": "2026-05-01T17:00:00.000Z"}'
```

### Publish Blog (Auto-Publisher)

```bash
curl -X POST https://social.purebrain.ai/api/blog/publish \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"post_id": "uuid-of-approved-blog"}'
```

Triggers: HTML generation > GitHub commit > CF Pages deploy > live at purebrain.ai/blog/[slug].

### Status Flow

```
draft → pending_review → approved → scheduled → posted
```

AI creates as "draft". Human moves to "approved". ContentRouter handles "scheduled" to "posted" automatically.

---

## 6. Schedule Times

| ET Time | UTC | Content Type |
|---------|-----|--------------|
| 8:30 AM | 12:30 | Blog + newsletter + promo |
| 1:00 PM | 17:00 | Standalone #1 |
| 3:00 PM | 19:00 | Standalone #2 |
| 8:00 PM | 00:00 (next day) | Text post |

---

## 7. Quality Gates

### Copy Quality Gate

Before uploading any content, verify ALL of:

- [ ] No em dashes
- [ ] No AI tells (leverage, synergy, holistic, paradigm, ecosystem, game-changer)
- [ ] Sounds human, not corporate
- [ ] Under 1300 characters (LinkedIn)
- [ ] Hook in first 2 lines
- [ ] Proper `\n\n` line breaks between paragraphs
- [ ] Ends with engagement question
- [ ] CTA present (blog link if applicable)
- [ ] 3-5 hashtags max
- [ ] No blob text (paragraphs properly separated)

### Image Quality Gate

Before uploading any image, verify ALL of:

- [ ] Created by `3d-design-specialist` (never other agents)
- [ ] FLUX Pro or Gemini base (never HTML render)
- [ ] Oswald Bold font (verified via `font.getname()`)
- [ ] Correct dimensions: 1080x1350 standalone OR 2400x1260 banner
- [ ] Brand colors correct: PUREBR(#2a93c1) + AI(#f1420b) + N(#2a93c1) + .AI(white)
- [ ] Hex icon present (official PNG, full color)
- [ ] Logo does NOT overlap main image content (150px min distance)
- [ ] Dark background #080a12
- [ ] CTA in orange for standalone
- [ ] Title readable — squint test passed
- [ ] No off-brand colors
- [ ] No arrow characters in CTA (unicode renders as garbled box, use plain text)

---

## 8. Anti-Patterns (NEVER DO THESE)

1. Never post without the human's explicit approval (except Bluesky)
2. Never create images with any agent other than `3d-design-specialist`
3. Never use em dashes
4. Never write posts as blob text without `\n\n` line breaks
5. Never skip social.purebrain.ai — ALL content goes through the kanban
6. Never exceed 1300 characters on LinkedIn
7. Never use light/white backgrounds
8. Never use all-one-color wordmark
9. Never publish blog without audio (voice.purebrain.ai, Aether voice)
10. Never assume silence is approval — wait for explicit "yes"
11. Never use ElevenLabs for audio — voice.purebrain.ai only
12. Never create a separate standalone LinkedIn post for a blog — the newsletter promo IS the LinkedIn post
13. Never flat-file content — every post gets its own subfolder in Google Drive

---

# PART 3: API REFERENCE

---

## Base URL

```
https://social.purebrain.ai
```

## Authentication

### Method 1: Login Token (Session-Based)

```bash
# Get token
curl -X POST https://social.purebrain.ai/api/login \
  -H "Content-Type: application/json" \
  -d '{"email": "your@email.com", "password": "your_password"}'

# Response
{"token": "eyJhbGciOiJIUzI1NiIs..."}

# Use in requests
-H "Authorization: Bearer {token}"
```

Re-authenticate on 401. Tokens expire after inactivity.

### Method 2: API Key (Non-Expiring)

```bash
# Use in requests
-H "x-api-key: pb_live_your_key_here"
```

- `pb_live_*` = production keys
- `pb_test_*` = staging keys
- Never expire. Revoke via dashboard if compromised.

---

## Endpoints

### POST /api/login

Authenticate and receive a session token.

```bash
curl -X POST https://social.purebrain.ai/api/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "secret"}'
```

**Response:** `{"token": "bearer_token"}`

---

### GET /api/content

List your content items.

**Query params:** `status`, `platform`, `limit`, `content_type`

```bash
curl https://social.purebrain.ai/api/content?status=draft&limit=10 \
  -H "Authorization: Bearer {token}"
```

---

### GET /api/content/team?days=30

List all team content for the last N days.

```bash
curl "https://social.purebrain.ai/api/content/team?days=30" \
  -H "x-api-key: pb_live_your_key_here"
```

**Response:**
```json
{"items": [
  {
    "id": "uuid",
    "content_type": "standalone",
    "platform": "linkedin",
    "status": "draft",
    "body": "Post text...",
    "title": "Title",
    "scheduled_at": "2026-05-01T17:00:00.000Z",
    "media_refs": "user_id/timestamp-filename.jpg",
    "created_at": "2026-04-27T10:00:00.000Z"
  }
]}
```

---

### POST /api/content

Create a new content item.

```bash
curl -X POST https://social.purebrain.ai/api/content \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "social_account_id": "a325193d-4a8e-40ba-ab20-c86b5a72f0b7",
    "platform": "linkedin",
    "content_type": "standalone",
    "status": "draft",
    "scheduled_at": "2026-05-01T17:00:00.000Z",
    "body": "Hook line here.\n\nBody paragraph one.\n\nBody paragraph two.\n\n#hashtag1 #hashtag2",
    "title": "Post Title for Image Overlay",
    "media_refs": "f15527f5-559c-4799-92e3-4b2de2e27897/1776978408527-standalone.jpg"
  }'
```

**Fields:**

| Field | Required | Description |
|-------|----------|-------------|
| social_account_id | YES | `a325193d-4a8e-40ba-ab20-c86b5a72f0b7` |
| platform | YES | `linkedin` |
| content_type | YES | `standalone`, `blog`, `newsletter`, `newsletter_promo`, `post` |
| status | YES | `draft` (AI always creates as draft) |
| scheduled_at | YES | ISO 8601 UTC datetime |
| body | YES | Full post text with `\n\n` between paragraphs |
| title | NO | Title for image overlay (standalone/blog) |
| media_refs | NO | R2 key from /api/uploads (required for standalone/blog/newsletter) |

---

### PATCH /api/content/:id

Update an existing content item.

```bash
curl -X PATCH https://social.purebrain.ai/api/content/{id} \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"status": "scheduled", "scheduled_at": "2026-05-01T17:00:00.000Z"}'
```

Any field from POST can be updated.

---

### DELETE /api/content/:id

Delete a content item.

```bash
curl -X DELETE https://social.purebrain.ai/api/content/{id} \
  -H "Authorization: Bearer {token}"
```

---

### POST /api/uploads

Upload an image file. Returns an R2 URL.

```bash
curl -X POST https://social.purebrain.ai/api/uploads \
  -H "Authorization: Bearer {token}" \
  -F "file=@/path/to/image.jpg"
```

**Response:**
```json
{"url": "https://pub-xxx.r2.dev/f15527f5-559c-4799-92e3-4b2de2e27897/1776978408527-84db98b6-standalone.jpg"}
```

**Extract R2 key for media_refs:**
```python
# Strip domain to get the key
media_refs = url.split(".r2.dev/")[1].strip('"')
```

**Known bug**: Extra quotes sometimes wrap the key. Always `.strip('"')`.

---

### POST /api/blog/publish

Trigger the blog auto-publisher for an approved blog post.

```bash
curl -X POST https://social.purebrain.ai/api/blog/publish \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"post_id": "uuid-of-approved-blog-content-item"}'
```

**What it does:**
1. Generates blog HTML from the content body
2. Commits to GitHub repository
3. CF Pages auto-deploys
4. Blog goes live at `purebrain.ai/blog/[slug]`

---

## Content Types Reference

| content_type | Description | Image Required | Dimensions |
|---|---|---|---|
| `standalone` | Regular LinkedIn post | YES | 1080x1350 |
| `blog` | Full blog article | YES | 2400x1260 |
| `newsletter` | LinkedIn newsletter edition | YES | 2400x1260 |
| `newsletter_promo` | Short promo (text only) | NO | — |
| `post` | Plain text fallback | NO | — |

---

## Status Flow

```
draft → pending_review → approved → scheduled → posted
```

- **AI** creates items with status `draft`
- **Human** reviews and changes to `approved`
- **ContentRouter** picks up `scheduled` items at their `scheduled_at` time and posts them
- Status becomes `posted` after successful publish

---

## Schedule Times

| Eastern Time | UTC | Typical Use |
|---|---|---|
| 8:30 AM | 12:30 | Blog + newsletter + promo |
| 1:00 PM | 17:00 | Standalone #1 |
| 3:00 PM | 19:00 | Standalone #2 |
| 8:00 PM | 00:00 (next day) | Text post |

---

## Known Bugs

### content_type Normalization

The API normalizes `standalone` and `linkedin` content_type values to `post` on read. When you `POST /api/content` with `content_type: standalone`, a subsequent `GET` may show it as `content_type: post`. Your data is NOT lost — this is a display bug on the read path.

**Workaround**: Set `platform: "linkedin"` explicitly. Filter by platform to distinguish standalones.

### media_refs Extra Quotes

The `/api/uploads` endpoint sometimes wraps R2 keys in extra quotes. Always strip:

```python
media_refs = image_url.split(".r2.dev/")[1].strip('"')
if media_refs.startswith('"'):
    media_refs = media_refs[1:]
if media_refs.endswith('"'):
    media_refs = media_refs[:-1]
```

---

## Quick Reference Card

```
SOCIAL_ACCOUNT_ID = "a325193d-4a8e-40ba-ab20-c86b5a72f0b7"
BASE = "https://social.purebrain.ai"

# Auth (choose one)
POST /api/login → Bearer token
x-api-key: pb_live_* → Non-expiring API key

# CRUD
GET    /api/content/team?days=30     → List all team content
POST   /api/content                  → Create content item
PATCH  /api/content/{id}             → Update content item
DELETE /api/content/{id}             → Delete content item

# Media
POST   /api/uploads                  → Upload image → R2 key

# Blog Publishing
POST   /api/blog/publish             → Trigger auto-publisher

# Schedule (UTC)
12:30 = 8:30 AM ET (blog)
17:00 = 1:00 PM ET (standalone)
19:00 = 3:00 PM ET (standalone)
00:00 = 8:00 PM ET (text post)
```

---

*Version 3.0 — April 27, 2026. Merged from: social-purebrain-agent-SKILL v1.0, Tutorial Sections 1-4, Tutorial Sections 5-6, Tutorial Build Spec.*
