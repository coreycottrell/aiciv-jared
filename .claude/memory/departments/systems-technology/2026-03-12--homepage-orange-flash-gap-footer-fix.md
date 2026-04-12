# Homepage Fixes - Orange Flash, Top Gap, Footer Logo (v4.9.0)
**Date**: 2026-03-12
**Agent**: dept-systems-technology
**Type**: bug-fix

## Issues Fixed

### Issue 1: Orange flash on first load
**Root cause**: The `wp-custom-css` Additional CSS in the exported HTML contains a broad selector:
```css
[class*="magic"] { background-color: #f1420b !important; }
```
The artistics theme hardcodes `class="...tt-magic-cursor..."` on the body element (page-id-11). Since `tt-magic-cursor` contains "magic", this selector matches the body and turns the entire page orange on first paint.

The v4.8.5 fix used `html body.tt-magic-cursor { background-color: #080a12 }` with higher specificity, but it was not sufficient because:
1. The `body.tt-magic-cursor` class is merged from the nested body tag (HTML5 parser merges subsequent body attributes)
2. The rule ordering and context of the static export caused the orange to still flash

**v4.9.0 Nuclear Fix (multiple layers)**:
1. Added `style="background:#080a12;background-color:#080a12;"` as inline style on outer `<body>` tag (line 12) — inline styles override all CSS
2. Added `html body { background:#080a12 }` rule in the existing fix block
3. Added new `pb-body-orange-nuke-v490` CSS block injected AFTER the second `wp-custom-css` block but BEFORE page-11's body element
4. Added `style="background:#080a12!important..."` inline to both `theme-preloader` divs

### Issue 2: Too much space above brain (hero section)
**Root cause**: The `.hero` section used `align-items: center` which vertically centers all hero content in the 100vh container, creating equal empty space above and below the brain image.

**Fix**: Changed to `align-items: flex-start` with `padding: 80px 24px 60px` (was `60px 24px`). Now hero content starts 80px from the top of viewport, reducing the perceived gap above the brain.

### Issue 3: Footer logo wrong proportions
**Root cause**: Two conflicting CSS rules in the exported HTML:
- Inner CSS: `.footer__logo { height: 40px; width: 240px; }` (correct)
- Outer CSS override: `.footer__logo { height: 100px; width: auto; }` (wrong - too tall)

The 100px rule was overriding the correct 40px rule because it appeared LATER in the document.

**Fix**: Changed the conflicting rule to `.footer__logo { height: 40px; width: auto; max-width: 240px; }` which matches the correct proportions for the horizontal Pure Technology "Side by Side" logo.

## Architecture Notes
- purebrain.ai is served as static HTML via Cloudflare Pages (not live WordPress)
- The `exports/cf-pages-deploy/index.html` is the deployed homepage
- ALL external CSS files (artistics theme, elementor CSS) return 404 from CF Pages — only inline CSS matters
- The homepage HTML is a deeply nested structure:
  - Outer wrapper (line 1-12)
  - Page 1502 WP render (lines 2842-5060)
  - Page 11 WP render (lines 5064-8100ish)
  - Inner homepage HTML widget (lines 5080-end)
- Multiple `body` tags get merged by HTML5 parser into single body with all classes
- Both `theme-preloader` divs exist (one per page render)

## Files Changed
- `/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/index.html`

## Git Commit
`7f37ff2c` - Fix homepage: orange flash, top gap above brain, footer logo proportions (v4.9.0)
