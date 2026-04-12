# Audit Nurture Brevo Deployment Verification - 2026-02-23

**Type**: operational
**Agent**: full-stack-developer
**Topic**: Verifying and completing AI Partnership Audit nurture sequence deployment

## Task
Verify and complete deployment of 4-email Brevo nurture sequence for audit leads (List 4).

## Findings

### Templates (from 2026-02-22 session) — All Live
- Template 13: Email 1 - Audit Debrief (Day 0)
- Template 14: Email 2 - Tool vs Partner (Day 2)
- Template 15: Email 3 - Week in Practice (Day 4)
- Template 16: Email 4 - Direct Ask (Day 7)
- All active, all have correct CTAs, unsubscribe tags, personalization

### Contact Attributes — Created Today
- AUDIT_SCORE: float — CREATED 2026-02-23 (was missing)
- AUDIT_TIER: text — CREATED 2026-02-23 (was missing)
- ASSESSMENT_SCORE and ASSESSMENT_TIER already existed (separate from AUDIT_*)

### Audit Page Verified
- Page slug: ai-partnership-audit, WP ID: 620
- Form JS confirmed at position 34975 in rendered content
- Sends: FIRSTNAME, AUDIT_SCORE, AUDIT_TIER, LEAD_SCORE:30, COMPANY (if provided)
- listIds: [4] — correct (Enterprise Leads)
- updateEnabled: true

## Key Patterns

### Brevo attribute creation
```bash
curl -X POST -H "api-key: $KEY" -H "Content-Type: application/json" \
  "https://api.brevo.com/v3/contacts/attributes/normal/ATTR_NAME" \
  -d '{"type": "float"}'   # or "text"
# Returns: {} on success (empty body = success, NOT an error)
```

### Template variable verification
- Use GET /v3/smtp/templates/{id} and search htmlContent for variable names
- Email 2 intentionally omits AUDIT_TIER (only uses AUDIT_SCORE) — not a bug

## What Still Needs Manual Action
- Brevo automation workflow (trigger: List 4 add → send 4 emails with delays)
- Brevo has NO REST API for automations — UI-only at app.brevo.com

## Files
- Deployment report: `exports/audit-nurture-deployment-report.md`
- Template IDs config: `config/audit_nurture_template_ids.json`
- Source emails: `docs/from-telegram/audit-lead-email-sequence.md`
