# Memory: PureBrain Blog Page 319 - Social Icons Border Fix (Second Pass)

**Date**: 2026-02-19
**Type**: teaching
**Topic**: Why the first orange border removal "fix" didn't actually fix it - CSS cascade override pattern

---

## Root Cause Analysis

The previous fix set `.social-link { border: none; }` in Style Block 1 (the main CSS block).
But Style Block 2 (a "blue color override" block added later) contained:

```css
.social-link {
    border-color: rgba(42, 147, 193, 0.3) !important;
    background: rgba(42, 147, 193, 0.08) !important;
}
```

**Why this created a visible border:**
1. Style Block 1 sets `border: none` (shorthand - sets width=0, style=none, color)
2. Style Block 2 sets `border-color: ... !important` - re-enables a visible border
3. The `!important` overrides the shorthand, and CSS then falls back to default `border-style: solid` and `border-width: medium` behavior = visible border

**Lesson**: `border: none` + `border-color: X !important` in a later rule = visible border.
You must use `border: none !important` in the later rule to actually suppress it.

---

## The Fix Applied

Changed Style Block 2's `.social-link` base rule:
```css
/* BEFORE (bad) */
.social-link {
    border-color: rgba(42, 147, 193, 0.3) !important;
    background: rgba(42, 147, 193, 0.08) !important;
}

/* AFTER (correct) */
.social-link {
    border: none !important;
    background: rgba(42, 147, 193, 0.08) !important;
}
```

Also changed hover rule to use `border-color: transparent !important` (was `#2a93c1 !important`).

---

## Page Architecture (Page 319)

- Pure custom HTML - NOT Elementor (elementor_data is empty)
- Content lives entirely in `content.raw` via REST API
- Has 2 `<style>` blocks inline in the HTML
- Style Block 1: main CSS (~300 lines)
- Style Block 2: orange-to-blue color override block (~40 lines)
- Both blocks are in scope for all elements - later block wins (with !important)

---

## API Pattern

```python
AUTH = ('Aether', os.getenv('PUREBRAIN_WP_APP_PASSWORD'))
BASE = 'https://purebrain.ai/wp-json/wp/v2'
# Fetch: GET /pages/319?context=edit
# Update: POST /pages/319 json={'content': new_html}
```

## Verification Steps That Proved Fix Worked

1. Re-fetched via API - confirmed `border: none !important` in content.raw
2. Re-fetched via API - confirmed old `border-color: rgba(42, 147, 193, 0.3) !important` gone
3. Fetched live public page - confirmed `border: none !important` in rendered HTML
4. Confirmed homepage (ID 11) untouched - content length unchanged
5. Confirmed page 319 slug/status/title unchanged

## Teaching Point

**When debugging "fix didn't stick" CSS issues:**
1. Look for MULTIPLE style blocks - later blocks can override earlier ones
2. `!important` in a later block beats non-important shorthand in an earlier block
3. `border-color: X !important` can re-enable a border even after `border: none` was set
4. Always search ALL style blocks, not just the one you modified
