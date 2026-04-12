# Social Dashboard Calendar View Rebuild

**Date**: 2026-04-06
**Agent**: dept-systems-technology
**Type**: operational
**Topic**: Rebuilt social.html calendar with Month/Week/List views

---

## Problem
The "Week" view in surf.purebrain.ai/social.html was broken -- the HTML and JS existed for a week grid view but had ZERO CSS rules defined. The view toggle buttons, week-grid, week-cell, week-header, week-post-chip, and view-toggle-btn classes all had no styling at all.

## What Was Built

### 1. Monthly Calendar View (NEW - default view)
- 7-column grid (Mon-Sun) using CSS Grid
- 5-6 rows for weeks, includes days from adjacent months (dimmed)
- Each day cell shows: date number, up to 3 content cards, "+N more" overflow
- Content cards are color-coded with left border: Blue=Blog, Orange=Standalone, Green=Newsletter, Purple=Bluesky
- Cards show time + truncated title + status dot (Draft=yellow, Approved=blue, Live=green, Failed=red)
- Today highlighted with blue inset box-shadow + blue date circle
- Click any card to jump to list view filtered to that post
- Click "+N more" to filter list view to that day

### 2. Weekly Calendar View (FIXED - was broken)
- 8-column grid: time slot labels + 7 day columns
- 5 time slot rows: 8-9am (Blog), 10-12pm (Newsletter), 1pm (Standalone), 3-5pm (Bluesky), Other
- Posts positioned by content type into appropriate slot
- Same card styling as month view (color-coded chips)
- Shows time + title + status indicator per chip

### 3. Calendar Navigation
- Prev/Next buttons to navigate months or weeks depending on active view
- "Today" button to reset to current period
- Title bar shows "April 2026" (month) or "Apr 1 - Apr 7, 2026" (week) or "All Scheduled Posts" (list)

### 4. List View (kept, fixed toggle)
- Same filter bar (content type, platform, status, date)
- Hidden by default, shown when "List" toggle active
- Filters and list now properly toggle visibility

### 5. View Toggle
- Styled pill-button group: Month | Week | List
- Active state = blue fill, inactive = ghost
- Replaces old "List | Week" toggle

## Technical Details
- ~250 lines of new CSS added before </style>
- Calendar panel HTML fully replaced (lines 926-1003 original)
- JS section replaced: setCalendarView, renderWeekView, scrollToPost
- New JS functions: calNavPrev, calNavNext, calNavToday, updateCalNavTitle, renderMonthView, showDayDetail
- Default view changed from 'list' to 'month'
- Added monthOffset state variable for month navigation
- Responsive: tablet reduces cell sizes, mobile hides cards and shows dot indicators

## Files
- **Server**: /var/www/puresurf/social.html on 157.180.69.225
- **Backup**: /var/www/puresurf/social.html.bak-20260406-* (timestamped)
- **Patch script**: exports/departments/systems-technology/social-calendar-patch.py (initial version)
- **Actual patch used**: /tmp/patch_calendar.py (surgical line-based approach)

## Key Gotcha
The original week view CSS was completely missing -- 0 rules in the stylesheet. Always verify CSS exists when HTML/JS references classes.

## Verification
- Page loads at surf.purebrain.ai/social.html
- 184 div tags perfectly balanced (opening = closing)
- All 9 new JS functions present, no duplicates
- Month view renders as default on page load
