# cto: Referral Payout System Research

**Agent**: cto
**Domain**: Technology Strategy & Vision
**Date**: 2026-03-06

---

## Memory Search Results

- Searched: `.claude/memory/agent-learnings/cto/` for referral, payout, paypal, stripe
- Found: `2026-03-05--referral-system-phase2-architecture.md` — Phase 2 is deployed with reward ledger, status fields (`pending | approved | paid`), and payout logic explicitly deferred to Phase 3
- Found: `2026-02-23--paypal-client-side-integration-patterns.md` — PayPal SDK integration security patterns already known
- Found: `2026-03-04--paypal-custom-buttons-sandbox3-routing.md` — Live PayPal integration already running on purebrain.ai
- **Applying**: Phase 2 ledger schema is payout-ready. We own the data model. This is a Phase 3 implementation question.

---

## Executive Summary

The PureBrain referral system Phase 2 already has the data foundation: a `wp_pb_reward_ledger` table with `status ENUM (pending | approved | paid)` and `amount` fields. The infrastructure is payout-ready.

**Recommended approach**: PayPal Payouts API + admin-initiated batch processing, with a user-facing withdrawal request button in the portal panel.

This is the lowest-friction path for a WordPress + FastAPI stack that already has PayPal live. It avoids KYC complexity, keeps the sender in control, and costs $0.25/domestic transaction — the cheapest credible option.

---

## Option Comparison Table

| Option | Cost per Transaction | Setup Complexity | Time to Live | Recipient Requirement | Control |
|--------|---------------------|------------------|--------------|----------------------|---------|
| **PayPal Payouts API** | $0.25 USD domestic; 2% intl (capped) | Medium — requires PayPal approval | 1–3 weeks (approval) + 1 week dev | PayPal account (email) | Sender initiates |
| **Stripe Connect (Custom)** | 0.25% capped at $25 per payout | High — KYC, onboarding, compliance | 3–6 weeks | Bank account (KYC required) | Full platform control |
| **Stripe Connect (Standard)** | 0.25% capped at $25 per payout | Medium — Stripe handles KYC | 2–4 weeks | Stripe account | Less control |
| **Wise Business API** | ~0.4% average; capped | Medium — business account required | 2–3 weeks | Wise account or bank | Good for intl |
| **Venmo** (manual) | $0 (manual) | None | Immediate | Venmo account | Fully manual |
| **Manual bank wire** | $15–$25/wire | None | Immediate | Bank account + routing | Fully manual |
| **AffiliateWP plugin** | $299/yr + PayPal fees | Low — WP plugin | Days | PayPal account | Admin initiates |
| **SliceWP plugin** | $169/yr + PayPal fees | Low — WP plugin | Days | PayPal account | Admin initiates |

---

## Option Deep-Dives

### Option 1: PayPal Payouts API (RECOMMENDED)

**What it is**: PayPal's official API for sending money to multiple recipients. The same PayPal infrastructure already running PureBrain payments.

**Fee structure**:
- US domestic: **$0.25 flat per payout** (sender pays, recipient gets full amount)
- International: **2% per payment** (capped by recipient country)
- No monthly fees; no minimum volume

**Requirements to unlock**:
1. PayPal Business account (already have this)
2. Apply via developer.paypal.com → My Account → Payouts → Enable
3. Provide business justification ("referral commission payouts to affiliates")
4. PayPal approves: instant for established accounts, or 5–15 business days for new

**How payouts work technically**:
- REST API: `POST https://api.paypal.com/v1/payments/payouts`
- Send by email address (recipient's PayPal) — no bank info needed
- Can batch up to 15,000 payments per call
- Funds come from your PayPal balance
- Recipient receives instantly to their PayPal balance

**Fit for PureBrain**:
- Jared already has a PayPal Business account (live payments are running)
- Approval is likely fast given existing transaction history
- The portal server (FastAPI) can call the Payouts API directly
- Alternatively, WordPress plugin can batch-pay from admin panel

**Limitations**:
- Payouts funded from PayPal balance only (must pre-fund)
- Some users may not have PayPal accounts
- API access requires manual approval (not self-serve)

---

### Option 2: Stripe Connect (Custom Accounts)

**What it is**: Stripe's marketplace infrastructure — users onboard as "connected accounts" and Stripe handles bank transfers.

**Fee structure**:
- 0.25% per payout, capped at $25
- Plus card processing fees if routing through Stripe charges

**Important update**: Stripe deprecated Express accounts. Current options are Standard or Custom.

**Custom accounts** give full control but require:
- KYC collection from each referral earner (name, DOB, SSN last 4, bank account)
- Handling Stripe's compliance requirements (identity verification)
- Stripe's Connect Onboarding UI integration

**Verdict for PureBrain**: Over-engineered for current scale. Custom accounts require significant compliance infrastructure. For small referral payouts, this is weeks of engineering for marginal benefit over PayPal.

**Better fit**: If PureBrain ever becomes a true marketplace (earners processing thousands/month), revisit Stripe Custom.

---

### Option 3: Wise Business API

**What it is**: Wise's API for international business transfers. Excellent FX rates, used widely for cross-border affiliate payouts.

**Fit**: Strong if referral earners are internationally distributed. For a US-heavy audience on PureBrain, this adds complexity without much gain over PayPal. Wise requires a Business account setup and API approval similar to PayPal.

**When to consider**: If more than 30% of referral earners are outside the US, add Wise as a second payout option alongside PayPal.

---

### Option 4: WordPress Affiliate Plugins (AffiliateWP / SliceWP)

**AffiliateWP**: $299/yr. Robust feature set, WooCommerce integration, PayPal payouts add-on. Designed for WP affiliate programs.

**SliceWP**: $169/yr. Simpler, lightweight. PayPal Payouts add-on available. Admin-initiated payout only (no user withdrawal request flow).

**The problem with both**: They replace the custom referral system already built and deployed in Phase 2. Migrating to a plugin would mean:
- Abandoning the `wp_pb_reward_ledger` schema
- Losing the portal proxy integration at `portal_server.py`
- Losing the custom `[pb_referral_dashboard]` shortcode already in production
- Paying recurring licensing costs for features we already built

**Verdict**: Do not switch to a plugin. The Phase 2 system is purpose-built for PureBrain and is already production-ready. Add payout capability to it instead.

---

### Option 5: Manual Payout (Bridge Approach)

**The simplest viable approach for launch**:
1. User clicks "Request Payout" in the portal panel
2. Portal logs the request to the WordPress plugin ledger (status: `pending`)
3. Jared gets a Telegram notification with the request details
4. Jared manually sends via PayPal (logged in to PayPal.com)
5. Admin marks the ledger entry as `paid`

**Cost**: $0 in infrastructure; time cost is Jared's
**Time to implement**: 1–2 days
**Best for**: First 10–20 payouts while awaiting PayPal Payouts API approval

---

## Recommended Approach: Phased Implementation

### Phase 3a — Manual Payout Bridge (Launch in Days)

Build the withdrawal request UX now. No API approval needed.

**What gets built**:
1. "Request Payout" button in the portal referral panel (visible when earnings >= $25 minimum threshold)
2. `POST /wp-json/pb-referral/v1/payout-request` endpoint in the WordPress plugin
3. Endpoint writes to `wp_pb_reward_ledger` with status `pending`, event_type `payout_request`
4. Sends Telegram notification to Jared with earner details
5. Admin dashboard shows pending payout requests
6. Jared pays manually via PayPal.com
7. Admin marks as `paid` via admin panel or REST call

**Why this first**:
- Real users can start withdrawing within days
- Validates demand before investing in API integration
- Builds the UI/UX pattern that Phase 3b inherits
- Zero risk (no automated money movement)

### Phase 3b — PayPal Payouts API (Fully Automated)

After API approval, swap the manual step for automated disbursement.

**What gets built**:
1. Apply for PayPal Payouts API access immediately (runs in parallel)
2. Portal server gets a `/admin/process-payouts` endpoint
3. Endpoint reads all `pending` ledger entries, batches them to PayPal Payouts API
4. PayPal sends funds to earner's PayPal account (by email)
5. On success, ledger entries updated to `paid` with PayPal batch ID
6. Telegram confirmation sent to Jared

**Required from earner**: Their PayPal email address (collect at payout request time)

---

## Implementation Outline (Phase 3a)

### 1. WordPress Plugin Addition (`purebrain-referral-system.php` v2.1.0)

```
New REST endpoint: POST /wp-json/pb-referral/v1/payout-request
  - Auth: X-WP-Nonce (same pattern as existing endpoints)
  - Body: { referral_code, paypal_email, amount_requested }
  - Validates: amount >= $25 minimum, pending balance exists
  - Writes: wp_pb_reward_ledger (event_type: payout_request, status: pending)
  - Sends: wp_mail() to jared@puretechnology.nyc with request details
  - Sends: Telegram via wp_remote_post() to tg_send endpoint
  - Returns: { ok: true, request_id: 123 }

New REST endpoint: POST /wp-json/pb-referral/v1/admin/mark-paid
  - Auth: WordPress admin capability check
  - Body: { ledger_id, paypal_transaction_id }
  - Updates: ledger status to 'paid', stores PayPal transaction ID
  - Sends: confirmation email to earner
```

### 2. Portal Panel Addition (`portal-pb-styled.html`)

In the referral panel, add below the earnings display:

```
[  Request Payout  ] button — visible when balance >= $25
→ Opens modal: "Enter your PayPal email to receive $XX.XX"
→ On submit: POST to portal proxy → WordPress endpoint
→ Success state: "Payout request submitted. Jared will process within 2 business days."
```

Portal server (`portal_server.py`) adds proxy route to `/payout-request` matching the existing referral proxy pattern.

### 3. Admin Panel Addition (WordPress admin page or simple REST call)

Simple table showing pending payout requests with:
- Earner name, referral code, PayPal email, amount
- "Mark as Paid" button (captures PayPal transaction ID)

---

## Phase 3b Implementation Outline (PayPal Payouts API)

### API Integration (`portal_server.py` addition)

```python
# Admin-triggered endpoint
POST /admin/process-payouts
  - Auth: admin bearer token
  - Fetches pending payout requests from WP plugin
  - Builds PayPal Payouts batch:
    {
      "sender_batch_header": { "email_subject": "Your PureBrain referral payout" },
      "items": [
        { "recipient_type": "EMAIL", "amount": { "value": "50.00", "currency": "USD" },
          "receiver": "user@example.com", "note": "PureBrain referral commission" }
      ]
    }
  - POST to https://api.paypal.com/v1/payments/payouts
  - On success: mark all as 'paid' in WP ledger
  - Send Telegram confirmation with batch ID
```

**PayPal credentials needed**:
- Client ID + Secret (already have from live integration)
- Payouts API scope: `https://uri.paypal.com/services/payouts` (new scope, requires approval)

---

## Security Considerations

### Critical

1. **Never auto-pay without admin review** in Phase 3a. All payouts are manual-approved. This prevents fraudulent payout requests.

2. **Verify balance before paying**. The plugin must confirm the requested amount does not exceed unspent, non-reversed earnings in the ledger before writing the payout request.

3. **PayPal email validation**. Validate email format server-side. Do NOT trust client-submitted PayPal emails without format check.

4. **Rate limit payout requests**. Maximum 1 payout request per referral code per 30 days. Prevents request spam.

5. **Admin-only mark-paid endpoint**. The `/admin/mark-paid` endpoint must require WordPress admin capability (`manage_options`), not just a nonce.

6. **Audit log**. Every payout request, approval, and payment must be logged with IP address, timestamp, and admin user who approved.

### Important

7. **Minimum payout threshold**: $25. Prevents micro-payout overhead and PayPal fee waste.

8. **Refund grace period**: Do not pay out earnings from conversions less than 14 days old. Protects against refund-then-payout abuse.

9. **Pre-fund PayPal balance**. For Phase 3b, maintain a PayPal balance buffer. Set a Telegram alert when balance drops below $200.

10. **HTTPS only**. All payout API calls must be over HTTPS with certificate verification. Already the case in the existing FastAPI stack.

11. **Tax consideration**: If any single earner receives more than $600 USD in a calendar year, US law requires a 1099 form. Flag this to legal/finance when Phase 3b launches. Keep earner records (name, PayPal email, total paid) accordingly.

---

## Timeline Estimate

| Phase | Work | Calendar Time |
|-------|------|--------------|
| Apply for PayPal Payouts API | 30 min to apply | 1–15 days for approval |
| Phase 3a — Manual bridge | 1–2 dev days | Available in 2–3 days |
| Phase 3b — Automated payouts | 2–3 dev days | After API approval |
| Admin panel for payout management | 1 dev day | Part of Phase 3a |
| Testing + QA | 1 day | End of each phase |

**Practical total**: Phase 3a live within 1 week. Phase 3b live 2–4 weeks after (pending PayPal approval).

---

## Decision: What to Do Now

1. **Immediate** (today): Apply for PayPal Payouts API at developer.paypal.com. Takes 30 minutes. Approval runs in background.

2. **This sprint** (2–3 days): Build Phase 3a manual payout bridge. Real users can request payouts. Jared processes manually via PayPal.

3. **Next sprint** (post-approval): Swap Phase 3a manual step with Phase 3b PayPal Payouts API call.

4. **Do not** switch to AffiliateWP or SliceWP — the Phase 2 custom system is already production-ready and purpose-built.

5. **Do not** implement Stripe Connect — overkill for this use case and scale.

---

## Sources

- [PayPal Payouts API Documentation](https://developer.paypal.com/docs/payouts/standard/integrate-api/)
- [PayPal Payouts Fees](https://developer.paypal.com/docs/payouts/standard/reference/fees/)
- [PayPal Payouts API Approval Process](https://www.paypal.com/us/cshelp/article/what-is-the-payouts-api-formerly-known-as-mass-pay-and-how-to-apply-for-it-help250)
- [Stripe Connect Custom Accounts](https://docs.stripe.com/connect/custom-accounts)
- [Stripe Connect Account Types](https://docs.stripe.com/connect/accounts)
- [SliceWP Paying Your Affiliates](https://slicewp.com/docs/paying-your-affiliates/)
- [Wise Platform API](https://docs.wise.com/)
- [Rewardful — PayPal and Wise Mass Payouts](https://www.rewardful.com/paypal-and-wise-mass-payouts)
- [Affiliate Payout Methods — ReferralCandy](https://www.referralcandy.com/blog/affiliate-payout-methods)

---

*Report produced by cto agent for PureBrain referral payout system Phase 3 planning.*
*Phase 2 referral system reference: `tools/security/purebrain-referral/purebrain-referral-system.php` v2.0.0*
