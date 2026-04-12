# Memory: Invitation Page Live State - Page 987 Still Unfixed (Feb 27 evening)

**Date**: 2026-02-27
**Type**: operational + gotcha
**Topic**: fixes deployed to page 983 but slug /invitation/ still serves page 987

---

## Situation

Live audit of purebrain.ai/invitation/ at ~17:30 UTC Feb 27 showed:
- 3D brain NOT rendering
- Orange background bug still active
- `Invalid or unexpected token` pageerror
- No importmap

## Root Cause

Earlier session fixed && encoding + added importmap to page 983 (new ID after WP regeneration).
BUT the /invitation/ slug is still pointing to page 987 (old unfixed page).

Confirmed via: `body.className` contains `page-id-987`

## The Three Active Bugs on Page 987

### Bug 1: `&#038;` entity encoding (4 lines)
```
Line 302: for (let i = 0; i < MAX_SPARKS &#038;&#038; spawned < actualCount; i++) {
Line 335: if (e.touches &#038;&#038; e.touches.length > 0) ...
Line 369: if (propagate &#038;&#038; depth < 4) {
Line 436: if (dist < MOUSE_RADIUS &#038;&#038; t - n.fireTime > FIRE_DURATION) {
```
Causes: `Invalid or unexpected token` pageerror

### Bug 2: No importmap
EffectComposer imports bare `"three"` specifier internally.
Without importmap: `TypeError: Failed to resolve module specifier "three"`

### Bug 3: Orange background
body computed = rgb(241, 66, 11) instead of rgb(10, 14, 26)
Fix: `body { background-color: #0a0e1a !important; background: #0a0e1a !important; }`

## Fix Path

Apply all three fixes directly to page 987 content (the one the slug serves).
All fixes are already documented in the 2026-02-27--threejs-importmap-wp-entity-encoding-fix.md memory.

## Verification Commands

```bash
# Quick check which page ID is being served
curl -s https://purebrain.ai/invitation/ | grep -o 'page-id-[0-9]*'

# Quick check for &#038; encoding in live page
curl -s https://purebrain.ai/invitation/ | grep -c '&#038;'

# Quick check for importmap
curl -s https://purebrain.ai/invitation/ | grep -c 'importmap'
```

## Screenshots

- exports/screenshots/invitation-live-2026-02-27/001-full-page.png (shows orange)
- exports/screenshots/invitation-live-2026-02-27/002-hero-top.png (hero OK)
