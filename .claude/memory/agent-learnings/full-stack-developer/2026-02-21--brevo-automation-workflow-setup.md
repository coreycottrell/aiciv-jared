# Brevo Automation Workflow Setup - Neural Feed Welcome Sequence

**Date**: 2026-02-21
**Type**: teaching
**Agent**: full-stack-developer
**Topic**: Brevo automation workflow creation via Playwright - patterns, lessons, and limitations

---

## Summary

Wrote `tools/setup_neural_feed_automation.py` to create the 7-email Neural Feed welcome sequence
automation in Brevo. This file consolidates all learnings from ~10 prior failed/partial attempts
into one clean, documented script.

---

## Critical Finding: No Brevo Automation REST API

**Brevo v3 API has NO endpoints for creating automation workflows.**

Tested endpoints all return 404:
- `GET/POST https://api.brevo.com/v3/automations` → 404
- `GET/POST https://api.brevo.com/v3/workflows` → 404
- All variations of automation/scenarios/flows → 404

The Brevo automation builder is a **GUI-only drag-and-drop SPA** at
`https://app.brevo.com/automation/edit/{id}`.

**Implication**: Must use Playwright to interact with the UI. There is no API shortcut.

---

## Session Management Lessons

### Sessions expire in minutes, not hours

Brevo sessions are very short-lived. The session file (`tools/brevo_session.json`) that
worked yesterday will be expired today. Always test session validity before using it.

### Detection pattern

```python
page.goto('https://app.brevo.com/', wait_until='domcontentloaded', timeout=30000)
time.sleep(2)
if 'login' in page.url.lower():
    # Session expired
```

### 2FA via Gmail IMAP works reliably

The `get_2fa_code()` function (using IMAP) successfully retrieves codes within ~30 seconds.
Key: search for emails from `account-alerts@t.brevo.com` with "verify" in subject.
Tested: code `575701` retrieved successfully during dry-run session.

### Login button quirk

Brevo login form uses `type="button"` (NOT `type="submit"`) with text "Log In".
Selector that works: `button:has-text('Log In')`.

---

## Automation Builder UI Patterns (From Screenshots)

### Confirmed from screenshot `brevo_d2_14_trigger_saved.png`:
- Trigger block shows: "Contact added to list" with "List The Neural Feed - Blog Subscribers - #3"
- Left panel shows Actions tab with draggable items: "Add contact to a list", "Send an email", etc.
- "Drop block here" slot appears BELOW the trigger block on canvas
- Actions tab is toggled via `button:has-text("Actions")`
- Triggers tab: `button:has-text("Triggers")`

### Canvas layout (1600px viewport):
- Left panel (actions/triggers/rules): x=0 to ~260px
- Canvas area: x > 350px
- Trigger block on canvas: approximately x=530, y=90

### Drag-and-drop challenges:

1. Standard `drag_to()` loses drag state when crossing element boundaries in Playwright
2. Step-by-step `mouse.move()` with 15 intermediate steps is more reliable
3. Must target "Drop block here" slot by exact bounding box coordinates
4. **CRITICAL BUG from prior attempts**: Clicking "Send an email" in the template picker
   WITHOUT being on the right canvas context navigates AWAY to the Brevo template editor
   (at `/templates`). This is why prior scripts ended up showing template HTML.

### Template picker flow:
1. Drag "Send an email" to drop slot
2. Config panel opens on left side automatically
3. Click "Add message" button in config panel
4. Template picker modal opens - list of existing templates
5. Click the template by name or index
6. Click "Use"/"Select" button to confirm
7. Click "Save" in config panel

### Wait step flow:
1. Drag "Wait" to drop slot
2. Config panel opens with `input[type="number"]` for duration
3. Set value and ensure unit is "Days" (not hours)
4. Click "Save"

---

## Workflow Details

### Automation ID: 4
URL: `https://app.brevo.com/automation/edit/4`
Name: "Neural Feed - Welcome Sequence"

### Template IDs (verified via API):
- ID 1: "Neural Feed - Email 1 - Welcome (Aether)" → send immediately
- ID 2: "Neural Feed - Email 2 - Jared's Story" → after 2 days
- ID 3: "Neural Feed - Email 3 - Aether Writes Directly" → after 2 days (day 4)
- ID 4: "Neural Feed - Email 4 - Partnership in Practice" → after 3 days (day 7)
- ID 5: "Neural Feed - Email 5 - The Context Tax" → after 3 days (day 10)
- ID 6: "Neural Feed - Email 6 - Social Proof & Results" → after 4 days (day 14)
- ID 7: "Neural Feed - Email 7 - The Invitation" → after 4 days (day 18)

### Trigger:
- Type: "Contact added to a list"
- List: List 3 - "The Neural Feed - Blog Subscribers"
- API-confirmed: 3 current subscribers

---

## Script Architecture

### File: `tools/setup_neural_feed_automation.py`

Key functions:
- `load_session()` / `save_session()` - session reuse to minimize 2FA
- `do_login_and_2fa()` - full login with Gmail IMAP 2FA code extraction
- `check_existing_automations()` - duplicate prevention, checks list page + edit/4 URL
- `setup_trigger()` - configures the trigger block on canvas
- `drag_action_to_canvas()` - step-by-step mouse drag with 15 intermediate steps
- `configure_email_step()` - opens template picker, selects template, saves
- `configure_wait_step()` - sets delay duration in days, saves
- `build_email_sequence()` - iterates EMAIL_SEQUENCE, adds waits + emails
- `activate_automation()` - clicks Activate, confirms dialog
- `run()` - main orchestrator with --dry-run and --fresh-login flags

### CLI flags:
```bash
python3 tools/setup_neural_feed_automation.py           # Normal run
python3 tools/setup_neural_feed_automation.py --dry-run # Check state only
python3 tools/setup_neural_feed_automation.py --fresh-login # Force new login
```

---

## What Prior Attempts Taught Us

| Attempt | What Worked | What Failed |
|---------|------------|-------------|
| `create_brevo_workflow.py` | API endpoint discovery | API 404s on all automation endpoints |
| `create_brevo_workflow_v3.py` | Login + 2FA flow confirmed | Builder drag-and-drop not reached |
| `brevo_final_build.py` | Trigger configured via combobox | All drag steps showed "drag_failed" |
| `brevo_definitive.py` | Session reuse (44 cookies) | Ended up in template editor instead |
| `brevo_d2_14_trigger_saved.png` | **Trigger successfully saved!** | Email drags still failing |

The trigger configuration approach works. The email sequence drag-and-drop is the unsolved challenge.

---

## Recommended Alternative: Manual Setup

Given the drag-and-drop fragility, if the script fails on the email sequence step,
here is the exact manual procedure:

1. Login to Brevo → Automations → find "Neural Feed - Welcome Sequence"
2. Click the trigger block → select "The Neural Feed - Blog Subscribers" → Save
3. Actions tab → drag "Send an email" to Drop slot → Add message → select Template 1 → Save
4. Actions tab → drag "Wait" → 2 days → Save
5. Actions tab → drag "Send an email" → Template 2 → Save
6. Repeat for each email with the delays in EMAIL_SEQUENCE
7. Click "Activate automation"

---

## Files Changed

- `tools/setup_neural_feed_automation.py` - NEW (consolidated automation setup script)
- `tools/brevo_session.json` - UPDATED (refreshed session after 2FA login)

---

## Known Limitations

1. **Session short-lived**: Brevo sessions expire in minutes during headless automation.
   The script handles this by detecting expiry and re-doing login+2FA.

2. **Drag-and-drop fragile**: Brevo's React-based drag-and-drop doesn't respond well to
   Playwright's mouse simulation. May need a visual browser (non-headless) debugging session.

3. **No idempotency guarantee for sequence**: If the script is interrupted mid-sequence,
   some steps may be partially added. Run `--dry-run` first to check state.

4. **No Brevo automation API**: This is a fundamental limitation, not a script bug.
   Brevo does not expose their automation builder via REST API.
