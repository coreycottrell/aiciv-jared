# Chatbox CTA Button Text + Input Disable Fix

**Date**: 2026-02-28
**Type**: pattern + gotcha
**Pages**: 688, 689, 468, 439, 11

---

## What Was Done

Two surgical changes to the pre-payment chatbox on all pay test pages:

1. **Button text change**: "See what ${aiName} can do for you" -> "Click to see what ${aiName} can do for you"
2. **Input disable when CTA appears**: Same pattern as the discover button (`userInput.disabled = true; userInput.placeholder = 'Click the button above ↑'`)

---

## Code Pattern - Input Disable

The discover button (earlier in flow) already had this pattern at the `shouldShowPricing` block:
```js
// Disable input while Discover button is showing (prevents loop)
userInput.disabled = true;
userInput.placeholder = 'Click the button above ↑';
```

We replicated the same pattern for the `bringToLifeDiv` CTA button (end of flow):
```js
chatMessages.appendChild(bringToLifeDiv);
scrollToBottom();
// Disable input while CTA button is showing (user must click the button)
userInput.disabled = true;
userInput.placeholder = 'Click the button above ↑';

// Log capabilities reveal
logConversationToBackend('capabilities_revealed', { ai_name: aiName });
```

---

## Key Technical Notes

### Cloudflare 1010 Blocks Python urllib Without User-Agent
- curl works fine with `-u user:pass`
- Python `urllib.request` gets blocked by Cloudflare (error 1010) without a User-Agent
- Fix: add `"User-Agent": "Mozilla/5.0 (compatible; AetherBot/1.0)"` to all request headers

### Elementor Data Uses Escaped Newlines
- `_elementor_data` stores JS code with `\\n` (escaped newlines), not actual `\n`
- post_content uses actual newlines
- Must use different search strings for each: `\\n` pattern for elementor_data, `\n` for post_content

### Page 11 Is A Different Chatbox Version
- Pages 688, 689, 468, 439 use button: `See what ${aiName} can do for you` (sparkle icon)
- Page 11 uses button: `Bring ${aiName} to Life` (different text, different version of chatbox)
- The input disable fix applied to all pages, but the button text change only applied to pages that had the matching text

### Always Update Both post_content AND _elementor_data
- Elementor renders from `_elementor_data`, NOT `post_content`
- Must update both fields in the REST API POST payload
- Must clear Elementor cache after: `DELETE /elementor/v1/cache`

---

## Verification Pattern

After updating, verify these in fresh API read:
- `NEW_BUTTON_TEXT in content` = True
- `OLD_BUTTON_TEXT not in content` = True (confirms no duplicate)
- `'Disable input while CTA button is showing' in content` = True
- Same checks for elementor_data
