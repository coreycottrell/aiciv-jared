# PureBrain Branded Content Creation Skill v1.0

**Date**: April 23, 2026
**Status**: LOCKED (Constitutional)
**Purpose**: THE definitive skill for ANY AI on the team to create properly branded PureBrain content — writing, images, audio, everything.
**Owner**: dept-marketing-advertising (CMO)

---

## TABLE OF CONTENTS

1. [Part 1: Brand Identity](#part-1-brand-identity)
2. [Part 2: Writing Standards](#part-2-writing-standards)
3. [Part 3: Image Creation (Locked Formats)](#part-3-image-creation-locked-formats)
4. [Part 4: Content Types + Scheduling](#part-4-content-types--scheduling)
5. [Part 5: Quality Gates](#part-5-quality-gates)
6. [Part 6: Anti-Patterns](#part-6-anti-patterns)
7. [Part 7: Audio Narration](#part-7-audio-narration)

---

## PART 1: BRAND IDENTITY

### Core Colors

| Color | Hex | RGB | Usage |
|-------|-----|-----|-------|
| PT Blue | #2a93c1 | (42, 147, 193) | PUREBR, N, accent elements, accent lines |
| PT Orange | #f1420b | (241, 66, 11) | AI in wordmark, CTAs, energy accents |
| White | #ffffff | (255, 255, 255) | .ai, titles, body text |
| Dark Navy | #080a12 | (8, 10, 18) | PRIMARY background (all images, bars) |
| Light Gray | #e2e8f0 | (226, 232, 240) | Secondary/subline text |
| Mid Gray | #94a3b8 | (148, 163, 184) | Tertiary/footer text |

### PUREBRAIN.AI Wordmark (LOCKED - Non-Negotiable)

The wordmark is split into 4 color segments. This is constitutional and never varies:

| Segment | Color | Case |
|---------|-------|------|
| PUREBR | PT Blue (#2a93c1) | UPPERCASE |
| AI | PT Orange (#f1420b) | UPPERCASE |
| N | PT Blue (#2a93c1) | UPPERCASE |
| .AI or .ai | White (#ffffff) | Context-dependent (uppercase in bars, lowercase in body) |

**NEVER**:
- Render the wordmark in a single color
- Make .ai orange (it is ALWAYS white)
- Split differently (e.g., PURE + BRAIN is wrong — it is PUREBR + AI + N + .ai)

### Hexagon Logo

- Asset path: `assets/pt-hex-icon-official.png`
- Must appear on EVERY branded image
- Minimum size: 60px on social, 80px on blog banners
- Full color from official PNG (never grayscale, never recolored)

### Font

- **Oswald Bold** — the ONLY font for image text
- Verify with `font.getname()` — must return "Oswald" family
- Install: `wget -O ~/.fonts/Oswald-Bold.ttf "https://github.com/googlefonts/OswaldFont/raw/main/fonts/ttf/Oswald-Bold.ttf" && fc-cache -fv`

### Background Rule

- Always dark: #080a12 (dark navy) for all branded content
- NEVER use light/white backgrounds
- NEVER use purple, green, or off-brand accent colors

### Logo Composition Rules

- Icon + wordmark always side by side (icon left, wordmark right)
- They form ONE unit that is then positioned/centered together
- Vertical alignment uses textbbox visual glyph bounds — align text visual midline with icon visual midline
- Minimum 80px breathing room from edges

---

## PART 2: WRITING STANDARDS

### Voice: LinkedIn Standalone Posts

**Voice**: Jared Sanborn (first-person, confident, data-driven, slightly edgy)
**Agent**: `linkedin-writer`
**Length**: Under 1300 characters (HARD LIMIT)

**Structure**:
1. **Hook** (1-2 sentences): Pattern interrupt. Stop the scroll.
2. **Tension**: What most people get wrong.
3. **Framework/Data**: The mechanism. The numbers. The story.
4. **CTA**: Blog link if applicable.
5. **Question** (last line): Drive comments. End with an engagement question.

**Hashtags**: 3-5 per post, at the very end.

### Voice: Blog Posts

**Voice**: Aether (first-person AI, thoughtful, direct)
**Agent**: `blogger`
**Length**: 800-1500 words

**Structure**: Hook → Core insight → Framework/evidence → Practical takeaway → CTA

**Blog CTA Links (every blog)**:
- LinkedIn: https://www.linkedin.com/company/purebrain-ai/
- Website: https://purebrain.ai/?ref=JAREDSB0

**Blog post footer CTA (mandatory)**:
```html
<hr>
<p><strong>Ready to awaken your AI partner?</strong> <a href="https://purebrain.ai">Begin the process at PureBrain.ai</a></p>
<p>And if this perspective was valuable, <a href="https://www.linkedin.com/build-relation/newsletter-follow?entityUrn=7428125791609192449">subscribe to our newsletter</a> where I share insights on building AI relationships every week.</p>
```

### Line Breaks (CONSTITUTIONAL — WYSIWYG Rule)

- Every post MUST have proper paragraph spacing with `\n\n` between paragraphs
- Hook (1-2 sentences) → blank line → body paragraphs (1-2 sentences each) → blank line → CTA
- Numbered lists: each item gets its own line
- The post in social.purebrain.ai MUST preview exactly as it will appear on LinkedIn
- **No blob text. Ever.**

### Writing Rules (ALL Content)

| Rule | Details |
|------|---------|
| No em dashes | Use commas, colons, periods instead |
| No AI tells | Banned: leverage, synergy, holistic, paradigm, delve, tapestry, landscape |
| Sound human | Not corporate, not robotic |
| Hook first | First 2 lines must stop the scroll |
| Engagement question | Every LinkedIn post ends with a question |
| CTA present | Every piece drives somewhere |

### Comment Writing (Traveling Comments)

- Under 100 words
- No em dashes, no AI tells
- Structure: Pattern (what you noticed) → Missing Layer (dimension not covered) → Smart Question (makes poster reply)
- Navigate via direct profiles: `/in/{handle}/recent-activity/all/` — NEVER /notifications/
- 90-second spacing between comments minimum

---

## PART 3: IMAGE CREATION (LOCKED FORMATS)

### Agent Rule (CONSTITUTIONAL)

**ALL images created by `3d-design-specialist` — ALWAYS. No exceptions.**
Never MA#, never other agents, never self-generate.

### Tool Chain (Non-Negotiable)

```
Step 1: Generate base image → FLUX Pro via Replicate API (PRIMARY) or Gemini 3 Pro Image (FALLBACK)
Step 2: Composite with PIL/Pillow → text, logos, brand elements via Oswald Bold
Step 3: Self-review → mandatory visual inspection checklist
Step 4: Export at correct dimensions
```

**CRITICAL**: ALWAYS save raw FLUX output as `{name}-flux-raw.png` (constitutional rule). Text edits = rebuild from raw FLUX background, NEVER paint over existing text.

### FLUX Prompt Suffixes (Brand Presets)

**For LinkedIn Posts (4:5)**:
```
"cinematic window framing, photorealistic, orange #f1420b and cerulean blue #2a93c1 volumetric lighting, dark navy background #080a12, glass elements, depth of field, professional, [YOUR SUBJECT HERE]"
```

**For Blog Banners (16:9)**:
```
"dark navy background #080a12, futuristic neural network aesthetic, volumetric lighting, glass ethereal elements, cinematic window framing, orange #f1420b and cerulean blue #2a93c1 accent lighting, pure black outside center frame, professional tech visualization, [YOUR SUBJECT HERE]"
```

---

### FORMAT A: v4.2 Standalone LinkedIn Post (1080 x 1350) — LOCKED April 23, 2026

```
+----------------------------------+
|  TOP BAR (140px, solid #080a12)  |
|     [Hex 80px] PUREBRAIN.AI     |
|     (side by side, CENTERED)     |
|  -- blue accent line (2px) ---   |
+----------------------------------+
|                                  |
|      FLUX Pro Base Image         |
|                                  |
|       POST TITLE                 |
|       (centered, 62pt,           |
|       stroke OR shadow)          |
|                                  |
+----------------------------------+
|  -- blue accent line (2px) ---   |
|  BOT BAR (90px, solid #080a12)   |
|  PUREBRAIN.AI       CTA text     |
|  (left, 26pt)    (right, orange) |
+----------------------------------+
```

**Top Bar (140px)**:
- Background: solid #080a12 (no transparency)
- Hex icon: 80px, full color from official PNG
- Wordmark: PUREBR(#2a93c1) + AI(#f1420b) + N(#2a93c1) + .AI(white) — 46pt Oswald Bold
- Icon + wordmark side by side, horizontally CENTERED as a unit
- **CRITICAL vertical alignment**: Use `textbbox` visual glyph bounds. Calculate: `wm_y = bar_center - text_visual_top_offset - text_visual_height/2`. PIL default text positioning includes ascent padding that throws off centering.
- Blue accent line: 2px, #2a93c1, at bottom of top bar

**Image Area**:
- FLUX Pro base image, resized to fill space between bars
- Post TITLE overlaid CENTERED (vertically + horizontally)
- Title: 62pt Oswald Bold, white, centered
- Title readability — designer picks PER IMAGE:
  - **STROKE**: 4px dark border (#080a12) around text — best for busy/colorful backgrounds
  - **SHADOW**: 4px radius black shadow behind text — best for darker/moodier backgrounds
- **Squint test**: if you can't read it with eyes half-closed, increase contrast
- Title wraps to 2-3 lines max (auto-size down if needed)
- **NO dark backdrop box behind title** (rejected April 23)

**Bottom Bar (90px)**:
- Background: solid #080a12 (no transparency)
- Blue accent line: 2px, #2a93c1, at top of bottom bar
- Left: PUREBRAIN.AI in brand colors, 26pt Oswald Bold
- Right: Custom CTA per post, ORANGE (#f1420b), 22pt Oswald Bold

**Per-Post Custom Elements**:
- Title (derived from post hook/topic) — CENTERED on image
- CTA (unique per post — actionable, relevant) — in bottom bar

**CTA Examples**:
| Post Topic | CTA |
|------------|-----|
| AI agents failing | Stop losing AI projects |
| Memory layer | Your AI should remember you |
| AI partnership | Meet your AI partner |
| ROI of AI | Get measurable AI ROI |

---

### FORMAT B: Option D Blog/Newsletter Banner (2400 x 1260) — LOCKED April 20, 2026

```
+----------------------------------------------+
|                                              |
|  [Hex Icon] PUREBRAIN.AI  (upper-left)       |
|                                              |
|         FLUX Pro Base Image                  |
|         (top 50%+ fully visible)             |
|                                              |
|  ░░░░░░░ gradient starts here ░░░░░░░░░░░░  |
|  ████████████████████████████████████████████|
|  ██  Blog Title (large, Oswald Bold, white)██|
|  ██  "Awaken Your AI Partner Today" (orange)█|
|  ██  The Neural Feed footer (dim white)    ██|
|  ████████████████████████████████████████████|
+----------------------------------------------+
```

**Treatment**: Strong bottom gradient (bottom 50% darkened, 94% opacity at base)
- Title anchored in the dark gradient zone
- Top 50%+ of image FULLY VISIBLE — preserves the art
- Gradient is gradual (not a hard cut)

**5 Mandatory Elements**:
1. Hex icon + PUREBRAIN.AI wordmark (upper-left, brand colors)
2. Blog title (large, Oswald Bold, white, in the dark gradient zone)
3. "Awaken Your AI Partner Today" (orange #f1420b, below title)
4. "The Neural Feed — A Blog by Aether — AI Partner for PureTechnology.ai" (footer, dim white)
5. FLUX Pro base artwork (top 50%+ unobstructed)

**Safe Zone (CONSTITUTIONAL)**:
- ALL text and logos MUST be within x=150 to x=2250 (6% margin on each side)
- Logo/wordmark: minimum 150px from left edge
- Title text: minimum 150px from left edge
- Right-side elements: minimum 150px from right edge
- Bottom bar and gradient overlays CAN go edge-to-edge (decorative only)
- **Why**: LinkedIn center-crops banner images. Text in the outer 6% gets cut off.

**Backup Treatments** (when Option D doesn't provide enough contrast):
- **Option C (Frosted Panel)**: Semi-transparent dark box behind text block. Modern, contained.
- **Option B (Text Stroke + Shadow)**: Soft shadow around text. No hard edges. Last resort.
- **NEVER Option A (Gradient Overlay)**: Fades out too much artwork.

**Same banner serves BOTH the blog post AND the LinkedIn newsletter** (one image, two uses).

---

### Platform Dimensions Reference

| Platform | Dimensions (px) | Aspect Ratio | 2K Version |
|----------|-----------------|--------------|------------|
| LinkedIn standalone post | 1080 x 1350 | 4:5 portrait | 2160 x 2700 |
| Blog/Newsletter banner | 2400 x 1260 | ~16:9 landscape | (already 2K) |
| Bluesky post | 1080 x 1080 or 1200x630 | 1:1 or 16:9 | 2160 x 2160 |

**ALL images 2K minimum**: Banners=2400x1260, Standalone=2160x2700 (or 1080x1350 minimum). No exceptions.

---

### PIL Compositing Code Reference

```python
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

# Brand colors
PT_BLUE = (42, 147, 193)       # #2a93c1
PT_ORANGE = (241, 66, 11)      # #f1420b
PT_WHITE = (255, 255, 255)     # #ffffff
PT_DARK = (8, 10, 18)          # #080a12
LIGHT_GRAY = (226, 232, 240)   # #e2e8f0

def load_oswald_bold(size):
    """Load Oswald Bold font at given size."""
    font_paths = [
        Path.home() / ".fonts/Oswald-Bold.ttf",
        Path("/usr/share/fonts/truetype/oswald/Oswald-Bold.ttf"),
    ]
    for p in font_paths:
        if p.exists():
            font = ImageFont.truetype(str(p), size)
            name = font.getname()
            if "Oswald" in name[0]:
                return font
    raise FileNotFoundError("Oswald-Bold.ttf not found. Install it first.")


def draw_purebrain_wordmark(draw, x, y, font_size=36):
    """Draw the PUREBRAIN.AI wordmark with correct per-letter colors."""
    font = load_oswald_bold(font_size)
    segments = [
        ("PUREBR", PT_BLUE),
        ("AI", PT_ORANGE),
        ("N", PT_BLUE),
        (".AI", PT_WHITE),
    ]
    cursor_x = x
    for text, color in segments:
        draw.text((cursor_x + 2, y + 2), text, font=font, fill=(0, 0, 0, 180))
        draw.text((cursor_x, y), text, font=font, fill=color)
        bbox = font.getbbox(text)
        cursor_x += bbox[2] - bbox[0]


def add_gradient_overlay(img, top_opacity=0.0, bottom_opacity=0.94):
    """Add dark gradient overlay for text readability (stronger at bottom)."""
    overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    width, height = img.size
    for y_pos in range(height):
        progress = y_pos / height
        alpha = int(255 * (top_opacity + (bottom_opacity - top_opacity) * progress))
        draw.line([(0, y_pos), (width, y_pos)], fill=(8, 10, 18, alpha))
    return Image.alpha_composite(img.convert('RGBA'), overlay)
```

### FLUX Model Options

| Model | Speed | Quality | Cost |
|-------|-------|---------|------|
| `flux-pro` | ~6s | Highest | ~$0.015+/MP |
| `flux-dev` | ~2.5s | High | ~$0.012/MP |
| `flux-schnell` | ~1s | Good | Cheapest |

---

## PART 4: CONTENT TYPES + SCHEDULING

### Content Types

| Type | Description | Image Required | Format |
|------|-------------|----------------|--------|
| `standalone` | Regular LinkedIn post | YES — v4.2 (1080x1350) | Text + image |
| `blog` | Blog post on purebrain.ai | YES — Option D banner (2400x1260) | Article + banner |
| `newsletter` | LinkedIn newsletter | YES — SAME banner as blog | Newsletter text + banner |
| `newsletter_promo` | LinkedIn post promoting newsletter | NO — text only | Promotional text |
| `bluesky` | Bluesky post/thread | Optional | Full autonomy |

### Blog Package = 3 Listings (ALWAYS Together)

Every blog post creates THREE entries in social.purebrain.ai:

1. **Blog listing** (`content_type: blog`) — The actual article + Option D banner
2. **Newsletter listing** (`content_type: newsletter`) — Same content for LinkedIn newsletter + SAME banner
3. **Newsletter promo** (`content_type: newsletter_promo`) — Short promotional LinkedIn post (text only, NO image)

**The blog and newsletter share the same banner. The promo is text-only.**

### Daily Schedule (Eastern Time)

| Time (ET) | UTC | Content |
|-----------|-----|---------|
| 8:30 AM | 12:30 | Blog package (blog + newsletter + newsletter_promo) |
| 1:00 PM | 17:00 | Standalone LinkedIn post #1 |
| 3:00 PM | 19:00 | Standalone LinkedIn post #2 |
| 8:00 PM | 00:00+1 | Text-only post (no image) |

### Weekly Engine

| Day | Action |
|-----|--------|
| **Sunday** | Batch creation: research, write all posts, generate all images, upload everything to social.purebrain.ai kanban as drafts |
| **Monday AM** | Jared reviews kanban, approves/rejects/revises |
| **Mon-Sun** | ContentRouter posts approved content at scheduled times automatically |
| **Following Sunday** | Review performance, identify what worked, create next batch |

### Approval Flow

- ALL content goes through social.purebrain.ai kanban
- Jared reviews cards (text + image + preview)
- Changes status to "scheduled" (approved) or "rejected"
- **NEVER post without explicit approval** (except Bluesky)
- **NEVER assume silence is approval**

---

## PART 5: QUALITY GATES

### Image Quality Checklist (HARD BLOCK — Fix Before Upload)

- [ ] Created by `3d-design-specialist`
- [ ] FLUX Pro or Gemini base image (never HTML render, never PIL-only)
- [ ] Oswald Bold font verified via `font.getname()`
- [ ] Correct dimensions (1080x1350 standalone OR 2400x1260 banner)
- [ ] Brand colors correct: PUREBR(blue) + AI(orange) + N(blue) + .AI(white)
- [ ] Hex icon present (official PNG, full color, not recolored)
- [ ] Logo does NOT overlap main image content (80px minimum distance)
- [ ] Dark background #080a12 (no white/light)
- [ ] CTA present and in orange (standalone bottom bar)
- [ ] Title readable (squint test — eyes half-closed, still legible)
- [ ] No off-brand colors (no purple, green, etc.)
- [ ] Blue accent lines present (2px, #2a93c1)
- [ ] Safe zone respected (banner: x=150 to x=2250)
- [ ] Raw FLUX saved as `{name}-flux-raw.png`

### Copy Quality Checklist (HARD BLOCK)

- [ ] No em dashes
- [ ] No AI tells (leverage, synergy, holistic, paradigm, delve, tapestry)
- [ ] Sounds human, not corporate
- [ ] Under 1300 characters (LinkedIn posts)
- [ ] Hook in first 2 lines (pattern interrupt)
- [ ] Proper `\n\n` line breaks between paragraphs (WYSIWYG)
- [ ] Ends with engagement question
- [ ] CTA present
- [ ] 3-5 hashtags (LinkedIn)

### Image Self-Review Template (MANDATORY Before Completion)

```
## IMAGE SELF-REVIEW: [filename]

**What I See**:
- Main elements: [describe composition]
- Colors: [describe palette]
- TEXT/LABELS PRESENT: [list ANY text visible]

**Brand Compliance**:
- [ ] Hexagon logo present and visible
- [ ] PUREBRAIN.AI wordmark colors correct
- [ ] Dark background
- [ ] Text readable at 50% zoom
- [ ] Correct dimensions
- [ ] CTA present (standalone)

**Verdict**: [APPROVED / NEEDS REDO]
```

---

## PART 6: ANTI-PATTERNS (COMPLETE "NEVER DO" LIST)

### Image Anti-Patterns

| Never | Why |
|-------|-----|
| HTML-to-image renders / Playwright screenshots | Not production quality |
| PIL-only renders without FLUX/Gemini base | Looks flat and amateur |
| Any image NOT by `3d-design-specialist` | Agent specialization is constitutional |
| `stroke_width` PIL parameter | Garbles with Oswald Bold — use manual shadow loop |
| Arrow characters in CTAs (unicode arrows, `->`) | Unicode renders as garbled box, `->` looks cheap |
| Light/white backgrounds | Brand is DARK |
| All-one-color wordmark | Must be multi-color PUREBR+AI+N+.ai |
| Purple, green, or off-brand accents | Only blue #2a93c1 and orange #f1420b |
| Paint over existing text | Rebuild from flux-raw.png instead |
| Dark backdrop box behind title (standalone) | Rejected April 23, 2026 |
| Missing hex icon | Constitutional — must appear on every branded image |
| Text within 80px of edges | Mobile crop safety zone |

### Writing Anti-Patterns

| Never | Why |
|-------|-----|
| Em dashes | Not Jared's voice |
| AI tells (leverage, synergy, holistic, paradigm, delve) | Sounds robotic |
| Blob text without line breaks | Fails WYSIWYG rule |
| Exceed 1300 chars on LinkedIn | Gets truncated |
| Post without engagement question | Misses comment opportunity |
| Separate standalone post for newsletter promo | Newsletter + promo are ONE publishing action |
| Skip social.purebrain.ai kanban | ALL content goes through it |
| Post without explicit Jared approval (except Bluesky) | Constitutional |
| Assume silence is approval | Must be explicit "yes" |

### Operations Anti-Patterns

| Never | Why |
|-------|-----|
| Use ElevenLabs for audio | BANNED — voice.purebrain.ai only |
| Use WordPress | CF Pages only |
| Skip pre-post comments | Algorithm warm-up is not optional |
| Skip first comment with blog link | This drives traffic |
| Exceed 25 comments/day | LinkedIn rate limits |
| Use Like reaction | Rotate Insightful/Celebrate/Love/Support |
| Comment via /notifications/ | Use direct profile `/in/{handle}/recent-activity/all/` |
| Flat-file content in Drive | Every post gets its own subfolder |
| Leave Column G outdated | Draft/Final/Live must reflect reality |
| Skip Google Drive folder move on publish | Content must move from Pending to Live |

---

## PART 7: AUDIO NARRATION (PureBrain Exclusive)

### Generation

- **Tool**: voice.purebrain.ai (GPU server at 37.27.237.109:8950, Chatterbox model)
- **Voice**: `aether` — this is Aether's voice, used for ALL Aether-branded content
- **Exception**: Use `chy` voice ONLY for content specifically from/for Chy
- **BANNED**: ElevenLabs. NEVER use rented TTS services.

### Workflow

1. Blog article finalized (HTML ready)
2. Preprocess through `clean_for_speech()` pronunciation guide
3. Generate audio via voice.purebrain.ai with `aether` voice
4. Embed audio player in blog post
5. Blog audio auto-generates on publish (two-step: HTML first, audio follows)

### Pronunciation Guide (50+ Rules — Key Examples)

| Written | Spoken |
|---------|--------|
| Aether | ae-ther |
| PureBrain | Pure Brain |
| AI | A I |
| SaaS | sass |
| API | A P I |
| URL | U R L |
| SEO | S E O |
| CTA | C T A |
| ROI | R O I |
| i.e. | that is |
| e.g. | for example |
| etc. | et cetera |
| vs. | versus |
| purebrain.ai | pure brain dot A I |

### Audio Filing

All TTS/voice work filed to Google Drive folder: `1kNB9L7ohiNMyDbfir0uWe-kjgMbvevaJ`

---

## AGENT ROUTING TABLE (Who Does What)

| Task | Delegate To | NEVER |
|------|-------------|-------|
| ALL images | `3d-design-specialist` | Never MA#, never other agents |
| LinkedIn post copy | `linkedin-writer` | |
| Blog post copy | `blogger` | |
| Topic research | `web-researcher` + `linkedin-researcher` | |
| Audio generation | voice.purebrain.ai | Never ElevenLabs |
| Campaign coordination | `dept-marketing-advertising` | |
| Comment execution | `linkedin-specialist` via scheduler | |
| Post publishing | `linkedin-specialist` or direct tool | |
| Social dashboard | `social-media-specialist` | |

---

## QUICK REFERENCE: DIMENSIONS

| Content | Width | Height | Ratio |
|---------|-------|--------|-------|
| LinkedIn standalone | 1080 | 1350 | 4:5 |
| LinkedIn standalone (2K) | 2160 | 2700 | 4:5 |
| Blog/newsletter banner | 2400 | 1260 | ~16:9 |
| Bluesky | 1080 | 1080 | 1:1 |

---

## QUICK REFERENCE: FONT SIZES (Standalone v4.2)

| Element | Size | Font |
|---------|------|------|
| Top bar wordmark | 46pt | Oswald Bold |
| Image title | 62pt | Oswald Bold |
| Bottom bar wordmark | 26pt | Oswald Bold |
| Bottom bar CTA | 22pt | Oswald Bold |

---

## SETUP REQUIREMENTS

### Python Dependencies

```bash
pip install Pillow replicate requests httpx google-genai
```

### Font Installation

```bash
mkdir -p ~/.fonts
wget -O ~/.fonts/Oswald-Bold.ttf "https://github.com/googlefonts/OswaldFont/raw/main/fonts/ttf/Oswald-Bold.ttf"
fc-cache -fv
```

### API Keys Needed

| Key | Purpose |
|-----|---------|
| `REPLICATE_API_TOKEN` | FLUX Pro image generation |
| `GOOGLE_API_KEY` | Gemini 3 Pro Image (fallback) |

### Assets Needed

- `assets/pt-hex-icon-official.png` — PureBrain hexagon logo (transparent background)
- Oswald Bold font (installed per above)

---

## CHANGELOG

| Date | Change |
|------|--------|
| 2026-04-23 | v1.0: Initial merged skill combining Content Creation SOP v2.2, Social Operations Guide, and Design Skill Package into one definitive document. |

---

**END OF SKILL**

This document is the single source of truth for PureBrain branded content creation. Any AI on the team reads this ONE document to know how to create properly branded content — writing, images, audio, everything.
