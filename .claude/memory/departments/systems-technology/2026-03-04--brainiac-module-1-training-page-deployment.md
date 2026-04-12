# Brainiac Module 1 Training Page Deployment

**Date**: 2026-03-04
**Type**: deployment | pattern
**Topic**: Brainiac Module 1 embedded in training page + slug change

---

## What Was Done

1. **Created Module 1 child page** (WP ID: 1249)
   - URL: `https://purebrain.ai/brainiac-mastermind-training/brainiac-module-1-foundations/`
   - Parent page: 1115 (training)
   - Template: default (empty string) — NOT elementor_canvas
   - Content: Full `brainiac-module-1-presentation.html` wrapped in `<!-- wp:html -->`
   - 11-slide interactive presentation with keyboard/touch navigation

2. **Updated training page** (WP ID: 1115)
   - Slug changed: `training` → `brainiac-mastermind-training`
   - New URL: `https://purebrain.ai/brainiac-mastermind-training/`
   - Added "Brainiac Master Mind — Training Modules" section with CSS + HTML
   - Section placed BEFORE the `#lib-grid-wrap` video library div
   - Module 1 card: live, links to child page
   - Modules 2 & 3: placeholder cards (coming soon, Q2 2026)

3. **Created redirect page** (WP ID: 1251)
   - Slug: `training` (reclaimed)
   - Uses JS `window.location.replace()` + meta refresh to redirect to new URL
   - NOTE: Cloudflare was caching old 404 for /training/ — redirect will work once CF cache expires

4. **Cleared Elementor cache** after both deployments

---

## Key Technical Details

- Training page template: `elementor_canvas` (this one intentionally uses it — it's a full self-contained HTML app)
- Module 1 page template: `''` (default) — uses standard WP theme, full-page presentation with CSS overflow:hidden
- Training page password gate: `brainiac2026` — kept in place (Jared's clients use this)
- Training page content is pure JS/HTML app, not Elementor blocks
- TRAINING_VIDEOS array for video content, SECTIONS array for categories
- Modules section is a STATIC HTML section (not rendered by the existing JS system)

---

## CSS Classes Added to Training Page

```css
.modules-section-wrap   /* outer wrapper, max-width 1200px */
.modules-section-header /* title area */
.modules-eyebrow        /* orange "BRAINIAC MASTER MIND" label */
.modules-title          /* "Training Modules" h2 */
.modules-grid           /* auto-fill grid, minmax(320px, 1fr) */
.module-card            /* individual module card */
.module-coming          /* coming soon card variant (opacity 0.55) */
.module-num-badge       /* "MODULE 01" label */
.module-tag             /* category badge (blue) */
.module-tag-soon        /* coming soon badge (muted) */
.module-launch-btn      /* blue gradient CTA button → new tab */
.module-coming-badge    /* "Coming Soon" muted footer on card */
```

---

## Presentation File Source

`/home/jared/projects/AI-CIV/aether/exports/brainiac-module-1-presentation.html`
- 756 lines, 27402 bytes
- 11 slides, keyboard/touch/click navigation
- Fonts: Plus Jakarta Sans + Oswald (Google Fonts)
- Pure dark theme (#080a12) with PureBrain blue (#2a93c1) + orange (#f1420b)

---

## Patterns Learned

- **Slug change + old URL redirect**: WordPress doesn't auto-redirect on slug changes. Must create a new page at the old slug with JS redirect. Cloudflare may cache old 404 for hours — nothing to do but wait.
- **Child page URL**: Child pages take the parent's current slug in their path. If parent slug changes, child URLs update automatically.
- **Training page is a JS app**: The HTML page content is a full single-page app with password gate, video library, HLS streaming. Do NOT try to edit it with Elementor — it's all in the `<!-- wp:html -->` block.
- **Elementor cache must be cleared** after any page content update.
- **PureBrain WP credentials**: `PUREBRAIN_WP_USER` + `PUREBRAIN_WP_APP_PASSWORD` from `.env`

---

## Verification Results

| Check | Result |
|-------|--------|
| New slug /brainiac-mastermind-training/ | 200 OK |
| Modules section in page | PASS |
| Module 1 card present | PASS |
| Module 1 presentation page | 200 OK |
| Slideshow JS present | PASS |
| Password gate intact | PASS |
| Elementor cache cleared | PASS |
| /training/ redirect page created | Created (CF cache delay) |
