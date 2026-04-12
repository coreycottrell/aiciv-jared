# Memory: Witness Birth Pipeline — Chatbox v4 Build & Deployment

**Date**: 2026-02-24
**Agent**: full-stack-developer
**Type**: operational + teaching
**Topic**: Integrated Witness birth pipeline into PureBrain chatbox; v4 deployed to pages 688 and 689

---

## What Was Built

Implemented the Witness Birth Pipeline integration into the PureBrain post-payment chatbox (v4).

### New Function: runBirthInit(dom, aiName, firstName)

**Location**: Between `runThankYouMessage` thank-you card render and the "Learn more" button.

**Flow**:
1. Resolve container name from `window._pbContainerName` (set by page) OR fall back to `purebrain-{firstName}`
2. POST `http://104.248.239.98:8099/api/birth/start` with `{container}` — 180s timeout
3. On success: show AI message + "Authorize Your AiCIV →" button (opens `oauth_url` in new tab)
4. Collect auth code via `promptText()` (validator: length > 4, no newlines)
5. POST `http://104.248.239.98:8099/api/birth/code` with `{container, auth_code}` — 120s timeout
6. On success: confirm authenticated, show "evolving" message
7. On any failure: graceful degradation (show email fallback, continue flow)

### Updated Function: runPortalButtonWatcher(dom, aiName)

**Changed from** (v3):
```javascript
POST https://api.purebrain.ai/api/portal-status
  body: { email, aiName, orderId }
```

**Changed to** (v4):
```javascript
GET http://104.248.239.98:8099/api/birth/portal-status/{containerName}
```

- Added container name guard (skip if no containerName in payTestData)
- Added 30-min timeout fallback message ("Check your email for portal access")
- Portal button text changed from "Click Here to enter X's Brain Stream" to "Enter Your AiCIV →"

### payTestData additions
```javascript
containerName: null,       // set in runBirthInit
birthOauthUrl: null,       // oauth_url from /start response
birthAuthenticated: false, // true after /code success
timestamps: {
  birthStarted: null,
  birthAuthenticated: null,
}
```

### Page-level hook
```javascript
window._pbContainerName = 'witness-corey'; // set this BEFORE calling initPayTestFlow
```
If not set, falls back to `purebrain-{firstName}` slug.

---

## Deployment Details

- **File**: `/home/jared/projects/AI-CIV/aether/exports/pay-test-script-chat-flow-v4.js`
- **Deploy script**: `/home/jared/projects/AI-CIV/aether/tools/deploy_chatbox_v4.py`
- **Page 688** (pay-test-sandbox-2): Deployed OK — 454,362 → 458,362 chars
- **Page 689** (pay-test-2): Deployed OK — 451,947 → 455,947 chars
- **Elementor cache**: Cleared (HTTP 200)
- **JS size**: 78,843 chars (up from ~70,111 in v3)

### Verification (both pages)
- Chat Flow v4 marker: YES
- runBirthInit present: YES
- runPortalButtonWatcher present: YES
- Witness host (104.248.239.98:8099): YES

---

## Architecture Notes

### Why runBirthInit is AWAITED (not fire-and-forget)
The OAuth flow requires user interaction (clicking button, pasting code). It must block the flow until the user pastes the code. The portal watcher then starts AFTER runBirthInit, concurrently with the learn-more loop.

### Graceful Degradation
Every Witness API call has `try/catch`. If /start or /code fails:
- Error logged to payTestData
- Friendly AI message shown
- Flow continues (portal watcher won't have a containerName, so it skips)
- User still sees the "Learn more" flow and gets the portal placeholder

### Timeout Values
- `/api/birth/start`: 180s (Witness reports ~145s in production)
- `/api/birth/code`: 120s (Witness contract recommendation)
- Portal polling: 30s interval, 60 polls max = 30 min

### Container Name Resolution Priority
1. `window._pbContainerName` (set by WP page — ideal path, Witness nursemaid confirms name)
2. `purebrain-{firstName}` slug (fallback for testing, until page metadata wired)

---

## Key Code Pattern: OAuth Button

Reused the exact "Open Claude Console" button pattern from Phase 1:

```html
<a class="ptc-link-btn" href="${oauthUrl}" target="_blank" rel="noopener"
   onclick="this.textContent='Opened ✓ — come back here with the code'; this.style.background='#4caf50';">
  Authorize Your AiCIV ↗
</a>
```

The onclick provides instant visual feedback when user clicks. The `ptc-link-btn` class has all existing orange/hover styles.

---

## Related Memory

- `/home/jared/projects/AI-CIV/aether/.claude/memory/agent-learnings/collective-liaison/2026-02-24--witness-birth-pipeline-contract.md`
- `/home/jared/projects/AI-CIV/aether/.claude/memory/agent-learnings/collective-liaison/2026-02-24--witness-api-contract-answers-confirmed.md`
- `/home/jared/projects/AI-CIV/aether/.claude/memory/agent-learnings/full-stack-developer/2026-02-22--chatbox-revamp-v3-build.md`

---

## Live URLs

- Test: https://purebrain.ai/pay-test-sandbox-2/ (Page 688)
- Live: https://purebrain.ai/pay-test/ (Page 689)
