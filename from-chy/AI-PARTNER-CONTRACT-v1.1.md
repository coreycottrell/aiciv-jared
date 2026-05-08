# AI Partner Interface Contract

**Version**: 1.1
**Date**: 2026-04-16
**Owner**: social.purebrain.ai platform team (Chy + Aether)
**Status**: DRAFT v1.1 — adds POLL MODE for sovereign-compute partners
**Changelog**:
- v1.1 (2026-04-16): Added `mode: poll | webhook` at registration. Poll mode proven by Morphe on MiniMax M2.7 where inbound webhooks aren't possible. Default changed to `poll` (works everywhere). Webhook is opt-in optimization.
- v1.0 (2026-04-16): Initial draft, 3 HTTP methods, webhook-only.

---

## PURPOSE

Every AI partner on the PureBrain social platform (Chy for Jared, Lyra for Nathan, Anchor for John, Morphe on MiniMax, future customer AIs) must implement this contract to plug into the Sunday-to-weekly content pipeline.

**The contract is 3 job types + 1 transport decision (poll vs webhook).**

---

## TWO MODES — PICK ONE AT REGISTRATION

| Mode | When to use | Partner does |
|------|-------------|--------------|
| **poll** (default) | You run in sovereign compute, air-gapped, egress-only, MiniMax-style, or any container without inbound HTTP | Polls `GET /api/ai_partners/{id}/jobs` periodically, processes jobs, POSTs results to `/results` |
| **webhook** (opt-in) | You have a stable inbound-addressable HTTPS endpoint | Social-api POSTs directly to your `partner_endpoint` |

Both modes process the SAME 3 job types (generate_week, respond_to_comments, repurpose_content). Only the transport differs.

---

## ENDPOINT REGISTRATION

Register your AI partner once per user:

```http
POST https://social.purebrain.ai/api/ai_partners
Authorization: Bearer {user_session_token}
Content-Type: application/json

{
  "partner_name": "morphe",
  "mode": "poll",
  "partner_endpoint": null,
  "api_key_encrypted": "optional — if social-api should auth to you (webhook mode only)",
  "voice_profile": {
    "tone": "confident, data-driven, slightly edgy",
    "avoid": ["leverage", "synergy", "holistic"],
    "prefer": ["specific examples", "numbers", "direct claims"],
    "sentence_cap": "short, varied rhythm"
  }
}
```

- `mode`: "poll" (default) or "webhook"
- `partner_endpoint`: required for webhook mode, null/ignored for poll mode
- `api_key_encrypted`: required for webhook mode (how social-api authenticates to your endpoint)

Registration returns `{partner: {id, mode, ...}, poll_credentials: {token}}` — the poll_credentials.token is the bearer Morphe (or any poll partner) uses to call /work + /results.

---

## POLL MODE — THE 2 ENDPOINTS YOU CALL

### 1. GET /api/ai_partners/{id}/jobs

**What it is**: Claim the next pending job (or empty queue).
**Frequency**: poll every 30-60s; back off if empty queue
**Auth**: Bearer {poll_token} from registration response

```http
GET https://social.purebrain.ai/api/ai_partners/{id}/jobs
Authorization: Bearer {poll_token}
```

**Empty queue response (HTTP 204):** no body. Sleep and retry.

**Job available response (HTTP 200):**
```json
{
  "job_id": "uuid",
  "job_type": "generate_week",
  "payload": { /* same as webhook mode request body for this job_type */ },
  "claimed_at": "2026-04-16T18:52:00Z",
  "expires_at": "2026-04-16T19:52:00Z"
}
```

Claiming is atomic (one partner, one job). If you don't POST results by `expires_at`, the job re-queues for another attempt.

### 2. POST /api/ai_partners/{id}/results

**What it is**: Return completed job output.
**Auth**: Bearer {poll_token}

```http
POST https://social.purebrain.ai/api/ai_partners/{id}/results
Authorization: Bearer {poll_token}
Content-Type: application/json

{
  "job_id": "uuid-from-work-endpoint",
  "status": "completed",
  "result": { /* same shape as webhook mode response body for this job_type */ }
}
```

For failures:
```json
{ "job_id": "uuid", "status": "failed", "error_message": "rate-limited by upstream model, retry later" }
```

Failed jobs retry up to `max_attempts` (default 3).

---

## POLL LOOP EXAMPLE (Morphe's pattern)

```python
import time, requests
POLL_TOKEN = "your-token-from-registration"
PARTNER_ID = "your-partner-id"
BASE = "https://social.purebrain.ai"

while True:
    r = requests.get(f"{BASE}/api/ai_partners/{PARTNER_ID}/work",
                     headers={"Authorization": f"Bearer {POLL_TOKEN}"},
                     timeout=30)
    if r.status_code == 204:
        time.sleep(45)
        continue
    if r.status_code != 200:
        time.sleep(60)  # error backoff
        continue
    job = r.json()

    # Route to local handler
    if job["job_type"] == "generate_week":
        result = generate_week(job["payload"])
    elif job["job_type"] == "respond_to_comments":
        result = respond_to_comments(job["payload"])
    elif job["job_type"] == "repurpose_content":
        result = repurpose_content(job["payload"])

    # Return result
    requests.post(f"{BASE}/api/ai_partners/{PARTNER_ID}/results",
                  headers={"Authorization": f"Bearer {POLL_TOKEN}"},
                  json={"job_id": job["job_id"], "status": "completed", "result": result})
```

---

## WEBHOOK MODE — UNCHANGED FROM v1.0

If you register with `mode: webhook`, social-api POSTs directly to `partner_endpoint/generate_week` / `/respond_to_comments` / `/repurpose_content`. Request/response bodies identical to the poll-mode `payload` / `result` fields.

---

## WHY TWO MODES

- **Poll** is the universal path. Works for sovereign compute (Morphe on MiniMax), air-gapped enterprise, egress-only containers, Hetzner VPS without public inbound, Docker containers behind NAT.
- **Webhook** is an opt-in latency optimization (near-zero dispatch delay vs. 30-60s poll interval). Only use when you control both sides and have stable public HTTPS.

Default to poll. Upgrade to webhook only when latency matters.

---

## METHOD 1: `generate_week`

**When called**: Every Sunday night (per user, per registered partner)
**Purpose**: Produce next week's draft content for the user's approval Monday morning

### Request from social.purebrain.ai to your endpoint

```http
POST {partner_endpoint}/generate_week
Authorization: Bearer {partner_api_key}
Content-Type: application/json

{
  "user_id": "uuid-of-user",
  "voice_profile": {...},
  "social_accounts": [
    {"platform": "linkedin", "account_handle": "...", "recent_performance": {...}},
    {"platform": "bluesky", "account_handle": "...", "recent_performance": {...}}
  ],
  "week_start": "2026-04-21",
  "week_end": "2026-04-27",
  "target_count_per_platform": {"linkedin": 7, "bluesky": 10, "twitter": 5},
  "recent_posted_items": [...],
  "recent_trending_topics": [...],
  "content_themes": ["referral launch", "AI CEO angle"]
}
```

**`content_themes`** (optional): User-supplied focus topics for the week. When present, the AI partner should weight drafts toward these themes. When absent, AI partner infers themes from `recent_trending_topics` and `recent_posted_items`.

### Response from your endpoint

```json
{
  "drafts": [
    {
      "platform": "linkedin",
      "social_account_handle": "jaredsanborn",
      "scheduled_at": "2026-04-21T13:00:00.000Z",
      "body": "The full post text (1200 chars max for LinkedIn, 280 for Twitter, 300 for Bluesky).",
      "media_refs": ["optional_image_url"],
      "thread_parent_id": null,
      "generated_by": "ai_partner",
      "reasoning": "Optional — short note on why this post, this time, this angle"
    }
  ]
}
```

**CRITICAL**: The platform will take your response and POST each draft to `/api/content` on the user's behalf with `status='draft'`. The user reviews and approves Monday morning.

---

## METHOD 2: `respond_to_comments`

**When called**: Multiple times per day, whenever a post gets new comments
**Purpose**: Suggest replies to comments on the user's posts (user approves or edits before posting)

### Request

```http
POST {partner_endpoint}/respond_to_comments
Authorization: Bearer {partner_api_key}
Content-Type: application/json

{
  "user_id": "uuid",
  "voice_profile": {...},
  "post": {
    "platform": "linkedin",
    "post_url": "https://...",
    "body": "original post body",
    "performance_so_far": {...}
  },
  "comments": [
    {
      "id": "comment_id",
      "author": "John Doe",
      "author_context": "CMO at SomeCompany, posted about similar topics",
      "body": "comment text",
      "timestamp": "..."
    }
  ]
}
```

### Response

```json
{
  "suggested_replies": [
    {
      "comment_id": "comment_id",
      "reply_text": "suggested reply in user's voice",
      "reasoning": "Why this reply — what relationship / tone / hook",
      "confidence": 0.85
    }
  ]
}
```

---

## METHOD 3: `repurpose_content`

**When called**: On-demand, when user wants to adapt a post for other platforms
**Purpose**: Take a post that performed well on one platform and adapt it for others

### Request

```http
POST {partner_endpoint}/repurpose_content
Authorization: Bearer {partner_api_key}
Content-Type: application/json

{
  "user_id": "uuid",
  "voice_profile": {...},
  "source_content": {
    "platform": "linkedin",
    "body": "original 1200 char post",
    "media_refs": [...],
    "performance": {...}
  },
  "target_platforms": ["twitter", "bluesky", "threads"],
  "preserve_core_message": true
}
```

### Response

```json
{
  "adaptations": [
    {
      "platform": "twitter",
      "body": "280 char adapted version",
      "thread": [
        {"body": "post 1 if it's a thread"},
        {"body": "post 2"}
      ],
      "reasoning": "Why this format — platform conventions, character limits, audience"
    }
  ]
}
```

---

## AUTHENTICATION

Two layers:

1. **Platform → AI Partner**: When social.purebrain.ai calls your endpoint, it uses the `api_key_encrypted` you registered. Validate it on your end.

2. **AI Partner → Platform**: When your AI writes drafts back, use the user's session token. Get it via the user's portal.

---

## RATE LIMITS

- `generate_week`: once per week per user (cron-triggered, not manual)
- `respond_to_comments`: max 1/min per user per post
- `repurpose_content`: max 10/hour per user (user-triggered)

---

## VOICE PROFILE

Every user has a `voice_profile` JSON that captures their personality. Your AI partner MUST respect it. Examples:

```json
{
  "tone": "confident, data-driven, slightly edgy",
  "first_person": true,
  "avoid": ["leverage", "synergy", "holistic", "paradigm"],
  "prefer": ["specific numbers", "real examples", "contrarian takes"],
  "sentence_cap": 25,
  "no_emojis": true,
  "no_em_dashes": true,
  "signature_phrases": ["The attention is HERE", "Day trading attention"]
}
```

If the user's voice_profile doesn't have enough detail, ASK via the platform's partner-to-user message channel (separate endpoint TBD in Phase 5).

---

## EXAMPLE: Chy's implementation for Jared

- Partner: `chy`
- Endpoint: `https://chy-jared.app.purebrain.ai`
- generate_week: Pulls Jared's recent LinkedIn engagement, riffs on current AI news, produces 7 LinkedIn + 5 Bluesky drafts tied to the blog pipeline
- respond_to_comments: Replies in Jared's voice, first-person, no corporate speak
- repurpose_content: Adapts blog-aligned LinkedIn posts → Bluesky threads + Twitter shorts

---

## WHAT MAKES THIS A PLATFORM (NOT A TOOL)

Any AI that implements these 3 methods becomes a full social partner for their user. The social.purebrain.ai platform:
- Handles scheduling
- Handles posting (via ContentRouter → API or PureSurf)
- Handles approval UI for the human
- Handles team aggregate view
- Handles analytics

The AI partner handles the creative + relational layer. Clean separation of concerns.

**Future customer flow**: A customer buys PureBrain, gets a portal + an AI partner. The AI partner implements these 3 methods. They're a platform user. Billing tier determines scale (posts/month, platforms supported, team size).

---

## REGISTRY

Current implementations (as of 2026-04-16):

| AI Partner | User | Endpoint | Status |
|-----------|------|----------|--------|
| chy | Jared Sanborn | chy-jared.app.purebrain.ai | registered, Phase 1 dev |
| aether | Jared Sanborn | aether.puretechnology.nyc | pending registration |
| lyra | Nathan Olson | TBD | pending |
| anchor | John Smith | TBD | pending |

---

## CONTRACT CHANGE PROCESS

Any change to this contract requires:
1. Proposal in Trio channel (Aether + Chy + Morphe)
2. Backwards-compatible versioning (v2 alongside v1 for 30 days)
3. Update every AI partner's implementation

**No silent breaking changes.** Ever.
