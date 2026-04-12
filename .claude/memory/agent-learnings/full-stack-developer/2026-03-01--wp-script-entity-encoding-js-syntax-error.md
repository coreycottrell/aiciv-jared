# WordPress HTML Entity Encoding Breaks JavaScript &&  Operators in Script Blocks

**Date**: 2026-03-01
**Type**: gotcha
**Severity**: CRITICAL - causes complete JS failure

---

## The Bug

WordPress renders `&&` (logical AND) as `&#038;&#038;` in the HTML output of `wp:html` blocks, EVEN when properly wrapped in `<!-- wp:html --><!-- /wp:html -->` comment tags.

This causes a JavaScript **syntax error** that crashes the ENTIRE script block - meaning ZERO functions (including `handleGateSubmit`, `window.*` assignments) are ever registered.

## Affected Page
- URL: https://purebrain.ai/training/
- Page ID: 1115
- Symptom: Password gate form submits but nothing happens - functions not defined

## Root Cause
WordPress's content rendering pipeline (wptexturize or kses filters) HTML-entity-encodes `&` to `&#038;` even inside `<script>` tags within `wp:html` blocks. The sequence `&&` becomes `&#038;&#038;`.

The raw stored content is correct (`&&`), but the rendered HTML output is broken.

## Fix Applied

Replace ALL `&&` logical AND operators in JavaScript that's stored in WordPress `wp:html` blocks with equivalent ternary expressions:

```javascript
// BEFORE (breaks in WP):
if (video.hlsUrl && Hls.isSupported()) {

// AFTER (safe):
if (video.hlsUrl ? Hls.isSupported() : false) {
```

```javascript
// BEFORE:
var durationBadge = (v.duration && !isComingSoon)

// AFTER:
var durationBadge = (v.duration ? !isComingSoon : false)
```

```javascript
// BEFORE:
if (quarter && isComingSoon)

// AFTER:
if (quarter ? isComingSoon : false)
```

```javascript
// BEFORE (double &&):
if (e.target && e.target.classList.contains("video-card") && e.key === "Enter")

// AFTER:
if (e.target ? (e.target.classList.contains("video-card") ? (e.key === "Enter") : false) : false)
```

## What Does NOT Break

- `&&` inside JS string literals (e.g., `"foo && bar"`) - WordPress also encodes these but they're in string context so JS still parses
- `&` inside HTML entity names in JS strings (e.g., `"&amp;"`) - renders as `&amp;amp;` in script source but JS reads it as literal text `&amp;` (5 chars), which IS the correct HTML entity value

## Secondary Finding: escHtml String Literals

The `escHtml` function had string literals like `"&amp;"`, `"&lt;"` etc. WordPress encodes these to `&amp;amp;` in rendered HTML. However, browsers do NOT HTML-decode `<script>` tag content - they read raw text. So `&amp;` in a script source is read by JS as the 5-char string `&amp;`. For the escHtml use case (replacing `&` with `&amp;`), this is actually correct.

To be safe, use character class regex instead of `//g` with escaped chars:
```javascript
// Safer - regex character class avoids entity confusion:
.replace(/[&]/g, "\x26amp;")  // \x26 = &
```

## Diagnosis Method

1. Fetch live page: `curl -s "https://purebrain.ai/training/" -o /tmp/page.html`
2. Find script block containing the JS code
3. Check for `&#038;` - if found, this is the WP entity encoding bug
4. Check for `&&` - should be 0 in operator positions if properly fixed

## Deployment Notes

- Page uses `post_content` (raw block) NOT Elementor `_elementor_data`
- Update via: `POST /wp-json/wp/v2/pages/1115` with `X-HTTP-Method-Override: PATCH`
- After update: clear Elementor cache (`DELETE /wp-json/elementor/v1/cache`) and republish

## Prevention Rule

**NEVER use `&&` in JavaScript stored in WordPress `wp:html` blocks.**
Always use ternary: `(a ? b : false)` instead of `a && b`.

This applies to ALL JavaScript deployed via WordPress REST API to page content.
