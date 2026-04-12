# Portal Sidebar Panels Outside .content Bug

**Date**: 2026-03-13
**Type**: structural-bug

## Problem
Refer & Earn, Bookmarks, and Tasks sidebar panels filled only the RIGHT HALF of the main content area. Status panel (correct reference) filled full width.

## Root Cause
The three panels (`#panel-referrals`, `#panel-bookmarks`, `#panel-scheduled`) were placed OUTSIDE the `.content` div in the HTML — positioned after its closing `</div>`.

`.main` uses `display: flex` (row direction). The orphaned panels became flex siblings of `.content` and `.sidebar`. When activated (`display: flex`), they appeared as a new column to the right of `.content`, taking only the remaining half of the window.

## Fixes Applied (portal-pb-styled.html)
1. Removed the premature `</div>` that closed `.content` before the referrals panel
2. Added the `.content` closing `</div>` after `#panel-scheduled` closes
3. Removed `align-items: center` from `#panel-referrals.active` CSS
4. Removed `max-width: 680px` from Refer & Earn inner wrapper div

## Rule Going Forward
Any new sidebar panel MUST be placed inside the `<div class="content">` wrapper, before its closing `</div>`. The content div is at line ~4284. All panels open at depth 1 (inside .content) and close back to 1.

## File
`/home/jared/purebrain_portal/portal-pb-styled.html`
