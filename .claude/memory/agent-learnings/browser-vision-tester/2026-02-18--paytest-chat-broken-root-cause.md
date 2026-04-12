# pay-test Chat Broken - Root Cause Analysis (Updated)

**Date**: 2026-02-18 (updated with fresh visual audit)
**Type**: gotcha + pattern
**Topic**: JS scope issue causing chat to appear broken on /pay-test/

---

## Context

Audited https://purebrain.ai/pay-test/ to diagnose "chat not connected to anything."

## Root Cause: Functions Not Exposed on Window Scope

The chat script (Script 6, 56,633 chars) IS wrapped in DOMContentLoaded (good), BUT
functions declared inside are only local to that callback:

```javascript
document.addEventListener('DOMContentLoaded', function() {
    function scrollToChat() { ... }  // LOCAL - not accessible as window.scrollToChat
    function startConversation() { ... }  // LOCAL
    function handleSubmit() { ... }  // LOCAL
});
```

HTML onclick handlers call these as global: `onclick="startConversation()"` - fails.

**Console errors**:
```
[pageerror] scrollToChat is not defined
[pageerror] startConversation is not defined
[pageerror] handleSubmit is not defined
```

**Fix**: Add at end of DOMContentLoaded callback:
```javascript
window.scrollToChat = scrollToChat;
window.startConversation = startConversation;
window.handleSubmit = handleSubmit;
```

## Bug 2: Duplicate Scripts

The page loads 24 inline scripts. Scripts 6-13 appear AGAIN as 15-23 (8 duplicates).
This causes SCC Library double-load error and potential conflicts.

**Fix**: Remove one copy of the duplicate script block set in WordPress page editor.

## PayPal Issue (Separate)

- `PAYPAL_CLIENT_ID` is a placeholder string, not a real ID
- Console: `[PB PayPal] USE_SDK_APPROACH is true but PAYPAL_CLIENT_ID is still a placeholder`
- PayPal SDK request returns HTTP 400 (invalid client ID)
- Fix: Replace `PAYPAL_CLIENT_ID` with real PayPal client ID from developer.paypal.com

## Orange Section Visual Issue

- The page has a large orange area at certain scroll positions
- This is NOT a broken section - it's the canvas background showing through
- Sections at that point are missing background override
- MAIN site has this same issue at ~2825px scroll depth

## API Endpoints (Both Work)

- Primary: `https://api.puremarketing.ai/v1/messages` - responds 200
- Fallback: `https://pure-brain-dashboard-api.purebrain.workers.dev/v1/messages` - works
- Issue is NOT the API - the JS never reaches API call stage

## Visual Comparison: pay-test vs main

| Feature | MAIN | PAYTEST |
|---------|------|---------|
| Hero | Identical | Identical |
| Section rendering | Normal sequence | Different scroll ordering |
| Chat function | Works | Broken (scope issue) |
| Testimonials | 3 | 6 (more complete) |
| Footer | Partial | Complete with PT branding |
| PayPal | None | Present but broken |
| Script count | ~14 | 24 (8 duplicated) |

## Chat Flow Test Results

- Click Awaken: PASS (scrolls to modal)
- Begin Awakening modal: PASS (appears correctly)
- Click Begin Awakening: PARTIAL - modal stays, input hidden, JS errors fire
- Type message: FAIL - input not accessible
- API call: NEVER REACHED

## Files

- Visual comparison report: `/home/jared/projects/AI-CIV/aether/exports/site-analysis/paytest-visual-comparison-2026-02-18.md`
- Screenshots: `/home/jared/projects/AI-CIV/aether/exports/site-analysis/screenshots/paytest-compare/`
- Key screenshot for Jared: `PAYTEST_CHAT_02_after_begin.png` (modal stuck, not activating)

---

**Tags**: purebrain, pay-test, chat-broken, javascript, window-scope, PayPal, duplicate-scripts
