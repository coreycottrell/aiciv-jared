# Timer 15:00 Flash Bug Fix — 2026-02-28

## Bug
After user names their AI on purebrain.ai pages, the session timer briefly shows "15:00" before switching to 30-minute countdown.

## Root Cause
HTML initial display value was hardcoded as `15:00` in the DOM:
```html
<span class="session-timer__time" id="sessionTimeDisplay">15:00</span>
```
The JavaScript `startSessionTimer()` correctly starts at `30 * 60` (30 minutes), but there is a brief flash of the static `15:00` HTML before the JS fires and overwrites the display value.

## Fix
Changed initial HTML display from `15:00` to `30:00` on all affected pages.

```
OLD: id="sessionTimeDisplay">15:00</span>
NEW: id="sessionTimeDisplay">30:00</span>
```

## Pages Fixed
- Page 11 (pure-brain-agentic-ai-partner) — main purebrain.ai page
- Page 439 (pay-test)
- Page 468 (pay-test-sandbox)
- Page 688 (pay-test-sandbox-2)
- Page 689 (pay-test-2)

## How Fixed
Via WP REST API: GET raw content → string replace → POST updated content.
No plugin, no Elementor — these pages store content in `post_content` directly.

## Verification
Re-fetched each page after update. All 5: old=15:00 x0, new=30:00 x1. PASS.

## Pattern Note
When JS overwrites a DOM value on user action, always initialize the static HTML
to match the JS starting value. Avoids flash-of-wrong-content (FOWC) bugs.
