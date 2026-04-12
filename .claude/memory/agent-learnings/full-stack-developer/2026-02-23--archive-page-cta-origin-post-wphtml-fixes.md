# Archive Page CTA + Origin Post wp:html Fix

**Date**: 2026-02-23
**Agent**: full-stack-developer
**Type**: teaching
**Topic**: Archive page 700 CTA button added; posts 696 and 1180 wrapped in wp:html block

---

## Tasks Completed

### 1. Archive Page 700 CTA Button (purebrain.ai/blog-neural-feed-memories/)

**What was done**: Added "Start Your AI Partnership" CTA button to the static HTML of archive page 700.

**Insertion point**: After the `nfm-header` closing div, before the `<!-- GRID -->` comment:
```html
    </div>

    <!-- GRID -->
```
was replaced with:
```html
    </div>
    <!-- CTA div with orange button linking to #awakening -->

    <!-- GRID -->
```

**Button spec**:
- Background: `#f1420b` (orange)
- Text: `#ffffff` white, `!important`
- Hover: background changes to `#2a93c1` (blue) via `onmouseover`/`onmouseout`
- Link: `https://purebrain.ai/#awakening`
- Font: Oswald, uppercase, 700 weight

**Inline hover approach**: Used `onmouseover`/`onmouseout` JS attributes for hover because this page uses `elementor_canvas` template and there's no guaranteed external stylesheet for this specific element.

**Verification**:
- `Start Your AI Partnership` anchor found in live HTML
- `href` points to `#awakening`
- Orange `#f1420b` background present

---

### 2. Post 696 (purebrain.ai - Origin Story) wp:html Wrap

**What was done**:
1. Removed `<p><!-- Social Sharing Icons - Pure Tech Blue --></p>` artifact (wpautop wrapping HTML comment in `<p>` tags)
2. Wrapped entire post content in `<!-- wp:html --> ... <!-- /wp:html -->` block

**Why needed**: Without `<!-- wp:html -->`, WordPress's wpautop filter can inject `</p>` tags inside `<style>` blocks on certain versions/configurations. The wrap prevents all such corruption.

**Key insight**: Content can LOOK correct in `content.raw` and even in `content.rendered` while still having subtle wpautop artifacts (like `<p><!-- comment --></p>`). Always wrap with wp:html when deploying self-contained HTML with embedded `<style>` blocks.

**Verification**:
- All 3 CSS blocks present: `pb-transparency-cta-v394`, `pb-link-hover-v393`, `pb-origin-post-v1`
- No wpautop corruption (`</p></style>` not found in rendered)
- "every day" text confirmed (not "every week")
- Feb 22, 2026 transparency data confirmed (26 tasks, 21 agents, 2,016+ lines)

---

### 3. Post 1180 (jareddsanborn.com - Origin Story) wp:html + every day fix

**What was done**:
1. Fixed "every week" → "every day" in newsletter CTA text
2. Removed `<p><!-- Social Sharing Icons --></p>` artifact
3. Wrapped entire content in `<!-- wp:html --> ... <!-- /wp:html -->` block

**Verification**:
- All 3 CSS blocks present
- "every day" confirmed live
- Feb 22 transparency data confirmed

---

## Patterns Locked In

### wp:html Wrapping Rule (PERMANENT)
Every post/page with embedded `<style>` blocks deployed via REST API MUST be wrapped in:
```
<!-- wp:html -->
[all content]
<!-- /wp:html -->
```
Even if wpautop doesn't visibly corrupt the CSS, the `<p><!-- comment --></p>` artifact can still appear.

### Inline Hover for Archive-Style Pages
For pages using `elementor_canvas` without a blog post body class, use inline JS for hover states:
```html
onmouseover="this.style.background='#2a93c1';"
onmouseout="this.style.background='#f1420b';"
```

### Cache Behavior After REST API Update
- Elementor cache: `DELETE /wp-json/elementor/v1/cache` → 200 on PB, 404 on JDS
- Cloudflare CDN: Still caches aggressively - users need hard refresh
- REST API verify: Use `?context=edit` to get `content.raw` (unprocessed) vs `content.rendered` (processed)

---

## Files Referenced

- Page 700: `https://purebrain.ai/blog-neural-feed-memories/`
- Post 696: `https://purebrain.ai/we-both-wrote-this-post/`
- Post 1180: `https://jareddsanborn.com/2026/02/23/we-both-wrote-this-post/`
