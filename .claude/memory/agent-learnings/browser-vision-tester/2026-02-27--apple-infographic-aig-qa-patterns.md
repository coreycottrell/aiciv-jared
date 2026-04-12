# Memory: Apple Infographic QA - aig- Class System

**Date**: 2026-02-27
**Type**: technique + pattern
**Topic**: Visual QA of Apple Leadership Infographic on purebrain.ai/your-ai-tim-cook/

---

## Infographic Structure Discovered

The Apple Leadership Infographic uses the `aig-` class prefix (Apple Infographic Grid).

### Precise DOM Positions (1280px viewport, page height 10551px)

| Element | Class | Y-position | Height |
|---------|-------|------------|--------|
| Section header | `.aig-outer-title` | 2724 | 22 |
| Main title "Two Eras..." | `.aig-main-title` | 2757 | 43 |
| Subtitle | `.aig-main-subtitle` | 2808 | 24 |
| Steve Jobs panel | `.aig-panel-1` | 2872 | 616 |
| macOS chrome bar | `.aig-chrome` | 2872 | 40 |
| macOS dots | `.aig-dot-red/yel/grn` | 2885 | 12 |
| SJ avatar | `.aig-avatar-jobs` | 2935 | 64 |
| SJ stat (+$344.5B) | `.aig-stat-jobs` | 2930 | 46 |
| SJ chart | `.aig-chart-wrap` | 3046 | 286 |
| SJ product chips | `.aig-icon-chip` | 3405 | 24 |
| Tim Cook panel | `.aig-panel-2` | 3507 | 616 |
| TC avatar | `.aig-avatar-cook` | 3571 | 64 |
| TC stat (+$3,353B) | `.aig-stat-cook` | 3565 | 46 |
| TC product chips row | `aig-icons-row` | 4032 | 101 |
| Insight callout (plain div) | no aig- class | 4163 | 137 |

### Insight Box: No .aig-insight Class
The insight callout box does NOT use `.aig-insight`. It's a plain `div` at y=4163.
Text: "Tim Cook didn't invent the next iPhone. He built the operational infrastructure..."
To find it: search elements in y=4100-4300 range containing this text.

---

## macOS Dots Colors (Verified)
- Red: `rgb(255, 95, 87)`
- Yellow: `rgb(255, 189, 46)`
- Green: `rgb(40, 200, 64)`
- Total count: 6 (3 per panel x 2 panels)

---

## Bar Chart Colors
- Steve Jobs bars: Blue (`rgb(42, 147, 193)` = Pure Tech Blue)
- Tim Cook bars: Green (`rgb(22, 163, 74)`)

---

## Product Chips (18 total)
Jobs era: iMac (1998), Mac OS X (2001), iPod (2001), iTunes (2003), MacBook Pro (2006), iPhone (2007), MacBook Air (2008), App Store (2008), iPad (2010), iCloud (2011)
Cook era: Mac Pro (2013), Apple Watch (2015), Apple Pay (2015), AirPods (2016), HomePod (2017), M1 Chip (2020), AirTag (2021), Vision Pro (2023)

---

## Image Rendering Pattern (IMPORTANT)
Both `amplify-founder` and `vc-fomo` images are wrapped in `div.tc-reveal.tc-visible`.

The `.tc-reveal` class has `opacity: 0` by default. The JavaScript IntersectionObserver adds `.tc-visible` which transitions to `opacity: 1`. In headless Playwright, even after scroll-triggering, the CSS transition timing can leave these at opacity:0.

**Correct capture sequence:**
1. Load page with networkidle
2. Scroll full page at 200px steps with 60ms waits (triggers lazy-load AND intersection)
3. Wait 1000ms extra after full scroll
4. Inject force-visible: `html body * { opacity: 1 !important; ... }`
5. Wait 800ms for the override to apply
6. Use `.scrollIntoView({behavior: 'instant', block: 'center'})` to center the image
7. Wait 600ms then screenshot

Note: `complete=True` and `naturalWidth=2560` in the DOM means the image IS loaded even if invisible.

---

## Screenshot Scroll Positions
To capture all key areas, use these scroll Y values at 1280x800 viewport:

| Screenshot | Scroll Y | What you see |
|-----------|---------|-------------|
| Infographic header | 2550 | "Two Eras of Apple Leadership" title + end of Section 2 |
| Steve Jobs panel top | 2800 | macOS chrome + SJ avatar + +$344.5B + start of chart |
| Steve Jobs chart+chips | 2980 | Chart bars + product chips |
| Tim Cook panel top | 3430 | macOS chrome + TC avatar + +$3,353B stat |
| Tim Cook chart+chips | 3620 | Green bar chart + product chips |
| Insight callout | 4050 | Insight box + start of Section 3 |

---

## SVG className Bug in Playwright Evaluate
When iterating `document.querySelectorAll('*')` and accessing `el.className`, SVG elements return an `SVGAnimatedString` object, not a string. Calling `.substring()`, `.includes()`, etc. throws TypeError.

**Fix**: Always guard with `typeof el.className === 'string'` or use `String(el.className || '')`.

---

## Page Structure Context
- Section 2 (The Problem / Hero's Delusion): ends around y=2700
- Apple Infographic: y=2724 to y=4300 (insight callout end)
- Section 3 (Soul vs Skeleton): starts at y=4540
- Soul vs Skeleton framework body: y=4738+
- amplify-founder image: y=935 (after hero)
- vc-fomo image: y=8597 (before closing CTA)
