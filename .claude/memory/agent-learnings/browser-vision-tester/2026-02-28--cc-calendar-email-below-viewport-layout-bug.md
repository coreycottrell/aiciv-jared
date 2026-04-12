# cc.purebrain.ai Calendar & Email Tab Layout Bug

**Date**: 2026-02-28
**Agent**: browser-vision-tester
**Type**: gotcha

## Context

Z-index fix was applied to cc.purebrain.ai to make Calendar and Email tabs visible above the neural canvas. The fix set:
- canvas: z-index -1
- calendar-view: z-index 100
- email-view: z-index 100

## Verification Findings

### PASS - Z-index fix is confirmed correct
- canvas z-index: -1 (correct, forced behind content)
- calendar-view z-index: 100 (correct)
- email-view z-index: 100 (correct)
- Both views have display: block and visibility: visible

### FAIL - Content positioned below viewport (NEW BUG FOUND)

Both `#calendar-view` and `#email-view` have:
```
rect: { top: 900, left: 120, width: 1200, height: ... }
```

The viewport is 900px tall. These views START at y=900 - exactly at the bottom edge, so nothing renders visually. User sees a black screen.

### Calendar content IS loaded and real
- 1028 DOM children in #calendar-view
- Events visible in DOM: "Family day Google", "Get Ready for Bed", etc.
- Date bar with inputs and "Load Events" button
- gw-events-list with real event cards

### Email content IS loaded and real
- "No messages" empty state with Outlook connect link
- Inbox for jared@puretechnology.nyc

## Root Cause Hypothesis

The layout container (sidebar + main content area) has a fixed height of 900px matching the viewport. When tabs like Calendar and Email are set to `position: relative` and placed in the flow AFTER the main content container, they push below. The sidebar occupies the left 120px, main content area is 1200px wide. The views appear to be stacked vertically in the DOM rather than being positioned within the content area.

Likely cause: The `.visible` class on the view div or the parent container has a `position` or `min-height` property that pushes the content below y=900 rather than placing it within the content area.

## Fix Needed

The fix should position calendar-view and email-view WITHIN the content area (top: ~50px for the topnav), not below it. Options:
- Check if the app container or content wrapper has a `height: 100vh` that causes the tab views to stack below
- The views may need `top: 0` relative to their container, or the container needs `overflow: auto`
- Check how tasks-view is positioned (it renders correctly) vs calendar-view positioning difference

## Key Selector for Future Testing

```python
# Check view positioning
view = page.evaluate("document.querySelector('#calendar-view').getBoundingClientRect()")
# GOOD: top should be < 900 (within viewport)
# BAD: top == 900 (below viewport)
```

## Logo Status - CONFIRMED CORRECT

The topnav logo is now showing the correct PB branding:
- SVG hexagon icon with blue-to-orange gradient
- SPAN 'PUREBR' in rgb(42, 147, 193) = Pure Tech Blue
- SPAN 'AI' in rgb(241, 66, 11) = Pure Tech Orange
- SPAN 'N' in rgb(42, 147, 193) = Pure Tech Blue
- Logo reads: "PB [hexagon] PUREBRAIN" in correct brand colors
