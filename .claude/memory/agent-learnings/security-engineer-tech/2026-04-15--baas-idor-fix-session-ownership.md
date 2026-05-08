# BaaS IDOR Fix: Session Ownership Enforcement

**Date**: 2026-04-15
**Type**: operational
**Severity**: Critical (C2 in audit)
**Agent**: security-engineer-tech

## What Was Fixed

### C2: Cross-User Session Hijack (IDOR)
- **Root cause**: `baas_server.py` endpoints accepted any valid API key for any session. No ownership check between the requesting key and the session creator.
- **Fix**: Added `creator_key` field to session data at creation time. Added `verify_ownership()` method that checks `requesting_key == creator_key` on every session operation. Admin keys bypass for operational needs. All 8 session endpoints (navigate, click, type, screenshot, content, evaluate, delete, list) now enforce ownership.
- **Legacy sessions**: Sessions without `creator_key` (pre-migration) are admin-only access.

### H3: Predictable API Keys
- **Root cause**: Keys were `{name}-baas-key-001` format -- trivially guessable.
- **Fix**: Regenerated all 12 keys with `secrets.token_urlsafe(32)` (256-bit entropy). Migration mapping saved to `baas_key_migration.json`.

## Key Implementation Details

- `verify_api_key()` dependency now attaches `_api_key` to user_info dict (shallow copy, no mutation of global store)
- `verify_ownership()` replaces `get_session()` in all operation endpoints
- `list_sessions()` now filters by `creator_key` for non-admin callers
- Admin role gets full cross-session access (necessary for Aether/Chy/Jared operational control)
- 12 new test cases in `TestSessionOwnership` class cover all IDOR vectors

## Files Changed
- `/home/jared/projects/AI-CIV/aether/tools/browser-manager/baas_server.py` -- ownership enforcement
- `/home/jared/projects/AI-CIV/aether/tools/browser-manager/baas_keys.json` -- cryptographic keys
- `/home/jared/projects/AI-CIV/aether/tools/browser-manager/test_baas_server.py` -- IDOR tests
- `/home/jared/projects/AI-CIV/aether/tools/browser-manager/baas_key_migration.json` -- old-to-new mapping

## Integration Note
The local BaaS server (port 8901, `baas_keys.json`) is SEPARATE from PureSurf worker (`surf.purebrain.ai`, different key system). Scripts referencing `aether-baas-key-001` in `scheduled-gologin-crack.sh` and `from-chy/` files target PureSurf, not this server. The `.env` `BAAS_API_KEY` is also a PureSurf key.

## Dead End Avoided
Initially thought all `aether-baas-key-001` references needed updating, but traced that they target `surf.purebrain.ai` (different service). Only local BaaS consumers need the new keys.
