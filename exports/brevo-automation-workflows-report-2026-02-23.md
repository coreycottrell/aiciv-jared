# Brevo Automation Workflows Build Report

**Date**: 2026-02-23
**Agent**: browser-vision-tester
**Task**: Build 4 Brevo automation workflows via Playwright

---

## Executive Summary

**Status**: BLOCKED - Brevo platform outage on workflow API

The 4 automation workflows could NOT be built today due to a Brevo server-side error on their `workflow-apis.brevo.com` API endpoints. The automation editor shows "Something's wrong. But we'll make it right." for all automation creation/editing attempts.

---

## Findings

### Root Cause

Brevo's workflow API backend is returning HTTP 500 errors on required endpoints:

```
500 https://workflow-apis.brevo.com/v1/workflow/premade/check-creatable
500 https://workflow-apis.brevo.com/v1/workflow/getCategoryData?with_category=true
```

These endpoints are required to load the automation editor (a React micro-frontend). Without them, the editor displays a generic error page instead of the drag-and-drop workflow builder.

**This is a Brevo platform outage, not a script error.**

### What Was Successfully Accomplished

1. **Login**: Successfully logged in as purebrain@puremarketing.ai with 2FA via Gmail IMAP (code: 098597)
2. **Automation List**: Successfully accessed `https://app.brevo.com/automation/automations`
3. **Session**: Valid session saved to `tools/brevo_session.json`
4. **Discovered correct URL**: Automation list is at `/automation/automations` (NOT `/automation/list` which returns 500)

### Current Brevo Automation State

6 automations exist (all Inactive):
- #6 - Automation #6 (blank, created 23-02-2026 by failed attempt)
- #5 - Automation #5 (blank, created 23-02-2026 by failed attempt)
- #4 - Neural Feed - Welcome Sequence (existing, has steps)
- #3 - Automation #3 (blank)
- #2 - Automation #2 (blank)
- #1 - Welcome message (existing)

### What Was Attempted

| Attempt | Outcome |
|---------|---------|
| `brevo_build_4_automations.py` (v1) | Session issue - automation module redirect to login |
| Fresh login via `brevo_session_login.py` | 2FA worked but session didn't cover automation editor |
| Direct URL `/automation/automations` | Page loaded but editor returned 500 errors |
| Clicking "Create from scratch" | Editor error page (500 from workflow-apis.brevo.com) |
| Editing existing automation #4 | Same 500 error - editor broken platform-wide |

---

## Action Required (Manual)

The 4 automation workflows need to be created manually when Brevo's platform is working. Here's the exact setup for each:

### Workflow 1: AI Partnership Audit — Lead Nurture

1. Login to https://app.brevo.com → Automations → Workflows
2. Click "+ Create an automation" → "Create from scratch"
3. Name: "AI Partnership Audit — Lead Nurture"
4. Trigger: "Contact added to a list" → List: "Enterprise Leads" (List 4)
5. Add steps:
   - Send email: Template 13 ("AI Audit Nurture - Email 1 - Audit Debrief")
   - Wait: 2 days
   - Send email: Template 14 ("AI Audit Nurture - Email 2 - Tool vs Partner")
   - Wait: 2 days
   - Send email: Template 15 ("AI Audit Nurture - Email 3 - Week in Practice")
   - Wait: 3 days
   - Send email: Template 16 ("AI Audit Nurture - Email 4 - Direct Ask")
6. Activate

### Workflow 2: Pricing Intent — Awakening Section

1. Create new automation
2. Name: "Pricing Intent — Awakening Section"
3. Trigger: "A contact triggers an event" → Event name: `awakening_section_viewed`
4. Add steps:
   - Send email: Template 17 ("Pricing Intent - Email 1 - Awakening Reframe")
   - Wait: 2 days
   - Send email: Template 18 ("Pricing Intent - Email 2 - Objection Handler")
5. Activate

### Workflow 3: 45-Day Inactive Re-engagement

1. Create new automation
2. Name: "45-Day Inactive Re-engagement"
3. Trigger: "Inactivity on emails" → 45 days → List 3 (The Neural Feed)
4. Add steps:
   - Send email: Template 19 ("Re-engagement Email 1")
   - Wait: 7 days
   - Send email: Template 20 ("Re-engagement Email 2")
   - Wait: 14 days
   - Send email: Template 21 ("Re-engagement Email 3")
5. Activate

### Workflow 4: Email Reply — High Engagement Tag

1. Create new automation
2. Name: "Email Reply — High Engagement Tag"
3. Trigger: "A contact triggers an event" → Event name: `email_replied`
4. Add steps:
   - Update contact attribute: ENGAGEMENT_LEVEL = "high"
5. Activate

---

## Screenshots Captured

All screenshots saved to: `/home/jared/projects/AI-CIV/aether/exports/screenshots/brevo-workflows/`

Key screenshots:
- `workflows_page.png` - Automation list fully loaded
- `investigate_02_create_clicked.png` - Create automation modal (Abandoned cart, Product purchase, etc.)
- `investigate_04_editor.png` - Editor error: "Something's wrong. But we'll make it right."
- `investigate_09_all_automations.png` - All 6 automations visible

---

## Next Steps

1. **Wait for Brevo to fix their workflow API** - Check status at https://status.brevo.com
2. **Try again when editor loads** - Run `python3 tools/brevo_build_4_automations_v2.py`
3. **Or build manually** - Use the step-by-step instructions above

---

## Technical Notes

- Brevo automation editor URL: `https://app.brevo.com/automation/automations`
- Direct editor edit URL pattern: `https://app.brevo.com/automation/edit/{id}`
- Session file: `tools/brevo_session.json` (expires in minutes-hours)
- Login: purebrain@puremarketing.ai + 2FA via Gmail IMAP from account-alerts@t.brevo.com
- Brevo has NO REST API for automation workflows (GUI-only)
- The Create modal shows templates: Abandoned cart, Product purchase, Welcome message, Marketing activity, Anniversary date

---

## Scripts Created

- `/home/jared/projects/AI-CIV/aether/tools/brevo_build_4_automations.py` - v1 (initial attempt)
- `/home/jared/projects/AI-CIV/aether/tools/brevo_build_4_automations_v2.py` - v2 (improved, ready to run when Brevo is fixed)
