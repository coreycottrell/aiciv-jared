# BOOP: Business Model Review — 2026-05-02

**Agent**: strategy-specialist
**Window analyzed**: Feb–Apr 2026 PayPal verification log + 777 money_map + payer UUID pipeline

---

## 🔴 HEADLINE: April revenue collapsed 88% MoM

| Month | Txns | Revenue | Avg Order |
|-------|------|---------|-----------|
| Feb 2026 | 1 | $0 | comp |
| Mar 2026 | 45 | $9,456 | $210 |
| **Apr 2026** | **15** | **$1,140** | **$76** |

That is a 67% drop in volume and an 88% drop in revenue in one month. Avg order value also collapsed from $210 → $76, meaning the mix shifted from premium tiers down to discounted Awakened.

**vs. The Number**: Monthly spend target $250k. April actual $1,140 = **0.46% of goal**. Finance score in 7Fs = 2/10.

---

## 🟡 PRICING IS LEAKING — 7 distinct price points active

| Price | Count | Notes |
|-------|-------|-------|
| $79.00 | 23 | Discounted Awakened (intended $149) |
| $0.00 | 15 | Comps / test / failed captures — **25% of all txns** |
| $149.00 | 9 | Awakened at sticker |
| $999.00 | 5 | Unified — premium tier holding |
| $499.00 | 4 | Partnered |
| $74.50 | 4 | 50% off Awakened |

**Strategy implications:**
1. **$0 transactions are 25% of the log.** Either captures are failing or comp policy has no gate. Both bleed cash.
2. **Three different "Awakened" prices** ($74.50, $79, $149) means no anchor — buyers see inconsistency and self-select the lowest signal.
3. **Premium pull-through is dying.** March: 7 Partnered + 5 Unified. April: 2 Partnered + 1 Unified. The high-margin tiers are evaporating.

Per memory: launch pricing ($149/$499/$999) is correct for our stage (sub-25 clients). The discount creep contradicts the locked policy.

---

## 🟡 ONBOARDING FUNNEL LEAK: payment ≠ activation

- **Paid events**: 61 total in log
- **Payer UUIDs in pipeline**: 20

Even after subtracting the 15 $0 events, that's 46 real payers vs 20 in the UUID-keyed payer email file. Half the payers may not have made it through to a seeded portal. This matches the chronic-issues memory (welcome-email flags, /insiders/ template rot fixed Apr 29, magic-link dependency).

**Action**: WTT# verify every paid PayPal event from April produced a delivered seed + active portal. Zero tolerance for payment-without-portal.

---

## 🟡 NO RETENTION VISIBILITY

`subscription_cancel`, `cancel`, `refund` events in payment log: **0**.

We cannot make pricing or conversion decisions without churn data. PayPal does emit `BILLING.SUBSCRIPTION.CANCELLED` and `BILLING.SUBSCRIPTION.SUSPENDED` webhooks — the agentmail-webhook worker should capture and log them.

**Action**: ST# add cancellation/refund event capture to the webhook + payments log.

---

## STRATEGIC RECOMMENDATIONS (delegate, do not execute)

| # | Recommendation | Owner | Priority |
|---|----------------|-------|----------|
| 1 | Audit the 15 $0 events — are these failed captures or unmetered comps? | AF# (finance) + ST# (engineering) | 🔴 |
| 2 | Lock single Awakened price ($149) — kill $74.50/$79 discount paths in payment pages | LC# review + ST# enforce | 🔴 |
| 3 | Verify every April paid PayPal event has a delivered seed + active portal | WTT# QA + CTS# remediation | 🔴 |
| 4 | Add `subscription_cancelled` / `refund` event capture to agentmail-webhook + payments log | ST# (1 day) | 🔴 |
| 5 | Diagnose premium tier collapse: why did Unified/Partnered fall off in April? Pricing page UX? Removed CTAs? | PD# + MA# joint review | 🟡 |
| 6 | April lead-flow audit: is the LinkedIn/Bluesky/blog top-of-funnel still feeding pricing pages? | MA# (CMO) | 🟡 |
| 7 | Set monthly conversion target with a published trajectory toward $250k/mo (today: $1.1k = 0.46%) | OP# (planning) + AF# | 🟢 |

---

## DEPT ROUTING (Aether to dispatch)

- **AF#** + **ST#** → Recs 1, 4 (financial reconciliation + webhook capture)
- **LC#** + **ST#** → Rec 2 (price enforcement, but compliant with FROZEN investor codes constitutional rule)
- **WTT#** + **CTS#** → Rec 3 (paid→portal verification)
- **PD#** + **MA#** → Recs 5, 6 (premium tier + funnel diagnostics)
- **OP#** + **AF#** → Rec 7 (planning trajectory)

Verification BOOP (different owner — operations-analyst) should re-probe in 7 days that recs 1–4 closed, not just routed.

---

**Bottom line**: April was not a slow month — it was a structural break. Pricing is fragmented, premium tiers collapsed, $0 transactions are 25% of the log, and we have no churn visibility. Fix the leaks before the next push, or any new top-of-funnel will pour through holes.
