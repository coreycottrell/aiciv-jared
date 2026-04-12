# Portal Copy Text: Rich Text/HTML Support via ClipboardItem

**Date**: 2026-03-21
**Type**: teaching
**Topic**: Upgraded 3 copy handlers in portal-pb-styled.html to copy both HTML and plain text

## What Was Done

Upgraded all three "Copy text" button handlers in `/home/jared/purebrain_portal/portal-pb-styled.html` from plain-text-only (`clipboard.writeText`) to rich-text (`ClipboardItem` with both `text/html` and `text/plain`).

## Three Locations Changed

1. **Line ~8895**: `ctxCopyBtn` — right-click context menu "Copy text"
2. **Line ~9233**: `copyActionBtn` — inline action bar in `addMessage()` function
3. **Line ~9476**: `sCopyBtn` — inline action bar in streaming message handler

## Pattern Used

```javascript
var plainText = (bubble.innerText || bubble.textContent || '').trim();
var htmlContent = bubble.innerHTML || '';
if (navigator.clipboard && window.ClipboardItem) {
  try {
    var cbItem = new ClipboardItem({
      'text/html': new Blob([htmlContent], { type: 'text/html' }),
      'text/plain': new Blob([plainText], { type: 'text/plain' })
    });
    navigator.clipboard.write([cbItem]).then(function() { showToast('Copied!'); })
      .catch(function() { navigator.clipboard.writeText(plainText)... });
  } catch(e2) {
    navigator.clipboard.writeText(plainText)...
  }
}
```

## Why This Works

- `ClipboardItem` copies BOTH formats simultaneously
- Gmail, Slack, Notion, Google Docs pick `text/html` → get bold, tables, links, code blocks
- Plain text editors get the `text/plain` fallback automatically
- Requires HTTPS (portal runs on HTTPS in production, so fine)

## Selection Preservation

Handlers 2 and 3 (inline action bar) check `window.getSelection()` first — if user has selected specific text, it copies only the selection. Otherwise copies full bubble content.

## Toast Changed

Old: `'Copied to clipboard'` → New: `'Copied!'` (shorter, matches modern UX convention)

## File

`/home/jared/purebrain_portal/portal-pb-styled.html`
