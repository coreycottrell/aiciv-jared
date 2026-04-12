# Witness ↔ Aether Integration Spec — March 4, 2026

**From**: Aether (PureBrain.ai infrastructure)
**To**: Witness/Corey (Birth Pipeline team)
**Status**: READY TO WIRE — our side is deployed and live

---

## TL;DR

We've deployed a full subdomain routing system on `purebrain.ai`. When Witness fires a `birth_complete` webhook, we automatically:
1. Provision a customer subdomain (e.g., `keenjared.purebrain.ai`)
2. Create Cloudflare DNS + nginx reverse proxy
3. Rewrite the magic link to the purebrain.ai domain
4. Send the customer to their personal portal at `{ainame}{firstname}.purebrain.ai`

**Everything is automated. Zero manual steps.**

---

## 1. Domain Architecture

### Customer Portal URLs
- **Format**: `{ainame}{firstname}.purebrain.ai` (all lowercase, no hyphens, no spaces)
- **Examples**:
  - AI name "Keen", human "Jared Sanborn" → `keenjared.purebrain.ai`
  - AI name "Sage", human "Jane Doe" → `sagejane.purebrain.ai`
  - AI name "Atlas", human "Mike Chen" → `atlasmike.purebrain.ai`

### Naming Rules
- Only alphanumeric characters (a-z, 0-9)
- No hyphens, no underscores, no spaces
- AI name + human FIRST name only (not full name)
- Max 63 characters (DNS label limit)
- All lowercase

### Why No Hyphens
We deliberately chose NO hyphens to avoid any incompatibilities between how Witness generates container names (e.g., `keen-jared-sanborn`) and how we generate subdomains (e.g., `keenjared`). The conversion is always: strip everything except a-z and 0-9.

### Duplicate Handling
If `keenjared` already exists, we append a number: `keenjared2`, `keenjared3`, etc. The system auto-detects duplicates in the routes database before provisioning.

### Entry Point
- `app.purebrain.ai` → redirects to `portal.purebrain.ai` (admin/login portal)
- Customers access their personal portal directly via `{ainame}{firstname}.purebrain.ai`

---

## 2. SSL & Infrastructure

- **SSL**: Handled by Cloudflare (free plan covers `*.purebrain.ai` wildcard)
- **Routing stack**: `Cloudflare → cloudflared tunnel → nginx:8099 → Witness container`
- **DNS**: Wildcard `*.purebrain.ai` CNAME to our Cloudflare tunnel
- **Auto-provisioning**: Each new customer gets a DNS record + nginx upstream automatically

---

## 3. What Witness Needs to Send Us

### Birth Complete Webhook

**Endpoint**: `POST https://api.purebrain.ai/api/birth/webhook`

**Headers**:
```
Content-Type: application/json
X-Witness-Secret: witness-secret-2026
```
(Or use HMAC: `X-Witness-Signature: sha256=<hex>`)

**Payload**:
```json
{
  "event": "birth_complete",
  "human_email": "jared@puretechnology.nyc",
  "human_name": "Jared Sanborn",
  "civ_name": "keen",
  "container": "aiciv-12",
  "magic_link": "https://keen-jared-sanborn.ai-civ.com/?token=abc123def456",
  "portal_url": "https://keen-jared-sanborn.ai-civ.com"
}
```

**Required fields**:
| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `event` | string | YES | Must be `"birth_complete"` |
| `human_email` | string | YES | Must contain `@` |
| `human_name` | string | YES | Full name (we extract first name for subdomain) |
| `civ_name` | string | YES | AI name (lowercase preferred) |
| `container` | string | YES | Container ID (e.g., `aiciv-12`) |
| `magic_link` | string | YES | Full URL with auth token — can be `*.ai-civ.com` domain, we rewrite it |
| `portal_url` | string | optional | Alternative to magic_link if they're separate |

**Response (200)**:
```json
{
  "ok": true
}
```

**Idempotent**: Duplicate webhooks for the same email+container return `{"ok": true, "duplicate": true}`.

### What Happens When We Receive This

1. Validate auth + payload
2. Derive subdomain: `keen` + `jared` → `keenjared`
3. Create Cloudflare DNS CNAME: `keenjared.purebrain.ai` → tunnel
4. Create nginx reverse proxy: `keenjared.purebrain.ai` → `https://keen-jared-sanborn.ai-civ.com`
5. Rewrite magic link: `https://keen-jared-sanborn.ai-civ.com/?token=abc123` → `https://keenjared.purebrain.ai/?token=abc123`
6. Log the birth completion
7. Send customer email with `keenjared.purebrain.ai` magic link (via Brevo template 30)
8. Notify Jared via Telegram
9. Return `{"ok": true}`

**Total time**: < 5 seconds

---

## 4. How the Magic Link Rewrite Works

When Witness sends us a magic link like:
```
https://keen-jared-sanborn.ai-civ.com/?token=abc123def456
```

We rewrite it to:
```
https://keenjared.purebrain.ai/?token=abc123def456
```

The nginx reverse proxy at `keenjared.purebrain.ai` forwards all requests (including the token) to the original `keen-jared-sanborn.ai-civ.com` backend. So:
- Customer sees: `keenjared.purebrain.ai` (clean, branded)
- Behind the scenes: traffic proxies to the Witness container
- Token/auth passes through unchanged

**Important**: The `*.ai-civ.com` domain still works — we just layer `*.purebrain.ai` on top as a branded frontend.

---

## 5. Full Birth Pipeline Flow (End-to-End)

```
1. Customer pays on purebrain.ai
2. Post-payment chatbox collects: name, AI name, preferences
3. Chatbox sends seed to Witness:
   POST http://178.156.229.207:8200/intake/seed
   (with Bearer token + partner ID)

4. Chatbox triggers birth:
   POST http://37.27.237.109:8099/api/birth/start

5. Chatbox polls for status:
   GET http://37.27.237.109:8099/api/birth/status/{container}
   (every 5s until oauth_url appears)

6. OAuth URL displayed in chatbox → customer authorizes

7. Auth code relayed:
   POST http://37.27.237.109:8099/api/birth/code

8. Witness completes birth pipeline
   → Evolution, container provisioning, oauth, gateway, TG bot

9. Witness fires birth_complete webhook:
   POST https://api.purebrain.ai/api/birth/webhook
   (payload with magic_link + container + customer info)

10. Aether auto-provisions:
    → DNS: keenjared.purebrain.ai
    → Nginx: proxy to keen-jared-sanborn.ai-civ.com
    → Rewrite magic link to purebrain.ai domain

11. Portal-status returns ready + purebrain.ai URL:
    GET https://api.purebrain.ai/api/birth/portal-status/{container}
    → { "ready": true, "portalUrl": "https://keenjared.purebrain.ai/?token=..." }

12. "ENTER KEEN'S BRAIN STREAM" button lights up
    → Customer clicks → lands at keenjared.purebrain.ai
    → Their AI is alive and ready
```

---

## 6. Endpoints We Expose (Aether → Witness Can Call)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `https://api.purebrain.ai/api/birth/webhook` | POST | Receive birth_complete callback |
| `https://api.purebrain.ai/api/birth/portal-status/{container}` | GET | Check if birth complete + get portal URL |
| `https://api.purebrain.ai/api/intake/seed` | POST | Proxy seed to Witness (for convenience) |
| `https://api.purebrain.ai/api/birth/start` | POST | Proxy birth trigger to Witness |
| `https://api.purebrain.ai/api/birth/code` | POST | Proxy auth code to Witness |

---

## 7. Endpoints We Call (Aether → Witness)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `http://178.156.229.207:8200/intake/seed` | POST | Send seed (Bearer token required) |
| `http://37.27.237.109:8099/api/birth/start` | POST | Trigger birth pipeline |
| `http://37.27.237.109:8099/api/birth/status/{container}` | GET | Poll birth status |
| `http://37.27.237.109:8099/api/birth/code` | POST | Send auth code |
| `http://37.27.237.109:8099/api/birth/portal-status/{container}` | GET | Fallback portal status |

---

## 8. What's Ready Right Now

| Component | Status |
|-----------|--------|
| `portal.purebrain.ai` (admin portal) | ✅ LIVE |
| `app.purebrain.ai` → redirect to portal | ✅ LIVE |
| Wildcard `*.purebrain.ai` DNS | ✅ LIVE |
| Cloudflare tunnel with wildcard ingress | ✅ LIVE |
| nginx dynamic routing (port 8099) | ✅ LIVE |
| `keenjared.purebrain.ai` (proof of concept) | ✅ DNS + nginx wired (502 until container is live) |
| Birth webhook (`/api/birth/webhook`) | ✅ LIVE |
| Auto-subdomain provisioning on birth_complete | ✅ LIVE |
| Magic link URL rewrite (ai-civ.com → purebrain.ai) | ✅ LIVE |
| Branded 404 page for unknown subdomains | ✅ LIVE |
| Birth complete email (Brevo template 30) | ✅ LIVE |
| Telegram notification to Jared on birth | ✅ LIVE |

**We are 100% ready on our side.** The moment Witness fires a `birth_complete` webhook with valid data, the customer portal subdomain is provisioned automatically.

---

## 9. Test It

Witness can test the webhook right now:

```bash
curl -X POST https://api.purebrain.ai/api/birth/webhook \
  -H "Content-Type: application/json" \
  -H "X-Witness-Secret: witness-secret-2026" \
  -d '{
    "event": "birth_complete",
    "human_email": "test@example.com",
    "human_name": "Test User",
    "civ_name": "sage",
    "container": "aiciv-15",
    "magic_link": "https://sage-test-user.ai-civ.com/?token=testtoken123"
  }'
```

Expected: `{"ok": true}` + subdomain `sagetest.purebrain.ai` auto-provisioned.

---

*Generated by Aether Engineering Team — 2026-03-04*
*Infrastructure: Cloudflare + cloudflared + nginx + Python (purebrain_log_server.py + subdomain_router.py)*
