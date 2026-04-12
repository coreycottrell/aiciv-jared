# Referral API Infinite Recursion Bug Fix — 2026-03-14

## Context
Jared reported purebrain.ai/refer/ and /refer/?code=JAREDSB0 were broken — pages load but nothing works.

## Root Cause 1: Infinite Recursion in _referral_db()

**File**: `/home/jared/purebrain_portal/portal_server.py`

**Bug** (lines ~2085-2090):
```python
@asynccontextmanager
async def _referral_db():
    async with _referral_db() as db:  # CALLS ITSELF — infinite recursion
        await db.execute("PRAGMA foreign_keys = ON")
        yield db
```

**Symptom**: All 19 referral endpoint callers used `async with _referral_db()`. Each call would hang ~70 seconds (asyncio timeout) then return HTTP 500 "Internal Server Error".

**Fix**:
```python
@asynccontextmanager
async def _referral_db():
    async with aiosqlite.connect(str(REFERRALS_DB)) as db:  # correct
        await db.execute("PRAGMA journal_mode = WAL")
        await db.execute("PRAGMA foreign_keys = ON")
        yield db
```

## Root Cause 2: Register Requires Password but Form Has None

**Bug**: `api_referral_register` required password >= 6 chars from unauthenticated callers. But the public form at /refer/ only sends name+email.

**Fix**: Auto-generate password when not provided (any caller):
```python
if not password or len(password) < 6:
    password = secrets.token_urlsafe(16)  # auto-generate for all
```

## Diagnostic Path
1. `curl https://app.purebrain.ai/api/referral/dashboard?code=JAREDSB0` → HTTP 500
2. Local test `curl http://localhost:8097/...` → hangs 70+ seconds then empty reply
3. Found `_referral_db()` calls itself — infinite recursion
4. Backup comparison (`portal_server.py.bak-referral-fix-20260313`) confirmed the self-call was introduced during the 2026-03-13 refactor

## Architecture Note
- purebrain.ai is served via Cloudflare Pages (static Astro build) — wp-json/* routes return homepage HTML
- app.purebrain.ai is the live portal server (uvicorn on port 8097, proxied via Cloudflare Tunnel)
- The /refer/ page calls app.purebrain.ai/api/referral/* directly (NOT via WP proxy)
- Dashboard is accessible with just ?code= param, no password needed (legacy behavior)

## Resolution
Portal server restarted at 2026-03-14 ~13:15 UTC. Both endpoints verified working via app.purebrain.ai.
