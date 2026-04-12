# Reply-To Message Feature — PureBrain Portal Chat

**Date**: 2026-03-03
**Type**: pattern
**Task**: ST# Priority — Add Telegram-style reply-to feature to portal chat

## What Was Built

Full reply-to message feature in `/home/jared/purebrain_portal/portal-pb-styled.html`.

### Architecture

**State management**: `replyingTo = { id, sender, role, text }` variable tracks active reply target. Cleared after send or cancel.

**Reply preview bar**: `.chat-input-wrapper` flex-column container wraps `.reply-preview-bar` (above) + `.chat-input-bar` (below). Bar activates with `.active` class. Shows sender name, message preview (80 char truncated), color-accented left border, X cancel button.

**Color logic**:
- Replying to Aether (assistant): orange accent (`var(--teal-dim)`)
- Replying to user (You): blue accent (`var(--gold)`)

**Message format**: When sending with active reply, fullMsg is prepended:
```
[replying to {sender}: "{truncated quoted text}"]
{actual message}
```
This format flows through the existing tmux send-keys pipeline — Aether reads it naturally.

**Quote block rendering**: `addMessage()` parses the `[replying to ...]` prefix via regex, strips it from displayText, and renders a `.msg-quote-block` DOM element before the message body. Shows sender + quoted text.

**Click-to-reply**: Each `.msg-bubble` gets a click listener (via IIFE closure capturing msgId, senderName, role, displayText) that calls `setReplyTarget()`.

### Key Functions Added

- `setReplyTarget(id, sender, role, text)` — activates reply bar, adjusts textarea border-radius
- `clearReplyTarget()` — dismisses bar, resets textarea corners
- `replyCancelBtn.addEventListener('click', clearReplyTarget)` — X button

### HTML Structure Change

Before:
```html
<div class="chat-input-bar">
  <input type="file">...<textarea>...<button>
</div>
```

After:
```html
<div class="chat-input-wrapper">
  <div class="reply-preview-bar" id="reply-preview-bar">
    <div class="reply-preview-accent"></div>
    <div class="reply-preview-content">
      <div class="reply-preview-sender"></div>
      <div class="reply-preview-text"></div>
    </div>
    <button class="reply-cancel-btn">×</button>
  </div>
  <div class="chat-input-bar">...(unchanged)...</div>
</div>
```

Border-top moved from `.chat-input-bar` to `.chat-input-wrapper`.

## Patterns / Gotchas

1. **Python replace approach**: For multi-location JS changes in a single large HTML file, use a single Python script that does all replacements and writes once. The Edit tool's "read first" requirement causes friction with large files and multiple changes.

2. **Playwright headless auth**: The portal login form's `doAuth()` function is NOT in global scope (inside DOMContentLoaded closure). Use `page.press('#loginToken', 'Enter')` for form submit, or intercept /api/status to return mock success. Direct `page.evaluate("doAuth()")` fails.

3. **Bubble click vs link click**: Always check `e.target.tagName` and `e.target.closest('button')` inside bubble click handlers to avoid triggering reply when clicking links or buttons inside the message.

4. **Textarea border-radius on reply**: When reply bar is active, set `borderTopLeftRadius: '0'` and `borderTopRightRadius: '0'` on textarea to make it visually connect to the bar above.

5. **Quote regex**: Pattern `^\[replying to ([^:]+): "([^"\n]{1,200})"\]\n?` — works for the format `[replying to Sender: "..."]`. The quote is stripped before `renderMarkdown()` is called.

## File Modified
`/home/jared/purebrain_portal/portal-pb-styled.html`

## Verification
21/21 checks passed. Portal server restarted. Screenshots delivered to Telegram (messages 16688-16690).
