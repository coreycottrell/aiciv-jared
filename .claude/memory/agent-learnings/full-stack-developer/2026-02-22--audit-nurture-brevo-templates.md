# Audit Nurture Brevo Templates Created - 2026-02-22

**Type**: operational
**Agent**: full-stack-developer
**Topic**: Creating 4 Brevo email templates for AI Partnership Audit nurture sequence

## Task
Created 4 email templates in Brevo for the AI Partnership Audit nurture sequence.
Source: `exports/audit-lead-email-sequence.md`

## Template IDs Assigned

| Email | Brevo ID | Timing | Job |
|-------|----------|--------|-----|
| Email 1 - Audit Debrief | 13 | Day 0 (immediate) | Score interpretation, no spin |
| Email 2 - Tool vs Partner | 14 | Day 2 | The gap: using vs partnering |
| Email 3 - Week in Practice | 15 | Day 4 | Real examples Monday-Friday |
| Email 4 - Direct Ask | 16 | Day 7 | Orange CTA button, reply invite |

## Sender Issue Encountered and Resolved

- **Requested sender**: `support@puremarketing.ai` — INACTIVE in Brevo (returns 400 invalid_parameter)
- **Working sender**: `purebrain@puremarketing.ai` — Active, ID 1
- **Fix**: Used `purebrain@puremarketing.ai` as sender for all 4 templates

## Brevo API Pattern Used

```python
# Create template
POST https://api.brevo.com/v3/smtp/templates
Body: {
    "templateName": "...",
    "subject": "...",    # supports {{params.VAR}}
    "htmlContent": "...",
    "sender": {"name": "...", "email": "purebrain@puremarketing.ai"},
    "replyTo": "jared@puremarketing.ai",
    "isActive": True,
    "tag": "ai-audit-nurture"
}
# Returns: {"id": N}

# Verify
GET https://api.brevo.com/v3/smtp/templates/{id}
# Returns full template object with htmlContent
```

## Verification Checks Applied

For each template after creation:
1. GET template by ID
2. Check `isActive == True`
3. Check `'purebrain.ai/#awakening' in html` (CTA link)
4. Check `'{{ unsubscribe }}' in html` (unsubscribe tag)
5. Check `'PUREBR' in html` (PureBrain logo)

All 4 templates passed all checks.

## Files

- Script: `tools/brevo_create_audit_nurture_templates.py`
- Config: `config/audit_nurture_template_ids.json`
- Source: `exports/audit-lead-email-sequence.md`

## Key Notes

- Brevo templates 1-12 are Neural Feed / purchase flows — do NOT touch
- These audit nurture templates are 13-16
- Brevo automation workflows are UI-ONLY (no REST API) — must be built in dashboard
- All CTAs point to `https://purebrain.ai/#awakening` per locked rule
- Template variables used: `{{params.FIRSTNAME}}`, `{{params.AUDIT_SCORE}}`, `{{params.AUDIT_TIER}}`, `{{params.COMPANY}}`
