# Memory: Graham Martin Mini-Site CSS Fixes — Padding + Hamburger Menu

**Date**: 2026-03-01
**Type**: pattern + technique
**Topic**: Multi-page CSS fix — padding reduction + mobile hamburger menu for fixed dual-nav

---

## What Was Fixed

3 issues across all 5 Graham Martin investor pages:
1. Too much padding between nav, sub-nav, and hero content
2. Hero section had excess top padding (100px/120px on top of 104px body offset)
3. Mobile: sub-nav pills disappeared completely — replaced with hamburger dropdown

---

## Pages Updated

| Page | WP ID | URL |
|------|-------|-----|
| Overview | 1150 | /purebrain-for-graham-martin/ |
| Casino AI | 1153 | /purebrain-for-graham-martin-casino-ai/ |
| Chairman | 1154 | /purebrain-for-graham-martin-chairman-intelligence/ |
| Virya VC | 1155 | /purebrain-for-graham-martin-virya-intelligence/ |
| Responsible Gambling | 1156 | /purebrain-for-graham-martin-responsible-gambling/ |

---

## CSS Architecture (Dual Fixed Nav)

- `#gm-nav` fixed at top: height ~62px (padding 16px + content)
- `#gm-mini-nav` fixed at `top: 61px`: height ~38px
- Total fixed nav height: ~100px
- `body { padding-top: 100px }` (was 104px) — accounts for both navs
- Mobile: body padding 88px (was 94px)

---

## Hero Padding Fix

**Before**: `padding: 100px 24px 60px` (Overview) / `120px 24px 70px` (sub-pages)
**After**: `padding: 48px 24px 60px` (all pages)

The 100-120px top padding on the hero was ADDITIVE on top of the body offset, creating massive dead space. The body padding-top already handles the nav offset — the hero only needs enough padding to breathe from the content start.

---

## Hamburger Menu Pattern

Structure: Two separate elements —
1. `<button class="gm-hamburger" id="gm-hamburger-btn">` — hidden on desktop, shown on mobile
2. `<div class="gm-mini-nav-dropdown" id="gm-mini-nav-dropdown">` — fixed positioned overlay

CSS key rules:
```css
/* Desktop: hamburger hidden, pills visible */
.gm-hamburger { display: none; }

/* Mobile: pills hidden, hamburger visible */
@media (max-width: 768px) {
  .gm-mini-nav-pill { display: none; }
  .gm-hamburger { display: inline-flex; }
  .gm-mini-nav-dropdown { top: 88px; }
}

/* Dropdown: hidden until .open class added */
.gm-mini-nav-dropdown { display: none; }
.gm-mini-nav-dropdown.open { display: flex; }
```

JS pattern (vanilla, no deps):
```js
btn.addEventListener('click', function(e){
  e.stopPropagation();
  drop.classList.toggle('open');
});
document.addEventListener('click', function(){ drop.classList.remove('open'); });
drop.addEventListener('click', function(e){ e.stopPropagation(); }); // keep open when clicking inside
```

The dropdown pills use `display: flex` with `width: 100%` for full-width tap targets on mobile.

---

## Deployment Pattern

These pages use `elementor_canvas` template but content is stored as `<!-- wp:html -->` blocks (NOT in `_elementor_data`). Standard REST API POST to `/wp-json/wp/v2/pages/{id}` works.

**Critical**: Use curl with `--data-binary @tmpfile.json` for large HTML payloads. Python `urllib` may 403 on large bodies due to WAF.

After deploy: `DELETE /wp-json/elementor/v1/cache` to clear Elementor cache.

---

## Link Audit Results (2026-03-01)

All 5 sub-nav cross-links verified 200 OK. Mailto links use `jared@puretechnology.nyc`. Google Fonts preconnect returns 404 (expected — it's a browser hint, not a page). All actual navigable links pass.
