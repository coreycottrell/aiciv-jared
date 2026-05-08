# PureBrain Business Metrics — 2026-04-29

**Generated**: 2026-04-29T18:37 UTC by data-scientist BOOP
**Sources**: `logs/purebrain_web_conversations.jsonl`, `logs/purebrain_payments.jsonl`, `logs/purebrain_guide_unlocks.jsonl`, `logs/birth_completions.jsonl`, `logs/seed_events.jsonl`, `logs/onboarding-session.jsonl`

## Headline Numbers
| Metric | All-time | 30d | 7d | 24h |
|---|---|---|---|---|
| Conversation events | 3,191 | 2,255 | 34 | 34 |
| Unique sessions | 2,150 | — | — | — |
| Verified payments | 60 | 22 | 0 | 0 |
| Revenue | $10,447.00 | $2,025.00 | $0 | $0 |
| Births complete | 10 | 0 | 0 | 0 |
| Seed events | 26 | 15 | 0 | 0 |
| Guide unlocks | 1 | 0 | 0 | 0 |

## Funnel
- Consent → Payment: **3.0%** (60 / 1,999)
- Payment → Birth: **16.7%** (10 / 60)

## Tier Mix (all-time, verified)
- Awakened: 44 (73%)
- Partnered: 9 (15%)
- Unified: 6 (10%)
- Unknown: 1

## Anomalies (require routing)

1. **Zero payments in last 7 days** — last verified payment was **2026-04-11**. 18-day gap. Route to SD# (Sales) + AF# (Finance).
2. **Birth-to-payment gap: 50 paid customers without `birth_complete` event** (16.7% completion rate). Either tracking is broken or 83% of paid users never birthed an AI. Route to ST# (Tech) + CTS# (Client Tech Support) for verification.
3. **Guide unlock instrumentation broken** — 1 event ever, last on 2026-03-11 from `test@example.com`. Lead-magnet capture is dead. Route to MA# (Marketing).
4. **Onboarding-session events: 43 all-time, 0 in last 30 days** — instrumentation likely moved/broken. Route to ST#.
5. **Consent flow active** (1,999 events, 34 in last 24h) — top of funnel is healthy. Conversion to payment is the choke point.

## Recommended Verifier Routing (per `feedback_verifier_independence_audit_separation.md`)
- Independent verifier (OP#) should confirm whether birth-to-payment gap is **tracking** or **product** — not the same agent that flags it.
