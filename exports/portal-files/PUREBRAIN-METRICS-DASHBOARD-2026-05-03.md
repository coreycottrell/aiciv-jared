# PureBrain Metrics Dashboard — 2026-05-03

**Owner**: data-scientist (BOOP: purebrain-metrics-boop)
**Scope**: conversations · payments · assessment/seed completions
**Window**: rolling 24h / 7d / 30d / all-time

---

## 🟢 Headline (last 7 days)
- **Conversations**: 563
- **Real payments**: 2 paid customers / **$648.00**
- **Seed completions (real)**: 0 — *gap signal: 7 paid in 30d, only 7 seeded; 0 in 7d means seed pipeline went cold*
- **24h activity**: 0 payments, 0 seeds, 64 conversations (only 1 unique client IP — logging anomaly worth investigating)

---

## 1. Conversations (purebrain.ai/chat)
Source: `logs/purebrain_web_conversations.jsonl` (3,720 records)

| Window | Conversations | Avg msgs/conv |
|---|---|---|
| 24h | 64 | 1.4 |
| 7d  | 563 | — |
| 30d | 2,159 | — |
| all-time | 3,720 | 4.1 |

- Unique sessions all-time: **2,622**
- Unique client IPs (24h): **1** ⚠️ (likely IP forwarding/logging bug — investigate)
- Total messages all-time: 15,139

---

## 2. Payments (production, real $ only)
Source: `logs/purebrain_payments.jsonl` (62 events: 47 real, 15 test/zero)

| Window | Count | Revenue |
|---|---|---|
| 24h | 0 | $0.00 |
| 7d  | 2 | $648.00 |
| 30d | 7 | $1,169.50 |
| all-time | 47 | **$11,095.00** |

**By tier (all-time real $):**
- Awakened: 37 × **$3,605.00** (volume tier)
- Unified: 5 × **$4,995.00** (highest revenue concentration)
- Partnered: 5 × **$2,495.00**

ARPU (all-time real): **$236.06**.
Sandbox/pay-test events (last 7d): 0 — pay-test page is quiet.

---

## 3. Assessment → Seed Completions
Source: `logs/seed_events.jsonl` (26 events: 11 real, 15 sandbox)

| Window | Real seeds |
|---|---|
| 24h | 0 |
| 7d  | 0 |
| 30d | 7 |
| all-time | 11 |

**AI names birthed (real)**: Keen ×4, Charlotte, PURE BRAIN, Alfred ×2, Nexus, Vira (10 distinct partnerships).

**Tier mix of real seeds**: Awakened 6 · Partnered 4 · Unified 1.
Seed addendum events: 18 (consent/upgrade flows).

---

## 4. Onboarding emails
Source: `logs/purebrain_emails.jsonl` (37 events)

- 24h / 7d / 30d: **0 / 0 / 0** ⚠️
- Event mix: neural_feed_email_sent ×33, welcome_email_sent ×2, setup_complete_email_sent ×2
- Only 4/37 events had `ai_name` populated — **drift from constitutional rule that AI name MUST populate before send**

---

## 5. Top-of-funnel
- Investor leads (30d): 5 · all-time: 6 (per `purebrain_investor_leads.jsonl`)
- Guide unlocks (all-time): 1 (per `purebrain_guide_unlocks.jsonl`)

---

## 6. Funnel (last 30 days)

```
Conversations  2,159
                  │
                  ▼  0.32% (raw, IP-deduped will be higher)
Payments           7
                  │
                  ▼  100%
Seed completions   7
```

- Conv→Pay rate (raw) = **0.32%** — low but uses IP-bug-affected conversation count.
- Pay→Seed parity (30d) = **7/7 = 100%** ✅ — every paid customer in window got seeded.

---

## 🔍 Signals worth routing

1. **Unique-IP logging anomaly** (64 conversations / 1 IP in 24h) — likely Cloudflare X-Forwarded-For not propagating. Route → **ST# (purebrain web infra)**.
2. **Onboarding email log empty 30d** while 7 seeds shipped — `purebrain_emails.jsonl` is no longer the source of truth. Route → **ST#** to confirm logging path.
3. **24h dead zone** (0 payments, 0 seeds, only 1 IP traffic) — sanity check production webhook + payment pages still firing. Route → **ST# health check**.
4. **Seed-7d = 0 vs Pay-7d = 2** — those 2 paid this week haven't seeded yet. Route → **OP#** to verify seeds are in flight, not stuck.

---

## File pointers
- Raw payments: `logs/purebrain_payments.jsonl`
- Raw conversations: `logs/purebrain_web_conversations.jsonl`
- Seeds: `logs/seed_events.jsonl`
- Onboarding: `logs/purebrain_emails.jsonl`
- UUID payer map: `logs/payer_emails_by_uuid.json` (20 UUIDs)

