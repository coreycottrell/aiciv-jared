# Full-Stack Developer Memory: Mobile Video Background Fix

**Date**: 2026-03-08
**Type**: teaching
**Topic**: Mobile video background shows poster/hexagon image instead of video

## Root Cause

The `.video-background__video` CSS used the old "centering trick":
```css
position: absolute;
top: 50%;
left: 50%;
min-width: 100%;
min-height: 100%;
width: auto;
height: auto;
transform: translate(-50%, -50%);
object-fit: cover;
```

On mobile Safari (iOS) and some Android browsers, `width: auto; height: auto` with a fixed-position parent can cause the video to render at 0x0 or not display its frame at all — the browser shows the `poster` attribute image instead (the hexagon/spiral in this case).

## Fix

Replace with the universally supported pattern:
```css
position: absolute;
top: 0;
left: 0;
width: 100%;
height: 100%;
object-fit: cover;
```

This works on all browsers (mobile Safari, Chrome Android, desktop) because:
- `width: 100%; height: 100%` fills the `position: fixed; inset: 0` parent
- `object-fit: cover` maintains aspect ratio while covering the full area
- No transform needed

## Required Video Element Attributes for Mobile Autoplay

All must be present:
```html
<video autoplay muted loop playsinline preload="auto">
```
- `autoplay` + `muted` = required for Chrome Android
- `playsinline` = required for iOS Safari (prevents fullscreen takeover)
- Without `playsinline`, iOS won't autoplay

## Files Changed

### Vercel (purebrain-site.vercel.app)
- `/home/jared/projects/AI-CIV/aether/purebrain-site/public/index.html` (line ~5066)
- Fixed inline `<style>` block in the page
- Redeployed via `npx vercel --prod --yes`

### WordPress (purebrain.ai)
- Page 11 (homepage): `_elementor_data` updated via REST API `POST /wp-json/wp/v2/pages/11`
- The CSS lives inside the Elementor page content as an inline `<style>` block
- Must update `_elementor_data` field (NOT `post_content`) — Elementor renders from meta
- Cache clears itself on next page load after REST API update

### Plugin (pb-video-handler)
- `/home/jared/projects/AI-CIV/aether/tools/security/pb-video-handler/pb-video-handler.php`
- Updated to v1.3.0 with the CSS fix + expanded to cover pages 689, 688, 1232, 319
- NOT YET deployed to WordPress (plugin install via REST API requires WP.org slug)

## Deployment Pattern for WordPress Pages with Elementor

When fixing CSS inside an Elementor page:
1. GET page with `?context=edit` to get `_elementor_data`
2. Find the escaped CSS string (newlines are `\\n`, quotes are `\\"`)
3. Replace the escaped string
4. POST the updated `_elementor_data` via `meta._elementor_data` key
5. Hit the page URL to bust cache

Note: The WP REST API for plugins only installs from WP.org repository.
Custom plugins must be deployed via FTP, SSH, or a pre-installed updater plugin.

## Pages with Video Background

Only homepage (page 11, `/`) has the actual `<div class="video-background">` element.
Other pages (pay-test-2, sandbox-2, sandbox-3) have CSS references but no video HTML.
