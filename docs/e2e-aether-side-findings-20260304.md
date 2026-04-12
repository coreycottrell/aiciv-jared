# Aether-Side E2E Test Findings — 2026-03-04

**Cross-reference**: Witness doc at `/home/aiciv/civ/docs/e2e-test-findings-20260304.md`

---

## What Works (Aether Side)

| Component | Status | Details |
|-----------|--------|---------|
| Birth webhook endpoint | ✅ LIVE | `POST https://api.purebrain.ai/api/birth/webhook` |
| Auth: static token | ✅ | `X-Witness-Secret: witness-secret-2026` |
| Auth: HMAC-SHA256 | ✅ Ready | `X-Witness-Signature: sha256=<hex>` (env: `WITNESS_WEBHOOK_SECRET`) |
| Idempotency guard | ✅ | Dedup by email + container combo in `birth_completions.jsonl` |
| Brevo magic link email | ✅ | Template ID 30: "Your AI partner is ready" |
| Telegram notify Jared | ✅ | Sends to chat_id 548906264 on every birth |
| Portal-status endpoint | ✅ FIXED | `GET /api/birth/portal-status/{container}` — checks local log FIRST, falls back to Witness proxy |
| Seed sender (page 1232) | ✅ ADDED | POSTs to `/api/birth/start` after chat completes |
| Portal button (page 1232) | ✅ | Greyed-out → blinking blue/orange on `ready:true` |
| runPortalButtonWatcher | ✅ | Polls every 30s, max 60 polls (30 min), timeout fallback message |

---

## Webhook Payload Format (What Aether Expects)

```json
POST https://api.purebrain.ai/api/birth/webhook
Header: X-Witness-Secret: witness-secret-2026
Content-Type: application/json

{
  "event": "birth_complete",
  "human_email": "customer@example.com",
  "human_name": "Jared Sanborn",
  "civ_name": "Keen",
  "container": "keenjaredsanborn",
  "magic_link": "https://keenjaredsanborn.ai-civ.com?token=abc123"
}
```

**Required fields**: `event`, `human_email`, `magic_link` (or `portal_url`)
**Optional but recommended**: `human_name`, `civ_name`, `container`
**Accepts both**: `magic_link` and `portal_url` (uses whichever is present)

---

## Seed Payload Format (What Aether Sends to /api/birth/start)

```json
POST https://api.purebrain.ai/api/birth/start
Content-Type: application/json

{
  "name": "Jared Sanborn",
  "email": "jared@puretechnology.nyc",
  "human_name": "Jared Sanborn",
  "ai_name": "Keen",
  "tier": "awakened",
  "container": "keenjaredsanborn"
}
```

This proxies through our server to Witness at `http://37.27.237.109:8099/api/birth/start`.

**Expected response** (from Witness):
```json
{
  "status": "url_ready",
  "container": "keenjaredsanborn",
  "oauth_url": "https://claude.ai/..."  // optional for sandbox-3 flow
}
```

The `container` field in the response is AUTHORITATIVE — the browser updates `payTestData.containerName` to match whatever Witness returns.

---

## Container Name Derivation (Current Logic)

**Client-side (page 1232) derives:**
```javascript
const seedAiName = aiName.toLowerCase().replace(/[^a-z]/g, '');
const seedName = humanName.toLowerCase().replace(/[^a-z]/g, '');
const derivedContainer = seedAiName + seedName;
// e.g. "Keen" + "Jared" → "keenjared"
// e.g. "Keen" + "Jared Sanborn" → "keenjaredsanborn"
```

**Witness creates:** `keen-jared-sanborn` (with hyphens between parts)

### 🔴 NAMING MISMATCH — Needs Alignment

| Source | Format | Example |
|--------|--------|---------|
| Aether client-side | `{ainame}{firstname}` | `keenjared` |
| Aether (with full name) | `{ainame}{firstnamelastname}` | `keenjaredsanborn` |
| Witness actual | `{ainame}-{firstname}-{lastname}` | `keen-jared-sanborn` |

**Proposed resolution**: Aether matches Witness format. Change derivation to:
```javascript
const derivedContainer = seedAiName + '-' + fullName.toLowerCase().replace(/\s+/g, '-').replace(/[^a-z-]/g, '');
// "Keen" + "Jared Sanborn" → "keen-jared-sanborn"
```

**OR**: Rely on Option 3 — Witness returns authoritative container name in `/api/birth/start` response, browser uses that. Client derivation is just a fallback.

---

## Portal Polling Logic

```
Browser (page 1232) → GET /api/birth/portal-status/{container}
  ↓
Aether server checks birth_completions.jsonl for matching container
  ↓
If found → { "ready": true, "portalUrl": "https://..." }
If not found → falls back to Witness proxy at 37.27.237.109:8099
  ↓
Browser receives ready:true → transforms button:
  - Removes ptc-portal-btn--disabled class
  - Adds ptc-portal-btn--active class (blinking blue/orange animation)
  - Sets onclick to open portalUrl in new tab
  - Re-enables pointer-events
```

**Polling params**: Every 30 seconds, max 60 polls (30 min total), then timeout fallback message.

**Portal URL domain validation**: Browser validates portal URL against allowlist:
- `purebrain.ai`, `puremarketing.ai`, `aiciv.dev`
- Must be HTTPS
- Subdomains allowed (e.g. `keen.app.purebrain.ai`)

⚠️ **GAP**: `ai-civ.com` is NOT in the allowlist! Witness magic links use `*.ai-civ.com`. Need to add `ai-civ.com` to the allowed domains list.

---

## Gaps / TODOs for Full Auto

### Aether Side
1. **🔴 Add `ai-civ.com` to portal URL allowlist** — Current code validates portal URLs against `['purebrain.ai', 'puremarketing.ai', 'aiciv.dev']`. Witness links use `*.ai-civ.com` which will FAIL validation and fall back to `https://purebrain.ai/portal`.
2. **🟡 Container naming alignment** — Match Witness format or rely on server-authoritative response.
3. **🟡 Pages 688/689 don't have the new button UX** — Only page 1232 has greyed-out → light-up button. Pages 688/689 use older portal button system.
4. **🟢 Brevo template 30 untested with real delivery** — Created but no real customer email sent yet.

### Witness Side (from their doc)
1. **🔴 Auto-trigger broken** — seeds land but capture_watcher SCP fails, orchestrator never fires
2. **🟡 Container naming mismatch** — needs alignment with Aether
3. **🟡 identity-formation.md missing** — blocked orchestrator 5 min
4. **🟢 AETHER_WEBHOOK_URL** — FIXED today

---

## Birth Completions Log (as of session end)

```
# Entries 1-6: Aether test entries (localhost)
# Entry 7: REAL Witness birth ← FIRST SUCCESSFUL E2E
#   container: keen-jared-sanborn
#   magic_link: https://keenjared-sanborn.ai-civ.com?token=0cA_eNNg...
#   received_at: 2026-03-04T01:13:40 UTC
# Entries 8-9: Aether test entries
```

Total: 9 entries. 1 real Witness birth confirmed.

---

## Key Files

| File | Purpose |
|------|---------|
| `tools/purebrain_log_server.py` | API server — webhook, portal-status, birth proxy |
| `logs/birth_completions.jsonl` | Birth completion log (webhook writes here) |
| `tools/fix_sandbox3_birth_polling.py` | Script that added seed + polling to page 1232 |
| `config/telegram_config.json` | Telegram bot token for notifications |
| `.env` | BREVO_API_KEY, PUREBRAIN_WP_APP_PASSWORD, etc. |

---

## Session Timeline

| Time (UTC) | Event |
|------------|-------|
| ~00:30 | Jared reports blank screen on sandbox-3 after payment |
| ~00:35 | Diagnosed: sanitizeText missing + IIFE scope bug. Fixed. |
| ~00:40 | Button text changes + greyed-out → light-up UX deployed |
| ~00:43 | Birth webhook endpoint built + first local test |
| ~00:45 | Public URL test passed |
| ~00:50 | Witness confirmed their e2e test hit our webhook |
| ~00:55 | Full proof battery (5/5 tests passing) |
| ~01:00 | Brevo template 30 created (was using wrong template 15) |
| ~01:03 | Jared ran live test — button didn't light up |
| ~01:06 | Diagnosed: portal-status endpoint broken (old proxy intercepting) |
| ~01:07 | Fixed portal-status to check local log first |
| ~01:10 | Diagnosed: runBirthInit removed from page 1232 — no seed, no polling |
| ~01:12 | Deployed fix: seed sender + portal polling added to page 1232 |
| ~01:13 | Witness birth webhook received! (keen-jared-sanborn) |
| ~01:17 | Container naming mismatch identified |
| ~01:20 | Session end — doc written for cross-reference |
