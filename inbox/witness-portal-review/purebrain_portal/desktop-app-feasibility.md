# Desktop App Feasibility Report: AiCIV Desktop

**Date**: 2026-03-01
**Requested by**: Corey (Primary / Witness)
**Research by**: Witness Research Team Lead + 2 specialist researchers
**Status**: Final

---

## Executive Summary

A desktop app for AI civilization users is **highly feasible and strategically compelling**. The primary motivation — eliminating the mixed content HTTP/HTTPS problem — is solved immediately by any desktop app framework. The recommended approach:

**Electron + existing HTML monolith for a rapid MVP (1-2 days), evolving to Electron + React rebuild for a polished product (1-2 weeks).**

The core insight: a desktop app connects to containers via **direct SSH** rather than through the HTTP gateway. This eliminates the gateway as a bottleneck for terminal connections, removes the mixed-content issue permanently, and enables a richer real-time experience. Terminal mode becomes a genuine PTY stream (not a tmux snapshot poll). Chat mode uses the same proven tmux inject/capture pattern as the Telegram bot.

Key findings:
- Electron is the clear framework winner for this use case (xterm.js native territory, direct SSH via ssh2, Node.js ecosystem)
- The 13.5K HTML monolith can be wrapped and shipped as a desktop app in under a day
- Direct SSH architecture is superior to gateway-via-HTTP for terminal — proven by electerm (30K+ stars)
- Chat mode mirrors the Telegram bot pattern exactly — same tmux send-keys/capture-pane logic
- Multi-CIV support (sidebar with Witness/Clarity/Nexus) follows Telegram's multi-account pattern

---

## 1. Framework Decision

### Recommendation: Electron

**Why Electron wins for this project:**

| Criterion | Electron | Tauri v2 | Others |
|-----------|----------|----------|--------|
| **Bundle size** | ~85 MB installer | ~3-10 MB | Wails ~10MB, NW.js ~500MB |
| **Memory (idle)** | ~120-250 MB | ~30-93 MB | Wails ~400MB, Neutralino ~880MB |
| **xterm.js compatibility** | EXCELLENT (VS Code, Hyper, electerm) | Good (system webview varies by OS) | Unknown/untested |
| **SSH library (ssh2)** | Native Node.js — mature, battle-tested | Would need Rust SSH crate or WASM bridge | — |
| **node-pty** | Direct integration | Not available natively | — |
| **Reuse existing HTML monolith** | YES — `loadFile('frontend.html')` | Partial rewrite needed | — |
| **Mixed content eliminated** | YES (file:// protocol) | YES | YES |
| **Auto-update** | Mature (electron-updater, 1.2M/wk downloads) | Built-in but newer | Variable |
| **Cross-platform signing** | Fully documented (Mac/Win/Linux) | Supported but less documented | Limited |
| **Team skill match** | JavaScript — matches existing codebase | Rust backend needed | — |
| **Verdict** | **RECOMMENDED** | Strong future option | Skip |

**Why NOT Tauri for now:** Tauri v2 (stable Oct 2024) is excellent but the ssh2 + xterm.js + node-pty ecosystem is deeply Node.js-native. Electerm (30K+ GitHub stars) proves the entire Electron SSH terminal stack in production. Porting to Rust would add weeks for uncertain gains. Tauri is the right choice for a v2 ground-up rebuild if binary size or mobile support become priorities.

**Why NOT PWA:** PWAs enforce HTTPS and prohibit mixed content by specification. A PWA frontend talking to an HTTP gateway is architecturally identical to the current problem — it doesn't solve it, it doubles down on it.

---

## 2. Architecture

### 2.1 Connection Architecture

The key architectural shift: **direct SSH to containers, no HTTP gateway for terminal or chat.**

```
┌─────────────────────────────────────────────────────────────────┐
│                    AiCIV Desktop App (Electron)                  │
│                                                                   │
│  ┌──────────────────────────┐  ┌──────────────────────────────┐  │
│  │ MAIN PROCESS (Node.js)   │  │ RENDERER (Chromium)          │  │
│  │                          │  │                              │  │
│  │ ┌────────────────────┐   │  │ ┌──────────┐ ┌───────────┐  │  │
│  │ │ Connection Manager │◄──IPC►│ │ Sidebar  │ │ Terminal  │  │  │
│  │ │ ssh2.Client pool   │   │  │ │ CIV list │ │ xterm.js  │  │  │
│  │ └──┬──────┬──────┬───┘   │  │ └──────────┘ └───────────┘  │  │
│  │    │      │      │        │  │              ┌───────────┐  │  │
│  │ ┌──▼──┐ ┌─▼────┐ │        │  │              │ Chat      │  │  │
│  │ │Safe │ │SQLite│ │        │  │              │ Bubbles   │  │  │
│  │ │Store│ │msgs  │ │        │  │              │ Input box │  │  │
│  │ └─────┘ └──────┘ │        │  │              └───────────┘  │  │
│  │ ┌────────────────┐│        │  └──────────────────────────────┘  │
│  │ │ Auto-Updater   ││        │                                     │
│  │ │ GitHub Releases││        │                                     │
│  │ └────────────────┘│        │                                     │
│  └──────────────────┘│        │                                     │
└─────────────────────────────────────────────────────────────────┘
         │                │                │
     SSH :2203        SSH :2208        SSH :220N
         ▼                ▼                ▼
  ┌──────────┐    ┌──────────────┐   ┌──────────────┐
  │ witness  │    │clarity-jordan│   │ CIV-N        │
  │ container│    │ container    │   │ container    │
  │ tmux     │    │ tmux         │   │ tmux         │
  │ Claude   │    │ Claude       │   │ Claude       │
  └──────────┘    └──────────────┘   └──────────────┘
```

### 2.2 Terminal Mode (Direct SSH PTY)

**Current (web):** Gateway polls `tmux capture-pane` → sends delta JSON over WebSocket → xterm.js replays
**Desktop:** `ssh2.Client.shell()` returns a live PTY stream → pipe directly to xterm.js

```javascript
// Main process: establish SSH connection
conn.connect({
  host: '37.27.237.109',
  port: 2203,  // witness container
  username: 'aiciv',
  privateKey: safeStorage.decryptString(storedKey),
  keepaliveInterval: 10000
});

conn.on('ready', () => {
  conn.shell({ term: 'xterm-256color', cols: 220, rows: 50 }, (err, stream) => {
    // pipe to renderer via IPC
    stream.on('data', data => mainWindow.webContents.send('terminal-data', data));
    ipcMain.on('terminal-input', (e, data) => stream.write(data));
    // Once inside: type 'tmux attach -t witness-primary'
  });
});
```

**Why this is better:** No polling, no delta computation, no snapshot lag. Real terminal input/output. The user is actually in the tmux session, not watching a replay.

**One SSH connection, two modes:** A single `ssh2.Client` can multiplex:
- `conn.shell()` for the live terminal PTY
- `conn.exec('tmux send-keys -t witness-primary -l "message" Enter')` for chat injection
- `conn.exec('tmux capture-pane -t witness-primary -p')` for chat output capture

### 2.3 Chat Mode (Telegram Pattern)

Chat mode mirrors the proven Telegram bot architecture exactly:

**Input:** User types message → `conn.exec('tmux send-keys -t SESSION -l "MESSAGE" Enter')`
**Output:** Poll `tmux capture-pane` every 500ms → diff against previous → render new lines as AI bubble

```
User types "What's the fleet status?"
  ↓
IPC: renderer → main process
  ↓
conn.exec('tmux send-keys -t witness-primary -l "What\'s the fleet status?" Enter')
  ↓
Claude Code in container receives input, processes, generates response
  ↓
Poll: conn.exec('tmux capture-pane -t witness-primary -p -S -')
  ↓
Diff against previous → extract new lines → send via IPC
  ↓
Renderer renders as AI chat bubble (streaming: append tokens as they arrive)
```

**Message storage:** `better-sqlite3` for local persistence (same as Signal Desktop, Obsidian). Schema: `messages(id, civ_name, role, content, timestamp)`. No cloud dependency.

**Notifications:** `new Notification({ title: 'Witness', body: '...' })` for OS-native alerts. `app.setBadgeCount(n)` for macOS dock badge.

### 2.4 Auth & Credentials

The gateway JWT is **not needed** for the desktop app. SSH key authentication replaces it.

```javascript
// Electron safeStorage (replaces deprecated keytar — archived Dec 2022)
const { safeStorage } = require('electron');
const Store = require('electron-store');
const store = new Store();

// Store encrypted SSH key
function saveSSHKey(civName, privateKey) {
  const encrypted = safeStorage.encryptString(privateKey);
  store.set(`creds.${civName}`, encrypted.toString('latin1'));
}

// Retrieve
function getSSHKey(civName) {
  const enc = store.get(`creds.${civName}`);
  return enc ? safeStorage.decryptString(Buffer.from(enc, 'latin1')) : null;
}
```

Platform backends: macOS Keychain, Windows DPAPI, Linux kwallet/libsecret.

**First-launch flow:** Enter SSH connection details + select key file → test connection → store encrypted → auto-connect on all future launches.

### 2.5 Multi-CIV Support (Telegram Multi-Account Pattern)

Sidebar shows all configured CIVs. Each CIV = one `ssh2.Client` connection + one SQLite message DB.

```
┌─────────────────────────────────────────────────────┐
│ [W] Witness    │ [Tab: Terminal] [Tab: Chat]          │
│ [C] Clarity    │                                      │
│ [N] Nexus      │  $ tmux attach -t witness-primary    │
│ [K] Keel       │  [live terminal output streams here] │
│ [+] Add CIV    │                                      │
└─────────────────────────────────────────────────────┘
```

Active CIV's terminal/chat is shown in main panel. Switching CIV swaps the SSH stream. Unread message badges aggregate across all CIVs.

---

## 3. Converting the Existing Frontend

### Option A: Wrap the HTML Monolith (Fastest — Hours)

```javascript
// main.js — ~30 lines total
const { app, BrowserWindow } = require('electron');
const path = require('path');

function createWindow() {
  const win = new BrowserWindow({
    width: 1400, height: 900,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true
    }
  });
  win.loadFile('purebrain-frontend.html');
}

app.whenReady().then(createWindow);
```

**Result:** The existing 13.5K line HTML monolith runs as a desktop app. All existing functionality works. Mixed content issues disappear immediately (file:// protocol, not HTTPS). Gateway still used for auth + terminal, but the HTTP-in-HTTPS problem is gone.

**Limitations of this approach:**
- Gateway is still the intermediary (not using direct SSH yet)
- No OS keychain, notifications, or tray icon
- Chat mode still web-style, not Telegram-style bubbles
- Still polling tmux via gateway HTTP

**Effort: S (Small) — 1-2 days including testing**

### Option B: Electron + New Chat/Terminal UI (Recommended — Weeks)

New Electron app with:
- Sidebar (CIV list)
- Terminal view (xterm.js + direct SSH via ssh2)
- Chat view (message bubbles, input box, streaming)
- OS integration (notifications, tray, keychain)
- Auto-update

**Can reuse from existing monolith:**
- xterm.js terminal initialization and addons
- Auth flow logic (adapted for local storage)
- Connection configuration patterns
- CSS design tokens / color scheme

**Must rebuild:**
- Gateway HTTP calls → direct SSH2 calls
- WebSocket terminal → ssh2.Client.shell() PTY
- Basic HTML layout → sidebar + chat bubble components
- No framework required (vanilla JS + custom elements), or use React/Vue for component structure

**Effort: M (Medium) — 1-2 weeks for MVP with terminal + chat + multi-CIV**

---

## 4. Effort Estimates

| Deliverable | Approach | Effort | Notes |
|-------------|----------|--------|-------|
| **MVP: Wrap HTML monolith** | Electron loadFile() | **S** (1-2 days) | Eliminates mixed content immediately; gateway still used |
| **MVP+: Wrap + direct SSH terminal** | Electron + ssh2 | **S-M** (3-5 days) | Replace gateway terminal with direct PTY |
| **Full: Terminal + Chat + Multi-CIV** | Electron rebuild | **M** (1-2 weeks) | New UI, sqlite, notifications, tray |
| **Full: Same but Tauri** | Tauri + React | **L** (3-5 weeks) | Smaller binary; requires Rust SSH work |
| **Polish: Auto-update + signing** | electron-builder | **S** (1-2 days) | Add-on to any Electron build |
| **Polish: Mobile (iOS/Android)** | Tauri v2 | **XL** (months) | Requires full architecture rethink |

**Recommended sequence:**
1. **Sprint 1 (this week):** Wrap HTML monolith → ship immediately, eliminate mixed content
2. **Sprint 2 (next):** Add direct SSH terminal (ssh2 + node-pty), remove gateway dependency for terminal
3. **Sprint 3:** Add chat UI (bubble view, sqlite, notifications)
4. **Sprint 4:** Multi-CIV sidebar, auto-update, signing

---

## 5. What Happens to the Gateway

The desktop app does NOT replace the gateway. The gateway continues serving:

| Use Case | Desktop App | Gateway |
|----------|-------------|---------|
| Terminal streaming | Direct SSH PTY (ssh2) | Not needed |
| Chat injection | Direct tmux send-keys (ssh2) | Not needed |
| Auth (first login) | Local SSH key + safeStorage | Not needed |
| Magic links (web) | N/A | Still needed |
| OAuth flows (Claude.ai) | Browser redirect (can use shell.openExternal) | Still needed |
| Mobile / Telegram clients | N/A | Still needed |
| Web access (no desktop app) | N/A | Still needed |

**The gateway becomes the web/mobile backend. The desktop app talks SSH.**

---

## 6. What Corey Said — Mapped to Architecture

> "Terminal mode is literally just an embedded tmux terminal window."

**Yes.** With direct SSH + ssh2.Client.shell() → xterm.js, it's a genuine embedded tmux terminal. The user attaches to `tmux attach -t witness-primary` through the PTY stream. No polling, no snapshots.

> "We populate and use chat mode a lot like we do w Telegram"

**Yes.** The chat architecture is identical to the Telegram bot: tmux send-keys for input, tmux capture-pane polling for output. The difference is a native bubble UI instead of Telegram's interface. Message history persists in SQLite locally.

---

## 7. Risk Flags

| Risk | Severity | Mitigation |
|------|----------|------------|
| SSH ports exposed to internet | HIGH | SSH key auth only (no password). Consider VPN or allowlist known IPs. |
| SSH key security on user machine | MEDIUM | safeStorage encrypts using OS keychain. Never transmit the key. |
| Electron security (Node.js access) | MEDIUM | contextIsolation: true, nodeIntegration: false, preload scripts only. |
| xterm.js rendering on Linux (WebKit) | LOW | Electron ships bundled Chromium — no OS webview variance. Works identically on all platforms. |
| better-sqlite3 native module | MEDIUM | Requires @electron/rebuild after npm install. Pin Electron + sqlite3 versions. CI test on all 3 platforms. |
| SSH connection drops on flaky networks | MEDIUM | keepaliveInterval: 10000 + exponential backoff reconnect logic. Queue chat messages during disconnect. |

---

## 8. Recommended Stack

```
aiciv-desktop/
  package.json              # electron, electron-builder, ssh2, better-sqlite3, xterm
  main.js                   # main process: window creation, connection manager
  preload.js                # IPC bridge (secure, contextIsolation)
  src/
    ui/
      sidebar.html          # CIV list
      terminal.html         # xterm.js terminal
      chat.html             # message bubbles + input
    lib/
      ssh-manager.js        # ssh2.Client pool, reconnect logic
      tmux-chat.js          # send-keys inject, capture-pane poll, delta extract
      credentials.js        # safeStorage encrypt/decrypt
      message-store.js      # better-sqlite3 wrapper
    assets/
      icons/                # per-CIV icons
```

**Dependencies:**
- `electron` (^33.x)
- `ssh2` (^1.x) — SSH connections to containers
- `@xterm/xterm` + `@xterm/addon-fit` + `@xterm/addon-web-links` — terminal
- `better-sqlite3` — local message persistence
- `electron-store` — settings/config persistence
- `electron-updater` — auto-updates
- `electron-builder` (dev) — packaging + signing

---

## 9. Conclusion

**Build the desktop app. Start with the HTML wrap (1-2 days) to immediately eliminate the mixed content pain. Then evolve to direct SSH architecture for a significantly better experience.**

The architecture is proven (electerm does exactly this, live in production). The tech stack is all JavaScript — no new languages. The chat mode is identical to what already works via Telegram. The terminal becomes a real PTY instead of a tmux snapshot replay.

This would make AiCIV the first AI civilization platform with a native desktop client — terminal + chat + multi-CIV in one window, like a Telegram for AI agents.

---

## Appendix: Sources

**Framework Research:**
- Electron vs Tauri comparison 2025 (DoltHub, Levminer, Hopp, Raftlabs, Codeology)
- Tauri v2.0 stable release announcement (Oct 2024)
- Web-to-desktop framework comparison benchmarks (Elanis/web-to-desktop-framework-comparison)
- Electron auto-update docs + electron-updater

**Terminal Architecture:**
- electerm source (deepwiki.com/electerm) — proven Electron SSH + xterm.js in production
- node-pty (Microsoft) + Electron integration examples
- ssh2 (mscdex) — Node.js SSH implementation
- example-electron-xterm-ssh2 (MyXterm)

**Chat Architecture:**
- SSE streaming patterns for LLM responses (Upstash, KeyValue Systems)
- Telegram Desktop (tdesktop) multi-account architecture
- Electron desktop chat app tutorial (DeadSimpleChat)

**Credentials:**
- Electron safeStorage API (official docs)
- VS Code keytar → safeStorage migration (GitHub issue #185677)

**Auto-Update + Signing:**
- electron-builder auto-update docs
- Tauri macOS + Windows code signing guides
- electron-updater GitHub Releases tutorial
