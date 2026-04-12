# Brevo Template: Reply-to Email Link Fix

**Date**: 2026-02-23
**Type**: operational
**Topic**: Fixing broken jared@purebrain.ai mailto links in Brevo email templates

---

## What Happened

Three Neural Feed email templates had broken "Reply to this email" buttons pointing to
`jared@purebrain.ai` - an email address that does not exist.

Affected templates:
- Template 1: Neural Feed - Email 1 - Welcome (Aether)
- Template 2: Neural Feed - Email 2 - Jared's Story
- Template 3: Neural Feed - Email 3 - Aether Writes Directly

## Root Cause

Templates were created with `jared@purebrain.ai` as the mailto href, but the actual
Brevo reply-to is set to `purebrain@puremarketing.ai`. The mailto link in HTML is
a separate field from the Brevo-level reply-to header.

## Fix Applied

Replaced all instances of `jared@purebrain.ai` with `support@puremarketing.ai` in
the htmlContent of each template.

Old: `mailto:jared@purebrain.ai?subject=...`
New: `mailto:support@puremarketing.ai?subject=...`

## Brevo API Patterns Learned

### GET template
```
curl -H "api-key: $KEY" "https://api.brevo.com/v3/smtp/templates/{id}"
```

### PUT template (update) - IMPORTANT gotcha
- Sender field: use EITHER `{"id": 1}` OR `{"email": "..."}` - NOT both together
- Passing both causes: `400 "Only one of Sender ID or Sender Email can be passed"`
- Correct payload:
```json
{
  "subject": "...",
  "htmlContent": "...",
  "sender": {"id": 1},
  "replyTo": "purebrain@puremarketing.ai"
}
```

### Finding templates quickly
- List with: `GET /v3/smtp/templates?limit=50&sort=desc`
- Subject line "Aether has something to say to you" = Template ID 3

## Future Prevention

When creating new Brevo templates, the mailto href in HTML must use a real, monitored
address. Current correct addresses:
- `support@puremarketing.ai` - for reply CTA buttons in emails
- `purebrain@puremarketing.ai` - Brevo reply-to header (sender identity)

Do NOT use `jared@purebrain.ai` - this domain does not have email configured.
