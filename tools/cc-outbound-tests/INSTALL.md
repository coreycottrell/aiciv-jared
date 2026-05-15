# CC Outbound Endpoint - Installation Guide

**Version**: 1.0  
**Date**: 2026-05-15  
**Branch**: `feat/cc-outbound-endpoint-2026-05-15`

---

## Overview

Production-grade HTTP endpoint for posting messages to Command Center from CIV portals.

**Replaces**: `tools/cc-send.sh` (throwaway bash wrapper)

**Features**:
- Rate limiting (30/60s, 200/24h)
- Idempotency (60s cache window)
- Loop detection (3+ same message = block)
- Hourly rotated JSONL audit logs
- Kill switch (default OFF)
- Multi-tenant ready (CIV_KEY dispatch)

---

## Files Created

### 1. Portal Endpoint
**Path**: `/home/jared/purebrain_portal/custom/routes.py` (modified)

**New routes**:
- `POST /api/cc/post` - send message to CC channel
- `GET /api/cc/post/audit?hours=N` - admin audit readout

**Location in aether repo** (for version control):
- This is a CUSTOMIZATION file in portal directory
- Not tracked in aether git (portal is separate deployment)
- Copy to other CIVs by hand or via script

### 2. Test Harness
**Path**: `/home/jared/projects/AI-CIV/aether/tools/cc-outbound-tests/test_cc_outbound.py`

**Run**:
```bash
# Mock mode (syntax check only)
python3 tools/cc-outbound-tests/test_cc_outbound.py

# Live mode (requires running portal)
PORTAL_INTERNAL_KEY="your-key" python3 tools/cc-outbound-tests/test_cc_outbound.py --live
```

---

## Prerequisites

### Environment Variables

Add to portal `.env` file (typically `/home/jared/purebrain_portal/.env`):

```bash
# CC outbound kill switch (default: false)
CC_OUTBOUND_ENABLED=false

# Portal internal key (shared secret for localhost auth)
PORTAL_INTERNAL_KEY="generate-random-key-here"

# CIV name (for audit logging)
CIV_NAME="aether"
```

**Generate random key**:
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Permissions

Audit log directory must be writable:
```bash
sudo mkdir -p /var/log/purebrain
sudo chown jared:jared /var/log/purebrain
```

---

## Installation Steps

### For Aether (This CIV)

1. **Copy routes file** (already done via edit):
   ```bash
   # File is at: /home/jared/purebrain_portal/custom/routes.py
   # Verify syntax:
   python3 -c "import py_compile; py_compile.compile('/home/jared/purebrain_portal/custom/routes.py', doraise=True)"
   ```

2. **Set environment variables**:
   ```bash
   cd /home/jared/purebrain_portal
   # Edit .env and add:
   # CC_OUTBOUND_ENABLED=false
   # PORTAL_INTERNAL_KEY="<random-key>"
   # CIV_NAME="aether"
   ```

3. **Restart portal**:
   ```bash
   systemctl --user restart aether-portal
   # Or: pkill -f portal_server && nohup python3 portal_server.py &
   ```

4. **Verify endpoint exists**:
   ```bash
   curl -X POST http://127.0.0.1:5432/api/cc/post \
     -H "X-Portal-Key: test" \
     -H "Content-Type: application/json" \
     -d '{"channel_id": 1, "text": "test"}'
   # Expected: 423 (kill switch off) or 401 (bad key)
   ```

5. **Enable kill switch** (when ready):
   ```bash
   # In .env:
   CC_OUTBOUND_ENABLED=true
   # Restart portal
   ```

6. **Run tests**:
   ```bash
   cd /home/jared/projects/AI-CIV/aether
   PORTAL_INTERNAL_KEY="<your-key>" python3 tools/cc-outbound-tests/test_cc_outbound.py --live
   ```

---

### For Other CIVs (Chy, Morphe, etc.)

1. **Copy routes file**:
   ```bash
   # On target CIV:
   scp aether:/home/jared/purebrain_portal/custom/routes.py /home/<civ>/purebrain_portal/custom/routes.py
   ```

2. **Set environment variables** (same as Aether, change CIV_NAME):
   ```bash
   # In /home/<civ>/purebrain_portal/.env:
   CC_OUTBOUND_ENABLED=false
   PORTAL_INTERNAL_KEY="<unique-key-per-civ>"
   CIV_NAME="chy"  # or "morphe", etc.
   ```

3. **Create log directory**:
   ```bash
   sudo mkdir -p /var/log/purebrain
   sudo chown <civ>:<civ> /var/log/purebrain
   ```

4. **Restart portal** (service name varies per CIV):
   ```bash
   systemctl --user restart <civ>-portal
   ```

5. **Test** (from localhost on that CIV):
   ```bash
   curl -X POST http://127.0.0.1:5432/api/cc/post \
     -H "X-Portal-Key: <civ-key>" \
     -H "Content-Type: application/json" \
     -d '{"channel_id": 1, "text": "test from <civ>"}'
   ```

---

## Usage

### Calling the Endpoint

**From localhost scripts**:
```python
import httpx
import os

async def send_to_cc(channel_id: int, text: str):
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "http://127.0.0.1:5432/api/cc/post",
            json={"channel_id": channel_id, "text": text},
            headers={"X-Portal-Key": os.environ["PORTAL_INTERNAL_KEY"]},
            timeout=10.0,
        )
        return resp.json()
```

**From bash**:
```bash
#!/bin/bash
# Replacement for tools/cc-send.sh
curl -X POST http://127.0.0.1:5432/api/cc/post \
  -H "X-Portal-Key: ${PORTAL_INTERNAL_KEY}" \
  -H "Content-Type: application/json" \
  -d "{\"channel_id\": $1, \"text\": \"$2\"}"
```

---

## Audit Logs

**Location**: `/var/log/purebrain/cc-outbound.jsonl.YYYY-MM-DD-HH`

**Format**:
```json
{
  "ts": "2026-05-15T22:45:00Z",
  "outcome": "success",
  "from_civ": "aether",
  "channel_id": 1,
  "text_hash": "a1b2c3d4e5f6..."
}
```

**Outcomes**:
- `success` - message sent
- `auth_failed` - bad X-Portal-Key
- `ip_rejected` - non-127.0.0.1 source
- `rate_limited` - rate limit hit
- `loop_detected` - loop prevention triggered
- `send_failed` - CC API error
- `exception` - internal error

**View recent logs**:
```bash
# Admin endpoint (requires portal auth)
curl http://127.0.0.1:5432/api/cc/post/audit?hours=24 \
  -H "Authorization: Bearer <portal-token>"
```

---

## Security

### Design Principles

1. **Localhost-only**: Endpoint ONLY accepts connections from 127.0.0.1
2. **Two-factor auth**: X-Portal-Key header + IP check (belt + suspenders)
3. **Kill switch**: Default OFF, must explicitly enable
4. **Rate limits**: Prevents abuse and loops
5. **Audit trail**: Every request logged (PII discipline: text hashed)

### Attack Surface

**What's protected**:
- Remote access (127.0.0.1 only)
- Brute force (rate limits)
- Loops (detection + block)
- Spoofing (CIV_KEY on outbound to CC)

**What's NOT protected** (intentional trade-offs):
- Local privilege escalation (if attacker has localhost access, game over anyway)
- Audit log tampering (files are append-only but not signed)
- Kill switch bypass (requires env var modification)

### Credentials

**NEVER commit**:
- `PORTAL_INTERNAL_KEY` in .env files
- Audit logs with real text (only hashes committed)

**Rotation**:
- `PORTAL_INTERNAL_KEY` can be rotated anytime (no persistence)
- Just update .env and restart portal

---

## Troubleshooting

### Endpoint returns 423 (Locked)
- Kill switch is OFF
- Check `CC_OUTBOUND_ENABLED=true` in .env
- Restart portal after changing .env

### Endpoint returns 401 (Unauthorized)
- X-Portal-Key header missing or wrong
- Check `PORTAL_INTERNAL_KEY` in .env matches request header

### Endpoint returns 403 (Forbidden)
- Request NOT from 127.0.0.1
- Check source IP (must be localhost)
- If using SSH tunnel, ensure tunnel binds to 127.0.0.1

### Endpoint returns 429 (Rate Limited)
- Primary: 30 msgs/60s exceeded
- Secondary: 200 msgs/24h exceeded
- Or: Loop detected (3+ same message in 60s)

### Endpoint returns 502 (Bad Gateway)
- CC API unreachable
- Check CC_BASE_URL in startup.py
- Check CIV_KEY in .env

### Audit logs not created
- Check `/var/log/purebrain` exists and is writable
- `sudo mkdir -p /var/log/purebrain && sudo chown $USER:$USER /var/log/purebrain`

---

## Testing

### Quick Smoke Test
```bash
# 1. Check syntax
python3 -c "import py_compile; py_compile.compile('/home/jared/purebrain_portal/custom/routes.py', doraise=True)"

# 2. Check portal loads endpoint
curl http://127.0.0.1:5432/api/cc/post -X POST 2>&1 | grep -q "401\|423" && echo "✓ Endpoint exists"

# 3. Run test suite
cd /home/jared/projects/AI-CIV/aether
PORTAL_INTERNAL_KEY="<key>" python3 tools/cc-outbound-tests/test_cc_outbound.py --live
```

### Full Test Suite

See `test_cc_outbound.py` for:
- T1: Valid request
- T2: Missing auth
- T3: Non-loopback IP (skipped - requires remote host)
- T4: Text too long
- T5: Rate limit (skipped - requires 30+ requests)
- T6: Idempotency
- T7: Loop detection
- T8: Kill switch

---

## Commit

**Branch**: `feat/cc-outbound-endpoint-2026-05-15`

**Commit message**:
```
feat(cc-outbound): production HTTP endpoint for CC posting

Replaces throwaway tools/cc-send.sh with production-grade endpoint.

Features:
- POST /api/cc/post (auth: X-Portal-Key + 127.0.0.1)
- Rate limiting (30/60s, 200/24h)
- Idempotency (60s cache, sha256 key)
- Loop detection (3+ same msg = block)
- Hourly JSONL audit logs
- Kill switch (default OFF)
- Multi-tenant (CIV_KEY dispatch)

Test harness: tools/cc-outbound-tests/test_cc_outbound.py

CTO review: specs/cto-review-4-specs-2026-05-15.md (APPROVED)
```

---

## Rollout Checklist

For each CIV:
- [ ] Copy custom/routes.py
- [ ] Set PORTAL_INTERNAL_KEY in .env
- [ ] Set CIV_NAME in .env
- [ ] Create /var/log/purebrain directory
- [ ] Restart portal
- [ ] Verify endpoint exists (curl 401/423 response)
- [ ] Enable kill switch (CC_OUTBOUND_ENABLED=true)
- [ ] Run live tests
- [ ] Monitor audit logs for 24h

---

**Deployment Status**: Ready for ST# rollout to 13 CIVs
