---
name: atproto-session-heal
description: Self-heal corrupted atproto/Bluesky session strings. Catches BOTH truncated and bloated (9-part) session corruption that crashes Client.login(session_string=...). Use in any self-healing Bluesky session monitor.
allowed-tools: Bash, Read, Write
status: provisional
tick_count: 0
last_used: 2026-06-03
introduced: 2026-06-03
author: aether-collective
tags: [bluesky, atproto, self-healing, session, gotcha, reliability]
---

# atproto Session Self-Heal

## Purpose

A self-healing Bluesky session monitor must recognize **all** corruption modes of
the atproto session string and re-login when it sees them. The non-obvious failure
is **bloated** session strings, not just truncated ones.

## The Gotcha (hard-won 2026-06-03)

`atproto`'s `Client.login(session_string=...)` expects a **5-part** session string.

Two distinct corruption modes both raise a `ValueError`:

| Corruption | What it looks like | Exception |
|------------|-------------------|-----------|
| **Truncated** | short / missing fields | `not enough values to unpack (expected 5)` |
| **Bloated (9-part)** | a `session_managed` marker + **duplicated** handle/did/pds glued on | `too many values to unpack (expected 5)` |

A naive heal-monitor that only matches `"not enough values to unpack"` (or worse,
classifies the bloated case as `UNKNOWN_ERROR`) goes **blind** to the 9-part mode —
the session stays broken and every Bluesky BOOP silently fails.

## The Fix

Use the **substring `"values to unpack"`** as the heal trigger — it catches both
directions in one check. Treat it as "file is malformed → re-login from creds."

```python
heal_signals = (
    "Authentication Required",
    "values to unpack",          # catches BOTH too-many (9-part) AND not-enough (truncated)
    "Token has expired",
    "InvalidToken",
)
if any(sig in str(err) for sig in heal_signals):
    relogin_from_env()           # BSKY_USERNAME / BSKY_PASSWORD from .env
    rewrite_session_file(mode=0o600)   # rewrite clean 5-part, perms 600
```

## Heal Procedure (manual or automated)

1. Detect: `Client.login(session_string=...)` raises any `ValueError` containing
   `"values to unpack"`, OR auth-required / expired-token.
2. Re-login from credentials in `.env` (`BSKY_USERNAME`, `BSKY_PASSWORD`).
3. Rewrite **all** canonical session paths with a clean 5-part string, `chmod 600`.
4. Verify: a fresh `Client.login(session_string=...)` succeeds before declaring healthy.

## Reference (Aether implementation)

- `tools/bsky-session-health/check_and_heal.py` — `check_session()` / `heal_signals`
- Commit `40db6f2` (2026-06-03) — added the generic `"values to unpack"` trigger.

## Gotchas

- Don't match only `"too many"` or only `"not enough"` — use the shared substring.
- Always re-verify after heal; a rewrite that itself produced a bad string will
  otherwise be reported as "healed" when it isn't (false-green).
- Session files are secrets → `0o600`, never commit them.
