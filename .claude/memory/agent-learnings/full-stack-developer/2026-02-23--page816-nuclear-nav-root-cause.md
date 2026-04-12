# Page 816 Nav Truncation - Root Cause & Nuclear Fix

**Date**: 2026-02-23
**Type**: teaching
**Page**: https://purebrain.ai/ai-website-analysis/ (WP page ID 816)

---

## Root Causes Found

### 1. WordPress Plugin CSS: `overflow-x: hidden` on `body`
File location: WordPress Additional CSS (plugin v3xx+)
The plugin injects:
```css
html, body {
    overflow-x: hidden !important;
    max-width: 100vw !important;
}
```
When `body` has `overflow-x: hidden`, browsers (especially Chrome/Safari) can create a new stacking context that clips `position:fixed` child elements. The nav text was getting clipped because the body itself was constraining viewport rendering.

### 2. onerror attribute curly-quote corruption
WordPress was converting straight quotes in `onerror="..."` attributes into curly/smart quotes (`&#8216;` = left single quote, `&#8221;` = right double quote). This broke the JS fallback but also the attribute parsing itself, potentially invalidating the img tag and creating unexpected rendering.

**Fix**: Removed onerror attribute entirely since the icon URL is reliable.

### 3. CSS classes being overridden despite !important
Previous approach used CSS classes like `.pb-blue`, `.pb-orange`, `.nav-cta` with heavy `!important` rules. Despite high specificity selectors, Astra theme and other plugin CSS was still winning in some cases.

---

## Nuclear Fix Applied

### Approach: 100% inline styles, zero CSS classes

**Before** (class-based, overridable):
```html
<nav id="pb-site-nav">
  <a class="nav-brand">
    <span class="nav-name">
      <span class="pb-blue">PUREBR</span>...
    </span>
  </a>
  <a class="nav-cta">Get Your Report</a>
</nav>
```

**After** (nuclear inline, not overridable):
```html
<div id="pb-site-nav" style="position:fixed!important;top:0!important;left:0!important;width:100vw!important;display:flex!important;...">
  <a href="https://purebrain.ai" style="display:flex!important;flex-shrink:0!important;white-space:nowrap!important;...">
    <img src="..." style="width:36px!important;height:36px!important;flex-shrink:0!important;...">
    <span style="font-family:Space Grotesk,...;white-space:nowrap!important;...">
      <span style="color:#2a93c1!important;display:inline!important;">PUREBR</span>
      <span style="color:#f1420b!important;display:inline!important;">AI</span>
      <span style="color:#2a93c1!important;display:inline!important;">N</span>
      <span style="color:#8a9ab8!important;...font-size:17px!important;">.ai</span>
    </span>
  </a>
  <a href="#order" style="background:#f1420b!important;color:#ffffff!important;display:inline-block!important;white-space:nowrap!important;flex-shrink:0!important;...">Get Your Report</a>
</div>
```

### Key inline style properties for nav robustness:
- `position:fixed!important` - anchors to viewport
- `width:100vw!important` - full viewport width
- `display:flex!important;flex-direction:row!important;flex-wrap:nowrap!important` - prevents wrapping
- `flex-shrink:0!important` on ALL children - prevents any child from shrinking
- `white-space:nowrap!important` on ALL text containers
- `overflow:visible!important` on ALL elements
- `z-index:2147483647!important` - maximum z-index
- `contain:none!important;clip:auto!important;clip-path:none!important` - defeats any clip context

### Fix script also added overflow-x override:
```javascript
html.style.setProperty('overflow-x', 'visible', 'important');
body.style.setProperty('overflow-x', 'visible', 'important');
```
This defeats the plugin's `overflow-x: hidden !important` at runtime.

---

## Deployment Details

**File**: `/home/jared/projects/AI-CIV/aether/exports/client-marketing/website-analysis/index.html`
**WP API**: `PUT /wp-json/wp/v2/pages/816` with full HTML as `content`
**Cache**: `DELETE /wp-json/elementor/v1/cache` after each deploy

## Verification Steps
1. Fetch live page with `Cache-Control: no-cache`
2. Check for `position:fixed!important;top:0!important;left:0!important` in response
3. Check for `Get Your Report` in response
4. Check for `PUREBR</span>`, `>AI<`, `>N<`, `.ai<` segments

---

## Key Lesson

**When CSS classes fail after 3+ attempts**: switch to 100% inline styles immediately.
Inline styles are the ONLY guarantee that WordPress/theme CSS cannot override them.
`!important` on inline styles beats `!important` on class-based rules every time.

**onerror attributes in WordPress**: WordPress content sanitization converts quotes in HTML attributes.
Avoid complex inline JS in HTML attributes. Use `<script>` tags instead.
