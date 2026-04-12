# Task Record: Homepage Bar Removal + Invitation Page Blue Overlay

**Date**: 2026-02-27
**Agent**: dept-systems-technology
**Type**: two-part deployment

---

## Task 1: Remove "See Why PureBrain Is Different" Fixed Footer Bar

**Plugin file**: `/home/jared/projects/AI-CIV/aether/exports/purebrain-security-plugin-v466.php`

**What was removed**: The `WHY PUREBRAIN HOMEPAGE BANNER (v4.6.0)` block (formerly lines 4575-4627).
This was an `add_action('wp_footer', ..., 99)` that:
- Only fired on `is_front_page()`
- Injected `#pb-why-purebrain-bar` fixed bar at `bottom: 36px` (above the Aether credit bar)
- Overrode body `padding-bottom` to `76px` on homepage (36px Aether + 40px Why bar)

**What remains intact**:
- Aether footer credit bar (priority 100) with `padding-bottom: 36px` - unchanged, all pages
- Homepage body now correctly reverts to 36px padding (from Aether bar's rule)

**Deployment method**: Plugin editor via admin-ajax (`edit-theme-plugin-file` action)
**Verification**: `curl homepage | grep pb-why-purebrain` = empty (confirmed removed)

### IMPORTANT DISCOVERY
There is a SECOND "See Why PureBrain Is Different" text on the homepage - this is an **Elementor widget** (`data-id="why_purebrain_hp_txt"`, `elementor-widget-html.default`) embedded directly in the page body. This is NOT from the plugin. It's an inline content section, not a fixed footer bar. This was NOT removed - it's a different element requiring Elementor edit if removal needed.

---

## Task 2: PT Blue Overlay on Invitation Page (Page 987)

**URL**: https://purebrain.ai/invitation/
**Page ID**: 987
**Template**: elementor_canvas (no theme chrome)

**What was added**: A `#pb-canvas-container::after` CSS pseudo-element rule:
```css
#pb-canvas-container::after {
  content: '';
  position: absolute;
  inset: 0;
  background: rgba(42, 147, 193, 0.15);  /* PT Blue at 15% opacity = 85% transparent */
  pointer-events: none;
  z-index: 1;
}
```

**Placement**: Added immediately after the `#pb-vignette` CSS block in the page's post_content.
**Deployment method**: REST API PATCH to `/wp-json/wp/v2/pages/987`
**Verification**: `curl invitation page | grep rgba(42, 147, 193, 0.15)` = matched (confirmed live)

### Why This Approach
- Safest: purely additive, zero changes to existing CSS
- `#pb-canvas-container` already has `position: fixed; inset: 0` so `::after` fills it perfectly
- `pointer-events: none` ensures clicks pass through to the brain canvas
- `z-index: 1` sits between the canvas (z:0) and the vignette (z:1) - actually same level as vignette

---

## Deployment Pattern Reference
- Plugin editor nonce retrieved from: `/wp-admin/plugin-editor.php?plugin=purebrain-security%2Fpurebrain-security-plugin.php`
- Cookies stored at `/tmp/wp_cookies.txt` during session
- REST API auth: `base64("Aether:{PUREBRAIN_WP_APP_PASSWORD}")`
