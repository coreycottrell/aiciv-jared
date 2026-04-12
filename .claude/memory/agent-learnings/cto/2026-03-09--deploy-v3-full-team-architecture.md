# CTO Memory: Deploy v3 Full Team Architecture

**Date**: 2026-03-09
**Type**: teaching + operational
**Topic**: Complete homepage clone + mobile fix deployment architecture

---

## What Was Built

Wrote `/home/jared/projects/AI-CIV/aether/tools/deploy_full_homepage_clone_v3.py` — the definitive deployment script that handles all known issues in one shot.

## Root Cause Analysis (from memory review)

Previous attempts failed for 3 compounding reasons:

### Reason 1: Wrong Cut Point
The cut at `<!-- Calculator CTA Section -->` KEPT the old `.pricing-section` and `.comparison-section` in the functional top — these are JS-gated with `display:none` by default. Adding homepage sections BELOW them didn't help because users couldn't see the gated sections anyway.

**v3 Fix**: The cut finds the beginning of the bottom design sections (any of 8 markers) and removes them, replacing with homepage versions. If the old gated sections are already gone (prior fix removed them), the cut falls back to `rfind('<section')` before Compare PureBrain.

### Reason 2: Nested HTML Documents
Prior to the March 8 fix, pages 689 and 1232 had NESTED complete HTML documents inside the Elementor HTML widget. Mobile Safari closes the outer `</body>` at the first occurrence — sections injected after are invisible on iOS.

**v3 Fix**: `clean_nested_html_docs()` removes ALL `</body>`, `</html>`, `<!DOCTYPE html>`, `<html>`, and `<head>` tags from the widget HTML. The outer Elementor page provides proper closing tags.

### Reason 3: Transparent Section Backgrounds
Even when sections were visible in the DOM, they had `background: transparent` or `rgba(0,0,0,0)` backgrounds. The fixed-position video with dark overlay (rgba 0,0,0,0.75) made content effectively invisible.

**v3 Fix**: `add_mobile_video_css_fix()` injects CSS that gives solid `#080a12` backgrounds to all transparent sections on mobile (max-width 767px).

### Reason 4: Mobile Video Shows Poster Image
`width:auto; height:auto` on the video element fails on iOS Safari — browser shows `poster` attribute (hexagon image) instead of playing the video.

**v3 Fix**: CSS changed to `width:100%; height:100%; object-fit:cover`. Video attrs patched to include `autoplay muted loop playsinline preload="auto"`.

## Key Technical Facts

- Both 689 and 1232: `_elementor_data[0].elements[0].settings.html` is the single HTML widget
- Homepage (page 11): Uses full Elementor layout sections, different navigation path
- WP auth: `purebrain@puremarketing.ai` + `PUREBRAIN_WP_APP_PASSWORD` from .env
- Cache clear: `DELETE /wp-json/elementor/v1/cache` after every deploy
- PayPal LIVE: in .env as `PAYPAL_CLIENT_ID`
- PayPal SANDBOX: in .env as `PAYPAL_SANDBOX_CLIENT_ID`

## CTO Tool Limitation Learned

The CTO agent (this agent) does NOT have Bash or Task tools. Cannot directly execute scripts or invoke sub-agents. Must:
1. Write artifacts (scripts, briefs, checklists)
2. Direct team through written instructions
3. Rely on the invoking orchestrator to run agents with Bash access

This is by design — CTO is strategic, not executor.

## Delegation Pattern Used

1. Wrote complete deployment script (FSD to execute)
2. Wrote deploy brief with verification checklist (BVT to follow)
3. Wrote security brief about PayPal credential exposure (security-auditor to verify)

## Files Created This Session

- `/home/jared/projects/AI-CIV/aether/tools/deploy_full_homepage_clone_v3.py` — main script
- `/home/jared/projects/AI-CIV/aether/exports/cto-deploy-brief-v3.md` — team brief
- This memory file
