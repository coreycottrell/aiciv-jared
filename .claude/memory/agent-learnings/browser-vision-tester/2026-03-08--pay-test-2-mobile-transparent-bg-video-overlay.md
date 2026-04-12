# Memory: pay-test-2 Mobile Content Invisible - Transparent Background + Video Overlay

**Date**: 2026-03-08
**Agent**: browser-vision-tester
**Type**: teaching + gotcha + pattern
**Tags**: mobile, z-index, background, transparency, video-background, fixed-element, pay-test-2, timeline-section, testimonials-section

---

## Root Cause

Content below "WHAT HAPPENS NEXT" on pay-test-2 (page 689) is invisible on mobile because:

1. `.timeline-section` has `background: rgba(15,15,15,0.5)` — semi-transparent
2. `.testimonials-section` has `background: rgba(0,0,0,0)` — fully transparent
3. `.video-background` is `position: fixed; z-index: 0; height: 100vh; width: 100vw` (covers full screen)
4. `.video-background__overlay` has `background: rgba(0,0,0,0.75)` — 75% dark overlay
5. The sections have `position: static; z-index: auto` — they don't establish their own stacking context

Result: transparent/semi-transparent sections + dark fixed video overlay = invisible content

---

## The Fix

```css
@media (max-width: 767px) {
    .timeline-section,
    .testimonials-section {
        background: #080a12 !important;
        position: relative !important;
        z-index: 2 !important;
    }
}
```

This makes content fully visible immediately. Verified with before/after screenshots.

---

## Diagnosis Technique

When content is invisible on mobile but DOM shows it exists:
1. Run `document.elementsFromPoint(x, y)` at multiple scroll positions to see what's at the top of the z-stack
2. Check section backgrounds with `getComputedStyle(el).backgroundColor` — look for rgba with alpha < 1
3. Check for fixed-position elements covering the viewport (video-background, overlays)
4. TEST: Temporarily add `background: #080a12 !important; z-index: 2 !important` to suspect sections
5. Screenshot before/after — if content appears, you found it

---

## Key Lesson: "DOM visible does NOT mean visually visible"

The DOM showed:
- `timeline-section`: display: block, visibility: visible, height: 896px ✓
- `testimonials-section`: display: block, visibility: visible, height: 2644px ✓
- All child elements: display: block, color: white ✓

But visually: nearly invisible because transparent backgrounds + dark fixed overlay

The standard hidden-element checks (display:none, visibility:hidden, overflow:hidden, maxHeight:0) ALL PASSED. The bug was purely visual — transparent backgrounds bleeding the dark video overlay through.

---

## Pattern: "Fixed dark overlay + transparent sections = invisible on mobile"

This pattern appears when:
- A fixed background/overlay div covers the full viewport
- Content sections below the hero have transparent or semi-transparent backgrounds
- The overlay is dark enough (> 50% opacity) that content blends in
- Desktop works because the video/overlay doesn't dominate visually at large viewports

---

## Page Context

- Page: purebrain.ai/pay-test-2 (page ID 689)
- Password: PureBrain.ai253443$$$
- Affected sections: `.timeline-section` (offsetTop ~9929), `.testimonials-section` (offsetTop ~10826)
- Not affected: hero, about, value-pyramid, capabilities, awakening, value sections (all have solid dark backgrounds)

---

## Screenshots Evidence

Before fix: `/home/jared/projects/AI-CIV/aether/exports/screenshots/pay-test-2-mobile-20260308/020-at-timeline-position.png`
After fix: `/home/jared/projects/AI-CIV/aether/exports/screenshots/pay-test-2-mobile-20260308/035-with-bg-fix-timeline.png`
