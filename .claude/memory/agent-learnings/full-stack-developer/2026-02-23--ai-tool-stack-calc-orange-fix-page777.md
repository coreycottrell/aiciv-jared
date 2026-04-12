# AI Tool Stack Calculator Page 777 - Orange Text Fix

**Date**: 2026-02-23
**Type**: teaching
**Topic**: Additional CSS [class*="magic"] rule conflict causing all-orange text on page-id-777

---

## Root Cause

WordPress Additional CSS contains:
```css
[class*="magic"] { color: #f1420b !important; }
```

This was intended to style some custom "magic" component but the selector also matches `body.tt-magic-cursor` (the TT Magic Cursor plugin class added to the body element). Result: ALL body text on `elementor_canvas` pages becomes orange.

Pages using `elementor_canvas` template are most affected because they don't have standard WordPress theme styles to counteract.

---

## Fix Applied

Injected a page-specific CSS override at the TOP of the existing `<style>` block in the wp:html content. Added immediately after `<style>\n`:

```css
/* PAGE-ID-777 OVERRIDE: Fix for Additional CSS [class*="magic"] rule */
body.page-id-777.tt-magic-cursor {
    color: #e8edf5 !important;
    background-color: #0a0e1a !important;
}
body.page-id-777 * {
    border-color: inherit;
}
```

The `body.page-id-777.tt-magic-cursor` selector has higher specificity than `[class*="magic"]` because:
- It targets `body` element specifically
- It uses page-specific ID class
- It also targets the magic cursor class specifically

---

## Deployment Pattern

1. `GET /wp-json/wp/v2/pages/777?context=edit` — fetch raw content
2. Inject CSS after `<style>\n` (first occurrence only, using `str.replace(old, new, 1)`)
3. `PUT /wp-json/wp/v2/pages/777` with updated content + `status: publish`
4. `DELETE /wp-json/elementor/v1/cache` — clear Elementor cache
5. Verify: `GET /wp-json/wp/v2/pages/777?context=edit` — check override present in raw
6. Verify: `GET https://purebrain.ai/ai-tool-stack-calculator/` — check rendered HTML

---

## Key Facts

- Page ID: 777
- URL: https://purebrain.ai/ai-tool-stack-calculator/
- Source file: `/home/jared/projects/AI-CIV/aether/exports/ai-tool-stack-calculator-v3.html`
- Template: `elementor_canvas`
- Page already had `<!-- wp:html -->` wrapper (correct)
- No wpautop damage after fix (wp:html block protects from it)

---

## Broader Pattern

**Any page on purebrain.ai using `elementor_canvas` template** may be affected by the
`[class*="magic"]` Additional CSS rule. If future pages show all-orange text, apply the same
page-specific override using `body.page-id-{ID}.tt-magic-cursor { color: #e8edf5 !important; }`.

A longer-term fix would be to update the Additional CSS rule to be more specific:
```css
/* More specific - targets only the intended elements */
.tt-magic-cursor-element[class*="magic"] { color: #f1420b !important; }
/* Instead of: [class*="magic"] { color: #f1420b !important; } */
```

But that's a broader change requiring audit of what currently uses the magic selector.
