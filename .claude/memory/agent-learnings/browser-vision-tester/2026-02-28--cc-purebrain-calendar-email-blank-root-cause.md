# cc.purebrain.ai Calendar & Email Blank — Root Cause Analysis

**Date**: 2026-02-28
**Agent**: browser-vision-tester
**Type**: gotcha + pattern

## Context

Jared reported Calendar and Email tabs show nothing (blank dark screen) at cc.purebrain.ai.

## Root Cause: CSS z-index / visibility — `#calendar-view` and `#email-view` are BEHIND the neural canvas

### What switchView() does:
```javascript
// Adds class "visible" to either #calendar-view or #email-view
calView.classList.add('visible');
// CSS: .calendar-view.visible, #email-view.visible { display: block; }
```

### What's wrong:
The `#neural-canvas` (3D particle animation) sits on top of the calendar/email content area.
The sections ARE rendering (DOM has full event data, 127 event cards loaded), but the neural canvas
overlays them with z-index priority, making them visually invisible.

Evidence: Full-page screenshot (cc_cal_loaded.png) at 1280px wide shows events when scrolling
full page, but 1440x900 viewport screenshot shows ONLY the neural canvas — meaning the canvas
covers the content at standard viewport sizes.

### Confirmed:
- `/api/calendar/events` returns 200 with real events (Family day, Bed Time, Get Ready for Bed, etc.)
- `/api/email/inbox` returns 200 with `{"messages":[],"pagination":{...}}` — empty but not erroring
- DOM contains all calendar event cards (127 `.gw-event-time` divs populated)
- No 401 errors, no CORS errors, no JS console errors
- `credentials: 'include'` IS present on all fetch calls — that's not the issue

## Secondary Bug: All-Day Events HTML Escaping

In `gwLoadCalendar()`, the all-day time string is built as:
```javascript
timeStr = '<span class="gw-event-allday">All Day</span>';
// Then assigned via:
timeDiv.innerHTML = timeStr;  // BUG: gets double-escaped
```
Result: 3 all-day events show literal text `<span class="gw-event-allday">All Day</span>` 
instead of the styled "All Day" badge.

## Email Tab Status

Truly empty — no Outlook/Microsoft connection has been made.
The page correctly shows: "Inbox is empty. Connect Outlook to start syncing email."
Link: `/auth/microsoft/login` — Microsoft OAuth not yet connected.

## Fix Required

**For Calendar/Email blank display**:
CSS fix — ensure `#calendar-view` and `#email-view` have z-index ABOVE the neural canvas.
The neural canvas likely has `position: fixed` or `position: absolute` with high z-index.

```css
#calendar-view.visible, #email-view.visible {
  position: relative;
  z-index: 100; /* must exceed neural canvas z-index */
}
```

**For all-day badge**:
In `gwLoadCalendar()`, use `innerHTML` assignment or `insertAdjacentHTML` instead of 
double-assignment that escapes the HTML string.

## Pattern for Future

When a tab shows blank dark screen but DOM has data: CHECK z-index vs background animation layers.
Neural canvas animations sitting at top of z-stack are a common masking pattern in this codebase.

## Screenshots
- `/tmp/cc_cal_top.png` — blank calendar (canvas on top)
- `/tmp/cc_email_top.png` — blank email (canvas on top)
- `/tmp/cc_cal_loaded.png` — full page shows events DO render (just hidden)
