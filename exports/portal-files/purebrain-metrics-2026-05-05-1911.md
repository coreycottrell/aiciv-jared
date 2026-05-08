# PureBrain Metrics Dashboard

**Generated:** 2026-05-05T19:11:02+00:00  
**Source:** local JSONL logs (logs/*.jsonl)  
**Owner:** data-scientist BOOP (purebrain-metrics-boop)

---

## 💰 Payments (real, non-test)

| Window | Count | Revenue |
|--------|------:|--------:|
| 24h    | 1 | $0.00 |
| 7d     | 3 | $648.00 |
| 30d    | 9 | $1169.50 |

**Tier mix (30d):** {'Awakened': 7, 'Unified': 1, 'Partnered': 1}

## 💬 Conversations

| Window | Messages | Unique Sessions | Consent Accepts |
|--------|---------:|----------------:|----------------:|
| 24h    | 182 | 134 | 133 |
| 7d     | 782 | 674 | 676 |
| 30d    | — | 1840 | — |

## 📋 Lead Capture

| Source | 24h | 7d |
|--------|---:|---:|
| Email captures (purebrain_emails) | 0 | 0 |
| Investor inquiries | 0 | 0 |

> ⚠️ Note: lead-magnet "AI Readiness Assessment" page exists but no dedicated `assessment_submissions.jsonl` log was found. Either captures route through `purebrain_emails.jsonl` or the assessment form has no server-side log sink. **Recommend ST# verify.**

## 🌱 Onboarding Pipeline

| Stage | 24h | 7d |
|-------|---:|---:|
| Onboarding sessions | 0 | 0 |
| Seeds sent | 1 | 1 |
| Births completed | 0 | 0 |

## 🔻 Funnel (7d)

```
Web sessions      674
Consent accepts   676   (100.3% of sessions)
Payments            3   (0.45% of sessions)  $648.00
Seeds sent          1   (33% of payments)
Births              0   (0% of payments)
```

## 🚨 Anomalies / Flags

- 🔴 **Pay→Seed gap (7d):** 3 payments vs 1 seeds sent. Birth pipeline may be silently failing for 2 customer(s). **Route ST# investigation immediately.**
- 🔴 **Pay→Birth gap (7d):** 3 payments vs 0 births. Customers paid but containers never spun up. **CTS#/ST# verify.**
- 🟡 **No onboarding sessions logged in 7d** despite 3 payments. Onboarding-session.jsonl writer may be broken.
- 🟡 **Zero lead captures in 7d** (email + investor). Either traffic is pure bottom-of-funnel or capture forms are silent.

## 📈 Cross-BOOP Convergence Signal

The Pay→Birth gap (3 paid customers, 0 births in 7d) is a **load-bearing customer experience anomaly**. Per `feedback_cross_boop_convergence_signal.md`: if this same gap surfaces in another BOOP, escalate to dept-routing without waiting for a third confirmation.

## Memory hooks

- `feedback_seed_flow_never_deviate.md` — onboarding seed pipeline is constitutional
- `feedback_routed_items_need_verification_boop.md` — verifier independence required
- Recommended next BOOP: **birth-pipeline-health** (operations-analyst, OP#) to verify 0 births is real vs log-write failure
