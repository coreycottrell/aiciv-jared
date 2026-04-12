# Software Requirements Specification
## PureBrain.ai Platform
### Sections: System Architecture, API Specification, Data Flow Diagrams, Deployment Architecture

**Document Version**: 1.0
**Date**: 2026-02-26
**Prepared By**: Aether (AI Engineering Team)
**Prepared For**: Development Agency / DevOps Quoting

---

## Table of Contents

1. System Architecture Overview
2. API Specifications
3. Data Flow Diagrams
4. Deployment Architecture
5. Infrastructure Inventory

---

---

# SECTION 1: SYSTEM ARCHITECTURE OVERVIEW

## 1.1 High-Level Architecture

The PureBrain.ai platform is a distributed system composed of six primary service layers and four third-party integrations. The architecture follows a hub-and-spoke pattern with the Log/API Server (`api.purebrain.ai`) acting as the central backend hub for all authenticated service calls.

```
                        ┌─────────────────────────────────────────┐
                        │            CLIENTS (browsers)            │
                        └────────────┬────────────────────────────┘
                                     │ HTTPS
                   ┌─────────────────┼──────────────────────┐
                   │                 │                        │
          ┌────────▼──────┐ ┌────────▼──────┐   ┌───────────▼──────────┐
          │ purebrain.ai  │ │ app.purebrain │   │  purebrain-hub       │
          │ (WordPress)   │ │    .ai        │   │  .vercel.app         │
          │ GoDaddy host  │ │ (Netlify)     │   │  (Vercel)            │
          └───────┬───────┘ └───────┬───────┘   └───────────┬──────────┘
                  │                 │                         │
                  │ WP REST API     │ fetch()                 │ fetch()
                  │ Elementor       │                         │
                  └────────┬────────┘─────────────────────────┘
                           │
                           │ HTTPS (all calls from WordPress plugin
                           │ routed server-side to protect API keys)
                           │
              ┌────────────▼─────────────────┐
              │       api.purebrain.ai        │
              │    Flask/Python Log Server    │
              │    VPS: 89.167.19.20:8443     │  ← HTTPS (self-signed cert)
              │    Cloudflare Tunnel →        │
              │    public HTTPS exposure      │
              └──────────┬───────────────────┘
                         │
          ┌──────────────┼─────────────────────┐
          │              │                      │
  ┌───────▼──────┐ ┌─────▼──────┐   ┌──────────▼─────────────┐
  │ Witness VPS  │ │  A-C-Gee   │   │  Third-Party Services  │
  │ 104.248.239  │ │  VPS       │   │  - Brevo (email)       │
  │ .98:8099     │ │  5.161.90  │   │  - PayPal (payments)   │
  │ (birth API)  │ │  .32:3001  │   │  - Telegram (ops)      │
  └──────────────┘ └────────────┘   │  - Google Drive        │
                                    └────────────────────────┘

          ┌────────────────────────────────────────────┐
          │        pure-tech-dashboard.netlify.app      │
          │        Team Dashboard (Netlify)             │
          │        Supabase PostgreSQL backend          │
          └────────────────────────────────────────────┘
```

---

## 1.2 Service Inventory

### 1.2.1 purebrain.ai (WordPress Frontend)

| Property | Value |
|----------|-------|
| Platform | WordPress (latest stable) |
| Hosting | GoDaddy Managed WordPress |
| DNS | Cloudflare (proxied) |
| SSL | Cloudflare SSL (full strict) |
| Page Builder | Elementor Pro |
| Custom Plugin | `purebrain-security-plugin.php` (custom, v6.1+) |

**Function**: Primary marketing site and content delivery. All customer-facing pages: homepage, blog, assessment tool, chatbox, pay-test purchase flow, comparison pages, migration portal pages, AI tool calculator, partner program landing page.

**WordPress Plugin Responsibilities**:
- HSTS header injection (`max-age=31536000; includeSubDomains; preload`)
- Content Security Policy (enforced mode)
- Server-side proxy for log server calls (hides VPS IP from client JS)
- Server-side proxy for PayPal verification (hides PayPal credentials)
- Block user enumeration via REST (`/wp/v2/users`)
- Block `?author=` enumeration attacks
- IndexNow pinging on publish events
- UTM parameter persistence

**WordPress REST API Base URL**: `https://purebrain.ai/wp-json/wp/v2/`
**Custom Plugin REST Namespace**: `https://purebrain.ai/wp-json/purebrain/v1/`

---

### 1.2.2 api.purebrain.ai (Log / Proxy Server)

| Property | Value |
|----------|-------|
| VPS IP | 89.167.19.20 |
| Port | 8443 (HTTPS) |
| Framework | Python 3.x / Flask |
| SSL | Self-signed certificate (RSA 2048-bit, SAN: 89.167.19.20) |
| Public Exposure | Cloudflare Tunnel (domain: api.purebrain.ai) |
| Process Manager | systemd (`purebrain-log-server.service`) |
| CORS Origin Whitelist | `https://purebrain.ai`, `https://www.purebrain.ai`, `https://jareddsanborn.com`, `https://www.jareddsanborn.com` |
| Max Request Body | 1 MB |

**Function**: Central backend API. Handles conversation logging, payment verification, Witness birth pipeline proxying, Brevo email automation, and PayPal webhook reception. All calls that require secrets (API keys, credentials) pass through this server so no credentials are exposed in client-side JavaScript.

**Persistent Background Services** (run inside same process):
- `neural_feed_welcome_sequence.py` — welcome email scheduler for blog subscribers
- `rss_to_email.py` — RSS-to-email daemon for automated blog distribution

---

### 1.2.3 app.purebrain.ai (Portal Frontend)

| Property | Value |
|----------|-------|
| Hosting Platform | Netlify |
| Netlify Site ID | `2139f9ed-32cc-4abd-8364-8bb81b94df9b` |
| Netlify Site Name | `purebrain-app` |
| Custom Domain | `app.purebrain.ai` |
| DNS | CNAME: `app.purebrain.ai` → `purebrain-app.netlify.app` |
| Technology | Single-file self-contained HTML (~895 KB) |

**Function**: Customer portal application after purchase. Three.js 3D neural network background, glassmorphism login card, post-purchase dashboard. Communicates with Witness VPS to provision and track AI partner containers.

**Source File**: `exports/purebrain-frontend-3d.html`

---

### 1.2.4 PureBrain Hub (Vercel)

| Property | Value |
|----------|-------|
| Hosting Platform | Vercel |
| URL | `https://purebrain-hub.vercel.app` |
| Technology | Single-file HTML (vanilla JS, Canvas 2D animations) |
| Auth | Token-based (`team2025`, `safety2025`, `quality2025`, `demo`) |

**Function**: Internal team command center. Features: team wins board, file uploads, post feed, tag-based filtering, leaderboard, Google Drive sync status, NeuralCanvas animated login background. Used by Pure Technology internal team.

**Source File**: `exports/purebrain-hub-v2.html` / `tools/purebrain-hub-static/index.html`

---

### 1.2.5 Team Dashboard (Netlify)

| Property | Value |
|----------|-------|
| Hosting Platform | Netlify |
| Netlify Site ID | `d2556d0a-5333-47ca-a8d6-8add4141f090` |
| URL | `https://pure-tech-dashboard.netlify.app` |
| Technology | Single-file HTML (vanilla JS) |
| Backend | Supabase PostgreSQL (optional; falls back to localStorage) |

**Function**: Task management dashboard for Pure Technology team. Features: task CRUD, assignee management, priority/status/deadline tracking, real-time sync via Supabase. Offline-capable (localStorage fallback).

**Source File**: `exports/team-dashboard/dist/index.html`

---

### 1.2.6 Witness VPS (Birth / Provisioning API)

| Property | Value |
|----------|-------|
| VPS IP | 104.248.239.98 |
| Port | 8099 (HTTP, internal only) |
| Public Access | Via proxy at api.purebrain.ai |

**Function**: Provisions isolated AI partner containers ("births") for newly purchased PureBrain customers. Not directly accessible from the browser — all calls pass through the `api.purebrain.ai` proxy to resolve CORS and mixed-content issues.

---

### 1.2.7 Third-Party Services

| Service | Purpose | Integration Method |
|---------|---------|--------------------|
| **Brevo** | Transactional email + marketing automation | REST API v3 via Python (`requests`) |
| **PayPal** | Payment capture + webhook events | REST API v2 (OAuth2) via Python (`urllib`) |
| **Telegram Bot API** | Operational notifications to Jared | REST API via `urllib` |
| **Google Drive** | File storage for all deliverables and training data | `gdrive_manager.py` tool (service account) |
| **A-C-Gee VPS** | Shared conversation database (cross-CIV integration) | HTTP POST to `5.161.90.32:3001/api/landing-chat` |
| **Cloudflare** | DNS, CDN, SSL, DDoS protection | DNS provider for `purebrain.ai` |

---

## 1.3 Service Communication Map

```
purebrain.ai (WordPress)
├── Calls wp-json/purebrain/v1/log-conversation-fallback (own plugin proxy)
├── Plugin calls → https://89.167.19.20:8443/api/log-conversation
├── Plugin calls → https://89.167.19.20:8443/api/verify-payment
└── Blog pages embed chatbox JS (calls api.purebrain.ai directly)

api.purebrain.ai (89.167.19.20:8443)
├── Writes → /logs/purebrain_web_conversations.jsonl
├── Writes → /logs/purebrain_pay_test.jsonl
├── Writes → /logs/purebrain_payments.jsonl
├── Writes → /logs/purebrain_emails.jsonl
├── Calls → Brevo API (transactional email)
├── Calls → PayPal API (order verification, OAuth2)
├── Calls → Telegram Bot API (operational notifications)
├── Proxies → Witness VPS 104.248.239.98:8099 (birth pipeline)
├── Forwards → A-C-Gee 5.161.90.32:3001 (cross-CIV logging)
└── Publishes → AICIV comms hub (git-based, hub_cli.py)

app.purebrain.ai (Netlify)
├── Calls → api.purebrain.ai/api/proxy/birth/start
├── Calls → api.purebrain.ai/api/proxy/birth/code
└── Polls → api.purebrain.ai/api/proxy/birth/portal-status/{container}

purebrain-hub.vercel.app (Vercel)
└── Standalone (localStorage, no backend calls in current v2)

pure-tech-dashboard.netlify.app (Netlify)
└── Calls → Supabase REST API (PostgreSQL via HTTPS)
```

---

---

# SECTION 2: API SPECIFICATIONS

## 2.1 Log Server API (api.purebrain.ai)

**Base URL**: `https://api.purebrain.ai`
**Protocol**: HTTPS (TLS 1.2+)
**Auth**: None for public endpoints (CORS whitelist enforced)
**Content-Type**: `application/json` required on all POST requests
**Max Body Size**: 1 MB

---

### POST /api/log-conversation

**Purpose**: Record a chatbox conversation session to the server JSONL log and forward it asynchronously to A-C-Gee's shared database.

**CORS**: Allowed from purebrain.ai, jareddsanborn.com

**Request Body**:
```json
{
  "session_id": "string (optional; UUID auto-generated if absent)",
  "messages": [
    {"role": "user", "content": "string"},
    {"role": "assistant", "content": "string"}
  ],
  "user_agent": "string (optional)",
  "page_url": "string (optional)",
  "referrer": "string (optional)",
  "aiName": "string (optional — AI partner's chosen name)",
  "userName": "string (optional)",
  "userTier": "string (optional)",
  "referralCode": "string (optional)",
  "conversationId": "string (optional)",
  "brainId": "string (optional)"
}
```

**Note**: Accepts both `messages` and `conversationHistory` as the message array key for backward compatibility.

**Response 200**:
```json
{
  "success": true,
  "session_id": "pb-{uuid}",
  "timestamp": "2026-02-26T12:00:00.000000+00:00"
}
```

**Response 400**: `{"error": "Content-Type must be application/json"}`
**Response 400**: `{"error": "Missing required field: messages or conversationHistory"}`
**Response 500**: `{"error": "Failed to write log"}`

**Side Effects**:
- Appends JSON line to `/logs/purebrain_web_conversations.jsonl`
- Spawns background thread: forward to A-C-Gee `5.161.90.32:3001/api/landing-chat` (3 retries on 500)
- Spawns background thread: publish to AICIV comms hub `operations` room

---

### POST /api/verify-payment

**Purpose**: Server-side PayPal order verification for the AI Website Execution service (page 826). Prevents client-side payment spoofing by calling PayPal API directly with stored credentials.

**CORS**: Allowed from purebrain.ai

**Request Body**:
```json
{
  "order_id": "string (PayPal order ID, required)",
  "tier": "critical|complete (required)"
}
```

**Expected Amounts**:
| Tier | Amount |
|------|--------|
| `critical` | $197.00 USD |
| `complete` | $497.00 USD |

**Response 200**:
```json
{
  "verified": true,
  "status": "COMPLETED",
  "amount": "197.00",
  "payer_email": "buyer@example.com",
  "payer_name": "Jane Smith",
  "order_id": "PAYPAL-ORDER-ID-ABC",
  "server_timestamp": "2026-02-26T12:00:00.000000+00:00"
}
```

**Response 200 (failure case)**:
```json
{
  "verified": false,
  "status": "PENDING",
  "amount": "",
  "payer_email": "",
  "payer_name": "",
  "order_id": "...",
  "server_timestamp": "...",
  "error": "Could not obtain PayPal access token"
}
```

**Response 400**: `{"error": "Missing required field: order_id"}`

**Side Effects (on verified=true)**:
- Appends entry to `/logs/purebrain_payments.jsonl`
- Spawns background thread: Telegram notification to Jared
- Spawns background thread: Brevo confirmation email to buyer (Template ID 11)

**PayPal API Flow**:
1. POST `https://api-m.paypal.com/v1/oauth2/token` → access token
2. GET `https://api-m.paypal.com/v2/checkout/orders/{order_id}` → order details
3. Validate `status == "COMPLETED"` and `captures[0].amount.value == expected_amount`

---

### POST /api/log-pay-test

**Purpose**: Record the complete post-payment onboarding flow data after a customer finishes the PureBrain purchase questionnaire. Triggers the post-purchase email sequence when `flowCompleted=true`.

**CORS**: Allowed from purebrain.ai

**Request Body**:
```json
{
  "tier": "Awakened|Bonded|Partnered|Unified",
  "orderId": "string (PayPal order ID)",
  "aiName": "string (AI partner name chosen by user)",
  "name": "string (customer full name)",
  "email": "string (customer email)",
  "company": "string (optional)",
  "role": "string (optional)",
  "primaryGoal": "string (optional)",
  "telegramBotToken": "string (optional — if Telegram setup completed)",
  "claudeMaxStatus": "connected|skipped|pending",
  "flowCompleted": "boolean"
}
```

**Response 200**:
```json
{
  "success": true,
  "logged": true,
  "server_timestamp": "2026-02-26T12:00:00.000000+00:00"
}
```

**Side Effects**:
- Appends entry to `/logs/purebrain_pay_test.jsonl`
- Spawns background thread: Telegram notification to Jared (always)
- If `flowCompleted=true` AND `email` is present: spawns background thread to trigger post-purchase email sequence:
  - Upsert Brevo contact (List 8: PureBrain Customers) with AI_NAME, TIER, COMPANY, ROLE, PRIMARY_GOAL attributes
  - Send Brevo Template 11 (Welcome: "Your AI partner is live") immediately
  - Schedule Brevo Template 12 (Setup Complete: "40 minutes in") via `threading.Timer` at 40-minute delay

---

### GET /api/health

**Purpose**: Health check endpoint. Used for monitoring and uptime verification.

**Auth**: None

**Response 200**:
```json
{
  "status": "ok",
  "ssl": true,
  "timestamp": "2026-02-26T12:00:00.000000+00:00"
}
```

---

### GET /api/stats

**Purpose**: Conversation log statistics.

**Auth**: None

**Response 200**:
```json
{
  "conversation_count": 142,
  "file_size_bytes": 524288,
  "log_file": "purebrain_web_conversations.jsonl",
  "timestamp": "2026-02-26T12:00:00.000000+00:00"
}
```

---

### POST /api/paypal-webhook

**Purpose**: Receive PayPal `PAYMENT.CAPTURE.COMPLETED` events. Signed by PayPal and verified via PayPal's webhook signature verification API.

**Auth**: PayPal webhook signature headers
- `PAYPAL-AUTH-ALGO`
- `PAYPAL-CERT-URL`
- `PAYPAL-TRANSMISSION-ID`
- `PAYPAL-TRANSMISSION-SIG`
- `PAYPAL-TRANSMISSION-TIME`

**Registration URL** (at PayPal Developer Dashboard): `https://api.purebrain.ai/api/paypal-webhook`
**Subscribed Events**: `PAYMENT.CAPTURE.COMPLETED`

**Request Body**: PayPal webhook event object (application/json)

**Response 200 (processed)**:
```json
{"status": "processed", "capture_id": "CAPTURE-ID-XYZ"}
```

**Response 200 (ignored)**:
```json
{"status": "ignored", "reason": "event_type=PAYMENT.SUBSCRIPTION.ACTIVATED"}
```

**Response 400**: `{"status": "ignored", "reason": "invalid json"}`

**Side Effects**:
- Appends webhook entry to `/logs/purebrain_payments.jsonl` (includes gross, net, fee, inferred tier)
- Spawns background thread: Telegram notification to Jared

---

## 2.2 Witness Birth Pipeline Proxy Endpoints

These three endpoints are proxy pass-throughs on `api.purebrain.ai` that forward to the Witness VPS at `http://104.248.239.98:8099`. The upstream IP is hardcoded server-side; it is never accepted from request input.

**Rationale for proxy**: The Witness VPS serves plain HTTP. The PureBrain portal is served over HTTPS. Browsers block "mixed content" (HTTPS page calling HTTP resource). Additionally, the Witness VPS does not have CORS headers configured for the purebrain.ai origin. The proxy solves both problems.

---

### POST /api/proxy/birth/start
**Alias**: POST /api/birth/start

**Purpose**: Provision a new AI partner container for a purchasing customer.

**Rate Limit**: 5 calls per minute per client IP (sliding window, per-IP, prevents container pool exhaustion)

**Request Body** (optional):
```json
{}
```
or
```json
{"container": "specific-container-name"}
```

**Body Validation**: If body is present, must be valid JSON. Max body size: 64 KB.

**Timeout**: 120 seconds (provisioning can take up to 145 seconds in worst case)
**Connect Timeout**: 10 seconds

**Successful Response** (pass-through from Witness):
```json
{
  "status": "url_ready",
  "oauth_url": "https://oauth.purebrain.ai/...",
  "container": "aiciv-07",
  "auto_allocated": true
}
```

**Error Responses**:
| Code | Body |
|------|------|
| 429 | `{"error": "Too many requests", "details": "Maximum 5 birth starts per minute"}` |
| 400 | `{"error": "Invalid JSON body"}` |
| 413 | `{"error": "Request body too large"}` |
| 503 | `{"error": "Birth service unavailable", "details": "Could not connect to birth service"}` |
| 504 | `{"error": "Birth service timeout", "details": "Upstream did not respond in time"}` |
| 502 | `{"error": "Birth service error", "details": "Unexpected proxy error"}` |

---

### POST /api/proxy/birth/code
**Alias**: POST /api/birth/code

**Purpose**: Submit an authentication code during the birth/provisioning OAuth flow.

**Rate Limit**: 10 calls per minute per client IP

**Request Body**: Passed through unchanged (must be valid JSON)

**Timeout**: 30 seconds

**Response**: Witness response pass-through

---

### GET /api/proxy/birth/portal-status/{container}

**Purpose**: Poll the birth status of a specific container. Returns when the portal is ready.

**Rate Limit**: 60 calls per minute per client IP (supports 1/second polling)

**URL Parameter**:
- `container`: Container name. Validated against regex `^[a-zA-Z0-9_-]{1,50}$`. Returns 400 if invalid.

**Timeout**: 15 seconds

**Successful Response** (pass-through from Witness):
```json
{
  "ready": false,
  "portal_url": null
}
```
or when ready:
```json
{
  "ready": true,
  "portal_url": "https://portal.purebrain.ai/..."
}
```

**Error Responses**:
| Code | Body |
|------|------|
| 400 | `{"error": "Invalid container name"}` |
| 503 | `{"error": "Birth service unavailable", ...}` |
| 504 | `{"error": "Birth service timeout", ...}` |

---

## 2.3 Witness Portal API (104.248.239.98:8099)

These are the upstream Witness endpoints. Client code should never call these directly — use the proxy endpoints at `api.purebrain.ai` described in section 2.2.

**Note**: This is the A-C-Gee / Witness collective's internal API. Full spec maintained by that team.

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/birth/start` | Begin container provisioning (accepts empty `{}` or `{"container": "name"}`) |
| POST | `/api/birth/code` | Submit OAuth code during provisioning |
| GET | `/api/birth/portal-status/{container}` | Poll container readiness |
| GET | `/api/health` | Witness health check |
| GET | `/portal-status` | Alias for portal-status |
| POST | `/evolution` | Signal container upgrade/evolution |
| POST | `/auth` | Magic link authentication initiation |

---

## 2.4 WordPress REST API (purebrain.ai)

**Base URL**: `https://purebrain.ai/wp-json/wp/v2/`
**Auth**: HTTP Basic (Base64-encoded `username:app_password`)
- purebrain.ai: username `Aether`, app_password in `.env` as `PUREBRAIN_WP_APP_PASSWORD`
- jareddsanborn.com: username `jared`, app_password in `.env` as `WORDPRESS_APP_PASSWORD`

### Pages CRUD

**Get page (with edit context)**:
```
GET /wp/v2/pages/{id}?context=edit
Authorization: Basic {base64}
```

**Create page**:
```
POST /wp/v2/pages
Authorization: Basic {base64}
Content-Type: application/json

{
  "title": "Page Title",
  "content": "<!-- wp:html -->\n<div>...</div>\n<!-- /wp:html -->",
  "status": "publish|draft",
  "template": ""  // "" = default theme template (for blog posts)
                  // "elementor_canvas" for standalone Elementor pages (NON-blog)
}
```

**Update page**:
```
POST /wp/v2/pages/{id}
Authorization: Basic {base64}
Content-Type: application/json

{"content": "...", "meta": {"_elementor_data": "serialized_json_string"}}
```

**Delete page (move to trash)**:
```
DELETE /wp/v2/pages/{id}
Authorization: Basic {base64}
```

### Elementor Data Manipulation

**CRITICAL**: All Elementor widget content is stored as serialized JSON in the `_elementor_data` post meta field. A full double-serialization pattern is used.

**Read Elementor data**:
```python
resp = requests.get(f"{base_url}/wp/v2/pages/{id}?context=edit", auth=auth)
elementor_data = json.loads(resp.json()['meta']['_elementor_data'])
html_content = elementor_data[0]['elements'][0]['settings']['html']
```

**Write Elementor data**:
```python
requests.post(
    f"{base_url}/wp/v2/pages/{id}",
    auth=auth,
    json={"meta": {"_elementor_data": json.dumps(elementor_data)}}
)
```

**Clear Elementor cache after update**:
```
DELETE /wp-json/elementor/v1/cache
Authorization: Basic {base64}
```

**CRITICAL NOTE**: REST API updates to `_elementor_data` do NOT trigger re-rendering. For pages where Elementor fails to re-render, the solution is to delete the page and recreate it with a fresh ID.

### Media Upload

```
POST /wp/v2/media
Authorization: Basic {base64}
Content-Type: image/png
Content-Disposition: attachment; filename="banner.png"

[binary image data]
```

**Response**: Media object with `id`, `source_url`, `link`

### Custom Plugin Endpoints (purebrain.ai)

**Server-side proxy for logging** (hides VPS IP from client JS):
```
POST /wp-json/purebrain/v1/log-conversation
POST /wp-json/purebrain/v1/log-conversation-fallback
```

**Server-side proxy for payment verification** (hides PayPal credentials from client JS):
```
POST /wp-json/purebrain/v1/verify-payment
```

---

## 2.5 Brevo API

**Base URL**: `https://api.brevo.com/v3`
**Auth**: `api-key: {BREVO_API_KEY}` header

### Contact Management

**Upsert Contact**:
```
POST /contacts
Content-Type: application/json
api-key: {key}

{
  "email": "customer@example.com",
  "attributes": {
    "FIRSTNAME": "Jane",
    "LASTNAME": "Smith",
    "AI_NAME": "Keen",
    "TIER": "Awakened",
    "COMPANY": "Acme Corp",
    "ROLE": "CEO",
    "PRIMARY_GOAL": "save 10hrs/week"
  },
  "listIds": [8],
  "updateEnabled": true
}
```

**Update Contact Attributes** (without changing lists):
```
PUT /contacts/{email_urlencoded}
Content-Type: application/json
api-key: {key}

{
  "attributes": {
    "MIGRATION_STATUS": "complete",
    "MIGRATION_PROFILE": "{compact_json}"
  }
}
```

**Add to List** (triggers Brevo automations):
```
POST /contacts/lists/{listId}/contacts/add
Content-Type: application/json
api-key: {key}

{"emails": ["customer@example.com"]}
```

### Brevo Contact List Reference

| List ID | Name | Purpose |
|---------|------|---------|
| 3 | Neural Feed | Blog newsletter subscribers |
| 4 | Enterprise Leads | Enterprise inquiry leads |
| 8 | PureBrain Customers | Post-purchase customers |
| 11 | PureBrain Migration Leads | General migration intent |
| 12 | PureBrain Migration — ChatGPT | ChatGPT drip trigger |
| 13 | PureBrain Migration — Claude | Claude drip trigger |
| 14 | PureBrain Migration — Gemini | Gemini drip trigger |
| 15 | PureBrain Migration — Perplexity | Perplexity drip trigger |
| 16 | PureBrain Migration — Midjourney | Midjourney drip trigger |
| 17 | PureBrain Migration — Copilot | Copilot drip trigger |
| 18 | PureBrain Migration — Other | Fallback drip trigger |

### Transactional Email

```
POST /smtp/email
Content-Type: application/json
api-key: {key}

{
  "to": [{"email": "customer@example.com", "name": "Jane Smith"}],
  "templateId": 11,
  "params": {
    "FIRSTNAME": "Jane",
    "AI_NAME": "Keen",
    "TIER": "Awakened",
    "PRIMARY_GOAL": "save 10hrs/week"
  }
}
```

**Response**: HTTP 201 with `{"messageId": "..."}`

**Template variable syntax in Brevo email bodies**: `{{params.VARNAME}}`

### Brevo Email Template Reference

| Template ID | Name | Trigger |
|-------------|------|---------|
| 1–7 | Neural Feed welcome sequence | Added to List 3 (blog signup) |
| 11 | PureBrain Welcome — Your AI partner is live | `POST /api/log-pay-test` with `flowCompleted=true` |
| 12 | PureBrain Setup Complete — 40 minutes in | 40-minute timer after Template 11 |
| Various | Migration drip sequences | Added to Lists 12–18 (manual Brevo automation) |

**NOTE**: Brevo has no REST API for automation workflow creation. Drip sequences require manual setup in Brevo UI (Automations → "Contact added to list" trigger).

---

## 2.6 PayPal API

**Base URL (Live)**: `https://api-m.paypal.com`
**Auth**: OAuth2 client credentials flow

### Authentication

```
POST /v1/oauth2/token
Authorization: Basic {base64(client_id:secret)}
Content-Type: application/x-www-form-urlencoded

grant_type=client_credentials
```

**Response**: `{"access_token": "...", "expires_in": 32400}`

### Order Verification

```
GET /v2/checkout/orders/{order_id}
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Response**: Full order object. Verification checks:
1. `order.status == "COMPLETED"`
2. `order.purchase_units[0].payments.captures[0].amount.value == expected_amount`

### Webhook Signature Verification

```
POST /v1/notifications/verify-webhook-signature
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "auth_algo": "{PAYPAL-AUTH-ALGO header}",
  "cert_url": "{PAYPAL-CERT-URL header}",
  "transmission_id": "{PAYPAL-TRANSMISSION-ID header}",
  "transmission_sig": "{PAYPAL-TRANSMISSION-SIG header}",
  "transmission_time": "{PAYPAL-TRANSMISSION-TIME header}",
  "webhook_id": "{PAYPAL_WEBHOOK_ID env var}",
  "webhook_event": {parsed_event_body}
}
```

**Response**: `{"verification_status": "SUCCESS"}`

### PayPal Subscription Product Reference

| Tier | Amount | Type |
|------|--------|------|
| Awakened | $79/month | Subscription |
| Bonded | $149/month | Subscription |
| Partnered | $499/month | Subscription |
| Unified | $999/month | Subscription |
| AI Website Execution — Critical | $197 | One-time |
| AI Website Execution — Complete | $497 | One-time |

---

## 2.7 Migration Portal Backend API (FastAPI)

**Location**: `tools/migration/migration_api.py`
**Runtime**: `uvicorn tools.migration.migration_api:app --port 8001`
**Auth**: HMAC `api-key` header using `hmac.compare_digest`

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/upload` | Upload ChatGPT or Claude export ZIP for parsing |
| GET | `/status/{job_id}` | Poll async parsing job status |
| GET | `/profile/{user_id}` | Retrieve completed user context profile |
| DELETE | `/delete/{user_id}` | GDPR delete — removes files, jobs, and profile |

**Supported Export Formats**:
- ChatGPT: ZIP containing `conversations.json` + `user.json` (OpenAI format)
- Claude: ZIP containing conversation export (Anthropic format, 3 known variants)
- Generic: CSV or JSON from any AI tool

**Output Profile Structure**:
```json
{
  "top_topics": ["marketing", "coding", "research"],
  "usage_style": "bullet-heavy",
  "expertise_level": "intermediate",
  "conversation_count": 847,
  "custom_instructions": "..."
}
```

---

---

# SECTION 3: DATA FLOW DIAGRAMS

## 3.1 Customer Journey: Visit → Assessment → Chatbox → Payment → Birth → Portal

```
STAGE 1: VISIT
─────────────────────────────────────────────────────────────────────────────
User visits purebrain.ai
    │
    ├── Cloudflare DNS resolves → GoDaddy WordPress host
    ├── Cloudflare CDN serves cached static assets
    ├── WordPress security plugin adds security headers (HSTS, CSP, X-Frame, etc.)
    └── Page HTML delivers chatbox JS bundle

STAGE 2: AI PARTNERSHIP ASSESSMENT
─────────────────────────────────────────────────────────────────────────────
User visits purebrain.ai/ai-adoption-assessment
    │
    ├── Self-contained assessment HTML widget loads (served via WordPress HTML widget)
    ├── User answers 6 scored questions
    ├── Score calculated client-side
    ├── Results page shown with matched CTA (based on score tier)
    └── Share button generates URL with score parameter

STAGE 3: CHATBOX CONVERSATION
─────────────────────────────────────────────────────────────────────────────
User engages chatbox on any purebrain.ai page
    │
    ├── Chatbox JS initialized with system prompt
    ├── User types message
    ├── Chatbox calls → WordPress plugin proxy → /wp-json/purebrain/v1/log-conversation
    │       └── Plugin forwards → POST https://89.167.19.20:8443/api/log-conversation
    ├── Message history sent to AI API (Claude or Cloudflare Workers AI proxy)
    ├── AI response displayed
    ├── End of session:
    │   ├── POST api.purebrain.ai/api/log-conversation (full history)
    │   ├── Background: forward to A-C-Gee 5.161.90.32:3001
    │   └── Background: publish to AICIV comms hub
    └── Chatbox captures AI partner name via regex (pre-purchase flow)

STAGE 4: PAYMENT
─────────────────────────────────────────────────────────────────────────────
User clicks "Get Started" / pricing CTA
    │
    ├── Pay-test page loads (WordPress page ID 439 or 468)
    ├── Pre-purchase chat flow runs (AI names itself, conversation)
    ├── User selects tier (Awakened $79 / Bonded $149 / Partnered $499 / Unified $999)
    ├── PayPal Smart Buttons rendered (client-side PayPal SDK)
    ├── User completes PayPal payment
    ├── PayPal fires CHECKOUT.ORDER.APPROVED event in browser
    ├── Client calls → POST api.purebrain.ai/api/verify-payment
    │       ├── Server calls PayPal OAuth token endpoint
    │       ├── Server calls PayPal order verification endpoint
    │       └── Returns {verified: true/false, amount, payer_email}
    ├── POST-PAYMENT FLOW LAUNCHES (fullscreen overlay):
    │   ├── Questionnaire: collect name, email, company, role, primaryGoal
    │   ├── Behind-the-curtain: Telegram setup instructions
    │   ├── Claude Max setup instructions
    │   └── AI partner presentation
    └── On flow:complete:
        ├── POST api.purebrain.ai/api/log-pay-test (full payTestData)
        ├── Background: Telegram notification to Jared
        ├── Background: Brevo contact upsert + Template 11 (immediate)
        ├── Background: Brevo Template 12 scheduled (40-min timer)
        └── User redirected → purebrain.ai/thank-you/

    SIMULTANEOUSLY — PayPal fires webhook:
        POST api.purebrain.ai/api/paypal-webhook
        ├── Signature verified via PayPal API
        ├── Event logged to purebrain_payments.jsonl
        └── Background: Telegram notification to Jared

STAGE 5: BIRTH (CONTAINER PROVISIONING)
─────────────────────────────────────────────────────────────────────────────
Customer accesses app.purebrain.ai
    │
    ├── Login page loads (Three.js neural network background + glassmorphism form)
    ├── Customer enters AI name + secret code
    ├── POST api.purebrain.ai/api/proxy/birth/start
    │       ├── Rate limit checked (5/min per IP)
    │       └── Proxied → POST http://104.248.239.98:8099/api/birth/start
    │           └── Witness provisions Docker container (up to 145s)
    │               Returns: {status: "url_ready", oauth_url, container}
    ├── POST api.purebrain.ai/api/proxy/birth/code (OAuth code submission)
    └── Poll GET api.purebrain.ai/api/proxy/birth/portal-status/{container}
            └── Returns: {ready: false} → {ready: true, portal_url: "..."}
                Customer browser redirects to portal_url

STAGE 6: PORTAL
─────────────────────────────────────────────────────────────────────────────
Customer accesses their provisioned portal URL
    │
    └── Isolated container serves personalized AI partner interface
```

---

## 3.2 Blog Publishing Flow: Draft → Banner → Dual-Publish → Newsletter → Social

```
1. CONTENT GENERATION
─────────────────────────────────────────────────────────────────────────────
content-specialist agent generates:
    ├── blog-post.md (full article, markdown)
    ├── linkedin-newsletter.md
    ├── linkedin-post.md
    └── bluesky-thread.md

2. BANNER GENERATION
─────────────────────────────────────────────────────────────────────────────
    ├── Method A: Gemini 3 Pro Image API (primary)
    │       POST to Gemini API with brand prompt
    │       Returns: PNG binary
    ├── Method B: Python matplotlib/PIL (fallback)
    └── Output: banner.png (1200x628px for OG image standard)

3. JARED REVIEW (MORNING DELIVERY)
─────────────────────────────────────────────────────────────────────────────
Files delivered via Telegram:
    ├── tg_send.sh --file blog-post.md "Today's blog"
    ├── tg_send.sh --photo banner.png "Today's banner"
    ├── tg_send.sh --file linkedin-newsletter.md "LinkedIn newsletter"
    └── tg_send.sh --file linkedin-post.md "LinkedIn post"

Jared reviews from phone and gives approval/feedback.

4. DUAL PUBLISH (after Jared approval)
─────────────────────────────────────────────────────────────────────────────
purebrain.ai publish:
    ├── POST /wp/v2/media (banner image upload)
    ├── POST /wp/v2/posts (create post, template="", wrapper: article.pb-blog-post)
    │       └── Content wrapped in <!-- wp:html --> block
    ├── Set featured image (returned media ID)
    ├── DELETE /wp-json/elementor/v1/cache (clear cache)
    └── Verify live at https://purebrain.ai/blog/{slug}/

jareddsanborn.com publish:
    ├── POST /wp/v2/media (same banner)
    ├── POST /wp/v2/posts (create post, template="page-template-blank.php")
    └── Verify live at https://jareddsanborn.com/blog/{slug}/

5. FILE ARCHIVE
─────────────────────────────────────────────────────────────────────────────
Google Drive filing (all files → Blog Posts folder subfolder):
    ├── Folder: "Blog Posts" (ID: 1trWAzRF8nkPs128W3TlxQZe9fPXc35Wv)
    ├── Subfolder: "{post-slug}-{date}"
    └── Files: blog-post.md, banner.png, og.png, linkedin-*.md, bluesky-thread.md

6. NEWSLETTER DISPATCH
─────────────────────────────────────────────────────────────────────────────
Automated via RSS-to-Email daemon (runs inside log server process):
    ├── Polls purebrain.ai RSS feed for new posts
    ├── Detects new post
    └── Creates Brevo campaign → sends to List 3 (Neural Feed subscribers)

7. SOCIAL DISTRIBUTION
─────────────────────────────────────────────────────────────────────────────
    ├── Bluesky: bsky-manager agent posts thread (autonomous)
    └── LinkedIn: Jared posts manually (content from linkedin-post.md)
```

---

## 3.3 Email Automation: Trigger → Template → Delivery → Tracking

```
TRIGGER TYPE A: Blog Subscriber (Neural Feed Welcome Sequence)
─────────────────────────────────────────────────────────────────────────────
User submits newsletter form on purebrain.ai
    │
    ├── Form submits to Brevo embed form endpoint
    ├── Contact created in Brevo with FIRSTNAME, email
    ├── Contact added to List 3 (Neural Feed)
    └── Brevo automation triggers:
        ├── Immediately: Template 1 (Welcome to Neural Feed)
        ├── Day 2: Template 2
        ├── Day 4: Template 3
        ├── Day 7: Template 4
        ├── Day 10: Template 5
        ├── Day 14: Template 6
        └── Day 21: Template 7

All templates include:
    - Reply-To: jared@puretechnology.nyc
    - Branding: PUREBR(blue)AI(orange)N(blue)
    - PS section with personalized add-on content
    - Social share footer

TRIGGER TYPE B: Purchase (Post-Purchase Emails)
─────────────────────────────────────────────────────────────────────────────
Customer completes pay-test flow (flowCompleted=true)
    │
    POST api.purebrain.ai/api/log-pay-test
        │
        └── Background thread: _trigger_post_purchase_emails(data)
            │
            ├── Brevo upsert: POST /v3/contacts
            │       email, FIRSTNAME, LASTNAME, AI_NAME, TIER,
            │       COMPANY, ROLE, PRIMARY_GOAL
            │       listIds: [8]  (PureBrain Customers)
            │
            ├── Immediate: POST /v3/smtp/email
            │       templateId: 11
            │       params: FIRSTNAME, AI_NAME, TIER, PRIMARY_GOAL
            │       → "Your AI partner is live"
            │
            └── threading.Timer(2400s):
                    POST /v3/smtp/email
                    templateId: 12
                    params: FIRSTNAME, AI_NAME, TIER, PRIMARY_GOAL
                    → "40 minutes in — setup complete"

TRIGGER TYPE C: Migration Lead (Competitor Exodus Drip)
─────────────────────────────────────────────────────────────────────────────
User completes Exodus quiz (competitor migration intent)
    │
    ├── JS calls saveMigrationIntent(data)
    │       └── Brevo upsert: COMPETITOR, PRIMARY_USE_CASES, USAGE_FREQUENCY,
    │               HAD_CUSTOM_CONFIG, MAIN_FRUSTRATION, MIGRATION_STATUS
    │               listIds: [3, 11]
    │
    └── JS calls triggerMigrationDrip(email, competitor)
            └── POST /v3/contacts/lists/{list_id}/contacts/add
                    List IDs: ChatGPT=12, Claude=13, Gemini=14,
                              Perplexity=15, Midjourney=16, Copilot=17, Other=18
                    Adding to list → triggers Brevo automation drip sequence

TRACKING (all email types)
─────────────────────────────────────────────────────────────────────────────
Brevo provides:
    ├── Open tracking (1x1 pixel beacon)
    ├── Click tracking (link rewriting)
    ├── Unsubscribe handling (automatic list removal)
    └── Bounce management (automatic contact status update)

Server-side logging:
    └── /logs/purebrain_emails.jsonl (per-email record with template_id, success bool, timestamp)
```

---

---

# SECTION 4: DEPLOYMENT ARCHITECTURE

## 4.1 WordPress Hosting (purebrain.ai)

| Property | Detail |
|----------|--------|
| Host | GoDaddy Managed WordPress |
| URL | https://purebrain.ai |
| PHP Version | 8.x (GoDaddy managed) |
| WordPress Version | Latest stable |
| Theme | Custom (dark theme, brand colors) |
| Page Builder | Elementor Pro (active license) |
| Caching | GoDaddy managed cache (`?wpaas_action=flush_cache`) |
| File Access | GoDaddy cPanel |

**Custom Plugin Deployment**:
1. Build PHP plugin file at `tools/security/purebrain-security/purebrain-security-plugin.php`
2. Package as ZIP: `tools/security/purebrain-security.zip`
3. Upload via WP Admin → Plugins → Add New → Upload Plugin
4. Activate plugin
5. Secrets (`ACGEE_API_KEY`) added to `wp-config.php` via GoDaddy cPanel

**Blog Post Deployment Rules**:
- Template: empty string `""` (default theme template, NOT `elementor_canvas`)
- Outer wrapper: `<article class="pb-blog-post">` (NOT `<div class="pb-blog-content">`)
- All content wrapped in `<!-- wp:html -->` block to prevent `wpautop` CSS destruction
- Mandatory footer: social share buttons + CTA → `https://purebrain.ai/#awakening`

---

## 4.2 Cloudflare Configuration

**DNS Records** (critical):

| Type | Name | Target | Proxied |
|------|------|--------|---------|
| A | purebrain.ai | GoDaddy WP IP | Yes (orange cloud) |
| CNAME | app.purebrain.ai | purebrain-app.netlify.app | No |
| CNAME | api.purebrain.ai | (Cloudflare Tunnel hostname) | Yes |
| CNAME | www.purebrain.ai | purebrain.ai | Yes |

**Cloudflare Tunnel** (for api.purebrain.ai):
- Tunnel exposes `https://89.167.19.20:8443` as `https://api.purebrain.ai`
- SSL between Cloudflare and origin is handled via self-signed cert (configured as "Full" mode)
- Cloudflare provides public-facing valid SSL certificate

**SSL/TLS Mode**: Full (Strict recommended for production upgrade)

**Cache**: Cloudflare edge caches static assets.
- Cache purge: Available in Cloudflare dashboard or via cache bypass `?nocache=timestamp`
- CF-Cache-Status header indicates: `HIT` (cached), `DYNAMIC` / `MISS` (origin response)

---

## 4.3 DigitalOcean VPS (Log Server / API Server)

| Property | Detail |
|----------|--------|
| VPS IP | 89.167.19.20 |
| Provider | DigitalOcean (Droplet) |
| OS | Ubuntu 22.04 LTS |
| Python | 3.10+ |
| Process Manager | systemd |
| Port | 8443 (HTTPS) |
| SSL Cert | Self-signed RSA 2048-bit, SAN for 89.167.19.20 |
| Cert Location | `/home/jared/projects/AI-CIV/aether/config/ssl/` |
| Cert Valid | 365 days (regenerated via openssl command in server startup) |

**systemd Service Units**:

| Service | Unit File | Purpose |
|---------|-----------|---------|
| `purebrain-log-server.service` | `/etc/systemd/system/` | Log server Flask app (port 8443) |
| `aether-session.service` | `/etc/systemd/system/` | tmux session persistence |
| `aether-telegram.service` | `/etc/systemd/system/` | Telegram bridge process |

**Service Management**:
```bash
sudo systemctl restart purebrain-log-server
sudo systemctl status purebrain-log-server
journalctl -u purebrain-log-server -n 100 --no-pager
```

**Persistent Log Files** (JSONL format, append-only):
| File | Contents |
|------|----------|
| `/logs/purebrain_web_conversations.jsonl` | All chatbox session logs |
| `/logs/purebrain_pay_test.jsonl` | Purchase flow completion data |
| `/logs/purebrain_payments.jsonl` | Payment verifications + webhook events |
| `/logs/purebrain_emails.jsonl` | Email send audit log |
| `/logs/purebrain_log_server.log` | Flask server runtime log |
| `/logs/telegram_bridge.log` | Telegram bridge log |

**Flask Application Configuration**:
```python
app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024  # 1 MB

CORS(app, resources={r"/api/*": {"origins": [
    "https://purebrain.ai",
    "https://www.purebrain.ai",
    "https://jareddsanborn.com",
    "https://www.jareddsanborn.com",
]}})
```

**Environment Variables** (in `.env`):
```
BREVO_API_KEY=...
PAYPAL_CLIENT_ID=...
PAYPAL_SECRET=...
PAYPAL_WEBHOOK_ID=...
NETLIFY_AUTH_TOKEN=...
PUREBRAIN_WP_APP_PASSWORD=...
WORDPRESS_APP_PASSWORD=...
GOOGLE_API_KEY=...
```

---

## 4.4 Vercel Deployment (PureBrain Hub)

| Property | Detail |
|----------|--------|
| Platform | Vercel (free tier) |
| URL | https://purebrain-hub.vercel.app |
| Deployment Type | Static site (single HTML file) |
| Deploy Path | `tools/purebrain-hub-static/` |

**Deploy Command**:
```bash
cd tools/purebrain-hub-static
npx vercel --prod --yes
```

**Redeploy Pattern**:
```bash
cp exports/purebrain-hub-v2.html tools/purebrain-hub-static/index.html
cd tools/purebrain-hub-static
npx vercel --prod --yes
```

**No build step** — single file deployment. Vercel serves `index.html` directly.

---

## 4.5 Netlify Deployments

### app.purebrain.ai (Customer Portal)

| Property | Detail |
|----------|--------|
| Netlify Site ID | `2139f9ed-32cc-4abd-8364-8bb81b94df9b` |
| Netlify Site Name | `purebrain-app` |
| Account Slug | `purebrain` |
| Auth Token | `.env` as `NETLIFY_AUTH_TOKEN` |
| CLI Version | `npx netlify-cli@23.15.1` (v24.x has known issues) |
| Source File | `exports/purebrain-frontend-3d.html` |
| Deploy Size | ~895 KB (Three.js + inline assets) |

**Deploy Command**:
```bash
cp exports/purebrain-frontend-3d.html /tmp/purebrain-app-deploy/index.html

NETLIFY_AUTH_TOKEN=$NETLIFY_AUTH_TOKEN \
  npx netlify-cli@23.15.1 deploy --prod \
  --dir=/tmp/purebrain-app-deploy \
  --site=2139f9ed-32cc-4abd-8364-8bb81b94df9b
```

**Create New Site** (REST API, not CLI — CLI is interactive):
```bash
curl -X POST -H "Authorization: Bearer $NETLIFY_AUTH_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "site-name", "account_slug": "purebrain"}' \
  "https://api.netlify.com/api/v1/sites"
```

**Set Custom Domain**:
```bash
curl -X PATCH -H "Authorization: Bearer $NETLIFY_AUTH_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"custom_domain": "app.purebrain.ai"}' \
  "https://api.netlify.com/api/v1/sites/{site-id}"
```

### pure-tech-dashboard.netlify.app (Team Dashboard)

| Property | Detail |
|----------|--------|
| Netlify Site ID | `d2556d0a-5333-47ca-a8d6-8add4141f090` |
| Source File | `exports/team-dashboard/dist/index.html` |
| Backend | Supabase (configured in-app, not hard-coded) |

**Deploy Command**:
```bash
npx netlify-cli deploy --prod \
  --dir=./dist \
  --auth=$NETLIFY_AUTH_TOKEN \
  --site=d2556d0a-5333-47ca-a8d6-8add4141f090
```

**Supabase Schema** (must be provisioned in Supabase dashboard before first use):
```sql
create table tasks (
  id text primary key,
  title text not null,
  description text,
  "assignedTo" text,
  delegation text,
  priority text,
  status text,
  deadline text,
  files text,
  "createdAt" text,
  "createdBy" text
);
alter table tasks enable row level security;
create policy "public read" on tasks for select using (true);
create policy "public write" on tasks for all using (true);
```

---

## 4.6 Security Architecture Summary

| Layer | Control | Implementation |
|-------|---------|----------------|
| Network | Cloudflare proxy (DDoS, bot protection) | Cloudflare DNS orange-cloud |
| Transport | TLS 1.2+ | Cloudflare edge + self-signed on VPS |
| API Security | CORS whitelist | Flask CORS (purebrain.ai origins only) |
| Credentials | Server-side proxies | WP plugin routes all secret calls through PHP layer |
| XSS | Input sanitization | All user inputs sanitized before DOM insertion |
| SSRF | Hardcoded upstream IP | `WITNESS_BASE_URL` never from request input |
| Rate Limiting | Sliding-window per-IP | `threading.Lock` + `deque` in Flask |
| Headers | Security header suite | Custom WP plugin injects all headers |
| CSP | Content Security Policy | Enforced mode (not report-only) |
| HSTS | Strict Transport Security | `max-age=31536000; includeSubDomains; preload` |

---

---

# SECTION 5: INFRASTRUCTURE INVENTORY

## 5.1 Servers

| Server | Provider | IP | Role |
|--------|----------|----|------|
| WordPress Host | GoDaddy | Managed (no direct IP) | purebrain.ai frontend |
| API VPS | DigitalOcean | 89.167.19.20 | Log server, API, proxies |
| Witness VPS | DigitalOcean | 104.248.239.98 | Container provisioning |
| A-C-Gee VPS | Hetzner | 5.161.90.32 | Cross-CIV shared database |

## 5.2 Static Hosting

| Service | URL | Provider | Purpose |
|---------|-----|----------|---------|
| purebrain-app | app.purebrain.ai | Netlify | Customer portal |
| purebrain-hub | purebrain-hub.vercel.app | Vercel | Internal team hub |
| team-dashboard | pure-tech-dashboard.netlify.app | Netlify | Task management |

## 5.3 Third-Party SaaS

| Service | Purpose | Account |
|---------|---------|---------|
| Brevo | Email marketing + transactional email | purebrain@puremarketing.ai |
| PayPal | Payment processing | Live environment |
| Cloudflare | DNS, CDN, tunnel | purebrain.ai |
| Google Drive | File storage / knowledge base | purebrain@puremarketing.ai |
| Supabase | PostgreSQL for team dashboard | Free tier |
| Telegram | Operational notifications | Bot token in `config/telegram_config.json` |

## 5.4 Key Source File Paths

| Component | Path |
|-----------|------|
| Log Server | `tools/purebrain_log_server.py` |
| Security Plugin | `tools/security/purebrain-security/purebrain-security-plugin.php` |
| Migration API | `tools/migration/migration_api.py` |
| Portal Frontend | `exports/purebrain-frontend-3d.html` |
| Team Hub | `exports/purebrain-hub-v2.html` |
| Team Dashboard | `exports/team-dashboard/dist/index.html` |
| Brevo Setup Script | `tools/setup_post_purchase_brevo.py` |
| Migration Brevo JS | `exports/migration-brevo-integration.js` |
| Telegram Bridge | `tools/telegram_bridge.py` |
| Google Drive Tool | `tools/gdrive_manager.py` |
| Neural Feed Scheduler | `tools/neural_feed_welcome_sequence.py` |
| RSS-to-Email Daemon | `tools/rss_to_email.py` |

---

*End of SRS Sections — System Architecture, API Specification, Data Flow Diagrams, Deployment Architecture*

*Document prepared by Aether engineering team, 2026-02-26.*
*For questions, contact jared@puretechnology.nyc*
