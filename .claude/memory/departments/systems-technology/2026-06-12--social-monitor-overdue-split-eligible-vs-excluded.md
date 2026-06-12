# Social Queue Monitor: overdue_scheduled split into eligible vs excluded-by-design

**Date**: 2026-06-12
**Agent**: dept-systems-technology (ST#)
**Type**: operational + teaching
**File**: `tools/social_queue_monitor.py`

## What changed

`overdue_scheduled: 17` had triggered TWO false "poster death" investigations, but all 17
items were content types (`newsletter`, `newsletter_promo`, `blog`) that the live
social-api CF Worker cron excludes BY DESIGN
(`AND ci.content_type NOT IN ('newsletter','newsletter_promo','blog')`, live worker ~line 3064).

Patch (per spec in `/home/jared/exports/social-queue-frozen-investigation-2026-06-12.md` §Recommended Fix #3):

- Added `CRON_EXCLUDED_TYPES = {"newsletter", "newsletter_promo", "blog"}` constant
  mirroring the worker SQL (tools/social_queue_monitor.py:37-42).
- Report now emits:
  - `overdue_eligible` — overdue items the cron WILL select. **This is the real alarm signal.**
  - `overdue_excluded_by_design` — overdue items of cron-excluded types. Informational only;
    their fulfillment path is blog-pipeline / manual LinkedIn newsletter, never the cron.
  - `overdue_scheduled` — kept as the sum (backward compat for existing parsers).
- `field_present_rate` emission untouched (constitutional: parser-monitors must emit it).
- Tool remains strictly READ-ONLY toward the queue.

## Verified

Run 2026-06-12T20:01:01Z: exit 0, `overdue_eligible: 0`, `overdue_excluded_by_design: 17`,
`overdue_scheduled: 17`, `field_present_rate: 1.0` — exact match to expected.

## Teaching

- **A raw "overdue" metric must be partitioned by which component is responsible for firing
  each item.** Items no live component will ever select mimic component-death in aggregate
  counts and burn investigation cycles.
- Failure-mode direction is safe: if `content_type` were ever missing from API items, those
  items fall into `overdue_eligible` (alarm side), never silently into "excluded".
- If the worker's NOT-IN list ever changes, `CRON_EXCLUDED_TYPES` must be updated in lockstep
  (constant comment points at worker line ~3064).
