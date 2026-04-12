# dept-legal-compliance Learning: PureBrain TOS + Privacy Policy Review

**Date**: 2026-03-05
**Type**: legal-triage + compliance-mapping
**Agent**: dept-legal-compliance
**Confidence**: high (AI-assisted analysis; requires attorney review)

---

## Matter Summary

Comprehensive legal review and drafting of Terms of Service and Privacy Policy for PureBrain.ai.

**Trigger**: Fresh restart request from Jared — prior analysis lost.

**Company**: Pure Technology Inc., New Jersey (relocated from Florida).

---

## Key Facts Established

- PureBrain.ai = SaaS AI Brain platform with persistent memory
- Data collected: name, email, business info, conversation data, payment info (via PayPal)
- Third-party processors: Anthropic (Claude API), Brevo (email), Cloudflare (CDN/security), PayPal
- Customers get personal subdomains: {ainame}{firstname}.purebrain.ai
- Real payments being accepted — legal documents are urgent
- Prior TOS/Privacy Policy (Feb 2026) used Florida governing law — now outdated

---

## Documents Delivered

| File | Path |
|------|------|
| Terms of Service | `exports/legal/purebrain-terms-of-service.md` |
| Privacy Policy | `exports/legal/purebrain-privacy-policy.md` |
| Legal Review Summary | `exports/legal/legal-review-summary.md` |

---

## Critical Findings

### 1. Florida to New Jersey Jurisdiction
- Both new documents use NJ governing law
- Legacy FL references in old legal pages and any vendor contracts must be updated

### 2. AI Content Liability — Key Risk Area
- TOS Section 7 contains explicit AI disclaimers
- Recommend adding in-product disclaimers (more effective than buried TOS clauses)

### 3. CCPA — Partial Compliance
- Rights framework included in Privacy Policy
- CCPA threshold analysis not yet conducted
- Privacy Notice at Collection not yet created (needed at signup form)

### 4. GDPR — Flagged, Not Complete
- Rights framework included
- EU Representative not designated
- DPAs with processors not yet executed
- Cookie consent banner not yet implemented
- Recommend geo-limiting to US until GDPR compliance is complete

### 5. Anthropic API Data Terms
- Policy states Anthropic does not use API calls for model training
- This needs contractual verification — check actual Anthropic agreement

### 6. Persistent Memory = Novel Legal Territory
- AI-extracted memory data (inferences) may qualify as "sensitive personal information" under CCPA/GDPR
- Deletion of AI memory (not just raw conversations) must be included in deletion process — covered in drafts

---

## Decisions Baked Into Drafts

- 7-day satisfaction refund for first-time subscribers
- Opt-out model for AI training data (not opt-in)
- AI output copyright uncertainty disclosed honestly — no overclaiming
- 30-day post-cancellation data retention
- Liability cap = greater of 12-month fees or $100
- Class action waiver included (NJ enforceability should be confirmed by attorney)
- Age 18+ required (recommend adding checkbox at signup)

---

## Highest Priority Next Steps

1. Engage NJ attorney for review (most important single action)
2. Publish updated TOS and Privacy Policy on live site
3. Add 18+ confirmation checkbox at signup
4. Verify Anthropic API DPA terms
5. Execute DPAs with Brevo and Cloudflare
6. CCPA threshold analysis
7. Inventory legacy FL contracts

---

## Pattern: AI SaaS Legal Document Structure

For any AI SaaS platform, the highest-risk areas in order:
1. AI content liability disclaimers (wrong info reliance)
2. Data processing disclosures for AI model APIs
3. Persistent/memory data retention and deletion
4. Jurisdiction clarity (where the company actually is)
5. CCPA/GDPR rights framework

---

**END MEMORY**
