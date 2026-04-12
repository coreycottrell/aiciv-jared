# CTO Memory: Homepage Mobile Video Spiral Root Cause

**Date**: 2026-03-07
**Type**: teaching, operational
**Topic**: Dual-plugin JS conflict causing wrong background on mobile — inline styles beat CSS !important

---

## The Bug

Homepage (page 11) shows spiral/vortex geometric pattern instead of brain video on mobile.
Pages 689 (pay-test-2) and 1232 (pay-test-sandbox-3) show brain video correctly on mobile.

---

## Root Cause

Two scripts were running simultaneously on page 11 only (both gated on `is_front_page()`):

| Plugin | Script ID | Priority | Mobile Action |
|--------|-----------|----------|--------------|
| `purebrain-security.php` v6.2.2 | `pb-video-mobile-pause` | 20 | `wrapper.style.display = 'none'` (hides brain video, living-background shows = spiral) |
| `pb-video-handler.php` v1.1.0 | `pb-video-handler-js` | 30 | `wrapper.style.display = 'block'` (shows brain video, hides living-background) |

The spiral IS the `.living-background` canvas element. When `.video-background` is hidden with `display:none`, the `.living-background` (geometric/vortex canvas) becomes visible.

Pages 689 and 1232 work correctly because `is_front_page()` returns false for them — the security plugin's `pb-video-mobile-pause` script never fires on those pages.

---

## Why The CSS Safety Net Failed

The `pb-video-handler.php` CSS block includes:
```css
@media (max-width: 767px) {
    body.home .video-background { display: block !important; }
}
```

This should override display:none. BUT — the security plugin sets the display via JS inline style (`element.style.display = 'none'`). **Inline styles from JS always override external CSS, even with `!important`.** The CSS safety net is useless against JS inline mutations.

The JS priority order (30 > 20) means the new plugin's HTML is output later and its JS function also fires later at page load. This SHOULD mean the `display: 'block'` wins. But execution order between two synchronous scripts in the same `wp_footer` render can be flaky depending on browser, and any async timing differences break the assumption.

---

## The Fix

Deploy `purebrain-security-plugin.php` (the already-extracted version, which has the `pb-video-mobile-pause` block replaced with a comment stub). This removes the conflicting code entirely.

The extracted version already shows at line 520:
```
// PERFORMANCE: Video Mobile Pause/Hide — extracted to standalone plugin: pb-video-handler (2026-03-07)
```

**Security Plugin Isolation Rule compliance**: Removing a non-security feature (bandwidth optimization video hide) from the security plugin makes it MORE compliant, not less.

---

## Lessons for Future

1. **Never fight JS inline style mutations with CSS** — you cannot win. CSS `!important` does not override `element.style.property`.

2. **Two plugins doing opposite things = unpredictable behavior** — when you extract code to a new plugin, REMOVE it from the old plugin immediately. Half-extractions create race conditions.

3. **`is_front_page()` is the key differentiator** — any script gated this way only fires on the homepage (page 11). If you see a homepage-only bug, look for homepage-only gated code in ALL plugins.

4. **Priority order is not the same as execution order** — WordPress priority controls output order in HTML, but browser JS execution for synchronous scripts in the same DOM is top-to-bottom. Priority 30 HTML outputs AFTER priority 20 HTML, so the priority-30 JS DOES run last. But this is brittle — don't rely on it when you can simply remove the conflict.

5. **The living-background canvas = spiral/vortex pattern** — this is the geometric animation that shows when `.video-background` is hidden. Both elements coexist in the DOM; CSS/JS controls which one is visible.
