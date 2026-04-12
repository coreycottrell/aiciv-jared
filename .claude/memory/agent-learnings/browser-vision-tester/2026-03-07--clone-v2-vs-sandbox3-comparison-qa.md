# Clone v2 QA — homepage-clone-test vs pay-test-sandbox-3

**Date**: 2026-03-07
**Agent**: browser-vision-tester
**Type**: pattern + gotcha + operational
**Tags**: clone-test, sandbox3, pricing-section, display-none, password-gate, mobile, desktop, comparison-qa

---

## Task

Side-by-side visual comparison of:
- Reference: `https://purebrain.ai/pay-test-sandbox-3/`
- Clone: `https://purebrain.ai/homepage-clone-test/`

Viewports: mobile 375x812 and desktop 1440x900.

---

## CRITICAL FINDING: Sandbox-3 is Password-Protected

**Sandbox-3 is WP password-gated** (`input[name=post_password]`, `#pwbox-0`). Headless Playwright sees ONLY the password gate screen — not the actual page content. `?bypass=true` URL param does NOT bypass the WP password gate (bypass=true is a different system — PayPal/waitlist bypass, not WP authentication).

**Impact**: Cannot do direct headless comparison of sandbox-3 content from Playwright. Only the clone page (`/homepage-clone-test/`) is publicly accessible.

**Teaching**: When comparing a password-protected page to its clone, use the WP REST API or admin cookie injection to access the reference page in headless mode. `?bypass=true` is NOT the WP password bypass.

---

## CRITICAL BUG FOUND: Pricing Section display:none on Clone

### The Bug

`.pricing-section` on `/homepage-clone-test/` has `display: none` in its base CSS:

```css
.pricing-section {
    padding: 120px 24px;
    background: linear-gradient(rgba(10, 10, 10, 0.6) 0%, transparent 100%);
    display: none;   /* <-- BASE STATE IS HIDDEN */
    position: relative;
    z-index: 1;
}

.pricing-section.active {
    display: block;
    animation: fadeInUp 0.8s ease;
}
```

The pricing section ONLY becomes visible when the `.active` class is added by JavaScript. But no JS is adding `.active` to it on the clone page — the section remains hidden.

**Result**: 3 pricing cards with "Reserve Your AI Now" buttons, "NO PAYMENT TODAY" badges, and all tier content is completely invisible on the clone page. Users see no pricing section at all.

### Evidence

- All `.pricing-card` elements: width=0, height=0
- All `.pricing-card__no-payment` badges: `visible=False`, `display=block`, `width=0`, `height=0`
- `window.getComputedStyle('.pricing-section').display` = `"none"`
- The ancestor chain above `.pricing-section` is all visible — the `.pricing-section` itself is the culprit

### Where pricing section should appear

Based on heading structure, it should appear BETWEEN:
- y=6844: "Begin Your Awakening" (chat section)
- y=7890: "What You Actually Get"

The heading "Bring Your AI Fully Online" exists in the DOM at y=0 (inside the hidden section).

---

## Clone Page: What IS Rendering Correctly

### Desktop 1440x900

| Feature | Status |
|---------|--------|
| Background video (`bgVideo`) | PLAYING — `PureResearch.ai-1.mp4`, fixed z=-1, paused=false |
| Body background | `rgb(10, 14, 26)` (#0a0e1a) — correct dark navy |
| Hero section | Full hero with PURE BRAIN logo, tagline, "Awaken Your PURE BRAIN" CTA |
| Demo video player | Present (`demoVideo`, `pbDemoVideo`), correct sources |
| Footer logo | Side-by-side Pure Technology logo, correct file |
| Footer copyright | "© 2026 Pure Technology Inc." |
| Footer links | Privacy & Terms, Contact Us, Team, PureTechnology.ai, PureMarketing.ai, PureInfluence.ai |
| Comparison section | Present (vs Jasper, vs Perplexity, etc.) |
| Testimonials | Present |
| Overall dark theme | Correct — all sections dark |

### Mobile 375x812

| Feature | Status |
|---------|--------|
| Background video | PLAYING — same PureResearch.ai-1.mp4 |
| Hero | Full hero visible, logo correct |
| Footer logo | Side-by-side logo, 240x117px (from 2560x1250 source) |
| Overall layout | Pages scroll correctly, content renders |

---

## NO PAYMENT TODAY Badges

- **Text color**: `rgb(34, 197, 94)` (green) — correct
- **CSS**: `display: block`, `visibility: visible`, `opacity: 1`
- **Problem**: width=0, height=0 because their PARENT (`.pricing-card`) is inside `.pricing-section` which is `display: none`
- **All 3 badges**: `pricing-card--featured`, `pricing-card--small` x2

---

## Button Text Comparison

| Page | Button Text Found |
|------|------------------|
| Sandbox-3 (headless) | "Awaken Your Personal AI Partner Today" (Elementor button, outside pricing section) |
| Clone (desktop) | "Reserve Your AI Now" x3 — but ALL HIDDEN in display:none pricing section |
| Clone (mobile DOM) | "Reserve Your AI Now" x3 — also hidden |

The clone does have the correct "Reserve Your AI Now" text — it's just hidden inside the display:none pricing section.

---

## Footer Analysis (Clone)

- Logo file: `MA1.BI-1.2.6-001-211107-Side-by-Side-Main-Orange-PT-scaled.png` (correct full side-by-side)
- Mobile rendered: 240x117px
- Desktop: visible, proportioned correctly in screenshot
- Copyright: "© 2026 Pure Technology Inc." — correct

---

## Screenshots Captured

Directory: `/home/jared/projects/AI-CIV/aether/exports/screenshots/clone-comparison-20260307/`

Key files:
- `mobile_clone_viewport.png` — hero with bg video, mobile
- `desktop_clone_viewport.png` — hero with bg video, desktop
- `mobile_clone_scroll_95.png` — footer area (best footer shot)
- `desktop_clone_footer.png` — footer (bg video still playing)
- `desktop_clone_begin_awakening.png` — section near where pricing should be

---

## Fix Required

Add JavaScript to the clone page that calls `.pricing-section.classList.add('active')` at page load (or after a scroll/trigger event matching how sandbox-3 handles it).

Check sandbox-3's actual JS (need WP admin or cookie access) to confirm what triggers `.active` — likely either:
1. Immediate on DOMContentLoaded
2. IntersectionObserver when user scrolls to pricing section
3. After a waitlist interaction

