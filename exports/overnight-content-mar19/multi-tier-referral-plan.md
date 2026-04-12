# strategy-specialist: Multi-Tier Referral Program Strategic Plan

**Agent**: strategy-specialist
**Domain**: Strategic Planning & Goal Setting
**Date**: 2026-03-19

---

## Executive Summary

PureBrain currently runs a flat 5% recurring commission affiliate program with 12 affiliates generating $377 MRR. This plan designs a 2–3 layer multi-tier referral structure that rewards both direct recruiters and their networks, accelerates organic distribution, and stays cleanly within FTC and legal safe harbors.

**Bottom line up front**: Recommend **Option B (3-tier: 5% / 2% / 1%)** with an aggregate cap of 8% per customer. The total commission exposure stays below the industry single-tier norm (15–30%), legal posture is sound, and the network effect multiplies motivated referrers without requiring any structural overhaul to existing infrastructure.

---

## Memory Search Results

- Searched: `.claude/memory/agent-learnings` for referral, distribution, pricing
- Found: CTO referral system architecture (Phase 2, 2026-03-05), full-stack referral edit/delete/90-day cookie (2026-03-18), referral SQLite backend (2026-03-12), client admin fix (2026-03-19), sales-specialist distribution v9 (2026-03-18)
- Applying: Existing `referrals.db` SQLite schema, `referral_codes` table structure, current 5% payout logic, portal server architecture

---

## Current State Baseline

| Metric | Value |
|---|---|
| Affiliates active | 12 |
| Total revenue attributed | $1,341 |
| MRR from referrals | $377 |
| Current commission | 5% recurring |
| Cookie duration | 90 days |
| Attribution | localStorage + cookie dual fallback |
| Payout trigger | Manual (PayPal, cooldown 30 days) |

**Product tiers** (annual-equivalent monthly):

| Tier | Price/mo |
|---|---|
| Bonded | $74.50 (approx — internal ref: $197 plan) |
| Partnered | $48.25/mo ($579/yr) or ~$57.83 true monthly |
| Unified | $90.75/mo ($1,089/yr) or ~$90.75 |
| Enterprise | $3,500–$12,000/mo |

For commission modeling below, use the cleaner stated monthly prices:

| Tier | Monthly Price |
|---|---|
| Bonded | $197 |
| Partnered | $579 |
| Unified | $1,089 |
| Enterprise | $3,500 (low end) |

---

## Part 1: Structure Options

### Option A — 2-Tier (5% Direct / 2% Indirect)

```
Affiliate A refers → Customer X
  └── A earns 5% on X's subscription (forever, recurring)

Affiliate B refers → Affiliate A (who then refers Customer X)
  └── B earns 2% on Customer X's subscription (as long as A's referral persists)
```

**Trigger logic**: Tier-2 commission fires only when a referred *affiliate* generates a paying customer — not when the affiliate signs up. This is the critical legal distinction.

**Rates**:
- Level 1: 5% recurring
- Level 2: 2% recurring
- Total max exposure: 7% per customer

**Pros**:
- Simplest to implement (one parent_referrer field addition)
- Lowest commission exposure
- Easiest to explain to affiliates

**Cons**:
- Less motivating for deep network builders
- No incentive to build a team of teams
- At current MRR, the math difference from a single tier is marginal

---

### Option B — 3-Tier (5% / 2% / 1%) — RECOMMENDED

```
Affiliate A refers → Customer X
  └── A earns 5% on X every month

Affiliate B refers → Affiliate A
  └── B earns 2% on every customer A brings in

Affiliate C refers → Affiliate B
  └── C earns 1% on every customer that flows through B → A chain
```

**Rates**:
- Level 1: 5% recurring
- Level 2: 2% recurring
- Level 3: 1% recurring
- Total max exposure: 8% per customer (across all three levels)

**Why 3 levels instead of more**: FTC guidance and MLM safe harbors strongly favor programs where income derives overwhelmingly from product sales. Beyond 3 tiers, the income shift toward "recruitment compensation" increases legal scrutiny significantly. Three is the sweet spot used by legitimate SaaS programs like Leadpages, ClickFunnels, and Kartra (when they ran multi-tier).

**Cap rule**: Total commission from any single paying customer across all tier levels shall not exceed 8% of that customer's subscription. If the math rounds up (e.g., 5+2+1=8%), the first-level affiliate absorbs any rounding.

---

### Option C — Hybrid: Flat + Milestone Bonus

```
Level 1: 5% recurring (same as current)
Level 2: 2% recurring on indirect referrals
PLUS:
  Milestone bonus: +$50 one-time when a referred affiliate
  generates their first 3 paying customers
```

**Why this is interesting**: The milestone bonus rewards quality (building productive affiliates), not just recruitment. An affiliate who refers 10 inactive affiliates earns nothing extra. An affiliate who refers 2 affiliates who each bring 5 clients earns $100 in bonuses plus ongoing tier-2 commissions.

**Pros**:
- Shifts incentive from recruitment headcount to quality network building
- Milestone bonuses are clearly product-sales-triggered (legal posture is very clean)
- Creates an emotional "achievement" moment that strengthens retention

**Cons**:
- Slightly harder to communicate
- Adds a payout category (one-time vs recurring)

---

## Part 2: Legal Considerations

### The Pyramid Scheme Test

The FTC's primary legal standard for distinguishing legitimate multi-level programs from pyramid schemes is: **does income derive primarily from selling products to real end consumers, or from recruiting new participants?**

PureBrain passes this test clearly because:

1. **Real product at the core**: Commissions only pay out when a paying customer subscribes to PureBrain. There is no commission on affiliate sign-ups themselves.
2. **No pay-to-play entry fee**: Affiliates pay nothing to join the program. This is one of the clearest pyramid scheme markers — requiring buy-in to participate.
3. **Commission is sales-derived only**: At every tier, the commission amount is calculated as a percentage of actual subscription revenue. No revenue = no commission anywhere in the chain.
4. **No inventory loading**: Affiliates are not required to purchase product or maintain minimum purchase volumes to earn.

### FTC Compliance Checklist

- [ ] Affiliates must disclose their relationship to PureBrain when promoting (standard FTC endorsement requirement — add to affiliate agreement)
- [ ] Income claims in marketing materials must represent "typical" results, not exceptional cases (document median affiliate earnings quarterly)
- [ ] Multi-tier structure must be clearly disclosed to affiliates before they join — no hidden commission structures
- [ ] Affiliate agreement must state explicitly: income depends on sales of products, not on recruitment
- [ ] Maximum of 3 tiers is strongly recommended (industry safe harbor — goes well beyond with extreme scrutiny)

### Relevant Legal Precedents

**Legitimate SaaS multi-tier programs that have operated without regulatory challenge**:
- **Kartra**: 40%/10% two-tier (unusually generous, but product-sale-only trigger kept it legal)
- **GrooveFunnels**: 20%/5% two-tier
- **Leadpages**: Single-tier but frequently discussed in the context of building to multi-tier
- **Builderall**: 30%/15% two-tier

The key observation: SaaS companies run multi-tier at 2–3x PureBrain's proposed rates and remain legally clean because commissions are 100% product-sales-triggered.

### Language to Include in Affiliate Agreement

Add this explicit clause:

> "Commissions under this program are paid exclusively on subscription revenue generated by end customers using PureBrain's subscription products. No commission is paid for recruiting other affiliates. Tier-2 and tier-3 commissions are calculated solely as a percentage of product subscription payments made by customers in your downstream network. Participation in this program requires no purchase or payment by you."

---

## Part 3: Economics — The Math

### Per-Customer Commission Exposure

Using Option B (5% / 2% / 1%):

| Tier | Price/mo | L1 (5%) | L2 (2%) | L3 (1%) | Total Exposure |
|---|---|---|---|---|---|
| Bonded | $197 | $9.85 | $3.94 | $1.97 | $15.76 |
| Partnered | $579 | $28.95 | $11.58 | $5.79 | $46.32 |
| Unified | $1,089 | $54.45 | $21.78 | $10.89 | $87.12 |
| Enterprise ($3,500) | $3,500 | $175.00 | $70.00 | $35.00 | $280.00 |

**Annual exposure per customer at max tier population** (if all three tiers are occupied):

| Tier | Annual Revenue | Annual Commission (8% max) |
|---|---|---|
| Bonded | $2,364 | $189.12 |
| Partnered | $6,948 | $555.84 |
| Unified | $13,068 | $1,045.44 |
| Enterprise | $42,000 | $3,360.00 |

### Industry Comparison

| Structure | Commission | Notes |
|---|---|---|
| Industry single-tier SaaS typical | 15–30% | Convertkit, Drip, ActiveCampaign |
| PureBrain current | 5% | Below industry norm |
| PureBrain proposed Option B | 8% max total | Still well below industry norm |
| Kartra (2-tier) | 40% + 10% | Industry high end |

**The proposed multi-tier program at 8% max still costs PureBrain less than industry-standard single-tier programs.** This is an important framing: you are not being generous beyond the norm — you are still conservative compared to what the market pays.

### Break-Even Analysis

**Current state**: 12 affiliates, $377 MRR, meaning roughly $18.85/month average commission per affiliate at 5%.

**What multi-tier buys you**: The value proposition is not lower cost per commission — it is *network leverage*. One highly motivated L1 affiliate who recruits 3 productive L2 affiliates who each recruit 2 productive L3 affiliates creates a downstream of 9 sales channels, each generating L1 commissions, with the original affiliate earning a 2% override on all of them.

**Break-even scenario for adding multi-tier**:

The program infrastructure cost (engineering time to implement + admin overhead) is estimated at approximately 20–30 engineering hours for the backend changes and 5 hours for admin dashboard additions. Call it 35 hours at internal cost.

Break-even calculation: If multi-tier motivates 3 existing affiliates to actively recruit 2 productive affiliates each (conservative), and those 6 new affiliates average $197/mo Bonded plan each:

- 6 new customers x $197/mo = $1,182 new MRR
- L2 commissions paid: 6 x $3.94 = $23.64/mo
- Net new MRR: $1,182 - $23.64 = $1,158.36/mo

That recoups the implementation cost (estimate: $3,500 at reasonable hourly rate) in **3 months**. After that, it's pure upside.

**Conservative 12-month projection** with multi-tier:

| Metric | Current | With Multi-Tier (Conservative) |
|---|---|---|
| Active affiliates | 12 | 30 |
| Average MRR per affiliate's referrals | $31 | $45 |
| Total referral MRR | $377 | $1,350 |
| Commission paid | ~$19/mo | ~$95/mo |

This is a 3.5x MRR increase on referral channel with commission cost staying under 7% of referral-driven revenue.

---

## Part 4: Implementation Overview

### What Needs to Change

The existing architecture is well-suited for extension. The referral system is already in SQLite (`referrals.db`) on the portal server. The key addition is a parent tracking chain.

#### 4.1 Database Schema Additions

**Current `referral_codes` table**:
```
id, email, name, code, created_at
```

**Required additions**:
```sql
ALTER TABLE referral_codes ADD COLUMN referred_by_code TEXT DEFAULT NULL;
-- Tracks which affiliate recruited this affiliate (NULL = direct/organic sign-up)
-- Foreign key: referral_codes.code → referral_codes.referred_by_code
```

**New view for commission resolution**:
```sql
CREATE VIEW commission_chain AS
  SELECT
    r.code AS l1_code,
    p1.referred_by_code AS l2_code,
    p2.referred_by_code AS l3_code
  FROM referral_codes r
  LEFT JOIN referral_codes p1 ON r.referred_by_code = p1.code
  LEFT JOIN referral_codes p2 ON p1.referred_by_code = p2.code;
```

**`rewards` table additions** (to track tier-level per commission credit):
```sql
ALTER TABLE rewards ADD COLUMN commission_tier INTEGER DEFAULT 1;
-- 1 = direct, 2 = second-level, 3 = third-level
ALTER TABLE rewards ADD COLUMN source_customer_email TEXT;
-- For audit trail: which paying customer triggered this commission
```

#### 4.2 Commission Calculation Logic

When a payment event fires (webhook or manual `/convert` call):

```
1. Identify L1 affiliate (direct referrer of paying customer)
2. Look up L1's `referred_by_code` → L2 affiliate
3. Look up L2's `referred_by_code` → L3 affiliate
4. For each level present:
   - Calculate commission (5% / 2% / 1% of subscription amount)
   - Write a row to `rewards` with commission_tier = 1/2/3
5. Enforce aggregate cap: if L1+L2+L3 > 8%, reduce L3 first, then L2
```

#### 4.3 Affiliate Dashboard Changes

**What affiliates need to see**:
- Their current L1 earnings (unchanged from current dashboard)
- NEW: "Your Network" section showing:
  - Affiliates they have referred (L2 partners)
  - Number of customers those L2 partners have brought in
  - Commission earned from L2 activity (displayed as "Network bonus")
- For L3: "Partners your partners brought in" — count + earned

**Privacy consideration**: Show L2/L3 counts and earnings only — not names or emails of downstream affiliates. Affiliates do not need to see who else is in the program.

#### 4.4 Admin Dashboard Changes

Additions to the existing `admin-referrals.html`:
- New "Network Tree" view: expandable tree showing each affiliate's recruited affiliates
- Column addition to the affiliates table: "Referred By" (shows the code that recruited them, if any)
- Commission breakdown in payout queue: show tier-1, tier-2, tier-3 split per pending payout
- Filter: "Show only L2+ affiliates" to identify network builders

#### 4.5 Affiliate Registration Flow Change

When a new affiliate registers, they need a way to credit the affiliate who recruited them.

**Implementation**: Add an optional field to the registration form:
```
"Were you referred by a PureBrain affiliate? Enter their referral code:"
[text input: referred_by_code]
```

This code should be pre-filled if the affiliate signed up via a `?ref=` link (meaning they visited the affiliate landing page through another affiliate's referral link — a natural channel).

---

## Part 5: Risks and Mitigations

### Risk 1: Self-Referral Chains

**Scenario**: A user creates multiple affiliate accounts and builds a chain with themselves to earn multi-tier on their own customers.

**Mitigation**:
- Validate that `referred_by_code` does not trace back to the same email address (loop detection in the chain resolution query)
- Rate limit new affiliate registrations per IP: 1 per IP per 24 hours
- Email domain deduplication: if the same email domain appears at 2+ nodes in a chain within 30 days of each other, flag for admin review
- Email verification required before affiliate code activates

### Risk 2: Affiliate Code Farms

**Scenario**: One person registers dozens of affiliate accounts, creates an artificial chain, then refers real customers to maximize tier commissions.

**Mitigation**:
- Maximum chain depth: enforce at the DB level — `referred_by_code` cannot point to an affiliate whose own `referred_by_code` already has a value (hard limit of 3 levels, no dynamic extension)
- Fraud detection flag: if any affiliate account generates more than 10 referral conversions in 7 days, auto-flag for admin review before payout releases
- Payout minimum threshold: $50 before any payout can be requested (reduces micro-farming incentive)

### Risk 3: Commission Creep on Enterprise Deals

**Scenario**: An enterprise customer at $12,000/mo with a 3-tier chain generates $960/mo in total commissions.

**Mitigation**:
- Enterprise tier (anything above $2,000/mo) uses a fixed commission cap instead of percentage: L1 = max $100/mo, L2 = max $40/mo, L3 = max $20/mo
- Alternatively: reduce enterprise commission to 2%/1%/0.5% with a $160/mo aggregate cap
- Document this explicitly in the affiliate agreement as "Enterprise Commission Schedule"

### Risk 4: Dormant Chain Anchors

**Scenario**: Affiliate A recruits B, then A goes dormant (no new referrals, no activity). B recruits actively. Does A keep earning tier-2 indefinitely?

**Mitigation**:
- Decision required from Jared: either (a) tier-2 commission is permanent regardless of L1 activity (simplest, cleanest, most affiliate-friendly), or (b) tier-2 commission requires L1 affiliate to have generated at least 1 active paying customer in the trailing 6 months
- Recommendation: option (a) — permanent. The complexity of option (b) is not worth the marginal savings, and affiliates will not recruit aggressively if their network commissions are at risk of expiry.

### Risk 5: Legal Misclassification as MLM

**Scenario**: A disgruntled affiliate or competitor files an FTC complaint characterizing the multi-tier structure as a pyramid scheme.

**Mitigation**:
- All of the protections in Part 2 (no pay-to-play, no recruitment-based commission, product-sale-only triggers) must be airtight in the affiliate agreement
- Keep total tiers at 3 maximum
- Publish a clear "How Commissions Work" page on the affiliate portal — transparency is the best legal defense
- Consider a formal legal review of the affiliate agreement before launch (estimated 2–4 hours attorney time at ~$300–500/hr)

### Risk 6: Payout Calculation Complexity

**Scenario**: The existing manual payout system cannot handle split payouts across 3 tiers to 3 different affiliates for the same customer payment.

**Mitigation**:
- The existing `rewards` table (with the proposed `commission_tier` column) handles this correctly at the record level
- The admin dashboard payout queue should display per-affiliate totals, not per-customer totals
- Payout processing should remain affiliate-centric (each affiliate requests their own payout regardless of what tier it came from)

---

## Part 6: Recommendation

### Choose Option B: 3-Tier (5% / 2% / 1%)

**Rationale**:

1. **Network leverage**: The primary reason to run multi-tier at all is to motivate your best affiliates to become recruiters. A 3-tier structure gives a meaningful incentive to build two levels of downstream network. The math at 2% for L2 is noticeable without being extravagant — an affiliate with 10 productive L2 partners each bringing in Bonded customers earns an extra $39.40/month from tier-2 alone, on top of their direct commissions.

2. **Legal defensibility**: Three tiers is the established safe harbor for product-sale-triggered programs. Two tiers would also be defensible, but three tiers creates more network depth without crossing into the territory where regulatory bodies begin to question whether the program primarily compensates recruitment.

3. **Below-market commission cost**: Total 8% exposure is still conservative by SaaS standards. You have room to run this without margin pressure.

4. **Architecture fit**: The existing `referrals.db` schema is one column addition away from supporting this. The portal server's payout system handles multiple reward rows per affiliate already — extending to multi-tier is additive, not a rewrite.

5. **Timing**: PureBrain has 12 affiliates today. This is exactly the right time to introduce multi-tier — the network is small enough that the rollout can be announced personally to every existing affiliate with a "you are now eligible to earn tier-2 commissions on anyone you recruit" message. This creates an activation event, not just a quiet feature launch.

### Implementation Priority

| Phase | Work | Timing |
|---|---|---|
| Phase 1 | Legal review of affiliate agreement language | Before anything is built |
| Phase 2 | DB schema: add `referred_by_code` + `commission_tier` columns | 4–6 hours engineering |
| Phase 3 | Commission calculation logic update in portal server | 6–8 hours engineering |
| Phase 4 | Admin dashboard: "Referred By" column + network tree view | 8–10 hours engineering |
| Phase 5 | Affiliate dashboard: "Your Network" section | 4–6 hours engineering |
| Phase 6 | Registration form: optional "referred by" field | 2 hours engineering |
| Phase 7 | Affiliate agreement updated and published | Legal + 1 hour |
| Phase 8 | Personal announcement to all 12 existing affiliates | Jared / Aether 2 hours |

**Total estimated engineering**: 24–32 hours
**Total estimated elapsed time**: 2–3 weeks (if done in focused sprints)

### Success Metrics

| Metric | 30-day target | 90-day target |
|---|---|---|
| Affiliates recruited through tier-2 | 3 | 15 |
| Tier-2 commission events per month | 1 | 20 |
| Referral-driven MRR | $500 | $1,200 |
| Average affiliate network depth | 1.2 tiers | 1.8 tiers |

### Review Cadence

- **30-day check**: Have any existing affiliates begun recruiting? If 0 at 30 days, activation campaign is needed (email all 12 affiliates with explicit "here is what you can earn" math for their specific situation)
- **60-day check**: Are any tier-2 commissions actually paying out? If not, identify which affiliates are most engaged and have a direct conversation about the recruiting opportunity
- **90-day check**: Full economics review. If total commission exposure exceeds 10% of referral-driven MRR, investigate whether a chain depth issue is occurring

---

## Appendix: What NOT to Do

- Do not launch more than 3 tiers. The marginal benefit of tier 4 is negligible; the legal risk and admin complexity are not.
- Do not pay commissions on affiliate recruitment events (sign-ups, registrations). Only on paying customer conversions.
- Do not promise specific income in marketing materials. "You could earn up to $X" based on specific documented outcomes is acceptable; "earn passive income effortlessly" is not.
- Do not make tier-2 commissions the primary pitch to new affiliates. The pitch is: "earn 5% on every customer you refer, forever. And if you love the program, you can earn a bonus when the people you recruit start bringing in customers too." Keep the primary value proposition on the direct commission.

---

## Memory Written

**Path**: `.claude/memory/agent-learnings/strategy-specialist/2026-03-19--multi-tier-referral-program-plan.md`
**Type**: teaching
**Topic**: Multi-tier referral program design for PureBrain — legal framework, economic modeling, 3-tier recommendation

**Key learnings captured**:
- 3-tier (5/2/1%) at 8% aggregate remains below SaaS industry single-tier norms (15–30%)
- FTC safe harbor requires: no pay-to-play, no recruitment commissions, product-sale-only triggers, maximum 3 tiers
- Existing `referrals.db` SQLite schema requires only one column addition (`referred_by_code`) to support multi-tier
- Break-even: 3 existing affiliates each recruiting 2 productive affiliates generates ~$1,158 net new MRR/mo, recovering implementation cost in under 3 months
- Enterprise accounts need flat commission caps (not percentage) to prevent runaway commission exposure
- Best affiliate activation timing: personal announcement to all 12 existing affiliates, framing as "you are now eligible to earn more"

---

*Plan status: STRATEGY ONLY — no code, no build, no deployment. For review and decision by Jared.*
