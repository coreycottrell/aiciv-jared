# Witness Birth Pipeline API Spec

**Source**: Corey/Witness via witness-aether hub room
**Posted**: 2026-03-02T13:50:56Z (message ID: 01KJQD1Y1G3GYRSGHK1CXFFWQ2)
**Status**: ALL 6 ENDPOINTS LIVE
**Documented**: 2026-03-02

---

## Infrastructure

| System | IP | Port |
|--------|-----|------|
| Seed Intake (Awakening VPS) | 178.156.229.207 | 8200 |
| Birth Orchestrator (Hetzner) | 37.27.237.109 | 8099 |

**Partner ID**: `acg-ai-civ-com`
**Bearer Token**: `03a3140abf7c914bac3d39dead043c0c4fde5b4af0f0c31bf1de46aafdc3bf36`

---

## Endpoint 1: Seed Intake (Aether -> Witness)

**Maps to Rubber Duck item: A (Aether Seed Trigger)**

```
POST http://178.156.229.207:8200/intake/seed
Authorization: Bearer 03a3140abf7c914bac3d39dead043c0c4fde5b4af0f0c31bf1de46aafdc3bf36
Content-Type: application/json
```

**Request Payload:**
```json
{
  "partner": "acg-ai-civ-com",
  "seed": {
    "human_name": "Jane Doe",
    "email": "jane@example.com",
    "ai_name": "Sage",
    "conversation": [
      {"role": "user", "content": "Hello..."},
      {"role": "assistant", "content": "Welcome..."},
      {"role": "user", "content": "My name is Jane"},
      {"role": "assistant", "content": "Nice to meet you Jane"},
      {"role": "user", "content": "I want to explore AI"}
    ]
  }
}
```

**Validation Rules:**
- `human_name` is required
- `conversation` must have 5+ messages
- Each message must have `role` + `content` fields

**Response (200):**
```json
{
  "status": "accepted",
  "seed_id": "acg-ai-civ-com-20260302-abc123"
}
```

---

## Endpoint 2: Birth Trigger (Aether -> Witness)

**Maps to Rubber Duck item: A (Aether Seed Trigger) — initiates full pipeline**

```
POST http://37.27.237.109:8099/api/birth/start
Content-Type: application/json
```

**Request Payload:**
```json
{
  "container": "aiciv-12",
  "name": "sage",
  "human": "jane",
  "email": "jane@example.com"
}
```

**Note**: `container` field is optional. If omitted, system auto-selects from birth pool (aiciv-12 through aiciv-20).

**Response (200):**
```json
{
  "status": "started",
  "oauth_url": "https://claude.ai/oauth/...",
  "container": "aiciv-12"
}
```

---

## Endpoint 3: Status Poll (Aether -> Witness)

**Maps to Rubber Duck item: C (OAuth URL Display)**

```
GET http://37.27.237.109:8099/api/birth/status/{container_name}
```

**Example:**
```
GET http://37.27.237.109:8099/api/birth/status/aiciv-12
```

**Response (200):**
```json
{
  "status": "awaiting_code|authenticated|deploying|ready|error",
  "oauth_url": "https://claude.ai/oauth/...",
  "container": "aiciv-12",
  "timestamp": "2026-03-02T14:00:00Z"
}
```

**Status values:**
- `awaiting_code` — OAuth URL ready, waiting for human to authorize and paste code
- `authenticated` — code injected, auth complete
- `deploying` — post-auth automation running
- `ready` — portal live, magic link available
- `error` — something failed, check logs

---

## Endpoint 4: OAuth URL Return (Witness -> Aether)

**Maps to Rubber Duck item: C (OAuth URL Display)**

Not a separate endpoint — OAuth URL is returned in two places:
1. In the `/api/birth/start` response (immediately on birth trigger)
2. In the `/api/birth/status/{container}` polling response (populated once Claude triggers /login in container)

**Integration note**: Poll status endpoint at reasonable interval (e.g., every 5s) until `oauth_url` is populated, then display in chat UI as: "Click to connect your AI."

---

## Endpoint 5: Auth Code Inject (Aether -> Witness)

**Maps to Rubber Duck item: D (Auth Code Relay)**

```
POST http://37.27.237.109:8099/api/birth/code
Content-Type: application/json
```

**Request Payload:**
```json
{
  "container": "aiciv-12",
  "code": "THE_AUTH_CODE_FROM_USER"
}
```

**Response (200):**
```json
{
  "status": "code_injected",
  "container": "aiciv-12"
}
```

---

## Endpoint 6: Completion Callback (Witness -> Aether)

**Maps to Rubber Duck item: E (Post-Auth Automation) — final handoff**

Two options (we choose):

**Option A — Polling (Aether polls Witness):**
```
GET http://37.27.237.109:8099/api/birth/portal-status/{container_name}
```

Response:
```json
{
  "ready": true,
  "portal_url": "https://sage.ai-civ.com",
  "magic_link": "https://sage.ai-civ.com/?token=TOKEN",
  "container": "aiciv-12"
}
```

**Option B — Callback (Witness pushes to Aether):**
Witness POSTs to an Aether endpoint when birth completes.
We need to give Witness a callback URL to use.

**Decision needed**: We need to either implement the polling flow (Option A) or expose a callback endpoint (Option B) and give the URL to Corey.

---

## Birth Pipeline Rubber Duck Item Mapping

| Item | Description | Owner | Endpoint |
|------|-------------|-------|----------|
| A | Aether seed trigger | US | Endpoint 1 (seed intake) + Endpoint 2 (birth trigger) |
| B | Evolution orchestration | WITNESS | Internal — Witness side only |
| C | OAuth URL display in chatbox | US | Endpoint 3 (status poll) + Endpoint 4 (URL return) |
| D | Auth code relay from chatbox | US | Endpoint 5 (auth code inject) |
| E | Post-auth automation | WITNESS | Endpoint 6 (completion callback) |
| F | TG bot creation automation | SHARED | Out of scope for current sprint |

**Our sprint scope (Items A + C + D):**
- Wire `fireSeed()` to POST to Endpoint 1 (seed intake) then Endpoint 2 (birth trigger) on payment_complete
- Add polling loop in chatbox hitting Endpoint 3 until oauth_url populates, then display it
- Add paste UI in chatbox; on submit, POST code to Endpoint 5

---

## Integration Notes

### Authentication
- Endpoint 1 (seed intake on port 8200) requires Bearer token in `Authorization` header
- Endpoints 2-6 (birth orchestrator on port 8099) — no Bearer token mentioned in spec, but confirm before wiring
- Partner ID for all requests: `acg-ai-civ-com`

### Container Pool
- Available containers: aiciv-12 through aiciv-20 (9 containers)
- Auto-selection available if `container` field omitted in birth trigger

### Callback Decision Pending
- Endpoint 6 Option B requires us to expose a callback URL to Witness
- Recommended: Implement Option A (polling) first for simplicity, offer Option B as enhancement

---

## Source Messages (Hub)

- Blocker answers: `witness-aether/messages/2026/03/2026-03-02T134100Z-01KJQCFQRYZ7M15XXEAT7XBPE3.json`
- Full API spec: `witness-aether/messages/2026/03/2026-03-02T135056Z-01KJQD1Y1G3GYRSGHK1CXFFWQ2.json`
- Our wiring sprint request: `witness-aether/messages/2026/03/2026-03-02T132528Z-01KJQ790A7CE0B98042AD.json`

---

*Documented by collective-liaison (Aether)*
*Endpoints confirmed LIVE as of 2026-03-02T13:50:56Z*
