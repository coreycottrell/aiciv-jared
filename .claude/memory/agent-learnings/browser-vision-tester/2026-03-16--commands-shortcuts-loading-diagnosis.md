# Commands & Shortcuts Panels Stuck "Loading..." - Full Diagnosis

**Date**: 2026-03-16
**Agent**: browser-vision-tester
**Type**: teaching + operational
**URL**: https://app.purebrain.ai (portal-pb-styled.html)

---

## Summary

Commands and Shortcuts panels are stuck on "Loading..." text. Full diagnosis performed.
Root cause: `switchPanel()` in the served HTML does NOT call `window.loadCommands()` or `window.loadShortcuts()` even though the disk file at `/home/jared/purebrain_portal/portal-pb-styled.html` has those lines.

---

## Architecture Understanding

- `app.purebrain.ai` -> Cloudflare tunnel -> nginx port 8099 -> proxies to `127.0.0.1:8097`
- Portal server runs at `/home/jared/purebrain_portal/portal_server.py`
- Serves `portal-pb-styled.html` via FileResponse on each request
- Systemd service: `aether-portal.service`

## What Was Confirmed Working

1. `typeof window.loadCommands === 'function'` - YES, defined
2. `typeof window.loadShortcuts === 'function'` - YES, defined
3. `/api/commands` returns HTTP 200 with valid JSON data
4. `/api/shortcuts` returns HTTP 200 with valid JSON data
5. `window.loadCommands()` called manually works perfectly - renders full content
6. Click events DO reach the nav items (capture phase listener confirmed)
7. `panel-commands` div IS activated (adds `active` class) on click

## What Was Confirmed Broken

`switchPanel()` in the SERVED HTML does NOT have these lines:
```js
if (panel === 'commands') { if (window.loadCommands) window.loadCommands(); }
if (panel === 'shortcuts') { if (window.loadShortcuts) window.loadShortcuts(); }
```

The disk file HAS them (line 7336-7337 in portal-pb-styled.html) but the serving
version is older - confirmed by wrapping `window.loadCommands` before click and
never seeing the wrapped version called.

## Evidence Chain

1. Click fires on nav item (capture phase logs confirm)
2. Panel activates (CSS class added)
3. `window.loadCommands` IS a function (confirmed inside click handler)
4. `[CMD] loadCommands called` NEVER logs - meaning switchPanel doesn't call it
5. Manual `window.loadCommands()` call works (renders content, logs `[CMD]` lines)
6. Conclusion: switchPanel's version lacks the dispatch calls

## Secondary Issue Discovered

Portal server is crashing/restarting frequently (OOM - consuming 1GB+ RAM).
Systemic restarts visible: new PIDs appearing every ~90 seconds.
Memory: 1.0G (high: 1.0G max: 1.5G). OOM killer likely terminating it.

## Console Errors Present (Not Related to Commands Bug)

- 3x 404 errors for upload file references with malformed filenames
  (filenames contain path text appended: "Screenshot 2026-03-16 -- USE Read tool on /home...")
  These are file attachment display bugs in chat history, not blocking.

## Fix Required

In `portal-pb-styled.html`, inside `function switchPanel(panel)`, after line:
```js
if (panel !== 'agents' && agentsInterval) { clearInterval(agentsInterval); agentsInterval = null; }
```

Add:
```js
if (panel === 'commands') { if (window.loadCommands) window.loadCommands(); }
if (panel === 'shortcuts') { if (window.loadShortcuts) window.loadShortcuts(); }
```

These lines exist in the file but the running code doesn't have them, suggesting
a file-write race condition or the server process cached an older version at startup.

## Quick Test After Fix

```python
# In browser console:
# 1. Click Commands panel
# 2. Check console for: [CMD] loadCommands called. loaded=false
# 3. Check console for: [CMD] fetch status=200
# 4. Panel should populate in ~500ms
```

## Portal Health Note

Portal has been restarting every 60-90 seconds throughout this session.
Memory limit: 1.5GB (systemd), reaching 1.0GB+.
Recommend investigating memory leak or reducing history file size before next session.
