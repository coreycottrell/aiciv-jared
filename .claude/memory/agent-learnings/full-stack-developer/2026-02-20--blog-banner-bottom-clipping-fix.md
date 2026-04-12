# Memory: Blog Post Banner Bottom Clipping Fix - v1.9.0

**Date**: 2026-02-20
**Type**: teaching + operational
**Agent**: full-stack-developer
**Topic**: Root cause of featured image bottom-clipping on desktop/tablet and how v1.9.0 fixed it

---

## Problem

Jared reported: Blog post featured image banners were clipped at the bottom on desktop and tablet. The "THE DIFFERENCE" text and "Awaken Your Partner AI at PUREBRAIN.ai" CTA text at the bottom of banner images were being cut off. Mobile was PERFECT - do not touch.

---

## Root Cause

**File**: `https://purebrain.ai/wp-content/themes/artistics/style.css`

The Artistics theme sets:

```css
/* Base (applies to desktop + tablet) */
.post-single-image figure,
.post-single-image img {
    width: 100%;
    aspect-ratio: 1 / 0.50;  /* Forces container to 50% of its width */
    object-fit: cover;        /* Crops image from center to fill the container */
    border-radius: 40px;
}

/* Mobile override only */
@media only screen and (max-width: 767px) {
    .post-single-image figure,
    .post-single-image img {
        aspect-ratio: 1 / 0.70;  /* Slightly taller on mobile */
    }
}
```

**How clipping happens**:
1. `aspect-ratio: 1/0.50` = container height is only 50% of its width
2. For a 760px-wide image → container is only 380px tall
3. The banner image is 1920x1080 (16:9 = 0.5625 ratio) - taller than the 0.50 container
4. `object-fit: cover` centers the image and crops top+bottom equally
5. Bottom text in banners gets cropped off

**Why mobile was fine**: Theme's `max-width: 767px` media query overrides to `1/0.70` (taller proportionally), showing more of the image.

---

## The Previous Plugin CSS Bug (v1.8.0)

Our plugin v1.8.0 had:
```css
body.single-post .post-single-image figure {
    overflow: hidden !important;
    /* NO aspect-ratio override! */
}
body.single-post .post-single-image img {
    aspect-ratio: auto !important;   /* Only on IMG, not FIGURE */
    object-fit: cover !important;    /* Still cover! */
}
```

Problem: We overrode `aspect-ratio` on the `img` but NOT on the `figure`. The figure still had `aspect-ratio: 1/0.50` from the theme which constrained the container height. The img filled that short container with `object-fit: cover`, still clipping the bottom.

---

## Fix (v1.9.0)

```css
/* On both figure AND img: */
body.single-post .post-single-image figure {
    aspect-ratio: auto !important;  /* NEW: override on figure too */
    height: auto !important;        /* NEW: let it expand naturally */
    overflow: hidden !important;
}
body.single-post .post-single-image img {
    aspect-ratio: auto !important;
    object-fit: fill !important;    /* CHANGED: fill, not cover - no cropping */
    height: auto !important;
    width: 100% !important;
}

/* Also changed .post-single-image overflow: hidden -> visible */
body.single-post .post-single-image {
    overflow: visible !important;   /* CHANGED: was hidden */
}
```

`object-fit: fill` stretches the image to fill the container without cropping. Since we also let the container size naturally via `aspect-ratio: auto`, the image renders at its natural 16:9 dimensions.

---

## After Fix Results

| Viewport | figure aspect-ratio | img object-fit | img rendered height | Bottom clipped? |
|----------|--------------------|-----------------|--------------------|-----------------|
| Desktop 1440px | auto | fill | 428px (natural 16:9) | No |
| Tablet 1024px | auto | fill | 383px (natural 16:9) | No |
| Mobile 375px | 1/0.70 (theme) | cover (theme) | (untouched) | N/A (was fine) |

---

## Files Modified

- **Plugin**: `tools/security/purebrain-security-plugin.php` (v1.9.0)
- **Deploy script**: `tools/security/deploy_plugin_v190.py`
- **Screenshots**:
  - `exports/screenshots/plugin_v190_desktop.png` (1440px - fixed)
  - `exports/screenshots/plugin_v190_tablet.png` (1024px - fixed)

---

## Key Lessons

### 1. Always override BOTH figure AND img when dealing with aspect-ratio

The `aspect-ratio` on the **figure** (the container) constrains the box height. The `aspect-ratio` on the **img** doesn't matter if the container is still constrained. BOTH must be overridden.

### 2. `object-fit: cover` with constrained container = guaranteed cropping

If you set `aspect-ratio` on a container to something shorter than the natural image ratio, `object-fit: cover` will ALWAYS crop. Use `object-fit: fill` when you want the full image visible at natural aspect ratio.

### 3. Theme's aspect-ratio may differ by breakpoint

Always check the theme CSS at each breakpoint, not just the base style. Use:
```python
url = 'https://purebrain.ai/wp-content/themes/artistics/style.css'
# Search for 'aspect-ratio' to find all breakpoint-specific overrides
```

### 4. overflow: hidden on the wrapper can also clip

Changed `.post-single-image` from `overflow: hidden` to `overflow: visible` to ensure the full image is visible (border-radius clipping is handled by `overflow: hidden` on the figure, which is correct).

### 5. Deployment verification pattern

After deploy:
1. Fetch page HTML directly (with `Cache-Control: no-cache`) to check CSS text
2. Use Playwright at multiple viewports to get `getComputedStyle()` values
3. Check `aspectRatio`, `objectFit`, `offsetHeight` on both figure and img
4. GoDaddy cache flush URL: `options-general.php?wpaas_action=flush_cache&wpaas_nonce=NONCE`
