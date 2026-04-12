# investors-v8: Mobile Grid Layout Fixes

Date: 2026-03-21
Type: teaching + operational
Files changed:
- /home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/investors-v8/index.html

## Root Cause

Multiple grids on the investors-v8 page had inline `style="grid-template-columns:..."` attributes that overrode the responsive CSS class rules. Inline styles have higher CSS specificity than class rules, so `@media` breakpoints in the `<style>` block were silently ignored on mobile.

The existing `.vis-grid` class had `@media(max-width:600px){grid-template-columns:1fr}` but 4 vis-grid instances had `style="grid-template-columns:repeat(3,1fr)"` or `style="grid-template-columns:repeat(2,1fr)"` which always won.

## Issues Fixed (9 total)

1. **vis-grid inline overrides** (lines 686, 778 = repeat(3,1fr); line 712 = repeat(2,1fr)) — Added `.vis-grid{grid-template-columns:1fr!important}` in mobile `@media` block. `!important` is the correct tool here since the inline style is in markup we can't change without touching every element.

2. **Pitch 3 comparison grid** (PureBrain vs Everyone Else, line 743) — Added class `pitch-compare-grid` to the div, then `@media(max-width:600px){.pitch-compare-grid{grid-template-columns:1fr!important}}`.

3. **Business model 3-col grid** (line 807) — Added class `biz-model-grid`, same pattern.

4. **Portfolio grid inline override** (line 991, repeat(3,1fr)) — Added `!important` on `.portfolio-grid` in mobile override block.

5. **Market card "span 2"** (line 1160) — In a 2-col layout this spans both columns. On mobile (1-col) `grid-column:span 2` on a 1-col grid has no effect visually but can cause issues. Added class `market-card-full`, set `grid-column:auto!important` on mobile.

6. **Modal form rows** (lines 2879, 2889) — Two `1fr 1fr` grids inside the investor inquiry modal. Added class `modal-form-row` to both, stacked to `1fr` on mobile.

7. **Hero CTA buttons** — Added `flex-direction:column;gap:12px;align-items:stretch` + `width:100%` on mobile so both buttons fill the width instead of sitting side-by-side.

8. **Gate panel padding** — Reduced from 56px 52px to 40px 20px on mobile so it fits smaller screens without horizontal overflow.

## KEY PATTERN: Beating Inline Styles

When HTML has `style="..."` on elements you can't easily change, the fix is:
- Add a CSS class to the element
- In `@media` block, add `class-rule{property:value!important}`

This is cleaner than editing every inline style. The `!important` in a media query only applies within that breakpoint, so desktop is unaffected.

## Deployment
- CF Pages: purebrain-staging deployed
- Deployment ID: eea0d211.purebrain-staging.pages.dev
- Cache: Pages token doesn't have zone cache permissions — CDN propagates automatically on Pages deploy
- Live: https://purebrain.ai/investors-v8/
