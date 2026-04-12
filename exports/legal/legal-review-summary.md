# PureBrain.ai — Legal Review Summary

**Matter**: Terms of Service and Privacy Policy — Comprehensive Review
**Prepared By**: dept-legal-compliance (AI-assisted, informational purposes only)
**Date**: March 5, 2026
**Status**: Draft — Requires Licensed Attorney Review Before Publication

---

> **CRITICAL DISCLAIMER**: This summary and the accompanying documents were prepared with AI assistance for internal planning and triage purposes. Nothing in this summary or the accompanying documents constitutes legal advice. All final legal documents should be reviewed and approved by a licensed attorney before publication and public reliance. Pure Technology Inc. should engage qualified New Jersey legal counsel.

---

## Executive Summary

Pure Technology Inc. (New Jersey) operates PureBrain.ai, a SaaS platform providing AI Brains with persistent memory. The company collects significant personal data including conversation history, business information, email addresses, and payment information, and uses third-party services including Anthropic's Claude API, PayPal, Brevo, and Cloudflare.

**Bottom line**: The company needs solid, attorney-reviewed Terms of Service and a Privacy Policy before scaling. The AI-specific content and data collection profile create real liability exposure without them. The documents drafted in this engagement cover the correct ground — they need attorney review and fine-tuning, not ground-up rewriting.

**Urgency level**: HIGH. Real payments are being accepted. Real conversation data is being stored. Legal exposure without proper disclosures is not theoretical.

---

## Documents Produced

| Document | Path | Purpose |
|----------|------|---------|
| Terms of Service | `exports/legal/purebrain-terms-of-service.md` | Governs user relationship, liability caps, acceptable use |
| Privacy Policy | `exports/legal/purebrain-privacy-policy.md` | Data collection disclosure, user rights, compliance |
| This Summary | `exports/legal/legal-review-summary.md` | Triage, key decisions, next steps |

---

## Key Legal Issues Identified

### 1. Jurisdiction Change: Florida to New Jersey (RESOLVED IN DRAFTS)

**Issue**: Prior documents (February 2026) used Florida as the governing law jurisdiction. Pure Technology Inc. has relocated to New Jersey.

**Resolution in drafts**: Both documents now specify New Jersey as governing law and jurisdiction. Any legacy contracts or legal documents still referencing Florida jurisdiction should be inventoried and updated.

**Action required**: Review all existing vendor contracts, terms, and agreements for Florida jurisdiction clauses. Prioritize updating the live website legal pages.

---

### 2. AI-Generated Content Liability (HIGH PRIORITY)

**Issue**: PureBrain.ai's core product is AI-generated advice and content. This creates liability exposure if users rely on AI output for consequential decisions (business, legal, financial, medical).

**What the drafts do**: Section 7 of the TOS contains explicit AI disclaimers covering:
- AI can be inaccurate and hallucinates
- AI output is not professional advice
- Users are responsible for decisions they make
- Limitation of liability applies to AI output reliance

**What still needs attention**:
- Consider adding in-product AI disclaimers (not just in the TOS) — brief disclosures within the chat interface reduce liability more effectively than buried TOS clauses
- The class of AI output that is most legally sensitive (medical, financial, legal advice) should have real-time prompts discouraging reliance
- Attorney should confirm whether New Jersey law requires additional disclosures for AI-generated content

---

### 3. CCPA Compliance (California) — Partial

**Issue**: If any California residents use PureBrain.ai (highly likely), CCPA/CPRA applies.

**What the drafts do**: Privacy Policy Section 9.2 covers:
- Right to know
- Right to delete
- Right to correct
- Right to opt out of sale/sharing
- Right to limit sensitive personal information use
- Right to non-discrimination
- Categories of personal information (CCPA format)

**Gaps to address with counsel**:
- CCPA technically requires a "Do Not Sell or Share My Personal Information" link on the website homepage if you are subject to CCPA. Determine whether Pure Technology meets the CCPA threshold (revenue over $25M, data of 100,000+ consumers, or 50%+ revenue from selling data). At early stage, likely below threshold — but this should be confirmed.
- CCPA requires a Privacy Notice at Collection at the point data is collected (e.g., on the signup form). This is separate from the full Privacy Policy.
- Verify that your response process can actually handle CCPA rights requests within 45 days.

---

### 4. GDPR Basics — Flagged, Not Fully Compliant

**Issue**: If EU/EEA residents use PureBrain.ai, GDPR applies regardless of company location.

**What the drafts do**: Privacy Policy Section 9.3 covers the basic GDPR rights framework and notes the international data transfer issue.

**Important gaps — require attorney attention before serving EU customers**:

- **Data Protection Officer (DPO)**: Under GDPR, companies that process personal data at scale or process sensitive data may need a formal DPO. Evaluate whether Pure Technology meets the threshold.
- **EU Representative**: If Pure Technology offers services to EU residents but has no EU establishment, GDPR Article 27 requires designating a representative in the EU. This is not expensive but is a formal requirement.
- **Standard Contractual Clauses (SCCs)**: US-based processing of EU personal data requires an appropriate transfer mechanism. SCCs are the standard mechanism post-Privacy Shield. These need to be executed with each processor (Anthropic, Brevo, etc.).
- **Data Processing Agreements (DPAs)**: GDPR requires formal DPAs with all processors. Verify that Anthropic, Brevo, PayPal, and Cloudflare all offer GDPR-compliant DPAs (most major providers do — check and execute them).
- **Lawful Basis Documentation**: Create an internal Record of Processing Activities (ROPA) documenting the legal basis for each type of data processing. This is an internal document but required under GDPR.
- **Cookie Consent**: If serving EU users, a cookie consent banner (not just a disclosure) is required. Pre-checked boxes or implied consent are not compliant. A real consent mechanism is needed.

**Recommendation**: If EU customers are not a current priority, add a geo-block or explicit notice limiting service to US customers until GDPR compliance is fully in place. This is safer than accidentally serving EU customers without the required safeguards.

---

### 5. Conversation Data and Anthropic API — Data Processing

**Issue**: User conversation content is transmitted to Anthropic to generate responses. This is a significant data flow that requires disclosure and appropriate agreements.

**What the drafts do**: Both documents disclose this. The Privacy Policy explains it in Section 4.3.

**What needs verification**:
- Confirm Anthropic's API terms regarding use of API call data for model training. Anthropic's current API terms indicate they do not use API calls to train models — verify this is accurate for your contract tier and document it.
- Execute Anthropic's Data Processing Agreement if one is available for your account type.
- The Privacy Policy currently states: "We do not permit Anthropic to use your data to train their foundation models without your consent." Verify that this is actually contractually guaranteed by your Anthropic agreement.

---

### 6. Persistent Memory Data — Novel Legal Territory

**Issue**: PureBrain.ai's persistent memory feature is relatively novel. The AI retains user preferences, business context, and personal information across sessions. This creates a data profile that goes beyond standard SaaS.

**Key questions for counsel**:
- What is the legal classification of "AI memory" data under CCPA, GDPR, and NJ law?
- Does AI-inferred data (preferences and context extracted from conversations) constitute "sensitive personal information" under CCPA or GDPR? If so, additional protections apply.
- What are the obligations if a user exercises their right to deletion — does this require deleting the AI's extracted memory as well as raw conversations? The drafts currently say yes (both are deleted), which is the right approach but should be confirmed.

---

### 7. AI-Generated Content Ownership — Uncertain Copyright

**Issue**: Copyright law has not fully settled on AI-generated content. Courts and the Copyright Office have generally held that purely AI-generated content without sufficient human creative input is not copyrightable.

**What the drafts do**: TOS Section 8.3 addresses this honestly — it notes that AI output copyright status is uncertain and recommends users consult counsel if it's material to their use case.

**Recommendation**: This is the right approach. Do not overclaim copyright in AI output. The transparency is protective.

---

### 8. Subscription Terms and Refund Policy

**Issue**: Clear subscription and refund terms are essential to avoid chargebacks and consumer protection claims.

**What the drafts do**: TOS Sections 4 and 5 cover:
- 7-day satisfaction refund for first-time subscribers
- No prorated refunds after 7-day window
- 30-day data retention after cancellation
- 30-day price change notice

**Considerations**:
- The 7-day refund window is consumer-friendly and appropriate for this price point. It aligns with industry standard.
- Verify that PayPal's merchant policies align with your stated refund terms.
- New Jersey consumer protection law: The New Jersey Consumer Fraud Act (CFA) is notably broad. Ensure all billing practices, subscription terms, and refund policies are clearly disclosed and consistently honored. The drafts support this.

---

### 9. CAN-SPAM Compliance for Email Marketing

**Issue**: Brevo is used for transactional and marketing email. CAN-SPAM and potentially CASL (Canadian) apply.

**Current status** (from prior compliance memory): Email includes unsubscribe mechanisms. Verify:
- Every marketing email includes a functional unsubscribe link
- Unsubscribe requests are honored within 10 business days
- Physical address of the sender (Pure Technology Inc., NJ) is included in the footer of marketing emails
- Subject lines are not deceptive

**The Privacy Policy addresses this** in Section 3 (marketing email with opt-out) and Section 9.1 (right to opt out of marketing).

---

### 10. Children's Privacy — COPPA

**Issue**: If the platform were used by children under 13, COPPA would apply with strict requirements.

**What the drafts do**: Both documents state that the Service is not directed to children under 13 and that Pure Technology does not knowingly collect their data.

**Recommendation**: Add age verification at signup (checkbox confirming user is 18+). This creates a documented record that the user represented their age. The TOS already requires users to be 18+.

---

## Compliance Checklist — Current Status

| Item | Status | Priority |
|------|--------|----------|
| Terms of Service (NJ jurisdiction) | Drafted — needs attorney review | HIGH |
| Privacy Policy (NJ jurisdiction) | Drafted — needs attorney review | HIGH |
| NJ governing law (FL removed) | Updated in both drafts | HIGH |
| AI content disclaimers | Included in TOS Section 7 | COMPLETE |
| Third-party service disclosures | Included in both documents | COMPLETE |
| CCPA basics | Included in Privacy Policy Section 9.2 | PARTIAL |
| CCPA threshold analysis | Not yet conducted | MEDIUM |
| CCPA Privacy Notice at Collection | Not yet created | MEDIUM |
| GDPR rights framework | Included in Privacy Policy Section 9.3 | PARTIAL |
| GDPR EU Representative | Not yet designated | HIGH if serving EU |
| GDPR Data Processing Agreements | Not yet executed with processors | HIGH if serving EU |
| GDPR Cookie Consent Banner | Not yet implemented | HIGH if serving EU |
| CAN-SPAM email compliance | Address and unsubscribe in place | MONITOR |
| COPPA (no under-13) | Disclosure included; add age checkbox | MEDIUM |
| Anthropic DPA/API terms review | Not yet verified | HIGH |
| PayPal merchant terms alignment | Not yet verified | MEDIUM |
| Limitation of liability caps | Included in TOS Section 12 | COMPLETE |
| Class action waiver | Included in TOS Section 14.4 | COMPLETE |
| Data retention schedule | Included in Privacy Policy Section 6 | COMPLETE |
| In-product AI disclaimers | Not yet implemented | MEDIUM |
| Record of Processing Activities (ROPA) | Not yet created | MEDIUM |
| Legacy FL contracts inventory | Not yet conducted | MEDIUM |

---

## Recommended Next Steps (Prioritized)

### Immediate (Before Publishing Updated Legal Pages)

1. **Engage a New Jersey attorney** with SaaS and data privacy experience to review both documents. This is the single highest-value action. Cost: $500–$2,000 for a review and markup. Worth every dollar given the liability exposure.

2. **Update the live website** with attorney-approved TOS and Privacy Policy replacing any prior versions. Ensure the effective date and NJ jurisdiction are current.

3. **Add 18+ confirmation at signup** — a checkbox: "I confirm I am 18 years of age or older." Simple, protective.

### Short Term (Within 30 Days)

4. **Verify Anthropic API terms** — confirm that API call data is not used for model training under your current Anthropic agreement. Document the confirmation. If a DPA is available, execute it.

5. **Execute DPAs with Brevo and Cloudflare** — both offer standard DPAs. Executing them is routine and required for GDPR compliance if EU customers are anticipated.

6. **CCPA threshold analysis** — determine whether Pure Technology currently meets any CCPA threshold (revenue, user volume, revenue from data). If not yet at threshold, document the analysis; revisit as the company grows.

7. **Inventory legacy FL contracts** — identify any vendor agreements, contractor agreements, or prior legal documents that reference Florida jurisdiction. Assess which need to be amended.

### Medium Term (60–90 Days)

8. **In-product AI disclaimers** — add a short, visible disclaimer in the AI chat interface (e.g., "AI responses may be inaccurate. Do not rely on them for professional advice."). This is more effective at limiting liability than TOS language alone.

9. **Cookie consent audit** — confirm what cookies and trackers are actually running on purebrain.ai. If EU visitors are anticipated, implement a compliant consent mechanism.

10. **GDPR decision** — decide whether to actively serve EU/UK customers. If yes, engage GDPR counsel and implement required safeguards (EU representative, SCCs, consent mechanism). If no, consider a geographic limitation notice.

11. **Create Privacy Notice at Collection** — a short notice at the signup form informing users of data collection at point of collection. Separate from the full Privacy Policy.

---

## Key Decisions Made in the Drafts

The following decisions were made in drafting and should be reviewed:

| Decision | What Was Chosen | Rationale |
|----------|----------------|-----------|
| Governing law | New Jersey | Company relocated from FL to NJ |
| Refund window | 7-day satisfaction window (first-time only) | Industry standard; builds trust |
| AI training opt-out | Opt-out model (default allows, user can opt out) | Simpler for operations; GDPR recommends opt-in for EU |
| AI Output copyright | Uncertainty disclosed honestly | Legally accurate; not overclaiming |
| Data retention post-cancellation | 30 days | Balances operational needs with user expectations |
| Liability cap | Greater of 12-month fees paid or $100 | Standard SaaS cap; reduces catastrophic exposure |
| Class action waiver | Included | Reduces class action risk; enforceability varies by jurisdiction — attorney should confirm NJ enforceability |
| COPPA | No under-13; add age 18+ representation | Appropriate for business-focused SaaS |

---

## Memory Written

**Path**: `.claude/memory/departments/dept-legal-compliance/2026-03-05--purebrain-tos-privacy-policy-review.md`

---

*Legal Review Summary prepared by dept-legal-compliance | Pure Technology Inc. | March 5, 2026*

*This document is for internal planning purposes only. It does not constitute legal advice. Engage qualified legal counsel for all final legal decisions.*
