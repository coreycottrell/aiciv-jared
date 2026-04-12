# Sandbox-3 (Page 1232) — 3 Bug Fixes Deployed

**Date**: 2026-03-04
**Page**: purebrain.ai page 1232 (pay-test-sandbox-3)
**Agent**: dept-systems-technology

---

## Bugs Fixed

### Fix 1: Hardcoded "AiCIV" → Dynamic AI Name
**Problem**: Three places in the chatbox JS used the hardcoded string "AiCIV" instead of the dynamic AI name.

**Locations changed**:
1. `sanitizeText(aiName || 'Your AiCIV')` → `sanitizeText(aiName || 'Your AI')` (safeAiName fallback in `runPortalButtonWatcher`)
2. `fallbackMsg.textContent = 'Your AiCIV is still finishing up...'` → `safeAiName + ' is still finishing up...'`
3. `'Your AiCIV is ready.'` → template literal `${safeAiName} is ready.`

**Key insight**: The variable `safeAiName` is declared at the top of `runPortalButtonWatcher` — it's already sanitized and available. The original code simply forgot to use it for the user-visible fallback messages.

---

### Fix 2: Send Button Disabled After Q&A Completes
**Problem**: After `runLearnMoreLoop` ends and the portal placeholder button appears, the textarea and send button remain active, letting the user type when they shouldn't.

**Where to apply**: End of `runLearnMoreLoop()`, immediately after `msgList.appendChild(portalBtnRow)`.

**Code added**:
```javascript
const { inputRow, textarea, sendBtn } = dom;
if (textarea) {
  textarea.disabled = true;
  textarea.placeholder = 'Waiting for your portal…';
}
if (sendBtn) {
  sendBtn.disabled = true;
}
if (inputRow) {
  inputRow.style.opacity = '0.4';
  inputRow.style.pointerEvents = 'none';
}
```

**Important**: The `dom` object with `inputRow`, `textarea`, `sendBtn` is in scope at the end of `runLearnMoreLoop` — just destructure it again.

---

### Fix 3: BRAIN STREAM Button Disabled Until Magic Link
**Problem**: The "System B" BRAIN STREAM button (`#pb-brain-stream-btn`) was fully active (pulsing glow animation, clickable) the moment the page loaded, before any magic link arrived.

**Two-part fix**:

**Part A - HTML default state** (the `<a>` tag):
```html
<a
  id="pb-brain-stream-btn"
  ...
  aria-disabled="true"
  style="pointer-events:none; opacity:0.35; filter:grayscale(0.7); animation:none; cursor:not-allowed;"
>
```

**Part B - `showBrainStreamButton()` activation** (removes disabled state):
```javascript
// Before the wrapper reveal animation:
btn.style.removeProperty('pointer-events');
btn.style.removeProperty('opacity');
btn.style.removeProperty('filter');
btn.style.removeProperty('animation');
btn.style.removeProperty('cursor');
btn.removeAttribute('aria-disabled');
```

**Key insight**: Using `style.removeProperty()` cleanly removes inline style overrides so the CSS class rules take over (the glow animation, full opacity, cursor pointer). This is cleaner than setting style values directly because the CSS already defines the active state.

---

## Deployment Pattern

```bash
# 1. Fetch
curl -s "https://purebrain.ai/wp-json/wp/v2/pages/1232?context=edit" \
  -u "Aether:ZGuh 1W8k WpWM c9iy kqyd buPr" \
  | python3 -c "import json,sys; p=json.load(sys.stdin); print(p['content']['raw'])" > /tmp/raw.html

# 2. Modify with Python (string replacement on the raw HTML)
# 3. Write JSON payload
python3 -c "import json; content=open('/tmp/fixed.html').read(); print(json.dumps({'content': content}))" > /tmp/payload.json

# 4. Deploy
curl -X POST "https://purebrain.ai/wp-json/wp/v2/pages/1232" \
  -u "Aether:ZGuh 1W8k WpWM c9iy kqyd buPr" \
  -H "Content-Type: application/json" \
  --data-binary @/tmp/payload.json

# 5. Clear Elementor cache
curl -X DELETE "https://purebrain.ai/wp-json/elementor/v1/cache" \
  -u "Aether:ZGuh 1W8k WpWM c9iy kqyd buPr"
```

---

## Verification Pattern

Read the page back and check for presence/absence of key strings:
- No `'Your AiCIV'` in user-visible strings
- `safeAiName +` present in fallback message
- `Waiting for your portal` placeholder text present
- `aria-disabled="true"` on the brain stream button
- `removeProperty('pointer-events')` in showBrainStreamButton

**Note**: Smart quotes vs straight quotes can cause Python string matching to fail even when content is correct. Use `'keyword' in content` checks on individual terms rather than full-string matches when debugging.
