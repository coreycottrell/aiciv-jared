# Memory: Sandbox-3 Mobile Missing Sections - TWO Bugs (display:none + transparent bg)

**Date**: 2026-03-09
**Agent**: browser-vision-tester
**Type**: teaching + pattern + gotcha
**Tags**: sandbox3, mobile, display:none, transparent-background, video-overlay, active-class, js-controlled, pay-test

---

## Context

Diagnosed why sandbox-3 (purebrain.ai/pay-test-sandbox-3/) was missing Compare PureBrain pills, "See Why PureBrain Is Different" heading, Awaken CTA, and pricing section on mobile (375x812). Page showed huge empty space with only video background after the Calculator CTA section.

---

## Root Cause: TWO Separate Bugs

### Bug 1: `.pricing-section` and `.comparison-section` are `display: none` by default in CSS

**Exact rule found in inline `<style>` tag (the page's embedded CSS):**

```css
.pricing-section {
    padding: 120px 24px;
    background: linear-gradient(rgba(10,10,10,0.6) 0%, transparent 100%);
    display: none;   /* <-- THIS IS THE BUG */
    position: relative;
    z-index: 1;
}
.pricing-section.active {
    display: block;   /* shown only when .active class added by JS */
    animation: 0.8s ease fadeInUp;
}

.comparison-section {
    padding: 100px 24px;
    position: relative;
    z-index: 1;
    background: transparent;
    display: none;   /* <-- THIS IS THE BUG */
}
.comparison-section.active {
    display: block;
}
```

**How sections are revealed (by design):**
- User chats with the AI chatbox
- After sufficient conversation, JS calls `window.revealPricing()`
- This adds `.active` class to `#pricing` and `#compare` sections
- A CTA button appears: "Click to see what [aiName] can do for you" which triggers `window.revealPricing()`
- This is intentional UX - sections are gated behind chat engagement

**Why it shows as "missing" on mobile:**
- On mobile, users may be scrolling past the chatbox without engaging
- Or: after payment on mobile, the revealPricing() trigger may not fire correctly
- Or: the user is on the page WITHOUT going through the chat flow (direct URL access)

### Bug 2: Transparent backgrounds make revealed sections invisible anyway

Even AFTER `.active` is added and sections become `display:block`:
- `#pricing` background: `rgba(0, 0, 0, 0)` - fully transparent
- `#compare` background: `transparent`
- The `.video-background` is `position:fixed; z-index:0; height:812px; width:375px`
- `#videoOverlay` has `background: rgba(0,0,0,0.3)` dark overlay

**Result**: Transparent section backgrounds on mobile let the dark video overlay show through, making content effectively invisible against the near-black background. Text is white-on-near-black = readable on desktop (larger viewport, brain video more visible), but on mobile the fixed 812px video + overlay fills the entire viewport creating a dark wash.

---

## The Fix

**Fix for Bug 1** - Add solid bg to revealed sections on mobile:

```css
@media (max-width: 767px) {
    .pricing-section.active,
    .comparison-section.active {
        background: #080a12 !important;
        position: relative !important;
        z-index: 5 !important;
    }
}
```

**Fix for Bug 2** - If sections need to always be visible (not gated), change CSS:

```css
/* Option A: Remove the gating (show always) */
.pricing-section,
.comparison-section {
    display: block !important;  /* override the display:none */
    background: #080a12;
    position: relative;
    z-index: 5;
}

/* Option B: Keep gating but fix mobile background after reveal */
@media (max-width: 767px) {
    .pricing-section.active,
    .comparison-section.active {
        background: #080a12 !important;
        z-index: 5 !important;
    }
}
```

**The right fix depends on whether Jared wants the sections always visible or gated behind chat.**

---

## Key Diagnostic Findings

- Page height: 15,083px (sections hidden), 23,311px (after both sections revealed)
- `#pricing` at offsetTop: ~13,490px (when revealed)
- `#compare` at offsetTop: ~10,826px (the comparison table section)
- The sections ARE in the DOM - just CSS `display:none`
- `.elementor-section` selector returned 0 results - page uses custom sections NOT Elementor sections
- The bypass word is `'pb-full-bypass'` typed in chat input
- `window.revealPricing()` is the function that triggers visibility

---

## Diagnosis Technique Used

1. Playwright screenshot full page - confirmed content truncates early
2. `document.querySelector('#pricing').offsetHeight` = 0 (zero height = display:none)
3. Loop all `document.styleSheets` looking for rules targeting `#pricing` / `.pricing-section`
4. Found: `.pricing-section { display: none; }` in inline style tag
5. Found: `.pricing-section.active { display: block; }` - JS-controlled
6. Force-tested by adding `.active` class via JS: heights jumped from 0 to 5,976px
7. But screenshots still black - confirmed second bug (transparent bg + video overlay)

---

## What Made This Different from pay-test-2

- pay-test-2: sections were always visible but had transparent backgrounds (opacity issue)
- sandbox-3: sections have BOTH display:none (gating) AND transparent backgrounds (rendering issue)
- Two separate problems requiring two separate fixes

---

## Page Architecture Notes

- Page uses custom HTML sections (not Elementor sections) inside a single Elementor HTML widget
- The entire page content is inside `.elementor-element-3b66b1a` widget
- `#pricing`, `#compare` are `<section>` elements with IDs
- `window.revealPricing()` is the public function to reveal them
- State object: `{ pricingRevealed: false, ... }` tracks whether sections are shown

---

## Screenshots

Directory: `/home/jared/projects/AI-CIV/aether/exports/screenshots/sandbox3-mobile-diagnosis-20260309/`
- `002-mobile-full-page.png` - Full page before fix (content truncates after calc CTA)
- `022-after-bypass-full-page.png` - Full page after forcing sections active (reveals true size)
