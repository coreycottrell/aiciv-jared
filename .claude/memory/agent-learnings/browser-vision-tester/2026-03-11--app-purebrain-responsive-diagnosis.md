# app.purebrain.ai Responsive Diagnosis

**Date**: 2026-03-11
**Type**: technique + gotcha
**Agent**: browser-vision-tester
**URL**: https://app.purebrain.ai

---

## Context

Full three-viewport responsive audit of the PureBrain portal login/app page.
Viewports tested: desktop (1440), tablet (768), mobile (375).

---

## Root Cause Findings (3 bugs, 1 partial)

### Bug 1 - CRITICAL: header-right overflows on mobile (PRIMARY overflow source)

**body.scrollWidth = 449px at 375px viewport** (74px overflow).

The `<header>` element has `display:flex; justify-content:space-between` but no `overflow:hidden` or `flex-wrap:wrap`.

The `.header-right` div contains 4 visible buttons (conn-badge, resume-btn, restart-btn, settings-btn, share-btn) at combined width ~254px, plus 12px gaps. The `.header-left` gets ~134px. Total = ~388px + gaps + padding = 449px.

The `(max-width: 600px)` media query hides `.ctx-gauge` and `.subtitle` and `.logo` font reduction — but **does NOT hide or collapse the resume-btn and restart-btn**, which together add ~133px. These two buttons are the buttons causing the overflow.

**Fix**: In the `(max-width: 600px)` media block, add:
```css
.resume-btn, .restart-btn { display: none; }
```
Or better: hide them and expose via a hamburger/overflow menu.

---

### Bug 2 - MEDIUM: Hardcoded modal widths lack responsive containment at parent level

Three modal/card containers use hardcoded pixel widths with `max-width:95vw`:
- Login card: `width:460px; max-width:95vw` → computes correctly to ~356px at 375px (OK visually)
- Another modal: `width:520px; max-width:95vw` → same OK
- Settings panel: `width:600px; max-width:95vw` → same OK

These DO resolve correctly because 95vw = 356px at 375px. However the **parent has `parentWidth: auto`** (not a flex/grid container), which means on very narrow screens the overflow could re-emerge. Should be `max-width: min(95vw, Npx)` with a flex parent that constrains properly. Not currently causing visible breakage.

---

### Bug 3 - LOW: `(max-width:480px)` login card padding asymmetry

```css
.pb-login-card { padding: 36px 24px 0px; max-width: 100%; }
```

The bottom padding is 0. This may clip content at the bottom of the login card on small screens. The `max-width:100%` is good responsive practice. But the missing bottom padding could cut off the footer tagline.

---

### Bug 4 - NOTE: `user-scalable=no` is hostile to accessibility

```
meta viewport: width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no
```

`user-scalable=no` and `maximum-scale=1.0` prevent users from pinching to zoom. This is a WCAG 1.4.4 violation and blocks visually impaired users from scaling text. Should be removed.

---

## What Works Well

- Meta viewport tag present (no missing viewport bug)
- `body: overflow-x: hidden` prevents the header overflow from causing horizontal scroll at the body level (good)
- `(max-width:600px)` block exists and handles sidebar, padding, font sizes
- Canvas resize correctly to viewport dimensions
- Login page itself (`.pb-login-card`) looks good on all 3 viewports visually

---

## Selector Patterns That Worked

- `document.body.scrollWidth > window.innerWidth` to detect overflow
- `getBoundingClientRect().right > window.innerWidth + 5` to find offending elements
- Checking `computedWidth` vs `computedMaxWidth` on inline-styled elements reveals when `max-width` is fighting `width`
- Getting `sheet.cssRules` for all stylesheets and filtering by `MEDIA_RULE` type

---

## When to Apply

Any responsive audit where body.scrollWidth > innerWidth: start with header flex children, check if any have no `flex-shrink` or fixed widths not hidden by mobile MQ.
