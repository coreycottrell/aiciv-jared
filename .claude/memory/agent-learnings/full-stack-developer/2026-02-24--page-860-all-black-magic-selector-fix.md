# Page 860 All-Black Fix: Broad [class*="magic"] Selector

**Date**: 2026-02-24
**Type**: teaching
**Topic**: WordPress dark theme CSS - broad attribute selectors kill page content

## Problem

Page 860 (ai-website-execution) showed ALL BLACK after a previous CSS override deployment. The dark background was working but all content was invisible.

## Root Cause

The CSS at the top of the page contained:

```css
[class*="magic"] {
  color: inherit !important;
  background-color: inherit !important;
  border-color: inherit !important;
  fill: inherit !important;
}
```

This broad attribute selector matches ANY element whose class contains "magic". The intent was to override the theme's orange poison plugin (`[class*="magic"]` is a legitimate theme selector for cursor elements). However, because we set `color: inherit` and `background-color: inherit` on ALL matching elements, if any ancestor element in the DOM tree had a dark/transparent background and the wrong color cascade, this would cause all child content to become invisible (dark text on dark background or zero opacity).

Additionally: `html body * { box-sizing: border-box }` wildcards compound cascade problems.

## Fix

Replace the broad nuclear CSS block with surgical targeting ONLY:

```css
/* CORRECT - surgical targeting only */
:root { --bs-body-bg: #080a12 !important; }
html, body, body.tt-magic-cursor, body.page, body.page-id-860 {
  background: #080a12 !important;
  background-color: #080a12 !important;
  color: #e8edf3 !important;
}
/* ONLY kill these two specific elements */
.theme-preloader { display: none !important; }
#magic-cursor { display: none !important; }
body { cursor: auto !important; }
```

**Do NOT use:**
- `[class*="magic"]` broad selectors (matches too many things)
- `html body *` wildcard rules
- `[class*="cursor"]` broad selectors

## Key Insight

The theme plugin's orange poison uses `[class*="magic"]` as its selector, which targets the magic cursor overlay elements. When WE also use `[class*="magic"]` with `inherit` values, we create a conflict where our selector matches the same elements but sets different values, causing unpredictable cascade behavior.

The correct approach: let the theme plugin's `[class*="magic"]` rule do what it does (it handles cursor elements), and we only explicitly hide `#magic-cursor` and `.theme-preloader` by element ID/class, not by broad attribute matching.

## Verification Checklist After Deploy

1. Fetch live page and check for hero heading text present
2. Check pricing cards render ($197, $497, $897)
3. Check FAQ section visible
4. Take playwright screenshot to confirm visual render
5. Confirm dark bg #080a12 in source

## Files

- Source: `exports/ai-website-execution.html`
- Fixed copy: `exports/ai-website-execution-fixed.html`
- Screenshot: `exports/page-860-screenshot.png`
- WP Page ID: 860 on purebrain.ai
