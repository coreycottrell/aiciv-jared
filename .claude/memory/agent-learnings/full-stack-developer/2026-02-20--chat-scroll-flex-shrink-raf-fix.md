# Memory: Chat Scroll Fix - flex-shrink + requestAnimationFrame

**Date**: 2026-02-20
**Agent**: full-stack-developer
**Type**: teaching
**Topic**: Fix for chat messages appearing below input box (scroll not working)

---

## Problem

On pay-test pages, after several chat messages, new AI messages appeared BELOW the
input box instead of staying within the scrollable `.ptc-messages` area. The previous
fix (adding `min-height: 0` to `.ptc-messages`) was necessary but not sufficient.

## Root Cause

Two separate issues:

### Issue 1: Missing flex-shrink: 0 on fixed-height siblings
The flex container (`#pay-test-post-payment.ptc-wrapper`) has children:
- `.ptc-header` (has `flex-shrink: 0` ✓)
- `.ptc-messages` (has `flex: 1; min-height: 0; overflow-y: auto` ✓)
- `.ptc-actions` (MISSING `flex-shrink: 0` ✗)
- `.ptc-input-row` (MISSING `flex-shrink: 0` ✗)

Without `flex-shrink: 0`, the actions and input-row elements could participate in
flex shrinkage calculations, disrupting the stable layout needed for proper scroll.

### Issue 2: scrollBottom calling before browser render
`scrollBottom(msgList)` was called synchronously right after `msgList.appendChild(wrapper)`.
The browser hasn't had a chance to calculate the new layout yet, so `scrollHeight` may
be stale (reflecting the pre-append height). This means `scrollTop = scrollHeight` sets
to the OLD scrollHeight, not scrolling far enough to show the new message.

## Fix

### Fix 1: Add flex-shrink: 0 to .ptc-actions and .ptc-input-row
```css
.ptc-actions {
  flex-shrink: 0;  /* ADD THIS */
}
.ptc-input-row {
  flex-shrink: 0;  /* ADD THIS */
}
```

### Fix 2: Use requestAnimationFrame (double-RAF) in scrollBottom
```javascript
function scrollBottom(msgList) {
  requestAnimationFrame(function() {
    msgList.scrollTop = msgList.scrollHeight;
    // Double-RAF for complex content (images, etc.)
    requestAnimationFrame(function() {
      msgList.scrollTop = msgList.scrollHeight;
    });
  });
}
```

The double-RAF pattern: first RAF fires after JS completes, second RAF fires after the
browser has painted. This guarantees `scrollHeight` reflects the actual rendered height.

## Deployment Pattern

Same as previous chatbox fixes:
1. Fetch via curl (NOT urllib - gets 403 for some reason with urllib Basic auth)
2. Parse `_elementor_data` JSON
3. Find `widgetType == 'html'` widget with 'ptc-messages' in html
4. String replace the CSS/JS in the widget's `settings.html`
5. `json.dumps(modified, separators=(',', ':'), ensure_ascii=False)`
6. POST back as `{"meta": {"_elementor_data": new_str}}`
7. Clear Elementor cache: `DELETE /wp-json/elementor/v1/cache`

## Key Strings for Future Reference

```
# FIX 1 - .ptc-actions
ADD: flex-shrink: 0;  (after gap: 10px;)

# FIX 2 - .ptc-input-row
ADD: flex-shrink: 0;  (after z-index: 2;)

# FIX 3 - scrollBottom (full replacement)
OLD: msgList.scrollTop = msgList.scrollHeight;
NEW: requestAnimationFrame + double-RAF pattern (see above)
```

## Important Notes

- Page 468 (pay-test-sandbox): has SANDBOX PayPal ID starting with AYTFob05DoSn0...
- Page 439 (pay-test LIVE): has LIVE PayPal ID starting with AWgWNlBQ...
- NEVER change PayPal client IDs when doing CSS/JS fixes
- urllib.request with Basic auth fails (403) - use subprocess curl instead
- The chatbox widget HTML is ~404K chars - always load via API, don't cache locally
