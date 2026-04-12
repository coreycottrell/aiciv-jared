# Chatbox v3 Security Patch Deployment

**Date**: 2026-02-22
**Agent**: full-stack-developer
**Type**: operational + teaching

---

## Summary

Applied 3 security patches to `pay-test-script-chat-flow-v3.js` and deployed to both pay-test pages.

---

## The 3 Security Fixes

### CRIT-001: Credential stripping from log payload
**Location**: `logPayTestData()` function (lines 63-83)
**Fix**: Destructure to strip `claudeSessionInfo` and `telegramBotToken` from `data` before building payload:
```javascript
const { claudeSessionInfo: _sk, telegramBotToken: _tg, ...safeData } = data;
// Then use safeData instead of data in payload
```

### CRIT-002: Mask Telegram token in chat UI
**Location**: `runTelegramSetup()` function, token display loop
**Fix**: Show only the numeric ID prefix + bullet dots, never the full token:
```javascript
const tokenNumericId = token.trim().split(':')[0];
const maskedToken = tokenNumericId + ':••••••••••••';
userSay(msgList, maskedToken);
```

### HIGH-001: Validate portal URL before href assignment
**Location**: `runPortalButtonWatcher()`, inside setInterval callback
**Fix**: Parse URL, validate protocol is `https:` and hostname ends with `purebrain.ai`:
```javascript
try {
  const parsedPortalUrl = new URL(rawPortalUrl);
  if (parsedPortalUrl.protocol !== 'https:' || !parsedPortalUrl.hostname.endsWith('purebrain.ai')) {
    throw new Error('Invalid portal URL');
  }
  portalBtn.href = rawPortalUrl;
} catch (_) {
  portalBtn.href = 'https://purebrain.ai/portal';
}
```

---

## Key Deployment Learnings

### Elementor Data Structure
- `_elementor_data` from WP REST API is a **JSON string** (not raw JSON)
- Must `json.loads()` it to work with it as Python objects
- The HTML widget is at `elem_data[0]['elements'][0]` for these pages
- `widgetType = 'html'`, content is at `settings['html']`
- **All script tags are stored as REAL newlines** (not escaped) inside this Python string

### Correct Replacement Pattern
1. `json.loads(elem_data_str)` → Python tree
2. Navigate to `elem_data[0]['elements'][0]['settings']['html']`
3. Find `<script>\n/* === Post-Payment Chat Flow v3` in the HTML string
4. Find the corresponding `</script>` after it
5. Replace that substring with the new `<script>\n...\n</script>`
6. `json.dumps(elem_data, separators=(',', ':'))` → new JSON string
7. PUT via REST API with `{'meta': {'_elementor_data': new_json_str}}`
8. `DELETE /wp-json/elementor/v1/cache` to clear Elementor cache

### What Went Wrong Initially
- Tried to validate as `'{"x":"' + elem_data_str + '"}'` — WRONG. The elem_data_str contains unescaped quotes and is already the content of a JSON value
- Correct validation: `json.loads(elem_data_str)` then `json.dumps()` round-trip

### Page 689 Had v2 (Not v3)
- Page 688 (sandbox) had v3, Page 689 (live) had v2
- Same replacement logic works for v2 marker: `'<script>\n/* === Post-Payment Chat Flow v2'`
- After replacement, both pages now have patched v3

---

## Files Modified
- `/home/jared/projects/AI-CIV/aether/exports/pay-test-script-chat-flow-v3.js` (patched JS — was already patched)
- WP Page 688 (pay-test-sandbox-2) — Elementor widget HTML updated
- WP Page 689 (pay-test-2) — Elementor widget HTML updated (also upgraded v2 → v3)

---

## Verification Checklist (8 checks, both pages)
- [x] CRIT-001: `claudeSessionInfo: _sk` destructure present
- [x] CRIT-001: `...safeData` spread in payload (not `...data`)
- [x] CRIT-002: `CRIT-002` comment marker present
- [x] CRIT-002: `maskedToken` variable used
- [x] HIGH-001: `HIGH-001` comment marker present
- [x] HIGH-001: `parsedPortalUrl` URL validation present
- [x] No `telegramBotToken: payTestData.telegramBotToken` line in payload
- [x] v3 script header present (not v2)
