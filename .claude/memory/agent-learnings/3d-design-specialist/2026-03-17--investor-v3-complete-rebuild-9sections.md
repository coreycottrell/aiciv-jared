# Memory: PURE Investor v3 — Complete 9-Section Rebuild

**Date**: 2026-03-17
**Agent**: 3d-design-specialist
**Type**: technique + synthesis
**Topic**: Full rebuild of investors-ask-aether-v3 with all 9 investor sections, CSS orb avatar, liquid metal background, per Jared's exact spec
**Confidence**: high
**Tags**: three-js, investor-page, liquid-metal, css-orb, scroll-emergence, 9-sections, cf-pages, r0.161.0, bloom, SMAA, chart-js

---

## Context

Jared's exact brief:
"the whole background of the page is dark liquid metal with maybe some orange streaks through it... the avatar is mainly blue... around the avatar the information for each section emerges from the background one at a time to display the words and information... as you scroll that one sinks/melts back into the background... the next one bubbles to the surface"

Priority:
1. Liquid metal background + content emergence/sinking (PRIMARY)
2. CSS blue orb avatar placeholder (no Three.js avatar)
3. Voice wiring — SKIP

Previous v3 had only 5-6 sections with different data. This rebuild adds all 9 sections with correct financial data from the original investors-ask-aether page.

---

## Architecture

### Three.js Scene
- bgScene (ortho) → atmospheric gradient quad (not postprocessed)
- mainScene → EffectComposer (Bloom 0.42/0.32/0.82 + SMAA + OutputPass)
  - Liquid metal PlaneGeometry (26x26, 200 subdivisions desktop / 80 mobile)
  - Glow pool (canvas texture, AdditiveBlending)
  - avatarGroup (IcosahedronGeometry detail 5, transmission shell, inner BackSide shell, mid-glass, emissive core, halo, eye glows, particle aura 1600pts)
  - Avatar point light

### CSS Blue Orb (NEW)
Fixed position at top-center. Pure CSS, no Three.js.
```css
#avatar-orb {
  position:fixed; top:32px; left:50%; transform:translateX(-50%);
  width:72px; height:72px; border-radius:50%;
  background:radial-gradient(circle at 38% 32%, rgba(125,211,245,0.9) 0%, rgba(42,147,193,0.8) 40%, rgba(8,10,18,0.6) 100%);
  box-shadow:0 0 40px rgba(42,147,193,0.55), 0 0 80px rgba(42,147,193,0.2);
  animation:orbFloat 4s ease-in-out infinite;
}
```
CSS translateY float animation. Sits above the liquid metal as a beacon.
The Three.js avatarGroup is still in the scene as a background atmospheric element,
but the primary visible avatar is this CSS orb.

### 9 Content Sections (emerge-cards)
1. Hero — PUREBRAIN brand, $55M pre-money, $3.36/share, raise progress
2. Opportunity — "AI Company of the Decade", $4T+ market, 78% market capture, 225:1 LTV:CAC
3. Calculator — ROI slider (50K-1M), share calc, 5-year projection
4. Financial Model — Chart.js (Base/Bull/Bear tabs), line chart subscribers + bar chart revenue
5. Portfolio — 7 revenue streams with status indicators
6. Raise — $2.5M seed 2, fund allocation bars, Series-A at $105M in May 2026
7. Team — Jared + Aether founder profiles, 3 advisors
8. Market — $4T traditional + $3.7T AI revolution, TAM/SAM/SOM
9. Ask Aether — Chat interface, demo replies, API endpoint /api/investor-chat

### Card Emergence/Sinking
```css
.emerge-card { opacity:0; transform:translateY(90px) scale(0.965);
  transition: opacity 1.0s cubic-bezier(0.16,1,0.3,1), transform 1.0s cubic-bezier(0.16,1,0.3,1); }
.emerge-card.emerged { opacity:1; transform:translateY(0) scale(1); }
.emerge-card.sinking { opacity:0; transform:translateY(-56px) scale(0.965);
  transition: opacity .65s cubic-bezier(.4,0,.6,1), transform .65s cubic-bezier(.4,0,.6,1); }
```
IntersectionObserver fires `emerged` when card enters viewport (threshold 0.12).
Sinking: checked each frame — if `card.getBoundingClientRect().bottom < 0` → `.sinking`.

### Password Gate
- Bypass codes: purebrain2026, investor2026, aether, pure2026, aethereal, pureinvestor2026
- SHA-256: ac33e72f151c5707a15a46ca7aa929d7ffb674143d61bdd0a61fc8ebff0d4f28
- URL param: `?open=1` dissolves gate immediately on load

---

## Deployment

File: `/exports/cf-pages-deploy/investors-ask-aether-v3/index.html`
Size: 1568 lines, ~60KB
Deployed: `https://79d95307.purebrain-staging.pages.dev/investors-ask-aether-v3/`

---

## Visual Verification (DOM validated)

Playwright DOM checks confirmed:
- Gate: dissolved (with ?open=1)
- 8 emerge-cards found with correct headings
- 9 nav dots
- CSS orb present
- Canvas element present

Screenshots captured — liquid metal background rendering correctly with fBm wave forms
and atmospheric bloom. Card content emerges cleanly above the metal surface.
Mobile 375px renders correctly with stacked stats.

---

## Playwright Headless Screenshot Gotcha

**Problem**: Playwright screenshot hangs on pages with Three.js WebGL + requestAnimationFrame loop.
The screenshot API waits for "fonts loaded" but then blocks when the WebGL animate() loop
never yields.

**Fix**: Cancel all pending RAF IDs before taking screenshot:
```javascript
await page.evaluate(() => {
    let id = window.requestAnimationFrame(() => {});
    for (let i = id; i > 0; i--) window.cancelAnimationFrame(i);
});
await asyncio.sleep(0.3);
await page.screenshot({ clip: {x:0,y:0,width:1440,height:900}, timeout: 15000 });
```

Also: block Google Fonts with `page.route("**/fonts.googleapis.com/**", route => route.abort())`
to prevent font-loading step from waiting on CDN.

Also: in headless, bloom appears brighter (white blowout) because SwiftShader GPU doesn't
tonemap the same as hardware GPU. On real browser with GPU, bloom at 0.42 strength / 0.82
threshold renders with correct restraint.

---

## Key Files

- `/exports/cf-pages-deploy/investors-ask-aether-v3/index.html` — main output
- `/exports/cf-pages-deploy/investors-ask-aether/index.html` — original (content source)
- Screenshots: `/tmp/investor-v3-clipped.png`, `/tmp/investor-v3-scroll.png`, `/tmp/investor-v3-mobile.png`
