# SSL Fix Plan: Replace Self-Signed Cert on 89.167.19.20:8443

**Author**: devops-engineer
**Date**: 2026-02-20
**Status**: RESEARCH COMPLETE — Awaiting Jared approval to execute

---

## Current State (Confirmed by Research)

| Component | Finding |
|-----------|---------|
| Server | Flask app (`tools/purebrain_log_server.py`) running as PID 3290325 |
| Port | 8443, listening on 0.0.0.0 |
| SSL cert | Self-signed, issued Feb 12 2026, expires Feb 12 2027 |
| Cert location | `/home/jared/projects/AI-CIV/aether/config/ssl/server.crt` |
| JS calling it | `LOGGING_ENDPOINT`, `VERIFY_ENDPOINT`, `log-pay-test` in Elementor widget |
| Pages affected | pay-test (ID 439) and pay-test-sandbox (ID 468) only |
| DNS | purebrain.ai → Cloudflare (NS: arely/kip.ns.cloudflare.com) |
| api.purebrain.ai | NO DNS record exists yet |
| certbot installed | NO |
| cloudflared installed | NO |

---

## Option Evaluation

### Option A: Let's Encrypt Certificate

**How it works**: Point `api.purebrain.ai` to `89.167.19.20`, get a free CA-signed cert with certbot.

| Pros | Cons |
|------|------|
| Industry standard | Requires port 80 or DNS challenge for validation |
| Auto-renewal possible | certbot must be installed on 89.167.19.20 server |
| Works with all browsers | 90-day cert, needs renewal automation (cron) |
| No Cloudflare account needed for cert | Must expose port 80 temporarily for HTTP challenge |

**Estimated time**: 30-45 minutes (mostly DNS propagation wait)

**Jared manual steps needed**: Add A record in Cloudflare DNS dashboard

---

### Option B: Cloudflare Tunnel (RECOMMENDED)

**How it works**: Install `cloudflared` daemon on server. It opens an outbound tunnel to Cloudflare's edge. Cloudflare terminates TLS using their trusted cert. No inbound ports needed beyond the tunnel.

| Pros | Cons |
|------|------|
| Cloudflare handles cert — trusted by all browsers | Requires Cloudflare login (zero-trust dashboard) |
| Free tier covers this entirely | cloudflared must be installed on 89.167.19.20 |
| No cert expiry management | 1 Jared step: authorize tunnel in Cloudflare dashboard |
| Traffic through Cloudflare CDN (DDoS protection bonus) | Tunnel traffic goes through Cloudflare infra |
| Works even if port 443 is blocked on VPS | Slight latency overhead (negligible for logging) |
| Auto-reconnects if server restarts | |

**Estimated time**: 15-20 minutes after cloudflared is installed

**Jared manual steps needed**: Log into Cloudflare Zero Trust dashboard, authorize the tunnel (1 click)

---

### Option C: WordPress Proxy

**How it works**: Add WordPress REST API endpoint that calls the backend server-to-server. Client JS hits WordPress (trusted cert), WordPress proxies to 89.167.19.20.

| Pros | Cons |
|------|------|
| No server changes needed | Adds WordPress as a dependency for logging |
| Uses existing trusted cert | Adds latency (two HTTP hops) |
| Already being built separately | Requires PHP code on GoDaddy WordPress |
| | If WordPress is down, logging breaks |
| | GoDaddy may have server-to-server firewall rules |

**Estimated time**: 1-2 hours

**Jared manual steps needed**: None, but relies on WordPress availability

---

## RECOMMENDATION: Option B (Cloudflare Tunnel)

**Rationale**:
1. purebrain.ai is already on Cloudflare — the account exists
2. Zero certificate management forever (Cloudflare auto-renews)
3. 15 minutes to implement vs 45 minutes for Let's Encrypt
4. The tunnel creates `api.purebrain.ai` automatically with a trusted cert
5. Adds Cloudflare protection (rate limiting, DDoS) to the logging endpoint for free
6. No port 80 exposure needed on the VPS
7. Single Jared action: one authorization click in Cloudflare dashboard

**Fallback if Cloudflare Tunnel doesn't work**: Option A (Let's Encrypt) is the clear second choice. Both scripts are prepared below.

---

## Implementation Plan: Option B (Cloudflare Tunnel)

### Phase 1: Install cloudflared on 89.167.19.20 [AUTOMATED]

Run `tools/security/setup-cloudflare-tunnel.sh` on the 89.167.19.20 server.

This script:
- Downloads and installs cloudflared
- Creates the tunnel config
- Registers a systemd service for auto-restart
- Outputs the tunnel token/URL for Jared to authorize

**Requires**: SSH access to 89.167.19.20

### Phase 2: Jared Authorizes Tunnel [1 MANUAL STEP]

1. Log into https://dash.cloudflare.com → Zero Trust → Access → Tunnels
2. Find the new tunnel named "purebrain-api"
3. Click "Authorize" or copy the tunnel token (shown by script output)
4. Add DNS CNAME in Cloudflare: `api.purebrain.ai` → tunnel URL

**Time**: 2 minutes

### Phase 3: Update JS Endpoints in WordPress [AUTOMATED]

Run `tools/security/update-endpoint-urls.py` to update the Elementor widget in both pages (ID 439 and 468).

Changes:
```javascript
// FROM:
const LOGGING_ENDPOINT = 'https://89.167.19.20:8443/api/log-conversation';
const VERIFY_ENDPOINT  = 'https://89.167.19.20:8443/api/verify-payment';

// TO:
const LOGGING_ENDPOINT = 'https://api.purebrain.ai/api/log-conversation';
const VERIFY_ENDPOINT  = 'https://api.purebrain.ai/api/verify-payment';
```

### Phase 4: Verify [AUTOMATED]

```bash
# Test the new endpoint
curl -s https://api.purebrain.ai/api/health
# Expected: {"status": "ok", "ssl": true, ...}
```

---

## Implementation Plan: Option A (Let's Encrypt) [FALLBACK]

Run `tools/security/setup-letsencrypt.sh` on 89.167.19.20 server.

### Phase 1: Jared adds DNS A record [1 MANUAL STEP]

1. Log into Cloudflare dashboard → purebrain.ai zone → DNS
2. Add record:
   - Type: A
   - Name: api
   - IPv4: 89.167.19.20
   - Proxy status: DNS only (gray cloud — NOT proxied, needed for Let's Encrypt)
3. Wait 2-5 minutes for DNS propagation

### Phase 2: Get certificate [AUTOMATED]

```bash
sudo apt install -y certbot
sudo certbot certonly --standalone -d api.purebrain.ai
```

Certbot temporarily binds port 80 to validate domain ownership.

### Phase 3: Restart server with new cert [AUTOMATED]

```bash
# Update server start to use Let's Encrypt certs
export SSL_CERT_FILE=/etc/letsencrypt/live/api.purebrain.ai/fullchain.pem
export SSL_KEY_FILE=/etc/letsencrypt/live/api.purebrain.ai/privkey.pem
./tools/launch_purebrain_log_server.sh restart
```

The `purebrain_log_server.py` already reads `SSL_CERT_FILE` and `SSL_KEY_FILE` from environment. No code changes needed.

### Phase 4: Set up auto-renewal [AUTOMATED]

```bash
# Add cron for auto-renewal + server restart
echo "0 3 * * * root certbot renew --quiet && systemctl restart purebrain-log-server" | sudo tee /etc/cron.d/certbot-renew
```

### Phase 5: Update JS Endpoints + set Cloudflare proxy to orange cloud [AUTOMATED]

Same as Option B Phase 3. Also change DNS A record proxy status to "Proxied" (orange cloud) after cert is issued for CDN protection.

---

## Files to Be Changed

| File | Change | Option |
|------|--------|--------|
| Elementor widget in WP page 439 | Update 3 URL constants | Both |
| Elementor widget in WP page 468 | Update 3 URL constants | Both |
| Server SSL config (env vars) | Point to new cert paths | A only |
| `/etc/systemd/system/purebrain-log-server.service` | Add env vars for cert paths | A only |
| Cloudflare DNS | Add api.purebrain.ai record | Both |

---

## What We Are NOT Changing

- The Flask server code itself — no changes needed
- The server port (8443 stays as-is internally, Cloudflare tunnels it)
- Any other pages on purebrain.ai (only pay-test pages are affected)
- PayPal integration (unrelated)

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| DNS propagation delay | Medium | Low | Wait 5-10 min, test with `dig` |
| Cloudflare tunnel authorization confusion | Low | Low | Clear instructions + script output |
| Pay-test page JS update breaks layout | Low | Medium | Test in sandbox (ID 468) first |
| Server down during update | Very Low | Medium | Keep current server running until new endpoint verified |

---

## Verification Steps After Implementation

```bash
# 1. Test endpoint health
curl -s https://api.purebrain.ai/api/health
# Expected: {"status": "ok", "ssl": true}

# 2. Verify no cert warning in Chrome
# Open https://api.purebrain.ai/api/health in Chrome incognito
# Should show green padlock, no warnings

# 3. Test pay-test page
# Open purebrain.ai/pay-test-sandbox/ in Chrome incognito
# Open DevTools → Console
# Should see NO net::ERR_CERT_AUTHORITY_INVALID errors

# 4. Verify logging works
curl -s -X POST https://api.purebrain.ai/api/log-conversation \
  -H 'Content-Type: application/json' \
  -d '{"messages": [{"role": "user", "content": "test"}], "session_id": "ssl-test-01"}'
# Expected: {"success": true}
```

---

## Time Estimates

| Task | Time |
|------|------|
| Jared: Add DNS record (either option) | 2 minutes |
| Jared: Authorize Cloudflare tunnel (Option B) | 2 minutes |
| Install cloudflared (Option B) | 5 minutes |
| DNS propagation wait | 2-10 minutes |
| Update JS endpoints in WordPress | 5 minutes |
| Testing and verification | 5 minutes |
| **Total** | **~20 minutes** |

---

## Scripts Prepared

| Script | Purpose |
|--------|---------|
| `tools/security/setup-cloudflare-tunnel.sh` | Install cloudflared + configure tunnel (run on 89.167.19.20) |
| `tools/security/setup-letsencrypt.sh` | Install certbot + get cert (fallback, run on 89.167.19.20) |
| `tools/security/update-endpoint-urls.py` | Update JS endpoint URLs in WordPress Elementor pages |

---

*Research complete. No live changes made. Awaiting Jared approval.*
