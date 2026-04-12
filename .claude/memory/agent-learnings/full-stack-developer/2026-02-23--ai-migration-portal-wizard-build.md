# AI Migration Portal — 4-Step Wizard UI Build

**Date**: 2026-02-23
**Type**: operational + teaching
**Agent**: full-stack-developer

---

## What Was Built

Full 4-step migration wizard UI as self-contained HTML page.
Deployed to purebrain.ai as draft page ID 800, slug: `migrate`.

File: `/home/jared/projects/AI-CIV/aether/exports/migration-portal.html`
Size: 1905 lines, ~69KB

---

## Architecture

### Single-file approach
- All CSS inlined under `#pb-migration-portal` scope
- All JS in IIFE at bottom of file
- JSZip loaded via CDN (cdnjs.cloudflare.com)
- Google Fonts (Oswald) via CDN

### 4 Step Panels
- Only active panel visible (`display:none` / `.active` toggle)
- `goToStep(n)` function handles transitions + progress dot updates
- Smooth scroll-to-top on step change

### Step 1: Connect Accounts
- Drag-and-drop + click upload zones for ChatGPT ZIP and Claude files
- JSZip parses `conversations.json` + `user.json` from ChatGPT ZIP
- If JSZip fails or file is JSON-only, falls back to demo data gracefully
- Accordion "How to export" instructions per source
- Perplexity textarea + Midjourney text input (no API = manual capture)

### Step 2: Review Import
- Populates from parsed data OR demo data if no file uploaded
- Shows "Demo mode" banner if no file
- Each data category has Remove/Restore toggle
- Removed categories tracked in `state.removedCategories` Set
- Privacy note with link always visible above CTA

### Step 3: Processing Animation
- CSS animated orb (pulsing radial gradient + ring animation)
- Progress bar fills over ~9 seconds with shimmer effect
- Checklist items go `done` at scheduled timestamps
- Insight cards animate in with staggered delays (translateX + opacity)
- Insight text is personalized from real parsed data
- After 9.8s total: advances to step 4

### Step 4: Task Cards
- Generated from analysis results (real or demo)
- Tasks adapt based on: top topic, detected style, custom instructions, perplexity/midjourney data
- Max 4 cards shown
- All "Start this task" buttons → `https://purebrain.ai/#awakening`
- Migration Complete badge with real stats from parsed data

---

## ChatGPT ZIP Parser

```javascript
// Key fields in conversations.json:
conv.title         // conversation title (for topic extraction)
conv.create_time   // unix timestamp (for date range)
conv.mapping       // message nodes (for total count)

// user.json:
userObj.chat_settings.custom_instructions.about_user_message
userObj.chat_settings.custom_instructions.about_model_message
```

Topic extraction: split titles into words, filter stopwords (>4 chars, not in stopword set), count frequency.

---

## WordPress Deployment Pattern

```bash
WP_PASS=$(grep PUREBRAIN_WP_APP_PASSWORD .env | cut -d= -f2)
AUTH=$(echo -n "Aether:${WP_PASS}" | base64)
# Content must be JSON-stringified via python3 -c "import json; print(json.dumps(content))"
# Template: elementor_canvas
# Status: draft (security review required before publish)
```

Page ID: 800
URL when published: `https://purebrain.ai/migrate/`

---

## CSS Patterns Used (WordPress-safe)

```css
body.page { background-color: #080a12 !important; }
.site-header, .site-footer, ... { display: none !important; }
#pb-migration-portal { /* all CSS vars defined here */ }
#pb-migration-portal .class { /* all selectors scoped */ }
```

---

## Brand Colors

- Blue: `#2a93c1`
- Orange (CTA/primary): `#f1420b`
- Dark bg: `#080a12`
- Card bg: `#0e1120`
- Logo: PUREBR (blue) + AI (orange) + N (blue)

---

## Lessons

1. **Demo data graceful fallback is critical** — many users won't upload a file first. Show them the UI works with demo data so they understand the value before committing to upload.

2. **JSZip parsing the OpenAI ZIP**: The ZIP contains `conversations.json` (array of conversation objects) and `user.json` (custom instructions). Both must be extracted via `zip.file('filename').async('text')` returning a Promise.

3. **Staggered animation timing** for insight cards: 1200ms initial delay + 1800ms per card. This feels natural and "alive" rather than all at once.

4. **Topic extraction from titles**: Simple frequency count of words >4 chars, excluding stopwords. No NLP needed for MVP. Works surprisingly well for surfacing real usage patterns.

5. **CSS animation for orb**: `radial-gradient` + two keyframe animations (scale pulse + ring ring) creates convincing "processing" feel without canvas/WebGL.
