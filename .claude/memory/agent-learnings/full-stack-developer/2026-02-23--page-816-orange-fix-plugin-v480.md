# Page 816 Orange Fix: Plugin v4.8.0 Magic Cursor Override with !important

**Date**: 2026-02-23
**Type**: teaching
**Topic**: [class*="magic"] !important defeating page-specific body color overrides — fixed with higher-specificity !important rules in wp_footer

---

## Root Cause

WordPress Additional CSS contains:
```css
[class*="magic"],
.site-cursor, .custom-cursor, ... {
    color: #f1420b !important;
    fill: #f1420b !important;
    background-color: #f1420b !important;
}
```

The Artistics theme adds class `tt-magic-cursor` to `<body>`. Since `[class*="magic"]` matches `tt-magic-cursor`, the body AND all its descendant SVGs become orange.

---

## Why Previous Fix (v4.7.1) Failed

Plugin v4.7.1 used:
```css
body.tt-magic-cursor {
    color: initial;         /* NO !important */
    background-color: initial;
}
```

`color: initial` WITHOUT `!important` cannot beat `[class*="magic"] { color: #f1420b !important }`.
Even though the rule ran in `wp_footer` (after Additional CSS), CSS cascade rules state:
- `!important` declarations beat non-`!important` declarations regardless of source order.
- `initial` keyword reverts to browser default, not to our desired color.

---

## The Fix (v4.8.0)

Three layers of protection:

### Layer 1: General elementor_canvas page fix
```css
body.tt-magic-cursor {
    color: #e8edf5 !important;           /* (0,1,1) > [class*="magic"] (0,1,0) */
    background-color: #0a0e1a !important;
    border-color: inherit !important;
}
```

### Layer 2: Page-816 specific maximum specificity
```css
body.page-id-816.tt-magic-cursor {
    color: #e8edf5 !important;           /* (0,2,1) - maximum specificity */
    background-color: #0a0e1a !important;
    background: #0a0e1a !important;
}
```

### Layer 3: SVG descendant override
```css
body.tt-magic-cursor svg,
body.tt-magic-cursor svg path,
body.tt-magic-cursor svg circle, ... {
    fill: currentColor !important;
    stroke: currentColor !important;
    color: inherit !important;
}
```

### Priority: wp_footer at 99 (was 1)
Changed `add_action('wp_footer', ..., 1)` to `add_action('wp_footer', ..., 99)`.
This ensures our CSS block is the VERY LAST thing output, after all other footer hooks.

---

## CSS Cascade Logic

For `!important` declarations:
1. Higher specificity wins
2. If same specificity, LATER source order wins

| Rule | Specificity | Source Order | Winner? |
|------|-------------|--------------|---------|
| `[class*="magic"]` Additional CSS | (0,1,0) | ~26491 | LOSES |
| `body.tt-magic-cursor` v4.8.0 fix | (0,1,1) | ~147080 | WINS |
| `body.page-id-816.tt-magic-cursor` v4.8.0 | (0,2,1) | ~147375 | WINS (backup) |

---

## Verification: 9/9 Checks Passed

- page_loads_200
- v4.8.0_fix_present
- body_tt_magic_cursor_override
- color_e8edf5_important
- page_id_816_override
- svg_descendant_override
- bg_0a0e1a_important
- no_wp_autop_damage
- footer_v470_present

---

## Files Modified

- `/home/jared/projects/AI-CIV/aether/tools/security/purebrain-security/purebrain-security-plugin.php` (v4.7.1 → v4.8.0)
- `/home/jared/projects/AI-CIV/aether/tools/security/deploy_plugin_v480_purebrain.py` (new deploy script)

---

## Key Lessons

1. **Always use `!important` when overriding Additional CSS `!important` rules**
2. **`color: initial` without `!important` loses to `!important` declarations**
3. **Specificity comparison only matters when BOTH declarations are `!important` or BOTH are not**
4. **wp_footer priority 1 fires FIRST (WordPress reverses normal priority for hooks with lower numbers)**
   - Priority 1 = fires early in wp_footer (still loads in body, so AFTER head CSS)
   - Priority 99 = fires LATE in wp_footer (LAST CSS on the page)
5. **The page content CSS (inside `<!-- wp:html -->`) also had correct overrides, but the CDN was caching the old version — cache bust via POST to /wp-json/wp/v2/pages/{id} is effective**
