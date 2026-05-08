# Content Creation SOP v2.0
## Pure Technology — Social Content Pipeline via social.purebrain.ai

**Date**: April 20, 2026
**Replaces**: Content Creation SOP v1.0 (Google Drive)
**Key Change**: All content now flows through social.purebrain.ai kanban for approval, not portal file delivery

---

## OVERVIEW

This SOP governs how content is created, branded, formatted, and submitted for approval. The entire workflow ends in social.purebrain.ai where Jared and the team review, approve, and schedule posts.

**Two content formats**:
1. **Standalone LinkedIn Posts** (1080x1350, 4:5 portrait) — locked in v4 format
2. **Blog/Newsletter Banners** (2400x1260, 16:9 landscape) — [pending final lock-in]

---

## PHASE 1: IDEATION & RESEARCH (Sunday)

### Sources
| Source | How | Priority |
|--------|-----|----------|
| Jared directive | "Write about X" | Highest |
| Blog backlog | 30+ existing blogs → promotional posts | High |
| Intel scan | AI news, industry trends (WebSearch) | Medium |
| Competitor analysis | What other AI companies post | Medium |
| Customer conversations | Portal feedback, seed calls | As they happen |

### Research Process
1. `web-researcher` → industry data, statistics, recent news (within 30 days)
2. `linkedin-researcher` → trending topics, engagement patterns, gap analysis
3. Combine into topic list with 1-sentence hooks

### Topic Approval
- If Jared gives topics → that IS the approval
- If AI-generated topics → present to Jared in portal, wait for explicit "yes"

---

## PHASE 2: WRITING

### 2A: LinkedIn Standalone Posts

**Voice**: Jared Sanborn (first-person, confident, data-driven, slightly edgy)
**Length**: Under 1300 characters
**Agent**: `linkedin-writer`

**Structure**:
1. **Hook** (1-2 sentences): Pattern interrupt. Stop the scroll.
2. **Tension**: What most people get wrong.
3. **Framework/Data**: The mechanism. The numbers. The story.
4. **CTA**: Blog link if applicable.
5. **Question** (last line): Drive comments.

**CRITICAL — Line Breaks (CONSTITUTIONAL)**:
- Every post MUST have proper paragraph spacing with `\n\n` between paragraphs
- Hook (1-2 sentences) → blank line → body paragraphs (1-2 sentences each) → blank line → CTA
- Numbered lists: each item gets its own line
- The post in social.purebrain.ai MUST preview exactly as it will appear on LinkedIn (WYSIWYG)
- No blob text. Ever.

**Rules**:
- No em dashes (use commas, colons, periods)
- No AI tells (leverage, synergy, holistic, paradigm)
- Sound human, not corporate
- 3-5 hashtags max

### 2B: Blog Posts

**Voice**: Aether (first-person AI, thoughtful, direct)
**Length**: 800-1500 words
**Agent**: `blogger`

**Structure**: Hook → Core insight → Framework/evidence → Practical takeaway → CTA
**Audio**: Generate via voice.purebrain.ai (Aether voice) before deploy
**Blog CTA Links** (every blog):
- LinkedIn: https://www.linkedin.com/company/purebrain-ai/
- Website: https://purebrain.ai/?ref=JAREDSB0

---

## PHASE 3: IMAGE CREATION

**Agent**: `3d-design-specialist` — ALWAYS. No exceptions.
**Tool**: FLUX Pro via Replicate API → PIL composite with Oswald Bold

### FORMAT A: Standalone LinkedIn Post (1080 x 1350)

**LOCKED — v4.2 Format (April 23, 2026)**

```
┌──────────────────────────────────┐
│  TOP BAR (140px, solid #080a12)  │
│     [Hex 80px] PUREBRAIN.AI      │
│     (side by side, centered)     │
│  ── blue accent line ──────────  │
├──────────────────────────────────┤
│                                  │
│      FLUX Pro Base Image         │
│                                  │
│       POST TITLE                 │
│       (centered, large,          │
│       stroke or shadow)          │
│                                  │
├──────────────────────────────────┤
│  ── blue accent line ──────────  │
│  BOT BAR (90px, solid #080a12)   │
│  PUREBRAIN.AI        CTA text    │
│  (left, white)    (right, orange)│
└──────────────────────────────────┘
```

**Top Bar Details**:
- Background: solid #080a12 (no transparency)
- Hex icon: 80px, full color from official PNG (`assets/pt-hex-icon-official.png`)
- Brand: PUREBR(#2a93c1) + AI(#f1420b) + N(#2a93c1) + .AI(white) — 46pt Oswald Bold
- Icon + wordmark side by side, horizontally centered as a unit
- **CRITICAL vertical alignment**: Use visual glyph bounds (textbbox) to align the text visual midline with the icon visual midline. PIL's default text positioning includes ascent padding that throws off centering. Calculate: `wm_y = bar_center - text_visual_top_offset - text_visual_height/2`
- Blue accent line (2px, #2a93c1) at bottom of bar

**Bottom Bar Details**:
- Background: solid #080a12 (no transparency)
- Blue accent line (2px, #2a93c1) at top of bar
- Left: PUREBRAIN.AI in brand colors, 26pt Oswald Bold
- Right: Custom CTA per post, ORANGE (#f1420b), 22pt Oswald Bold

**Image Area — Title Overlay (v4.2 LOCKED, April 23 2026)**:
- FLUX Pro base image, resized to fill space between bars
- Post TITLE overlaid CENTERED in the image area (vertically + horizontally)
- Title: 62pt Oswald Bold, white, centered
- Title readability — choose per image based on background contrast:
  - **STROKE**: 4px dark border (#080a12) around text — best for busy/colorful backgrounds
  - **SHADOW**: 4px radius black shadow behind text — best for darker/moodier backgrounds
  - Designer picks which treatment per image. Both are approved.
  - Squint test: if you can't read it with eyes half-closed, increase contrast
- Title wraps to 2-3 lines max (auto-size down if needed)
- NO dark backdrop box behind title (rejected April 23)

**Per-Post Custom Elements**:
- Title (derived from post hook/topic) — CENTERED on image
- CTA (unique per post — actionable, relevant) — in bottom bar

### FORMAT B: Blog/Newsletter Banner (2400 x 1260)

**LOCKED — Option D "Bottom Gradient" (April 20, 2026)**

```
┌──────────────────────────────────────────────┐
│                                              │
│  [Hex Icon] PUREBRAIN.AI  (upper-left)       │
│                                              │
│         FLUX Pro Base Image                  │
│         (top 50%+ fully visible)             │
│                                              │
│  ░░░░░░░ gradient starts here ░░░░░░░░░░░░░  │
│  ████████████████████████████████████████████ │
│  ██  Blog Title (large, Oswald Bold, white)██│
│  ██  "Awaken Your AI Partner Today" (orange)█│
│  ██  The Neural Feed footer (dim white)    ██│
│  ████████████████████████████████████████████ │
└──────────────────────────────────────────────┘
```

**Treatment**: Strong bottom gradient (bottom 50% darkened, 94% opacity at base)
- Title anchored at bottom-left in the dark zone
- Top 50%+ of image FULLY VISIBLE — preserves the art
- Gradient is gradual (not a hard cut)

**Backup treatments** (use when Option D isn't enough contrast):
- **Option C (Frosted Panel)**: Semi-transparent dark box behind text block. Modern, contained.
- **Option B (Text Stroke + Shadow)**: Soft shadow around text. No hard edges. Last resort only.
- **NEVER Option A (Gradient Overlay)**: Fades out too much of the artwork.

**5 Mandatory Elements**:
1. Hex icon + PUREBRAIN.AI wordmark (upper-left, brand colors)
2. Blog title (large, Oswald Bold, white, in the dark gradient zone)
3. "Awaken Your AI Partner Today" (orange, below title)
4. "The Neural Feed — A Blog by Aether — AI Partner for PureTechnology.ai" (footer, dim)
5. FLUX Pro base artwork (top 50%+ unobstructed)

**Same banner serves BOTH the blog post AND the LinkedIn newsletter** (one image, two uses).

---

## PHASE 4: UPLOAD TO social.purebrain.ai

**This replaces the old portal file delivery + Google Drive filing workflow.**

### Content Types in social.purebrain.ai

| Content Type | What It Is | Image Required | Format |
|-------------|-----------|----------------|--------|
| `standalone` | Regular LinkedIn post | YES — v4 standalone (1080x1350) | Text + image |
| `blog` | Blog post on purebrain.ai | YES — Option D banner (2400x1260) | Blog article text + banner |
| `newsletter` | LinkedIn newsletter | YES — SAME banner as blog | Newsletter text + banner |
| `newsletter_promo` | LinkedIn post promoting the newsletter | NO — text only | Promotional text, no image |

### Blog Content = 3 Listings (ALWAYS)

Every blog post creates THREE entries in social.purebrain.ai:

1. **Blog listing** (`content_type: blog`)
   - The actual blog article content
   - Uses Option D banner (2400x1260)
   - Links to purebrain.ai/blog/[slug]/

2. **Newsletter listing** (`content_type: newsletter`)
   - Same content adapted for LinkedIn newsletter format
   - Uses the SAME banner image as the blog (one image, two uses)
   - Published via LinkedIn newsletter "Next" button

3. **Newsletter promo** (`content_type: newsletter_promo`)
   - Short promotional LinkedIn post (text only, NO image)
   - Drives followers to read the newsletter
   - Example: "New on The Neural Feed: [Title]. The insight most people miss. Full post live now."

**The blog and newsletter share the same banner. The promo is text-only.**

### For Each Standalone Post:
1. Upload v4 image via `/api/uploads` → gets R2 URL
2. Create content item with `content_type: standalone`
3. Verify image displays and text previews correctly (WYSIWYG)

### For Each Blog:
1. Upload Option D banner via `/api/uploads` → gets R2 URL
2. Create 3 listings:
   - Blog (`content_type: blog`, same banner URL)
   - Newsletter (`content_type: newsletter`, same banner URL)
   - Newsletter promo (`content_type: newsletter_promo`, no image)
3. All 3 should have the same `scheduled_at` date (same day)

### Sunday Batch Upload:
- Create ALL posts for the week
- Standalones: 7-14 posts with v4 images
- Blogs: 7 blog packages (= 21 listings: 7 blog + 7 newsletter + 7 promo)
- All go into Column 1 (Pending Review) as drafts

### What Jared Sees:
- Kanban board with cards showing images
- Click any card → edit modal with:
  - Full post text (editable, with line breaks)
  - Live preview showing exactly how it looks on LinkedIn
  - Image preview
  - Schedule date/time
  - Approve / Reject buttons
- Jared drags approved cards to "Approved" column or changes status

---

## PHASE 5: APPROVAL & SCHEDULING

| Content Type | Approval Required | Where |
|-------------|-------------------|-------|
| LinkedIn standalone | Yes — Jared approves in social.purebrain.ai | Kanban |
| Blog post | Yes — full article + banner | Portal + kanban |
| Newsletter | Yes — article body + banner | Portal + kanban |
| Bluesky | No — full autonomy | Auto-post |

**Approval Flow**:
1. Jared reviews in social.purebrain.ai kanban
2. Clicks card → reviews text + image + preview
3. Changes status to "scheduled" (approved) or "rejected"
4. ContentRouter picks up scheduled posts at their scheduled_at time and posts via API

**NEVER post without explicit approval** (except Bluesky)
**NEVER assume silence is approval**

---

## IMAGE QUALITY GATE (HARD BLOCK)

Run every check. If ANY fails, fix before uploading.

### Toolchain (Non-Negotiable)
1. **FLUX Pro** via Replicate API → PIL composite — PRIMARY
2. **Gemini 3 Pro Image** — FALLBACK only
3. **Repurposed approved image** — with new PIL overlay

### Never Acceptable
- HTML-to-image renders / Playwright screenshots
- PIL-only renders without FLUX/Gemini base
- Any image not by `3d-design-specialist`
- `stroke_width` parameter (garbled with Oswald Bold — use manual shadow)
- Arrow characters in CTAs (unicode → garbled box, `->` → looks cheap)
- Light/white backgrounds

### Verification Checklist
- [ ] Created by `3d-design-specialist`
- [ ] FLUX Pro or Gemini base (never HTML render)
- [ ] Oswald Bold font (verified via `font.getname()`)
- [ ] Correct dimensions (1080x1350 standalone, 2400x1260 banner)
- [ ] Brand colors correct: PUREBR(blue) + AI(orange) + N(blue) + .AI(white)
- [ ] Hex icon present (official PNG, full color)
- [ ] Logo does NOT overlap main image content (80px min distance)
- [ ] Dark background #080a12
- [ ] CTA present and in orange (standalone only)
- [ ] Title readable (squint test)
- [ ] No off-brand colors
- [ ] Line breaks in post text (WYSIWYG preview matches LinkedIn)

---

## COPY QUALITY GATE

- [ ] No em dashes
- [ ] No AI tells
- [ ] Sounds human, not corporate
- [ ] Under 1300 characters (LinkedIn)
- [ ] Hook in first 2 lines
- [ ] Proper line breaks between paragraphs
- [ ] Ends with engagement question
- [ ] CTA present

---

## AGENT ROUTING TABLE

| Task | Delegate To | Never |
|------|-------------|-------|
| All images | `3d-design-specialist` | Never MA#, never other agents |
| LinkedIn post copy | `linkedin-writer` | |
| Blog post copy | `blogger` | |
| Topic research | `web-researcher` + `linkedin-researcher` | |
| Audio generation | `voice.purebrain.ai` | Never ElevenLabs |
| Campaign coordination | `dept-marketing-advertising` | |

---

## WEEKLY ENGINE (Sunday → Saturday)

### Sunday: Batch Creation
1. Research topics (Phase 1)
2. Write all posts with proper line breaks (Phase 2)
3. Generate FLUX images + PIL composite with v4 branding (Phase 3)
4. Upload everything to social.purebrain.ai kanban as drafts (Phase 4)

### Monday: Jared Approval
- Jared reviews kanban
- Approves, rejects, or requests revisions
- Approved posts move to "Approved" column with scheduled times

### Monday-Sunday: Autopilot
- ContentRouter posts approved content at scheduled times — every day of the week
- Team monitors engagement
- Traveling comments per linkedin-commenting-strategy

### Following Sunday: Review + Next Batch
- Review performance (impressions, comments, profile views)
- Identify what worked
- Create next week's batch

---

## ANTI-PATTERNS (NEVER DO THESE)

1. Never post without Jared's explicit approval (except Bluesky)
2. Never create images with any agent other than 3d-design-specialist
3. Never use em dashes
4. Never write posts as blob text without line breaks
5. Never skip social.purebrain.ai — ALL content goes through the kanban
6. Never exceed 1300 characters on LinkedIn
7. Never use light/white backgrounds
8. Never use all-one-color wordmark
9. Never publish blog without audio
10. Never assume silence is approval
11. Never use WordPress — CF Pages only
12. Never use ElevenLabs — voice.purebrain.ai only

---

## CHANGELOG

| Date | Change |
|------|--------|
| 2026-04-23 | v2.2: Standalone format LOCKED as v4.2 — title centered on image (stroke OR shadow, designer picks), top bar has 80px hex icon + 46pt wordmark side-by-side centered with visual-midline alignment, dark backdrop box REJECTED. |
| 2026-04-20 | v2.0: social.purebrain.ai replaces portal delivery. Standalone v4 locked. Banner Option D locked. Blog = 3 listings (blog + newsletter + promo). Line breaks constitutional. Official hex icon. |
| Pre-April 20 | v1.0: Original SOP with portal file delivery + Google Drive filing |


---

## BANNER TEXT SAFE ZONE (Added 2026-04-22 — CONSTITUTIONAL)

**Blog/Newsletter Banners (2400x1260):**
- ALL text and logos MUST be within x=150 to x=2250 (6% margin on each side)
- Logo/wordmark: minimum 150px from left edge
- Title text: minimum 150px from left edge
- Right-side elements: minimum 150px from right edge
- Bottom bar and gradient overlays CAN go edge-to-edge (decorative only)

**Why:** LinkedIn center-crops banner images. Text in the outer 6% gets cut off when the same banner is used as a LinkedIn article/newsletter cover.

**Standalone LinkedIn Posts (1080x1350):** NOT affected — portrait format, different crop behavior.

**This rule applies to:** ALL future blog banner generation via PIL/FLUX pipeline. Every blog banner prompt must include safe zone margins.
