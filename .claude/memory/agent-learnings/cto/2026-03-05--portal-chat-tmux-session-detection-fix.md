# Portal Chat Messages Ignored — Root Cause & Fix

**Date**: 2026-03-05
**Type**: operational
**Topic**: Portal chat message injection failing due to wrong tmux session detection

## Root Cause

The portal server's `get_tmux_session()` function in `/home/jared/purebrain_portal/portal_server.py` was not finding the active Claude Code session.

**The failure chain:**
1. `.current_session` file contains `28` (just a number — the tmux session ID)
2. `tmux has-session -t 28` fails — no session literally named `28`
3. Fallback scans for sessions with "aether-primary" or "aether" in the name
4. Claude Code sessions are numbered (e.g. `28`), not named with those strings
5. Falls back to dead hardcoded value `aether-primary-20260205-153800`
6. `tmux send-keys -t aether-primary-20260205-153800` fails silently → message lost

**Why Telegram works but portal doesn't:**
`telegram_bridge.py`'s `get_current_session()` uses a smarter approach — it FIRST checks for the currently **attached** tmux session (`#{session_attached}:1`). The attached session IS the active Claude Code session, regardless of its name. Portal server was missing this step.

## The Fix

Added attached-session detection as the FIRST step in `get_tmux_session()`:

```python
# FIRST: Find the currently attached session — mirrors telegram_bridge logic.
try:
    out = subprocess.check_output(
        ["tmux", "list-sessions", "-F", "#{session_name}:#{session_attached}"],
        stderr=subprocess.DEVNULL, text=True
    )
    for line in out.splitlines():
        if line.strip().endswith(":1"):
            attached = line.split(":")[0].strip()
            if attached:
                return attached
except Exception:
    pass
```

This is added BEFORE the existing `.current_session` file check and named-session scan.

## File Changed

`/home/jared/purebrain_portal/portal_server.py` — lines 78-92 (new attached-session block added)

## Requires Restart

The portal server (PID 2566155) must be restarted to pick up the fix. The file is written to disk. A graceful restart via systemd or manual kill+restart is needed.

## Pattern for Future

Any tool that needs to find the active Claude Code tmux session should ALWAYS check for the attached session first. Claude Code session names are numeric (e.g. `28`), not human-readable strings. The attached session is always the right target.

Reference: `telegram_bridge.py` `get_current_session()` method — the authoritative implementation.
