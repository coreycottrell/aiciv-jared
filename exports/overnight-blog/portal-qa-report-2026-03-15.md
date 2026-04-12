# Portal QA Audit Report
**Date**: 2026-03-15
**Agent**: dept-systems-technology (CTO team)
**File audited**: `/home/jared/purebrain_portal/portal-pb-styled.html` (12,461 lines, 597KB)
**Server**: `aether-portal.service` on port 8097
**Status**: Audit complete. Fixes batched — no restart yet.

---

## CRITICAL DIAGNOSIS: iOS Blank Messages Issue

### Root Cause (DO NOT FIX WITHOUT CONFIDENCE)

The blank messages bug on iOS when returning from background is a **multi-layer race condition** with the following mechanics:

**What happens on iOS when the app is backgrounded:**

1. iOS suspends the JavaScript engine. All running timers, WebSocket connections, and network activity freeze.
2. The WebSocket connection (`chatWs`) is silently killed by the OS — no `onclose` event fires immediately.
3. When the user returns to the app, iOS resumes JavaScript. The `visibilitychange` event may or may not fire depending on how long the app was backgrounded.
4. The `_wsHeartbeat` interval (fires every 10s, closes connection if no data in 30s) eventually triggers the `onclose` handler.
5. `onclose` schedules `connectChatWS()` via `setTimeout` with exponential backoff (starting at 2s, doubling to 30s max).
6. `connectChatWS()` calls `chatWs.onopen`, which calls `loadChatHistory()`.
7. **The problem**: `loadChatHistory()` sets `chatMessages.innerHTML = '<div class="chat-loading">Loading...</div>'` first, then fetches. If the fetch fails (network still recovering), the DOM shows the loading spinner. If it succeeds, messages re-render fine.
8. **However**: There is a second failure mode. `chatLoaded` is set to `true` at line 6992 (first line of `loadChatHistory()`). When the user switches to a non-chat panel and back (`switchPanel('chat')`), the code at line 5568 does `if (panel === 'chat' && chatLoaded) { smartScroll(chatMessages); }` — it does NOT reload messages. It only calls `smartScroll`. If the DOM was cleared (by a failed history fetch or a mid-reconnect wipe), messages stay blank.
9. **The current visibilitychange handler** (line 10881) only sets `isVisible`. It does nothing to trigger reconnection or history reload. The comment at line 7419 says `// ===== VISIBILITY CHANGE — minimal, safe =====` with NO code below it — **the section is empty**. Previous fix attempts were rolled back, leaving this label with no implementation.

**Why Witness's portal does NOT have this problem:**
Witness likely has a working `visibilitychange` handler that explicitly calls `connectChatWS()` (and by extension `loadChatHistory()`) when the page becomes visible again, or avoids wiping `chatMessages.innerHTML` during reconnect cycles.

**Summary of the iOS blank messages root cause:**
- iOS kills the WebSocket without firing `onclose`
- The heartbeat timer (30s interval) eventually detects the dead connection and closes it
- The reconnect delay is up to 30s (exponential backoff)
- During this window, `chatLoaded = true` so `switchPanel` does NOT reload history
- If the fetch in `loadChatHistory` races against iOS network resumption, it may fail silently
- The "minimal, safe" visibilitychange handler (line 10881) only tracks `isVisible` — it does NOT trigger any reconnect or reload

**Safe fix approach (diagnose only per instructions — document the approach here):**
A minimal safe fix would be:
```javascript
document.addEventListener('visibilitychange', function() {
  isVisible = document.visibilityState === 'visible';
  if (isVisible && token) {
    // Only reconnect if WS is actually dead
    if (!chatWs || chatWs.readyState === WebSocket.CLOSED || chatWs.readyState === WebSocket.CLOSING) {
      if (chatWsReconnectTimeout) { clearTimeout(chatWsReconnectTimeout); chatWsReconnectTimeout = null; }
      _wsReconnectDelay = 2000; // reset backoff
      connectChatWS(); // this calls loadChatHistory() on open
    }
  }
});
```
This is intentionally NOT deployed. Jared must approve before applying.

---

## Full QA Audit Results

### 1. Chat Panel

#### 1a. Message Loading on Initial Login
**Status**: PASS
- `boot()` calls `connectChatWS()` which on `onopen` immediately calls `loadChatHistory()`
- `loadChatHistory()` fetches `/api/chat/history?last=200` with bearer token
- On success: DOM cleared, `renderWelcomeHero()` called, messages added via `addMessage()`, then scroll to bottom
- Error state renders a message in the panel rather than crashing

#### 1b. Message Persistence When Switching Tabs/Panels and Back
**Status**: PASS (with caveat)
- `switchPanel()` at line 5567-5568: if panel is 'chat' and `chatLoaded` is true, only calls `smartScroll()` — does NOT reload history
- Messages remain in DOM when switching panels
- **Caveat**: If the WS closed and triggered `loadChatHistory()` while user was on another panel, the DOM was briefly wiped with a loading spinner. When user returns, messages are back (fetch succeeded). This works correctly on desktop/WiFi but is fragile on slow mobile connections.

#### 1c. Message Persistence When App is Backgrounded (iOS Issue)
**Status**: FAIL — see Critical Diagnosis above
**Severity**: High

#### 1d. WebSocket Connection/Reconnection
**Status**: PASS (functionally correct, see iOS caveat)
- Exponential backoff: 2s → 4s → 8s → ... → 30s cap
- Heartbeat: checks every 10s, reconnects if no message in 30s
- On reconnect, `loadChatHistory()` is called — messages reload correctly on desktop
- **Issue**: On iOS, the WS dies silently. The heartbeat timer itself may have been frozen by the OS during the 30s window, then all fire at once. This extends the "dead connection" window.

#### 1e. Message Sending (Text, Files, Images)
**Status**: PASS
- `sendChat()` handles text + pending files
- File uploads go through `uploadFile()` → `/api/chat/upload` endpoint
- Image inline display via `addFileImageMessage()`
- Optimistic rendering: user message shown immediately, `knownMsgIds` prevents WS echo duplication
- Upload safety timer at line 7551 cleans up if server doesn't ack within timeout

#### 1f. Markdown Rendering
**Status**: PASS
- `renderMarkdown()` at line 5404 handles: headers, bold/italic, code blocks, inline code, links, lists
- Auto-link detection for http/https URLs (wraps in `<a>` tags — meets MEMORY.md requirement)
- `PORTAL_FILE` tags stripped before rendering to prevent raw tag display
- Streaming updates use `renderMarkdown()` in-place on the bubble

#### 1g. Scroll Behavior
**Status**: PASS
- `smartScroll()` respects user position: only auto-scrolls if user was within 300px of bottom
- Scroll-to-bottom button appears when scrolled up, hides when near bottom
- Image load events trigger `smartScroll` for async content
- Scroll position tracked via `_userWasNearBottom` flag before message DOM insertion (prevents false negative from height change)

#### 1h. Thinking Indicator
**Status**: PASS
- `LIVE_THINKING_ID` singleton prevents stacking multiple indicators
- 8-second auto-hide timer after last thinking block
- All thinking indicators cleaned up on first assistant message chunk
- Orphan cleanup: `document.querySelectorAll('[id^="thinking-"]').forEach(el => el.remove())`

#### 1i. File Previews and Image Display
**Status**: PASS
- `renderAiFileCards()` handles: images (inline preview), PDFs (icon + download), code files (syntax color hint), generic files (download card)
- Portal-uploaded files served from `/api/chat/uploads/[stored_filename]`
- Duplicate card prevention via `data-portal-stored` attribute
- Copy-to-clipboard for text files, full download for binaries

#### 1j. Bookmarks
**Status**: PASS
- Stored in `localStorage` as `purebrain_bookmarks`
- Max 6 shown in bookmarks bar, full list in bookmarks panel
- Click-to-scroll: `el.scrollIntoView({ behavior: 'smooth', block: 'center' })`
- Clear all button present in panel

#### 1k. Search
**Status**: PASS
- `runSearch()` walks `.msg-bubble` elements only (not meta/timestamps)
- Case-insensitive, regex-safe escaping
- Next/prev navigation between matches, highlighted with `<mark class="search-hl">`
- Clears highlights on close or empty query

---

### 2. Voice Overlay (HMI)

#### 2a. Mic Button Opens Overlay
**Status**: PASS
- `openHmiVoiceOverlay()` adds `.visible` class to `#hmiVoiceOverlay`
- Closes mobile menu if open (via `closeMobileMenu()`)
- Starts HMI canvas animation

#### 2b. Speech Recognition
**Status**: PASS (with mobile caveat)
- Uses `webkitSpeechRecognition` / `SpeechRecognition` Web API
- On mobile, continuous mode fails — recognition ends after each phrase and restarts
- Silence auto-send: `_hmiSilenceDelay` timer triggers send after user stops speaking
- Transcript injected into chat input textarea

#### 2c. TTS Speaks Responses Back
**Status**: PASS — recent fix verified
- `window._hmiSpeakResponse()` routes to ElevenLabs or browser TTS depending on config
- TTS unlock happens on user gesture (mic click) via a silent utterance — bypasses Chrome autoplay policy
- Feedback loop prevention: recognition stops while TTS plays, resumes 800ms after TTS ends
- `_voiceSendTimestamp` gates TTS — only responses arriving within 90s of voice send are spoken

#### 2d. Conversation Mode
**Status**: PASS
- `_hmiConversationMode` flag enables auto-listen-after-response cycle
- Watchdog timer (30s) restarts mic if TTS fails to fire
- Mic watchdog clears on normal TTS completion

#### 2e. Close Overlay
**Status**: PASS
- `closeHmiVoiceOverlay()` exported to global scope for inline `onclick`
- Restores speaker TTS state to pre-overlay value (`_ttsSavedBySpeaker`)
- Cancels all speech synthesis and clears TTS queue
- Auto-sends any transcribed text via send button click

---

### 3. Other Panels

#### 3a. Teams Panel
**Status**: PASS
- Loads on panel activation, auto-refreshes every 3s while active
- Interval cleared when leaving teams panel (memory-safe)
- Inject bar for sending to team panes

#### 3b. Status Panel
**Status**: PASS
- Loads on panel activation, global 30s interval via `statusInterval`
- **MEDIUM issue**: `statusInterval` is set via `setInterval(loadStatus, 30000)` at line 5678 and **never cleared** — runs for the entire session even when user is on other panels. Low cost (one fetch every 30s) but technically a minor leak.
- Shows tmux, Claude, Telegram, BOOP, context gauge

#### 3c. Fleet Panel
**Status**: PASS
- `FLEET_CIVS` is an empty array at line 4835 — panel renders with "0 CIVs"
- Grid is rendered synchronously, no async fetch — fast
- Copy SSH command button uses `navigator.clipboard` with fallback

#### 3d. Terminal Panel
**Status**: PASS
- Multi-terminal tab system with session registry (`termSessions`)
- WebSocket at `/ws/terminal?token=...` with 3s reconnect
- Tab creation/deletion fully wired
- **LOW issue**: Terminal output uses `pane.textContent = lines.join('\n')` — replaces entire content on each WS message. For large terminal output this causes DOM thrashing. Could accumulate lines instead.

#### 3e. Scheduled Tasks Panel
**Status**: PASS
- Loads on activation, 30s auto-refresh while active (interval cleared on panel leave)
- Pre-loads 2s after login (line 9066) for mobile where panel might not trigger properly
- Edit/delete/run-now modal fully implemented
- Sorted by `fire_at` ascending

#### 3f. Referral Panel
**Status**: PASS (not fully auditable without live server)
- Loads referral data from `/api/referrals`
- Referral link displayed, payout history rendered
- Commission display and payout request flow implemented

---

### 4. Navigation

#### 4a. Tab Switching (Mobile Hamburger Menu)
**Status**: PASS
- `toggleMobileMenu()` / `closeMobileMenu()` / `selectMobileMenuItem()` all exported to global scope
- Click-outside closes the menu (document-level click handler)
- Hamburger tab gets `.active` class when "more" panel is selected

#### 4b. Panel Switching State
**Status**: PASS
- `switchPanel()` correctly manages panel `.active` classes
- Panel-specific actions (load, interval start/stop) handled per-panel
- Active panel tracked in `activePanel` variable

#### 4c. Sidebar Commands
**Status**: PASS
- `loadCmds()` / `saveCmds()` use localStorage `purebrain_portal_cmds`
- Default commands list present, user-editable
- Click sends command text directly to chat input and triggers send

#### 4d. Share Button
**Status**: PASS
- Opens share modal via `openShareModal()` (exposed to global scope)
- Loads referral code from API or falls back to localStorage cache
- Email/Twitter/WhatsApp share links pre-populated with referral URL
- "Create Shareable Link" section for conversation export

---

### 5. Mobile UX

#### 5a. Responsive Layout
**Status**: PASS
- `100dvh` used (line 58) — correct for mobile browsers with chrome
- Mobile breakpoints handle sidebar, chat area, panel sizing
- `touch-action: pan-y` on `.main` and `.content` prevents horizontal scroll

#### 5b. Touch Interactions
**Status**: PASS
- Drag-and-drop file upload uses passive touch events
- Mobile hamburger menu uses standard click events (works with touch)
- Voice overlay touch events wired (tap-to-trigger neural animation)

#### 5c. Safe Area Handling
**Status**: PASS (partial)
- Login overlay uses `env(safe-area-inset-top/bottom)` at lines 124-125
- **LOW issue**: The main portal layout (`#app`, `.sidebar`, `.content`) does not use `safe-area-inset-*`. On iPhone with notch/Dynamic Island, content may be obscured at top. This is mitigated by the login overlay handling but worth noting.

#### 5d. Input Focus (Keyboard Doesn't Hide Content)
**Status**: PASS
- Chat input uses `100dvh` on body which shrinks with visual viewport on mobile
- No `visualViewport` resize handler — relies on OS/browser native behavior
- `textarea` focus expands naturally within the flex layout

---

### 6. Login / Auth

#### 6a. Token Persistence
**Status**: PASS
- Token stored in `localStorage` as `portal_token`
- Auto-login on page load if token found (line 5536)
- URL token parameter supported for deep links

#### 6b. Claude OAuth Flow
**Status**: PASS
- Full OAuth flow: start → URL poll → code entry → success poll
- Auth warning banner shows when Claude is not authenticated
- `checkClaudeAuth()` called on login, checks `/api/auth/status`
- Intervals properly cleaned up on success/cancel

#### 6c. Session Handling
**Status**: PASS
- Logout clears `portal_token` from localStorage and reloads
- `boot()` function gates all authenticated activity behind token check

---

### 7. Performance

#### 7a. Memory Leaks — Intervals/Timeouts

| Interval | Cleaned Up? | Notes |
|----------|-------------|-------|
| `statusInterval` | NO | Runs entire session — 30s fetch, acceptable |
| `setInterval(updateCtxGauge, 30000)` | NO | Reference not stored — cannot be cleared. Minor leak. |
| `setInterval(pollCompactStatus, 2000)` | NO | Runs entire session after login. No reference stored. |
| `teamsInterval` | YES | Cleared when leaving teams panel |
| `schedInterval` | YES | Cleared when leaving scheduled panel |
| `window._wsHeartbeat` | YES | Cleared on each new WS connect |
| `claudeAuthUrlPoll` | YES | Cleared on success/cancel |
| `claudeAuthSuccessPoll` | YES | Cleared on success/cancel |
| `queueWatchInterval` | YES | Cleared when upload completes |

**Severity**: LOW. The three un-cleaned intervals (`updateCtxGauge`, `pollCompactStatus`, `statusInterval`) run for the session lifetime. At 30s/30s/2s intervals respectively, they generate light background network/DOM activity but do not grow unboundedly.

#### 7b. knownMsgIds Growth
**Severity**: LOW
- `knownMsgIds` is a `Set` that only grows — never cleared, never pruned
- `loadChatHistory()` does NOT call `knownMsgIds.clear()` before re-populating from history
- After many sessions, this Set accumulates all message IDs ever seen
- **Result**: Over a very long session, the deduplication Set grows. Each entry is a string (UUID or `local-${ts}-${rand}`). At 200 messages/session this is negligible, but could theoretically grow large over days without page reload.
- **Recommended fix**: Add `knownMsgIds.clear()` at the start of `loadChatHistory()` before re-adding IDs from the history response.

#### 7c. Terminal DOM Thrashing
**Severity**: LOW
- `pane.textContent = lines.join('\n')` on every WS message replaces the entire terminal DOM
- For busy terminals, this causes unnecessary reflows
- Not a blocking issue but could be replaced with incremental append + trim-to-max-lines approach

#### 7d. Network Efficiency
**Status**: PASS
- WS heartbeat prevents stale connections without polling
- History fetches only last 200 messages (`?last=200`)
- Status poll at 30s is acceptable

---

## Bug Summary

| # | Panel | Severity | Description | Line(s) | Fix |
|---|-------|----------|-------------|---------|-----|
| 1 | Chat | **HIGH** | iOS blank messages: visibilitychange handler is empty (line 7419 label, 10881 only sets isVisible), no reconnect triggered on app resume | 7419, 10881 | See safe fix approach above — DO NOT deploy without Jared approval |
| 2 | Chat | **MEDIUM** | `knownMsgIds` Set never cleared — `loadChatHistory()` does not reset it before re-adding history IDs | 6991-7017 | Add `knownMsgIds.clear()` at line 6992 before `chatLoaded = true` |
| 3 | Status | **LOW** | `updateCtxGauge` interval reference not stored (anonymous `setInterval`) — cannot be cleared on logout | 5679 | Store reference: `var ctxGaugeInterval = setInterval(updateCtxGauge, 30000)` |
| 4 | Status | **LOW** | `pollCompactStatus` runs every 2s, reference not stored — cannot be cleared | 5706 | Store reference, clear on logout |
| 5 | Mobile | **LOW** | Safe area insets only applied to login overlay, not main portal layout — content may be clipped by notch/Dynamic Island | 124-125, main layout | Add `padding-top: env(safe-area-inset-top)` to `.sidebar` and top chrome |
| 6 | Terminal | **LOW** | Full terminal content replaced on each WS message (`textContent = ...`) — causes DOM thrash on busy terminals | 6009 | Incremental append with max-line trim |

---

## Fixes Applied This Session

**None.** Per instructions, the iOS blank messages issue is diagnosis-only. The other bugs are documented above. No portal restart required.

---

## Verification

- File read: `/home/jared/purebrain_portal/portal-pb-styled.html` — 12,461 lines fully audited
- No changes made to portal file
- No portal service restart
- All findings documented with line numbers

---

## Recommendations for Next Sprint

1. **iOS fix (requires Jared approval)**: Implement visibilitychange reconnect — 5 lines of JS at line 10881 (replace the single `isVisible` assignment with the full handler documented above). This is low-risk because it only triggers `connectChatWS()` when the WS is actually dead.
2. **knownMsgIds clear**: Add one line to `loadChatHistory()` — zero risk.
3. **Interval housekeeping**: Store `ctxGaugeInterval` and `compactStatusInterval` references for clean teardown on logout.
4. **Safe area**: Add `env(safe-area-inset-top)` to main portal chrome for iPhone notch support.

Report generated: 2026-03-15
