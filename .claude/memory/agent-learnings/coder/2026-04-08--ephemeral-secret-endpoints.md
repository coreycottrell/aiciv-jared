# Ephemeral Secret Endpoints Implementation

**Date**: 2026-04-08
**Agent**: coder
**Type**: teaching
**Topic**: Burn-on-read ephemeral secret sharing for log server

---

## What Was Built

Added two endpoints to `purebrain_log_server.py` for secure ephemeral secret sharing:

1. **POST /api/ephemeral-secret** - Create a burn-on-read secret
2. **GET /api/ephemeral-secret/<uuid>** - View (and burn) a secret

---

## Implementation Details

### Storage
- In-memory only (survives until server restart)
- Thread-safe with `_ephemeral_lock`
- Opportunistic cleanup of expired entries on each POST/GET

### Security Features
1. **Admin token auth** - Constant-time comparison via `hmac.compare_digest`
2. **UUID as auth** - 128-bit unguessable token for viewing
3. **Burn-on-read** - Secret deleted immediately after first view
4. **TTL enforcement** - Configurable expiration (default 24h)
5. **No disk persistence** - Secrets never written to disk
6. **No secret logging** - Secret values never appear in logs

### Code Additions

**File**: `/home/jared/projects/AI-CIV/aether/tools/purebrain_log_server.py`

**Imports added** (lines 19, 30):
- `import hmac` (for constant-time comparison)
- `timedelta` added to datetime imports

**Global state** (lines 89-93):
```python
_ephemeral_secrets: Dict[str, Dict[str, Any]] = {}
_ephemeral_lock = threading.Lock()
```

**Endpoints** (lines 3320-3455, approximately):
- `_cleanup_expired_secrets()` - Helper function
- `create_ephemeral_secret()` - POST endpoint
- `view_ephemeral_secret(secret_uuid)` - GET endpoint

---

## API Specification

### POST /api/ephemeral-secret

**Auth**: `X-Admin-Token` header (matches `ADMIN_TOKEN` env var)

**Request**:
```json
{
  "secret": "sensitive-value",
  "ttl_seconds": 86400
}
```

**Response** (200):
```json
{
  "ok": true,
  "view_url": "https://api.purebrain.ai/api/ephemeral-secret/<uuid>",
  "expires_at": "2026-04-09T12:34:56.789Z"
}
```

**Errors**:
- 401: Unauthorized (bad/missing admin token)
- 400: Invalid request body

---

### GET /api/ephemeral-secret/<uuid>

**Auth**: None (UUID is the auth)

**Response** (200, first view):
```json
{
  "ok": true,
  "secret": "sensitive-value"
}
```

**Response** (410 Gone):
```json
{
  "error": "secret already viewed or expired"
}
```

Returned when:
- Secret doesn't exist
- Secret already viewed
- Secret expired

---

## Test Script

**Path**: `/tmp/test_ephemeral_secret.py`

**Usage**:
```bash
export ADMIN_TOKEN="your-admin-token"
python3 /tmp/test_ephemeral_secret.py
```

**Tests**:
1. Create secret with admin token
2. View secret (should succeed and return value)
3. View again (should return 410 Gone - burned)
4. Create short-TTL secret, wait for expiration (should return 410 Gone)

---

## Patterns Learned

### 1. Constant-Time Token Comparison
Always use `hmac.compare_digest()` for token/password comparison to prevent timing attacks:

```python
if not hmac.compare_digest(expected, provided):
    return unauthorized
```

### 2. Opportunistic Cleanup
For in-memory data structures with TTL, clean up expired entries on each access rather than background thread:

```python
def _cleanup_expired_secrets():
    now = datetime.now(timezone.utc)
    expired_keys = [k for k, v in store.items() if v['expires_at'] <= now]
    for k in expired_keys:
        del store[k]
```

### 3. Burn-on-Read Pattern
For one-time secrets:
1. Check if already viewed (before expiry check)
2. Delete immediately
3. Return secret
4. Log access (without secret value)

---

## File Paths

**Modified**:
- `/home/jared/projects/AI-CIV/aether/tools/purebrain_log_server.py`

**Created**:
- `/tmp/test_ephemeral_secret.py`

**Status**: Code complete, ready for security review and testing.
