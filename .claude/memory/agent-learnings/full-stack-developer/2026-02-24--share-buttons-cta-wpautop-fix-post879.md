# Memory: Share Buttons Dark Theme Fix + CTA White Text + wpautop Wrapper — Post 879

**Date**: 2026-02-24
**Type**: teaching
**Topic**: Blog post share buttons wrong colors + CTA orange-on-orange invisible text — root cause + fix pattern

---

## Problems Fixed

### Problem 1: Share buttons showing as broken blue circles
- `pt-social-share` div inside post content had `border-radius: 50%` circle buttons
- CSS: `background: rgba(42, 147, 193, 0.15)` with `color: #2a93c1` = transparent blue circles
- wpautop was injecting `<br />` inside the `<a>` elements (between tag and `<svg>`)
- The `<br />` broke `inline-flex` layout causing taller-than-circle rendering

### Problem 2: CTA button orange-on-orange invisible text
- `.blog-cta-block .cta-btn` anchor had CSS `color: #ffffff !important` in scoped block
- But `#pb-agent-manager-post a { color: #f1420b !important }` was winning due to specificity fights with `!important`
- Fix: Added `style="color: #ffffff !important; -webkit-text-fill-color: #ffffff !important;"` inline on the `<a>` tag directly — inline beats any CSS `!important`

---

## Root Cause

Post 879 was stored WITHOUT a `<!-- wp:html -->` wrapper. WordPress applies wpautop to ALL post content by default, even when deployed via REST API.

wpautop injects `<br />` after newlines it detects between tags. Inside the share button HTML:
```html
<a href="..." aria-label="Share on LinkedIn">   ← newline here
<svg viewBox="0 0 24 24">...                     ← becomes <br /><svg...
```

The `<br />` before the `<svg>` makes the button taller than 44px, destroying the circle layout.

---

## Fixes Applied

### 1. Added `<!-- wp:html -->` wrapper
Wraps entire post content to bypass wpautop filter entirely.

### 2. Changed share buttons from circles to dark theme pills
```css
/* BEFORE: blue circles */
#pb-agent-manager-post .pt-social-share a {
  width: 44px; height: 44px; border-radius: 50%;
  background: rgba(42, 147, 193, 0.15);
  color: #2a93c1 !important;
}

/* AFTER: dark theme pills matching site aesthetic */
#pb-agent-manager-post .pt-social-share a {
  display: inline-flex !important;
  gap: 6px; padding: 8px 14px; border-radius: 6px;
  background: rgba(255,255,255,0.06) !important;
  color: rgba(255,255,255,0.85) !important;
  border: 1px solid rgba(255,255,255,0.12) !important;
}
#pb-agent-manager-post .pt-social-share a:hover {
  background: #f1420b !important;
  color: #ffffff !important;
}
```

### 3. Share buttons HTML on single line (no newlines inside anchors)
Replaced multiline anchor HTML with single-line HTML. No newlines = wpautop can't inject `<br />` even without wrapper. Defense in depth.

### 4. Added text labels to share buttons
LinkedIn, X, Email, Copy Link (with SVG icons + text = pill design). Added Copy Link button with JS clipboard fallback.

### 5. Inline white color on `.cta-btn`
```html
<!-- BEFORE -->
<a href="..." class="cta-btn">Start Your AI Partnership</a>

<!-- AFTER -->
<a href="..." class="cta-btn" style="color: #ffffff !important; -webkit-text-fill-color: #ffffff !important;">Start Your AI Partnership</a>
```

---

## Key Patterns

### Pattern: Always wrap HTML posts in wp:html
Any post with `<style>` blocks or complex HTML MUST use `<!-- wp:html -->` wrapper. Without it:
- CSS gets `</p>` injected inside `<style>` → orange fallback theme
- Newlines inside anchors get `<br />` → layout breaks

### Pattern: Inline style beats CSS !important
When CSS specificity fights are causing invisible text, adding `style="color: #ffffff !important"` inline on the element always wins. Inline style has highest specificity.

### Pattern: Single-line HTML for interactive elements
Share buttons, CTA links — put all HTML on one line inside the wp:html block.
wpautop only injects `<br />` at newlines; single-line = immune even without wrapper.

---

## Affected Post

| Site | Post ID | Slug |
|------|---------|------|
| purebrain.ai | 879 | your-next-direct-report-wont-be-human |

---

## Verification

All checks passed (raw content + rendered page):
- wp:html wrapper: PASS
- Dark pill buttons CSS: PASS
- No br injection in rendered share HTML: PASS
- CTA btn inline white: PASS
- pb-inline-cta white text: PASS
