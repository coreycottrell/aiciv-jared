# Brevo Reply-To Mass Fix - 9 Templates

**Date**: 2026-02-23
**Type**: operational
**Agent**: full-stack-developer
**Topic**: Fixed replyTo field on 9 Brevo templates pointing to wrong email addresses

---

## What Was Fixed

9 templates had wrong replyTo addresses. After fix, ALL 21 templates now route replies to `purebrain@puremarketing.ai`.

### Templates Fixed

| ID | Name | Old replyTo | New replyTo |
|----|------|------------|------------|
| 13 | AI Audit Nurture - Email 1 - Audit Debrief | jared@puremarketing.ai | purebrain@puremarketing.ai |
| 14 | AI Audit Nurture - Email 2 - Tool vs Partner | jared@puremarketing.ai | purebrain@puremarketing.ai |
| 15 | AI Audit Nurture - Email 3 - Week in Practice | jared@puremarketing.ai | purebrain@puremarketing.ai |
| 16 | AI Audit Nurture - Email 4 - Direct Ask | jared@puremarketing.ai | purebrain@puremarketing.ai |
| 17 | Pricing Intent - Email 1 - Awakening Reframe | jared@puretechnology.nyc | purebrain@puremarketing.ai |
| 18 | Pricing Intent - Email 2 - Objection Handler | jared@puretechnology.nyc | purebrain@puremarketing.ai |
| 19 | Re-engagement - Email 1 - We Noticed You've Been Quiet | jared@puretechnology.nyc | purebrain@puremarketing.ai |
| 20 | Re-engagement - Email 2 - What Would Bring You Back | jared@puretechnology.nyc | purebrain@puremarketing.ai |
| 21 | Re-engagement - Email 3 - Last Chance Sunset | jared@puretechnology.nyc | purebrain@puremarketing.ai |

---

## Wrong Emails Found Across Account

- `jared@purebrain.ai` - does not exist (was fixed in templates 1-3 in a prior session)
- `jared@puremarketing.ai` - wrong prefix, corrected to `purebrain@`
- `jared@puretechnology.nyc` - entirely wrong domain, corrected

---

## Technical Pattern - Brevo PUT Template API

**Critical gotcha**: When updating a template via PUT, the sender object from GET contains both `id` and `email`. Passing both causes a 400 error:
```
{"code":"invalid_parameter","message":"Only one of Sender ID or Sender Email can be passed for the same request."}
```

**Fix**: In the PUT payload, only include `sender.id` (not `sender.email`):
```python
payload = {
    'replyTo': 'purebrain@puremarketing.ai',
    'subject': t['subject'],
    'htmlContent': t['htmlContent'],
    'name': t['name'],
    'sender': {'id': 1}  # ID only - NOT email
}
```

---

## HTML Content Check

Also scanned htmlContent of ALL 21 templates for `mailto:` links containing:
- `jared@purebrain.ai`
- `jared@puretechnology.nyc`
- `jared@puremarketing.ai`

**Result: Zero occurrences found.** The wrong email was only in the replyTo metadata field, not embedded in HTML.

---

## Correct State for All Templates

Every active template should have:
- `replyTo: purebrain@puremarketing.ai`
- `sender.email: purebrain@puremarketing.ai` (Sender ID 1, name "Jared Sanborn | PureBrain")
