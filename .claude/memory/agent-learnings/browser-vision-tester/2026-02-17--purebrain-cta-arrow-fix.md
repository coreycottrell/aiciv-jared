# PureBrain CTA Arrow Color Fix

**Date**: 2026-02-17
**Agent**: browser-vision-tester
**Type**: technique
**Topic**: Fixing CTA button arrow color from orange to white on purebrain.ai

---

## Context

The CTA button "Awaken Your PURE BRAIN" had an arrow icon that was inheriting orange color from the parent element's `currentColor`, making it difficult to see against the orange button background.

## Problem Analysis

DOM inspection revealed:
- SVG class: `.btn__icon--arrow` and `.btn__icon`
- Uses `stroke="currentColor"` which inherits from parent
- Parent element had orange text color, causing orange arrow

## Solution - CSS Override

Added to WordPress Additional CSS:

```css
/* CTA Button Arrow Fix - Force white stroke */
.btn__icon--arrow,
.btn__icon--arrow path,
.btn--primary .btn__icon,
.btn--primary .btn__icon path,
.btn--primary svg,
.btn--primary svg path {
  stroke: #ffffff !important;
  color: #ffffff !important;
}
```

## Key Learnings

### 1. SVG Arrow Icons Use Stroke, Not Fill

For arrow icons (lines, not solid shapes), target `stroke` property instead of `fill`.

### 2. currentColor Inheritance Chain

When SVG uses `stroke="currentColor"`:
- It inherits from element's CSS `color` property
- Must override both `stroke` AND `color` to be safe
- Use `!important` to override inline attributes

### 3. Target Multiple Levels for SVG

Always target:
- The SVG element itself
- Path children within SVG
- Both class-based and parent-context selectors

## Tool Created

`/home/jared/projects/AI-CIV/aether/tools/wp_fix_cta_arrow.py` - Playwright automation for this specific fix

## Verification

Screenshots captured:
- Before: `/tmp/purebrain-cta-before.png`
- After: `/tmp/purebrain-cta-after.png`
- Published state: `/tmp/purebrain-published.png`

CSS successfully added via CodeMirror API and published through WordPress Customizer.

## Related Files

- Existing CSS automation tool: `/home/jared/projects/AI-CIV/aether/tools/wp_fix_icon_css.py`
- WordPress CSS patterns: Memory entry `2026-02-16--wordpress-css-icon-fix-pattern.md`

---

**Tags**: wordpress, css, svg, icons, purebrain, cta, button, stroke, color
