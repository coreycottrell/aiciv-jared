# Assessment Page Share Section: Popup Modal + Button Style Fix

**Date**: 2026-02-23
**Type**: teaching
**Topic**: AI Partnership Assessment page 284 - share buttons styling + copy share message popup

---

## Fixes Applied to Page 284

Page: https://purebrain.ai/ai-partnership-assessment/
WordPress page ID: 284
Template: elementor_canvas
Structure: data[0] (container) > elements[0] (HTML widget directly - NOT section > column > widget)

### Fix 1: Share Button Styling
- Both "Download Score Card" and "Copy Share Message" buttons changed to:
  - Default: `background: #2a93c1` (blue) + `color: #ffffff !important`
  - Hover: `background: #f1420b` (orange) + `color: #ffffff !important` + orange box-shadow
- Critical: Use `!important` on color to override any specificity issues

### Fix 2: Share Message Popup Modal
- Replaced simple "Copied!" feedback with full premium dark-themed modal
- Modal features:
  - Shows the actual message text in a styled message box
  - Green "✓ Copied to clipboard" badge
  - 4 social share buttons: LinkedIn, X/Twitter, Facebook, Email
  - Each pre-populates with encoded share message + assessment URL
  - Click-outside-to-close (overlay click)
  - Escape key closes modal
  - × button in top right
  - CSS animation on open (scale + translate)
  - Closes via `closeShareModal()` function
- Clipboard copy happens automatically when modal opens (no separate click needed)

### Fix 3: HTML Entity Fix
- Problem: `btn.textContent = '&#10003; Copied!'` → HTML entities don't render in textContent
- Root cause: `textContent` is plain text, not HTML; `innerHTML` needed for HTML entities
- Solution: Replaced entire JS function - no longer uses textContent for button state
- Side note: `.textContent` vs `.innerHTML` matters:
  - `textContent` = raw text (entities show as literal)
  - `innerHTML` = parsed HTML (entities render correctly)

---

## Elementor Tree Structure for Page 284

**IMPORTANT**: Different from pages 403 (ai-readiness-assessment):

Page 284: `data[0]` (container, elType=container) > `elements[0]` (HTML widget directly)
Page 403: `data[0]` (section) > `elements[0]` (column) > `elements[0]` (HTML widget)

Always inspect actual structure before assuming hierarchy.

---

## Social Share URL Patterns

```javascript
// LinkedIn
'https://www.linkedin.com/sharing/share-offsite/?url=' + encodedUrl + '&summary=' + encodedMsg

// X/Twitter  
'https://twitter.com/intent/tweet?text=' + encodedMsg + '&url=' + encodedUrl

// Facebook
'https://www.facebook.com/sharer/sharer.php?u=' + encodedUrl + '&quote=' + encodedMsg

// Email
'mailto:?subject=Check%20out%20this%20AI%20Readiness%20Assessment&body=' + encodedMsg + '%0A%0A' + encodedUrl
```

---

## Deployment Pattern (Page 284)

```python
# 1. Fetch
curl -u "Aether:PASSWORD" "https://purebrain.ai/wp-json/wp/v2/pages/284?context=edit" > page284.json

# 2. Parse
data = json.loads(page['meta']['_elementor_data'])
widget = data[0]['elements'][0]  # Container > HTML widget
widget['settings']['html'] = new_html

# 3. Deploy (ONLY meta, never blank content)
payload = {"meta": {"_elementor_data": json.dumps(data, ensure_ascii=False)}}
curl -X POST --data @payload.json ".../wp/v2/pages/284"

# 4. Clear Elementor cache
curl -X DELETE ".../elementor/v1/cache"
```

---

## Files

- Modified HTML: `/tmp/page284_fixed.html` (temp)
- Payload: `/tmp/page284_payload.json` (temp)
