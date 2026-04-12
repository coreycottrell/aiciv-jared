# Brevo Automation Templates: 5 Created via API

**Date**: 2026-02-23
**Type**: operational
**Topic**: Pricing intent + re-engagement email templates created in Brevo

## What Was Done

Created 5 Brevo email templates using the Brevo REST API (`POST /v3/smtp/templates`).

## Template IDs

| Key | ID | Name | Tag |
|-----|----|------|-----|
| pricing_intent_email_1 | 17 | Pricing Intent - Email 1 - Awakening Reframe | pricing-intent |
| pricing_intent_email_2 | 18 | Pricing Intent - Email 2 - Objection Handler | pricing-intent |
| reengagement_email_1 | 19 | Re-engagement - Email 1 - We Noticed You've Been Quiet | re-engagement |
| reengagement_email_2 | 20 | Re-engagement - Email 2 - What Would Bring You Back | re-engagement |
| reengagement_email_3 | 21 | Re-engagement - Email 3 - Last Chance Sunset | re-engagement |

## Config File
`/home/jared/projects/AI-CIV/aether/config/brevo_automation_template_ids.json`

## Script
`/home/jared/projects/AI-CIV/aether/tools/create_brevo_templates.py`

## Key Details

- Sender: `purebrain@puremarketing.ai` (verified in Brevo) — NOT support@puremarketing.ai
- Sender name: "Jared Sanborn | PureBrain"
- Reply-to: `jared@puretechnology.nyc`
- All templates verified ACTIVE after creation via GET /v3/smtp/templates
- HTML source: `/home/jared/projects/AI-CIV/aether/docs/from-telegram/brevo-automation-plan.md`

## Pattern

Template creation requires:
1. `templateName`, `subject`, `sender` (name+email object), `htmlContent`, `replyTo`, `isActive: True`, `tag`
2. Returns `{'id': N}` on 201 Created
3. Verify with GET /v3/smtp/templates — check `isActive` field in response

## Next Step for Jared

Use these template IDs to build the automation workflows in Brevo dashboard:
- Pricing intent workflow: Templates 17 + 18 (trigger: awakening_section_viewed event)
- Re-engagement workflow: Templates 19 + 20 + 21 (trigger: 45 days inactive in List 3)
