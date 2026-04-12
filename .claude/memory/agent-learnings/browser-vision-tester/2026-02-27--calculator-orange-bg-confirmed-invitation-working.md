# Memory: Feb 27 Final State Audit — Calculator Orange BG + Invitation Working

**Date**: 2026-02-27
**Type**: operational
**Topic**: Live state of calculator page 777 and invitation page 987

---

## Calculator Page 777 (purebrain.ai/ai-tool-stack-calculator/)

- Body background: `rgb(241, 66, 11)` — ORANGE (bug active)
- Page template: elementor_canvas
- The orange is a body-level issue, same as invitation page had earlier today
- Content renders on top of orange: headline, calculator card, nav tabs all visible
- Fix needed: `body { background-color: #0a0e1a !important; }` scoped via plugin CSS

## Invitation Page 987 (purebrain.ai/invitation/)

- Body background: `rgb(10, 14, 26)` — DARK NAVY (correct)
- Canvas present: 1440x900
- 3D neural network particle animation rendering in background
- Countdown timer live and ticking
- Spinner/preloader elements exist in DOM but page content renders correctly through them
- All three bugs from earlier today confirmed FIXED (&&  encoding, importmap, orange bg)

## Screenshots

- `exports/screenshots/audit-2026-02-27-final/02-calculator-viewport.png` — orange bg confirmed
- `exports/screenshots/audit-2026-02-27-final/04-invitation-viewport.png` — dark + working
- `exports/screenshots/audit-2026-02-27-final/05-invitation-after-6s.png` — 3D particles visible

## Key Pattern

Same orange body background bug (rgb 241,66,11) can affect any elementor_canvas page.
Fix is always: body background-color override with !important in plugin CSS.
Invitation page was fixed today. Calculator page 777 still needs the same fix.
