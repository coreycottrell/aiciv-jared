# Media Upload + Tim Cook Image Injection + Pitch Page Deployment

**Date**: 2026-02-27
**Type**: operational + teaching
**Topic**: 3-task WordPress deployment — media library upload, page image injection, new page creation

---

## Task 1: Media Library Upload (3 images)

**Method**: `curl -F "file=@path" -F "title=Title" /wp-json/wp/v2/media`

**Results**:
- ID 997: amplify-founder-scaled.jpg → `https://purebrain.ai/wp-content/uploads/2026/02/amplify-founder-scaled.jpg`
- ID 998: vc-fomo-scaled.jpg → `https://purebrain.ai/wp-content/uploads/2026/02/vc-fomo-scaled.jpg`
- ID 999: vc-hero-scaled.jpg → `https://purebrain.ai/wp-content/uploads/2026/02/vc-hero-scaled.jpg`

**Gotcha**: WordPress auto-scales large PNGs and renames them `*-scaled.jpg`. The source_url returned differs from filename (e.g., `amplify-founder.png` → `amplify-founder-scaled.jpg`). Always fetch `source_url` from the media API response, don't guess the URL.

**Gotcha**: curl multipart upload sometimes returns empty response if the Python JSON parse runs too quickly. Use `RESULT=$(curl ...)` then inspect `$RESULT`, not pipe directly.

---

## Task 2: Tim Cook Page (993) Image Injection

**Method**: GET page with `?context=edit`, modify content string in Python, PUT back as JSON payload.

**Insertion logic**: Used Python `str.replace(marker, image_block + marker, 1)` to insert image divs before section comment markers.

**Image containers used**:
```html
<div style="width:100%;max-width:1200px;margin:60px auto;text-align:center;padding:0 24px;box-sizing:border-box;">
  <div class="tc-reveal" style="opacity:0;transform:translateY(30px);transition:all 0.8s ease;">
    <img src="URL" alt="Alt" style="width:100%;border-radius:16px;box-shadow:0 20px 60px rgba(0,0,0,0.4);display:block;">
  </div>
</div>
```

- `tc-reveal` class hooks into existing IntersectionObserver on the page (already in the JS)
- `max-width:1200px` keeps consistent with page sections
- `margin:60px auto` gives breathing room between sections

**Insertion points**:
- amplify-founder → before SECTION 2 comment (Hero → Problem bridge)
- vc-fomo → before SECTION 7 comment (Credibility → Closing CTA bridge)

---

## Task 3: Pitch Page Deployment (new page ID 1001)

**Method**: POST to `/wp-json/wp/v2/pages` with JSON payload.

**Settings**:
- title: "PureBrain — AI Executive Team for Founders"
- slug: "pitch"
- status: "publish"
- template: "elementor_canvas" (non-blog pages on purebrain.ai use this)
- Live URL: https://purebrain.ai/pitch/

**The pitch page file** (`exports/purebrain-pitch-page.html`) was already properly wrapped in `<!-- wp:html -->` / `<!-- /wp:html -->` from prior build session. No stripping needed.

**vc-hero.png insertion**: Added between HERO and COMPOUNDING CLOCK sections as full-width image with `border-radius:16px` and `box-shadow`.

---

## Teaching

**When inserting images into existing WP pages**: Read page first, find section comment markers, use Python string replace to inject at the right position. This is more reliable than trying to parse HTML structure.

**When creating new pages**: Always verify `template` is set correctly — elementor_canvas for non-blog purebrain.ai pages, default (empty string) for blog posts.

**JSON payload**: Write to `/tmp/payload.json` then use `curl -d @/tmp/payload.json` — avoids shell escaping issues with large HTML strings.
