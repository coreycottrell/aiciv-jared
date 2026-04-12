---
name: content-creation-sop
description: How to create content for PureBrain -- writing, images, and quality gates. The creation playbook from ideation through approval. For distribution, filing, and engagement, see social-operations-guide.
trigger: content creation, blog post writing, LinkedIn post writing, image creation, creating content, content pipeline, quality gate, FLUX image, blog structure, post copy
agents: [3d-design-specialist, linkedin-writer, blogger, web-researcher, linkedin-researcher, dept-marketing-advertising, marketing-strategist, content-specialist]
---

# Content Creation SOP

## PURPOSE

This skill governs HOW to create content for PureBrain / Jared Sanborn. Ideation, research, writing, image generation, and quality gates live here.

For filing, distribution, scheduling, engagement, and tracking, load `social-operations-guide`.

**Ownership**: `dept-marketing-advertising` (CMO) owns this skill and delegates to specialist agents listed in the routing table below.

**Related Skills** (this SOP references but does NOT replace):
- `purebrain-social-design` -- visual standards, brand elements, dimensions
- `social-operations-guide` -- filing, distribution, engagement, tracking

**Google Drive Content Hub**: https://drive.google.com/drive/folders/12QBh5yVTppCo04jh5wrmhvZlqUxPIp71

---

## PHASE 1: IDEATION AND RESEARCH

### Where Ideas Come From

| Source | How | Frequency |
|--------|-----|-----------|
| Jared directive | Jared says "write about X" | Any time -- highest priority |
| Intel scan | WebSearch for AI news, industry trends | Every session |
| Blog backlog | Existing 30+ blog posts mapped to LinkedIn topics | Ongoing |
| Content calendar | Pre-planned topics in Google Drive | Weekly planning |
| Trending topics | LinkedIn trending, competitor posts, industry events | Daily |
| Customer conversations | Seed calls, onboarding insights, portal feedback | As they happen |
| Competitor analysis | What other AI companies are posting | Weekly |

### Research Process

1. **Invoke `web-researcher`** to run parallel research on the topic:
   - Find industry data and statistics (must be verifiable)
   - Map competitor positioning on the same topic
   - Surface recent news or developments (within 30 days)
2. **Invoke `linkedin-researcher`** to check what is trending on LinkedIn:
   - Identify which large accounts have posted on similar themes
   - Analyze engagement patterns (comments vs likes)
   - Run gap analysis: what angle has NOT been covered
3. File research output to Google Drive: `Content Training/` subfolder

### Topic Approval Gate

**HARD STOP**: No content moves to Phase 2 without Jared's approval on the topic.

- Present topic + angle + 1-sentence hook to Jared via portal
- Wait for explicit "yes" or direction change
- If Jared gives a topic directly, that IS the approval -- proceed to Phase 2

---

## PHASE 2: CONTENT CREATION

### 2A: Blog Post Writing

**Delegate to**: `blogger`
**Voice**: Aether (first-person AI perspective, thoughtful, direct)
**Length**: 800-1500 words

**Structure** (follow this order):
1. Hook (first 2 sentences must stop the scroll)
2. Core insight (the thing most people get wrong)
3. Framework or evidence (data, examples, patterns)
4. Practical takeaway (what the reader does tomorrow)
5. CTA to purebrain.ai/#awakening

**Rules -- enforce every one**:
- No em dashes. Use commas, colons, ellipsis, periods. Be creative.
- No AI tells: leverage, synergy, holistic, paradigm, etc.
- No proper names in transparency sections
- Must sound human, not corporate
- Blog styling per `blog-styling-rules.md` (4 mandatory features: 60% opacity bg, background video, collapsible FAQs, daily recap section)

**Blog Banner** (5 MANDATORY elements):
1. Hexagon logo
2. PUREBRAIN.ai wordmark (PUREBR=blue #2a93c1, AI=orange #f1420b, N=blue #2a93c1, .ai=white #ffffff)
3. Blog title text
4. "Awaken Your AI Partner Today"
5. "The Neural Feed -- a blog by Aether -- AI Partner for PureTechnology.ai"

**Blog banner dimensions**: 1200 x 630px (16:9 landscape)

### 2B: LinkedIn Post Writing

**Delegate to**: `linkedin-writer`
**Voice**: Jared Sanborn (first-person human, confident, slightly edgy, data-driven)
**Length**: Under 1300 characters (hard limit)

**Structure**:
1. **Hook** (lines 1-2): Pattern interrupt. Stop the scroll.
2. **Tension** (lines 3-5): What most people get wrong.
3. **Framework/Data** (body): The mechanism. The numbers. The story.
4. **CTA** (near end): Blog link if applicable.
5. **Question** (last line): Drive comments.

**Rules -- enforce every one**:
- No em dashes
- No AI tells
- Sound like Jared talking, not a marketing department
- Every post gets a branded image (see 2C)
- Hashtags: 3-5 max, relevant, not spammy

### 2C: Image Creation

**Delegate to**: `3d-design-specialist` ALWAYS. Never any other agent for images.

**Tool Chain**:
1. FLUX Pro base image via Replicate API (`tools/flux_image_gen.py`)
2. PIL composite with Oswald Bold font for text overlay
3. Brand elements composited per `purebrain-social-design` skill

**Dimensions by Platform**:

| Platform | Dimensions | Aspect |
|----------|-----------|--------|
| LinkedIn post | 1080 x 1350 px | 4:5 portrait |
| LinkedIn newsletter banner | 1200 x 628 px | ~2:1 landscape |
| Blog banner | 1200 x 630 px | 16:9 landscape |
| Bluesky | 1200 x 630 px | 16:9 landscape |

See `purebrain-social-design` skill for complete brand elements, color codes, and dimension details.

**MANDATORY Brand Elements on Every Image**:
- Hexagon logo (source: `/exports/cf-pages-deploy/investor-avatar/pt-hex-logo.png`)
- PUREBRAIN.ai wordmark (per-letter colors: PUREBR=#2a93c1, AI=#f1420b, N=#2a93c1, .ai=#ffffff)
- Font: Oswald Bold (verify via `font.getname()` -- MUST print "Oswald Bold" or fail)
- Dark navy background #080a12
- 80px safe zones on all edges
- Post-specific CTA on social images (NOT on blog/newsletter banners)

**Image Delivery**: Generate 3 options per post. Jared picks one.

**FLUX Prompt Style**: Futuristic, neural networks, glass/ethereal, volumetric lighting, crystal, cinematic window framing. Orange #f1420b and cerulean blue #2a93c1 accents. Pure black outside center frame.

### 2D: Audio Generation

**Tool**: `voice.purebrain.ai` (Chatterbox TTS, self-hosted)
**When**: After blog is finalized, before deploy
**Voice**: Aether voice (cloned)
**Output**: MP3 embedded in blog post. Never publish blog without audio.

---

## PHASE 3: PRE-APPROVAL FILING

**All content goes to Google Drive BEFORE sending to Jared for approval. No exceptions.**

### Per-Post Subfolder Structure

Every post gets its OWN subfolder. No flat filing.

```
Google Drive: LinkedIn Operations/
  YYYY-MM-DD -- [Post Title]/
    linkedin-[topic]-post-YYYY-MM-DD.md      (post text)
    linkedin-[topic]-YYYY-MM-DD-v1.png        (image option 1)
    linkedin-[topic]-YYYY-MM-DD-v2.png        (image option 2)
    linkedin-[topic]-YYYY-MM-DD-v3.png        (image option 3)
    flux-prompt.md                             (FLUX prompt used)
    post-details.md                            (metadata: status, links, metrics)
```

**Pending Approval folder**: `1Cr6EhkNi0ToBqQs27q0TQzKtCNDGeFwz`

### Portal Delivery to Jared

After filing to Drive, send to Jared via portal:
1. Copy files to `~/exports/portal-files/`
2. Message in portal with `[FILE: /home/jared/exports/portal-files/filename.ext]` for each file
3. Include post text in the message body for quick review
4. Include all 3 image options

---

## PHASE 4: APPROVAL

1. Jared reviews image options + post text in portal
2. Possible outcomes:
   - **Approved** -- proceed to publishing (see `social-operations-guide`)
   - **Revision needed** -- iterate (new image, rewrite text, change angle)
   - **Killed** -- archive and move on
3. **NEVER post without explicit Jared approval** (except Bluesky -- full autonomy)
4. **NEVER assume silence is approval** -- ask again if no response

| Content Type | What Needs Approval |
|-------------|-------------------|
| LinkedIn post | Image + post text |
| Blog post | Full article + banner |
| Newsletter | Article body + banner |
| Bluesky | Full autonomy (no approval needed) |

---

## PORTAL DELIVERY FORMAT (Locked 2026-04-05)

Every content package sent to Jared for approval MUST follow this exact format:

```
## LINKEDIN POST -- [Title] ([Date])

### IMAGE
[FILE: /home/jared/exports/portal-files/[image-filename].png]

### POST COPY (paste into LinkedIn composer)
[Full post text in a code block for easy copy-paste]

### FIRST COMMENT (drop immediately after posting)
[Exact text of the first comment with purebrain.ai link]

### REACTION ON OWN POST
[Which reaction to use: Celebrate/Love/Insightful]

---

## PRE/POST ENGAGEMENT PLAN
- **Before posting**: 2-3 Traveling Comments on [specific niche] accounts
- **After posting**: 2-3 more Traveling Comments on aligned accounts
- All comments use the formula: Pattern + Missing Layer + Smart Question
- All reactions: [specific reaction type] (never Like)
```

For blog packages, add:
- Blog article (full markdown or link to deployed draft)
- Blog banner image
- Newsletter promotional text (for the LinkedIn "Next" pop-up)
- Blog audio status

---

## IMAGE QUALITY GATE (HARD BLOCK)

**Cannot deliver content without passing every check. No exceptions.**

### Toolchain Requirement (Non-Negotiable)

Images MUST be created using ONE of these methods:
1. **FLUX Pro** via Replicate API (`tools/flux_image_gen.py`) + PIL composite -- PRIMARY
2. **Gemini 3 Pro Image** via Google API -- FALLBACK ONLY if FLUX unavailable
3. **Repurposed approved image** from the content image repurpose pool -- with new text overlay via PIL

### Never Acceptable

- Playwright/browser screenshot renders
- HTML-to-image conversions
- Basic PIL-only renders without FLUX/Gemini base
- Any image not created by `3d-design-specialist` agent
- Using `stroke_width` parameter on `draw.text()` -- causes garbled rendering with Oswald Bold. Use manual shadow offset instead (draw text twice: shadow at +2,+2 in dark color, then clean text on top)
- Arrow characters in CTAs -- no unicode arrows (causes garbled box), no `->` (looks cheap). CTAs must be natural sentences: "Secure your AI stack at purebrain.ai" or "Visit purebrain.ai"
- Heavy dark overlays that wash out the FLUX base art -- overlay should be MINIMAL. Use gradient overlay only where text appears (top zone for logo/title, bottom zone for CTA). Middle of image should have ZERO or near-zero overlay to showcase the FLUX artwork. Max opacity for text zones: 100-120 alpha (NOT 140-150)

### Repurpose Pool Check (Mandatory First Step)

Before generating any new FLUX image, check if an existing approved image can be repurposed:
- Check Google Drive content training folders for approved visuals
- Check `project_content_image_repurpose_pool.md` in memory
- Reusing approved FLUX backgrounds with new text overlay = faster + consistent quality

### Image Verification Checklist

Run every check. If ANY fails, do not deliver. Fix and re-verify.

- [ ] Created by `3d-design-specialist` agent (never any other agent)
- [ ] Base image is FLUX Pro, Gemini, or repurposed approved image (NEVER HTML render)
- [ ] Font is Oswald Bold (verified via `font.getname()` -- MUST print "Oswald Bold" or fail)
- [ ] Correct dimensions for platform (1080x1350 LinkedIn post, 1200x630 blog banner)
- [ ] PUREBRAIN.ai wordmark has correct per-letter colors (PUREBR=#2a93c1, AI=#f1420b, N=#2a93c1, .ai=#ffffff)
- [ ] Hexagon logo present and visible (source: `/exports/cf-pages-deploy/investor-avatar/pt-hex-logo.png`)
- [ ] 80px safe zones maintained on all edges
- [ ] Dark navy background #080a12 (no light backgrounds)
- [ ] Post-specific CTA present (social images only, not blog/newsletter banners)
- [ ] Text is readable (squint test passes)
- [ ] No off-brand colors (no purple, green, etc.)
- [ ] FLUX prompt saved to `flux-prompt.md` in the post subfolder

---

## COPY QUALITY GATE

Run before every delivery. Every check must pass.

- [ ] No em dashes anywhere in the text
- [ ] No AI tells (leverage, synergy, holistic, paradigm, etc.)
- [ ] Sounds human, not corporate
- [ ] Under 1300 characters for LinkedIn posts
- [ ] 800-1500 words for blog posts
- [ ] Hook in first 2 lines stops the scroll
- [ ] Ends with engagement question
- [ ] CTA present and correct

---

## AGENT ROUTING TABLE

| Task | Delegate To | NEVER |
|------|-------------|-------|
| All images and visuals | `3d-design-specialist` | Never MA#, never any other agent |
| LinkedIn post copy | `linkedin-writer` | |
| Blog post copy | `blogger` | |
| Topic research | `web-researcher` | |
| LinkedIn research | `linkedin-researcher` | |
| Marketing strategy | `marketing-strategist` | |
| Audio generation | Tools (`voice.purebrain.ai`) | |
| Blog deploy | Tools (`cf-deploy.py`) | |
| Campaign coordination | `dept-marketing-advertising` | |

---

## ANTI-PATTERNS (NEVER DO THESE)

1. **Never post without Jared's explicit approval** (except Bluesky)
2. **Never create images with any agent other than 3d-design-specialist**
3. **Never use em dashes** in any content
4. **Never post newsletter article AND separate standalone post** (they are ONE action via the promotional pop-up)
5. **Never skip Google Drive filing** -- file BEFORE approval
6. **Never exceed 1300 characters** on a LinkedIn post
7. **Never use light/white backgrounds** on any image
8. **Never use all-one-color wordmark** -- per-letter coloring is mandatory
9. **Never publish blog without audio** from voice.purebrain.ai
10. **Never assume silence is approval** -- ask again
11. **Never use WordPress** -- CF Pages is the only deploy target

---

## WEEKLY BATCH CREATION (Sunday)

Create ALL content for the upcoming week in one batch:

| Deliverable | Quantity | Filed To |
|-------------|----------|----------|
| Blog posts + newsletter versions | 7 (one per day) | Pending Approval |
| LinkedIn promotional posts (for each blog/newsletter) | 7 | Pending Approval |
| Bluesky threads (for each blog) | 7 | Pending Approval |
| Regular LinkedIn posts + Bluesky versions | 7-14 (1-2/day) | Pending Approval |
| Blog banner images (1200x630) | 7 | Pending Approval |
| LinkedIn post images (1080x1350) | 7-14 | Pending Approval |

All post text clipped into **Column F** of tracking spreadsheet. **Column G** = "Draft" (red).

For the full weekly engine lifecycle (Monday approval, daily autopilot, spreadsheet management, folder moves), see `social-operations-guide`.

---

## CONTENT TRAINING AND SKILL UPDATES

### When to Update Skills

- New visual standard discovered or locked in by Jared
- New posting flow confirmed
- New comment strategy insight from data
- New platform feature that changes workflow

### Skills That May Need Updates

| Skill | What It Governs |
|-------|----------------|
| `purebrain-social-design` | Visual standards, brand elements, dimensions |
| `content-creation-sop` | This document -- creation and quality gates |
| `social-operations-guide` | Filing, distribution, engagement, tracking |

### Training Folder in Google Drive

All training materials filed to: `LinkedIn Operations / Content Training/`
Includes: design training notes, FLUX prompt experiments, style guides, example outputs

### Feedback Loop

After every batch of content (weekly):
1. Review which posts performed best (impressions, comments, profile views)
2. Identify what worked (hook style, image style, topic, time posted)
3. Document patterns in `Content Training/` folder
4. Update skills if a new pattern is locked in by Jared
