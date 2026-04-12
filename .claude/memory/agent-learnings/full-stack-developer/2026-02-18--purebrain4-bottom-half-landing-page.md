# PureBrain 4 — Bottom Half Landing Page

**Date**: 2026-02-18
**Type**: operational + teaching
**Agent**: full-stack-developer

---

## What Was Built

Created the complete bottom half of the /purebrain-4/ landing page.

**File**: `/home/jared/projects/AI-CIV/aether/exports/purebrain-4/bottom-half.html`
**Size**: 56K, 1826 lines
**Sections**: 8 sections + CSS + JS, all inline

---

## Sections Delivered

1. **Post-Awakening Bridge** — 3-slide animated carousel with auto-advance (4s), prev/next/dot controls
2. **Pricing** — 2 prominent tiers (Awakened $79, Bonded $149 RECOMMENDED), hidden tiers expand via "View All Plans" toggle
3. **Comparison Table** — 3-tier feature matrix with featured column highlight for Bonded
4. **Testimonials** — 3-card grid with star ratings and role labels
5. **FAQ** — 6-item accordion, only one open at a time, smooth max-height animation
6. **Final CTA** — Large full-width call to action with radial glow background
7. **Footer** — 3-column layout, social SVG icons (LinkedIn, Bluesky, Instagram, Facebook), legal links
8. **Exit Intent Popup** — Desktop (mouseleave), mobile (popstate), sessionStorage dedup, Escape key closes

---

## Brand Patterns Used

- Colors: `--blue: #2a93c1`, `--orange: #f1420b`, `--dark-bg: #0a0a1a`
- Fonts: 'Oswald' for headings, 'Plus Jakarta Sans' for body
- PUREBRAIN.ai logo text: PUREBR (blue) + AI (orange) + N (blue) + .ai (white)
- PayPal button gradient: orange on featured/CTA, blue-tinted ghost on secondary

---

## PayPal Integration Pattern

```html
<form action="https://www.paypal.com/cgi-bin/webscr" method="post" target="_blank">
  <input type="hidden" name="cmd" value="_xclick">
  <input type="hidden" name="business" value="support@puremarketing.ai">
  <input type="hidden" name="item_name" value="PB-AWAKENED|PB-BONDED|PB-PARTNERED">
  <input type="hidden" name="amount" value="79.00|149.00|499.00">
  <input type="hidden" name="currency_code" value="USD">
  <input type="hidden" name="return" value="https://purebrain.ai/thank-you/">
  <input type="hidden" name="cancel_return" value="https://purebrain.ai/purebrain-4/">
  <input type="hidden" name="no_note" value="1">
  <input type="hidden" name="no_shipping" value="1">
  <input type="hidden" name="rm" value="1">
  <button type="submit">...</button>
</form>
```

`rm=1` = POST redirect (cleaner than GET). `no_note` and `no_shipping` suppress PayPal extras.

---

## CSS Architecture Lessons

- CSS custom properties (`--blue`, `--orange`, etc.) in `:root` make brand theming trivial across 1800 lines
- `clamp()` for responsive font sizes: `font-size: clamp(2rem, 4vw, 3rem)`
- Hidden tiers use `display:none` → `display:grid` (not `visibility`) since grid is needed for layout
- FAQ accordion uses `max-height: 0` → `max-height: 400px` with `overflow:hidden` for smooth expand
- Carousel uses `flex` with `transform: translateX(-N%)` — simplest reliable approach

---

## Exit Intent Popup Pattern

```javascript
// Desktop: mouse leaves top of viewport
document.addEventListener('mouseleave', function (e) {
  if (e.clientY <= 0 && !exitShown) showExitPopup();
});

// Mobile: back button
window.history.pushState(null, '', window.location.href);
window.addEventListener('popstate', function () {
  if (!exitShown) {
    showExitPopup();
    window.history.pushState(null, '', window.location.href); // keep on stack
  }
});

// Session dedup
sessionStorage.getItem('exitPopupShown') // skip if already fired this session
```

---

## Integration Notes

This file is designed as a **standalone HTML file** to be:
- Previewed locally as a browser file
- Merged with the top half (top-half.html from another agent) for a complete page
- Deployed to WordPress via REST API (page ID approach used for purebrain-3)

For WordPress deployment: same pattern as purebrain-3 (page ID 338). Create new page for purebrain-4, inject HTML into `_elementor_data[0].elements[0].settings.html`, trigger cache bust with second POST.

---

## Dead Ends Avoided

- Do NOT use `:hover` in inline WordPress styles — use JS `onmouseover` instead
- Do NOT use `visibility: hidden` for toggle — `display` is needed for grid layout
- FAQ max-height must be large enough for longest answer (400px safe)
