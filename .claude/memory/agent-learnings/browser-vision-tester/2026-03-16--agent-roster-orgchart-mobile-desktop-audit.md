# Agent Roster Orgchart Mobile/Desktop Audit

**Date**: 2026-03-16
**Agent**: browser-vision-tester
**Type**: technique + pattern
**URL**: http://localhost:8097 (app.purebrain.ai:8097)

---

## Context

Full visual audit of the Agent Roster panel's 3 view toggle buttons (grid, list, orgchart) on desktop (1440px) and mobile (375px). Jared reported he can't see the orgchart view on mobile.

---

## Key Findings

### FINDING 1: Orgchart button IS visible on mobile (375px)
- All 3 toggle buttons visible at positions: Grid(278,59), List(305,59), Orgchart(332,59)
- `toggle_overflows: False` — buttons stay within 375px viewport
- CSS uses `order: 2; margin-left: auto` at `(max-width: 600px)` — moves toggle to right side of header

### FINDING 2: Orgchart RENDERS on mobile but is horizontally too wide
- `orgchart-container` renders correctly, `display: block`, `overflow: auto`
- `oct-tree` width = 454px on a 375px viewport = 79px OVERFLOW
- User must horizontally scroll to see right side of tree (CMO branch)
- Only 26% of tree visible vertically without scroll (388px visible, 1504px total scroll height)

### FINDING 3: Desktop orgchart is FULLY WORKING
- All 3 toggle buttons visible and functional
- Orgchart renders complete tree: TC (Primary) → CTO + CMO → all departments
- 555 DOM elements in orgchart container
- Scrollable: 1290px wide, 827px tall scroll area

### FINDING 4: Container class naming gotcha
- The orgchart container uses ID `#orgchart-container`, NOT class `.agents-orgchart`
- Searching `.agents-orgchart` yields nothing — always use `document.getElementById('orgchart-container')`
- The visible tree uses `.oct-tree`, `.oct-row`, `.oct-col`, `.oct-node` classes

---

## Root Cause for Mobile "Can't See Orgchart"

The button IS there and clickable. The issue is likely:
1. User doesn't know to look top-right for 3 small icon buttons (grid=▦ list=☰ orgchart=○)
2. On mobile the header wraps: title row 1, toggle+stats row 2 — toggle buttons are small (25x21px)
3. After clicking orgchart button, only the top ~25% of tree is visible and the tree is 79px wider than screen

The report button (○ circle) may be mistaken for a radio button/selection indicator, not an orgchart toggle.

---

## CSS Architecture (key facts for fixes)

```css
/* Header responsive layout at 600px */
@media (max-width: 600px) {
    .agents-header { gap: 6px; }
    .agents-stats { order: 3; width: 100%; margin-left: 0; }
    .agents-view-toggle { order: 2; margin-left: auto; }
    .agents-title { order: 1; }
}

/* Orgchart container */
.orgchart-container { flex: 1; overflow: auto; padding: 16px 12px 24px; }

/* Tree */
.oct-tree { display: inline-flex; flex-direction: column; align-items: center; min-width: 100%; }

/* Mobile node sizing */
@media (max-width: 768px) {
    .oct-node { min-width: 80px; max-width: 110px; }
}
```

The `oct-tree` is `inline-flex` with `min-width: 100%` — at 375px, "100%" still expands to fit content which is wider than 375px (nodes need 454px total).

---

## Fix Options for Mobile Width

Option A: Scale down `max-width` of nodes at `(max-width: 480px)`:
```css
@media (max-width: 480px) {
    .oct-node { min-width: 68px; max-width: 90px; }
    .oct-node.tier-primary { min-width: 80px; }
}
```

Option B: Add horizontal scroll affordance (pinch-to-scroll hint or scroll indicator):
The `overflow: auto` already allows scrolling but there's no visual cue.

Option C: Zoom-out scale transform on mobile:
```css
@media (max-width: 480px) {
    .oct-tree { transform: scale(0.82); transform-origin: top center; }
}
```

---

## Screenshot Evidence

- `/tmp/portal-orgchart-audit/03-desktop-agent-roster-open.png` — desktop grid view
- `/tmp/portal-orgchart-audit/04-desktop-orgchart-clicked.png` — desktop orgchart clicked (full tree)
- `/tmp/portal-orgchart-audit/04e-desktop-header-full-row.png` — header with all 3 buttons
- `/tmp/portal-orgchart-audit/09-mobile-agents-panel-after-js-click.png` — mobile grid view with buttons visible
- `/tmp/portal-orgchart-audit/10-mobile-orgchart-clicked.png` — mobile orgchart view (TC top visible)
- `/tmp/portal-orgchart-audit/11-mobile-orgchart-scrolled.png` — mobile orgchart scrolled down
- `/tmp/portal-orgchart-audit/13-desktop-orgchart-mid.png` — full desktop tree

---

## Portal Navigation Gotcha (Mobile)

On mobile, the left sidebar nav is not visible in the viewport.
Agent Roster panel nav item is `[data-panel="agents"]` — it exists in DOM but isn't in visible nav.
The bottom tab bar shows: Chat, Terminal, Earn, Saved, More.
"More" was not visible (element not interactive via Playwright click — off-screen).
Opening via JS: `document.querySelector('[data-panel="agents"]').click()` works.

This means the USER also has trouble navigating to Agent Roster on mobile — the "More" tab may not be working properly either. Worth a separate audit.
