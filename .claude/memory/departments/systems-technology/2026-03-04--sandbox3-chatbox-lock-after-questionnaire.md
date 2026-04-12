# Sandbox-3 Chatbox Input Lock After Questionnaire Complete

**Date**: 2026-03-04
**Page**: Pay Test Sandbox 3 (page 1232)
**Type**: UX fix
**Status**: Deployed and verified

---

## Problem

After the chatbox questionnaire completes and the greyed-out portal button placeholder appears,
users could still type and send messages that did nothing. The chat input (textarea + Send button)
remained active after the questionnaire flow ended.

Jared's requirement: "once the button pops up, make it so that messaging is no longer available.
it is greyed out and doesnt work... they cannot message anymore"

---

## Fix Applied

Three patches to the HTML widget (element ID `292c72a`) in `_elementor_data` on page 1232:

### Patch 1: lockChatInput() helper function
Added before `function runPortalButtonWatcher()`:

```javascript
function lockChatInput() {
  const chatInput = document.getElementById('ptc-input');
  const sendBtn   = document.getElementById('ptc-send-btn');
  if (chatInput) {
    chatInput.disabled       = true;
    chatInput.placeholder    = 'Questionnaire complete — waiting for your portal…';
    chatInput.style.opacity      = '0.35';
    chatInput.style.cursor       = 'not-allowed';
    chatInput.style.pointerEvents = 'none';
  }
  if (sendBtn) {
    sendBtn.disabled             = true;
    sendBtn.style.opacity        = '0.25';
    sendBtn.style.cursor         = 'not-allowed';
    sendBtn.style.pointerEvents  = 'none';
  }
}
```

### Patch 2: Primary lock call (questionnaire ends)
Right after `msgList.appendChild(portalBtnRow)` and `msgList.scrollTop = msgList.scrollHeight`:
```javascript
lockChatInput(); // Disable input after questionnaire complete
```

### Patch 3: Belt-and-suspenders (portal goes live)
Inside `runPortalButtonWatcher`, before `logPayTestData({ ...payTestData, event: 'portal:ready' })`:
```javascript
lockChatInput(); // Ensure input is locked when portal activates
```

---

## DOM Selectors Used
- `#ptc-input` — the textarea element
- `#ptc-send-btn` — the send button

CSS already had `.ptc-send-btn:disabled { opacity: 0.45; cursor: not-allowed; }` — the JS
inline styles reinforce this and also handle the textarea.

---

## Deployment Notes
- `_elementor_data` updated via `POST /wp-json/wp/v2/pages/1232?context=edit`
- Elementor cache cleared via `DELETE /wp-json/elementor/v1/cache` — returned 200
- Must use `context=edit` to read/write `_elementor_data` — standard context returns empty string
- All 6 verification checks passed on live page after deployment

---

## Key Learnings
- The chatbox flow: questionnaire ends → `That's everything` message → portal button placeholder
  injected → `lockChatInput()` fires → user cannot type until they click the portal button
- Two lockChatInput call sites = redundancy in case timing differs between portal states
- Placeholder text change ("Questionnaire complete — waiting for your portal…") reinforces the UX
