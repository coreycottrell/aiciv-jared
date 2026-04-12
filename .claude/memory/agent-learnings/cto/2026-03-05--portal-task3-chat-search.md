# Portal Task 3 — Chat Keyword Search

**Date**: 2026-03-05
**Type**: operational
**Agent**: cto

## What Was Built

Added full keyword search to `portal.purebrain.ai/pb` via a targeted patch script.

## Patch Script

`/home/jared/purebrain_portal/apply_task3_search.py`

## 4 Targeted Patches

| # | What | Anchor String |
|---|------|---------------|
| 1 | CSS (search bar, highlights, nav buttons) | `\n</style>` (line 2308) |
| 2 | Search toggle button in chat header | `<button class="poke-btn" id="poke-btn">` (line 2523) |
| 3 | Search bar HTML div | `<div id="bookmarks-bar">` (line 2525) |
| 4 | Search JS logic (IIFE) | `\n})();\n</script>\n` (line 5241) |

## Features Delivered

- Magnifying glass button next to Poke button in chat header
- Animated slide-down search bar (#141820 bg, blue border focus)
- Case-insensitive search across all `.msg-bubble` elements
- Orange-tinted highlights: `rgba(241, 66, 11, 0.3)` all matches, `rgba(241, 66, 11, 0.6)` current
- "X / Y matches" badge in PT Blue
- Enter / Shift+Enter navigation; up/down arrow buttons
- ESC or X closes and clears all highlights
- Ctrl+F / Cmd+F intercept when chat panel is active

## Architecture Notes

- Search uses DOM text node walking — safe with existing `renderMarkdown()` HTML content
- Highlights injected via `<mark class="search-hl">` — easily cleared with `replaceChild`
- `parent.normalize()` called after clearing to merge adjacent text nodes cleanly
- Only searches `.msg-bubble` elements — avoids timestamps, meta, and avatar noise
- Zero external dependencies — pure vanilla JS

## Pattern: Patch Script Approach

File is ~310KB+ self-contained HTML. DO NOT rewrite. Always:
1. Read file first with line-number grep to find exact anchor strings
2. Use Python `str.replace(anchor, new_content, 1)` with count=1 for uniqueness
3. Verify anchors are unique before patching
4. Run verification spot-checks after write
