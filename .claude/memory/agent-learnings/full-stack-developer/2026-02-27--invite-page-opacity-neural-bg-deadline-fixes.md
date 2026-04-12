# Memory: Invite Page Critical Fixes — opacity bug, neural bg, deadline, Tuesday→Wednesday

**Date**: 2026-02-27
**Type**: teaching
**Agent**: full-stack-developer
**File**: `/home/jared/projects/AI-CIV/aether/exports/purebrain-invite-only-page.html`

---

## The Invisible Element / Empty Space Bug (CRITICAL PATTERN)

**Problem**: Elements with `opacity: 0` that depend on CSS animations + IntersectionObserver remain invisible when WordPress theme CSS conflicts with animations. Result: huge empty gaps on page.

**Root cause**: CSS animations (`animation-fill-mode: both`) set initial state to `opacity: 0`. If WP theme CSS overrides or blocks animations, elements stay invisible forever while still taking up space.

**Solution pattern (3-layer defense)**:

1. **CSS default**: Set `opacity: 1` as the default. Elements are visible without JS/animation.
2. **JS gating**: Add `pb-js-ready` class to `body` via JS. Only then does CSS hide `pb-reveal` elements (because JS will reveal them via IntersectionObserver). Pattern:
   ```css
   /* Default: visible */
   .pb-reveal { opacity: 1; transform: none; }
   /* Only hide if JS is running (safe to animate) */
   body.pb-js-ready .pb-reveal { opacity: 0; transform: translateY(32px); }
   body.pb-js-ready .pb-reveal.pb-visible { opacity: 1; transform: none; }
   ```
3. **2-second hard fallback**: Force all elements visible after 2s regardless:
   ```js
   document.body.classList.add('pb-js-ready');
   setTimeout(function() {
     document.querySelectorAll('.pb-fade-in, .pb-reveal').forEach(function(el) {
       el.style.opacity = '1';
       el.style.transform = 'none';
     });
   }, 2000);
   ```
4. **`prefers-reduced-motion`**: Always include `opacity: 1 !important` here.

**For `pb-fade-in` (CSS animation)**: Use `animation-fill-mode: both` (not just `forwards`) — it starts from the keyframe `from` state and always ends at `to` state. The `opacity: 1` default ensures it shows even if animation is blocked.

---

## Fixed Background Layer Pattern (Neural Network / Ambient)

To add a fixed background visual BEHIND all WordPress content:

```html
<!-- Outside #pb-invite-page, before it -->
<div id="pb-neural-bg" aria-hidden="true">
  <svg class="pb-neural-svg">...</svg>
  <div class="pb-neural-overlay"></div>
</div>

<div id="pb-invite-page">
  ...page content...
</div>
```

```css
#pb-neural-bg {
  position: fixed;
  inset: 0;
  z-index: 0;
  pointer-events: none;
}
#pb-invite-page {
  position: relative;
  z-index: 1;  /* stays above background */
}
```

The gradient overlay (`radial-gradient` darker at center) ensures content readability while edges show the neural pattern.

---

## Deadline Timezone Math (EST deadlines in UTC)

- Wednesday March 4, 2026 11:59:59pm EST = **Thursday March 5, 2026 04:59:59 UTC**
- EST = UTC-5
- Formula: `EST deadline + 5 hours = UTC`
- Code: `var deadline = new Date('2026-03-05T04:59:59Z').getTime();`

---

## CTA Link Audit

All 8 CTA instances point to `https://purebrain.ai/pay-test-2/` (not password-protected):
- Hero primary CTA
- 4 pricing tier buttons (Awakened, Bonded, Partnered, Unified)
- Final big CTA
- Mobile sticky bar
- (one more in final section)

---

## Enhanced Orb Pattern (for dramatic ambient backgrounds)

```css
/* Blue orb: 800px, blur 200px */
/* Orange orb: 600px, blur 200px */
/* Purple accent orb: 550px, blur 180px, color rgba(58,96,171,0.1) */
/* Animation drift: 50px movement (vs original 30px) */
```

Adding a 3rd purple/indigo orb (`#3a60ab`) at ~10% opacity creates significant depth without overpowering the blue/orange brand colors.

---

## CSS Grain Texture (premium feel, no images)

```css
#pb-invite-page::before {
  content: '';
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 0;
  opacity: 0.02;
  background-image: repeating-radial-gradient(circle at 1px 1px, rgba(255,255,255,0.9) 0px, transparent 1px);
  background-size: 3px 3px;
}
```

Very subtle (opacity 0.02) but adds that expensive textured feel used in premium design.
