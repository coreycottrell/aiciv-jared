# CTO Memory: Homepage Clone Mission Architecture

**Date**: 2026-03-09
**Type**: teaching + operational
**Topic**: Full page rebuild of pay-test-2 and sandbox-3 using homepage design

---

## Mission Context

Jared frustrated with previous attempts. Both pay-test-2 (689) and sandbox-3 (1232) need full homepage design cloned.

## Root Cause of Previous Failure

From QA memory (browser-vision-tester 2026-03-09--sandbox3-mobile-bottom-sections...):
- `.pricing-section` and `.comparison-section` have `display:none` in CSS
- These sections are INTENTIONALLY gated — only shown when `window.revealPricing()` fires after chat engagement
- Even when revealed: transparent backgrounds + dark video overlay = invisible on mobile

The earlier fix (adding homepage bottom sections) was the right APPROACH but the CUT POINT was wrong — it cut at `<!-- Calculator CTA Section -->` but the JS-gated sections `.pricing-section` and `.comparison-section` were ABOVE that cut point.

## Correct Architecture

Both pages 689 and 1232:
- Use `_elementor_data[0].elements[0].settings.html` — single HTML widget
- Full page HTML lives here (DOCTYPE through body close)
- Template: `elementor_canvas`

## Build Scripts Created

1. `/home/jared/projects/AI-CIV/aether/tools/build_homepage_clone_final.py` — main deployment script
2. `/home/jared/projects/AI-CIV/aether/tools/deploy_homepage_clone_v1.py` — diagnosis/export script

## The Correct Cut Point

The cut point should be BEFORE the JS-gated sections begin, i.e. before `.pricing-section` and `.comparison-section` in the HTML. These are part of the chatbox UX. They need to STAY if the chatbox stays. OR they need to be replaced entirely.

**Decision tree:**
- If Jared wants chatbox + gated sections: keep them, fix CSS so sections are always visible (remove display:none)
- If Jared wants full homepage clone: replace the ENTIRE page with homepage design, keeping ONLY the PayPal integration and chat flow scripts

## What the Mission Actually Asks

Re-reading the brief:
> Replace the ENTIRE page content with the homepage design, BUT preserve:
> - The chatbox HTML + JavaScript
> - PayPal LIVE integration
> - Post-payment chatbox flow

This means:
1. Keep the chatbox HTML (the chat UI elements)
2. Keep the PayPal buttons/integration
3. Keep the post-payment flow JS
4. Replace everything ELSE with homepage design

The JS-gated `.pricing-section` and `.comparison-section` are PART OF the chatbox flow — they're the pre-chat sections that get revealed. These need to be REMOVED if we're cloning the homepage design to replace the pre-chat experience.

## Phase 2: Mobile Video

All 3 pages currently serve PureResearch.ai-1.mp4 (cosmic galaxy video).
This IS the intended video for now (confirmed in 2026-03-04 memory: "confirmed working 200 OK").
The Phase 2 ask says "show the animated brain video instead of static hexagon" — so the hexagon issue may be on specific iOS devices where the video fails to load.

Fix for iOS: Ensure video element has `autoplay muted loop playsinline preload="auto"` attributes.
CSS fix: Use `width:100%; height:100%` on video element (not `width:auto; height:auto`).

## Key References

- CTO architecture: this file
- FSD memory (sandbox3 replacement): 2026-03-09--sandbox3-bottom-sections-replacement.md
- QA diagnosis: browser-vision-tester/2026-03-09--sandbox3-mobile-bottom-sections-transparent-bg-display-none.md
- Homepage sections: full-stack-developer/2026-03-09--homepage-bottom-sections-extraction.md
- Video fix CSS: full-stack-developer/2026-03-08--mobile-video-background-fix.md
