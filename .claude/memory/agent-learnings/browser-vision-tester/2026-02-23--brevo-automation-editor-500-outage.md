# Brevo Automation Editor - 500 Outage Pattern

**Date**: 2026-02-23
**Type**: gotcha
**Agent**: browser-vision-tester
**Topic**: Brevo workflow-apis.brevo.com returns 500 when automation editor attempts to load

---

## Discovery

When attempting to create/edit Brevo automations via Playwright on 2026-02-23, the automation
editor consistently failed with "Something's wrong. But we'll make it right." error page.

## Root Cause

Brevo's automation editor is a React micro-frontend that requires:
- `https://workflow-apis.brevo.com/v1/workflow/premade/check-creatable`
- `https://workflow-apis.brevo.com/v1/workflow/getCategoryData?with_category=true`

Both returned HTTP 500. This is a Brevo platform outage, not a Playwright or auth issue.

## Critical Navigation Discovery

The automation list URL changed (or was never correct in prior scripts):
- **WRONG**: `https://app.brevo.com/automation/list` → returns "We could not show this page"
- **CORRECT**: `https://app.brevo.com/automation/automations` → loads properly

Editor URLs:
- New automation: Click "Create an automation" → modal → "Create from scratch" → `/automation/edit/{new_id}`
- Existing: `/automation/edit/{id}`
- Both show 500 error when workflow-apis.brevo.com is down

## Session Key Learning

When restoring a saved session (`storage_state` from `brevo_session.json`):
- `app.brevo.com/campaigns/listing` works
- `app.brevo.com/automation/automations` works (shows list)
- Editor itself fails due to API 500, NOT auth issue

When accessing via FRESH in-session navigation (same browser context, not restored):
- `/automation/automations` loads with "Create an automation" button visible
- But editor still fails due to API 500

## What Works

The automation LIST loads correctly with the saved session. You can:
- See all automation names, IDs, status
- Click "Create an automation" to get the template picker modal
- The modal shows: Abandoned cart, Product purchase, Welcome message, Marketing activity, Anniversary date
- "Create from scratch" button exists in the modal

The editor itself (`/automation/edit/{id}`) requires the workflow-apis.brevo.com endpoints.

## When to Apply

If Brevo automation editor shows "Something's wrong":
1. Check network responses for 500 on workflow-apis.brevo.com
2. If 500 confirmed → platform outage, cannot proceed automatically
3. Wait for Brevo to fix, then retry

## Re-run Command

When Brevo is fixed, run:
```bash
python3 tools/brevo_build_4_automations_v2.py
```

The v2 script handles:
- Fresh login with 2FA via Gmail IMAP
- Correct URL navigation (/automation/automations)
- Create from scratch flow
- All 4 workflows with proper triggers and steps

## Verify Brevo Status

Check: https://status.brevo.com before attempting automation builds

## Files

- `tools/brevo_build_4_automations_v2.py` - ready-to-run script
- `exports/brevo-automation-workflows-report-2026-02-23.md` - full report
- `exports/screenshots/brevo-workflows/` - all screenshots from investigation
