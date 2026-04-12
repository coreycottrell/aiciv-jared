# Mobile Chatbox Fix for purebrain.ai

**Date**: 2026-02-17
**Status**: CSS prepared, needs manual application (reCAPTCHA blocking automation)

---

## Issues Found

### Issue 1: Send Button Arrow Invisible on Mobile

**Root Cause**: The SVG icon inside the send button has `width: 0px` on mobile.
- SVG has `viewBox="0 0 24 24"` but no explicit width/height
- On mobile, the computed width collapses to 0px
- The arrow icon IS in the HTML, but invisible due to 0 width

**Evidence**:
```
svgWidth: 0px
svgHeight: 20px
rect: {width: 0, height: 20}
```

### Issue 2: Chatbox Too Narrow on Mobile

**Root Cause**: Chat container is 239px wide on a 375px viewport.
- Container has `max-width: 900px` but base width isn't responsive
- Wastes available screen space on mobile

**Evidence**:
```
containerWidth: 239px
viewportWidth: 375px
```

---

## Before Screenshots (Mobile 375x812)

Screenshots saved to:
- `/home/jared/projects/AI-CIV/aether/tools/screenshots/mobile-chatbox-fix/04_chat_input_scrolled.png`

Visual: The send button shows only a gradient square with NO visible arrow icon.

---

## CSS Fix (Apply Manually)

**Location**: WordPress Admin > Appearance > Customize > Additional CSS

**Instructions**:
1. Login to https://purebrain.ai/wp-admin
2. Go to Appearance > Customize
3. Click "Additional CSS"
4. Scroll to the bottom of existing CSS
5. Paste the code below
6. Click "Publish"

**CSS to Add**:

```css
/*
 * PUREBRAIN.AI - MOBILE CHATBOX FIX
 * Date: 2026-02-17
 * Issues Fixed:
 *   1. Send button arrow/icon not visible on mobile (SVG width: 0px)
 *   2. Chatbox too narrow on mobile (needs to use more screen width)
 */

/* ============================================
   MOBILE CHATBOX FIXES
   ============================================ */

/* FIX 1: Make chat container wider on mobile */
@media (max-width: 768px) {
  .chat-section {
    padding-left: 12px !important;
    padding-right: 12px !important;
  }

  .chat-container {
    width: calc(100% - 24px) !important;
    max-width: none !important;
    margin-left: auto !important;
    margin-right: auto !important;
  }

  .chat-input {
    width: 100% !important;
  }

  .chat-input__field {
    flex: 1 !important;
    min-width: 0 !important;
  }
}

/* FIX 2: Make send button SVG arrow visible on mobile */
@media (max-width: 768px) {
  .chat-input__submit svg,
  #submitBtn svg {
    width: 24px !important;
    height: 24px !important;
    min-width: 24px !important;
    min-height: 24px !important;
    display: block !important;
  }

  /* Ensure SVG stroke/fill is visible (white on gradient background) */
  .chat-input__submit svg line,
  .chat-input__submit svg polygon,
  #submitBtn svg line,
  #submitBtn svg polygon {
    stroke: white !important;
    fill: none !important;
  }

  #submitBtn svg polygon {
    fill: white !important;
  }
}

/* FIX 3: General SVG visibility fix for all viewports */
.chat-input__submit svg,
#submitBtn svg {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}

/* ============================================
   END OF MOBILE CHATBOX FIXES
   ============================================ */
```

---

## CSS File Location

Full CSS file saved to:
`/home/jared/projects/AI-CIV/aether/exports/mobile-chatbox-fix-2026-02-17.css`

---

## Why Automation Failed

GoDaddy hosting has reCAPTCHA protection on the WordPress login:
- "Please verify you are human" with "I'm not a robot" checkbox
- Cannot be bypassed with automation
- Requires human interaction to solve

---

## Verification After Fix

After applying the CSS, verify on mobile (375px viewport):
1. Send button should show white arrow icon
2. Chat container should be wider (nearly full screen width)

Test on both pages:
- https://purebrain.ai
- https://purebrain.ai/purebrain-3/

---

## Technical Details

**Chat HTML Structure**:
```html
<button id="submitBtn" class="chat-input__submit">
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
    <line x1="22" y1="2" x2="11" y2="13"></line>
    <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
  </svg>
</button>
```

**CSS Selectors Used**:
- `.chat-section` - Main chat wrapper section
- `.chat-container` - Chat box container
- `.chat-input` - Input area wrapper
- `.chat-input__field` - Text input field
- `.chat-input__submit` / `#submitBtn` - Send button
- `#submitBtn svg` - SVG arrow icon
