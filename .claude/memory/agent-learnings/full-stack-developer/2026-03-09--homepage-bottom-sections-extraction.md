# Homepage Bottom Sections Extraction Pattern

**Date**: 2026-03-09
**Type**: operational
**Topic**: Extracting self-contained bottom sections from purebrain.ai homepage for reuse

## Task

Extract the bottom 7 sections from the rendered homepage (page-id-11) for drop-in reuse on
pay-test-2 and sandbox-3 pages. Output: `/tmp/homepage_bottom_sections.html`

## Key Finding: Calculator CTA is JS-injected

The Calculator CTA section ("FREE TOOL / How Much Are You Wasting...") does NOT exist as static
HTML in the page. It is dynamically injected at runtime via `<script id="pb-calc-cta-injector">`.

The injector has 4 strategies to find the right insertion point:
1. Find "Compare PureBrain" text container → insert before its Elementor section
2. Find "See Why PureBrain is Different" heading → insert before its Elementor section
3. Find `#pb-awaken-cta-section` by ID → insert before it
4. Last resort: insert before `footer, .site-footer, #footer`

**Implication**: When adding these sections to pay-test-2/sandbox-3, the Calculator CTA should
be added as STATIC HTML (not rely on the injector), OR the injector script should also be
included. The extracted file uses static HTML for reliability.

## Sections Extracted (in order)

1. **Calculator CTA** (static version of JS-injected section) — gradient bg, "Free Tool" label,
   h2, description, orange CTA button
2. **Compare PureBrain** — dark `#0a0e1a` bg, 8 comparison pills + "See All Comparisons" button
3. **Awaken CTA** — transparent bg with z-index:2 (video shows through), blue→orange hover button
4. **See Why PureBrain Is Different** — 50% opacity dark bg, orange border top/bottom, orange button
5. **Footer** — `.footer` class, Pure Technology logo, © 2026, 2-row links
6. **Legal Footer** — `#purebrain-legal-footer`, Privacy Policy / Terms of Service / © 2026
7. **Aether Footer Bar** — `#pb-aether-footer`, fixed position, "Built by AETHER" with pulse animation

## CSS Variables Required

The footer uses `var(--grey)` and `var(--white)`. These are defined in a `:root` block inside
the main page's embedded `<style>`. The extracted file includes its own `:root` block to ensure
these work standalone.

## File Structure

- `<style>` blocks are all scoped with unique IDs
- All CSS variables are inlined in a standalone `:root` block
- All hover effects use inline `onmouseover`/`onmouseout` (no external JS needed)
- The `.footer` CSS class styles are fully self-contained in `<style id="pb-footer-component-css">`
- The Aether footer CSS uses `@keyframes pb-aether-pulse` for the AETHER text glow animation

## Deployment Notes

- When deploying to WP pages: wrap in `<!-- wp:html -->` block (per WP HTML deployment rule)
- Page template must be `elementor_canvas` for non-blog pages
- The `#pb-awaken-cta` section has `z-index:2` — this is intentional so the transparent
  background shows the video through on video-background pages. On non-video pages it just
  renders on the dark page background.
- The Aether footer bar is `position:fixed` — it will overlay any page it's added to

## Source

Homepage fetched via: `curl -s "https://purebrain.ai/?password=PureBrain.ai253443$$"`
Key line numbers in source:
- Compare PureBrain section: ~14437
- Awaken CTA: ~14461
- See Why Different: ~14479
- Footer: ~14492
- Legal Footer: ~14643
- pb-calc-cta-injector script: ~14725
- pb-aether-footer CSS: ~15076
- pb-aether-footer HTML: ~15292
