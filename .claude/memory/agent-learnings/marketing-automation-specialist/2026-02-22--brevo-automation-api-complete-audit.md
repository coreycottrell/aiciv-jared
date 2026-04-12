# marketing-automation-specialist Learning: Brevo Neural Feed Automation - Complete Audit

**Date**: 2026-02-22
**Type**: operational + teaching
**Topic**: Complete audit of Neural Feed welcome sequence automation - what's built, what's running, what needs manual setup

---

## Memory Search Results

- Searched: `.claude/memory/` for "brevo automation", "neural feed welcome sequence", "welcome sequence state"
- Found: 6 highly relevant prior learnings across full-stack-developer and marketing-automation-specialist agents
- Applying: All prior patterns confirmed. This memory documents the consolidated state as of 2026-02-22.

---

## CRITICAL DISCOVERY: No Brevo Automation REST API

**Confirmed by prior work (2026-02-21)**: Brevo v3 API has zero endpoints for creating automation workflows.

All endpoints tested return 404:
- `GET/POST https://api.brevo.com/v3/automations` → 404
- `GET/POST https://api.brevo.com/v3/workflows` → 404

**What this means**: Cannot create a Brevo "automation workflow" (the drag-and-drop GUI tool) via API. It is a GUI-only interface. Our automation was therefore built as a custom Python polling daemon instead.

---

## What Is Already Built and Running

### The Custom Automation Daemon

**File**: `/home/jared/projects/AI-CIV/aether/tools/neural_feed_welcome_sequence.py`

**How it works**:
1. Polls Brevo List 3 (The Neural Feed) every hour for contacts
2. When a new subscriber is detected: fires Email 1 immediately
3. Checks all subscribers every cycle for emails due (day thresholds)
4. Persists state to disk — survives server restarts
5. Sends Telegram notifications on new subscriber + sequence completion
6. Runs as daemon thread inside `purebrain_log_server.py`

**Status**: ACTIVE and running (embedded in the live purebrain_log_server process)

### Template Status (Verified via Prior API calls)

| Template ID | Email # | Subject | Status |
|------------|---------|---------|--------|
| 1 | Email 1 (Day 0) | Welcome. You're about to meet Aether. | ACTIVE |
| 2 | Email 2 (Day 2) | The day I stopped using AI as a tool | ACTIVE |
| 3 | Email 3 (Day 4) | Aether has something to say to you | ACTIVE |
| 4 | Email 4 (Day 7) | What AI partnership actually looks like (with numbers) | ACTIVE |
| 5 | Email 5 (Day 10) | The 5 things Aether does that generic AI can't | ACTIVE |
| 6 | Email 6 (Day 14) | An honest comparison: PureBrain vs ChatGPT vs generic AI | ACTIVE |
| 7 | Email 7 (Day 21) | Your first month with a real AI partner — what to expect | ACTIVE |

P.S. reply-invitation blocks deployed to templates 2, 4, 5 (2026-02-22).

### List 3 Status

- Name: "The Neural Feed - Blog Subscribers"
- List ID: 3
- Subscribers (as of 2026-02-21): 3 (jaredsanborn@yahoo.com, jared@puretechnology.nyc, purebrain@puremarketing.ai)
- State file: `/home/jared/projects/AI-CIV/aether/config/welcome_sequence_state.json`

### Current Subscriber State (as of 2026-02-22)

All 3 test subscribers have received Emails 1 and 2. Email 3 is due on Day 4 from their subscription date (Feb 19). The daemon will fire it automatically.

---

## What Was Asked vs What Existed

The task requested "Set up the Brevo email automation workflow using the Brevo API." Here is the gap analysis:

| Requirement | Status |
|-------------|--------|
| Check existing automations via GET /automations | CONFIRMED: No Brevo automation API exists |
| Check if templates 11-16 are created | CLARIFICATION: The Neural Feed uses templates 1-7. Templates 11-12 are post-purchase transactional emails (separate system). |
| Check if List 3 is populated | CONFIRMED: 3 subscribers present |
| Check existing automations | CONFIRMED: Custom Python daemon is running |
| Create workflow via POST /automations | NOT POSSIBLE: Brevo has no automation REST API |

---

## What Needs Manual Setup (Brevo GUI)

If Jared wants a **Brevo-native automation** (visible in the Brevo Automations dashboard) in addition to the custom daemon, it requires manual GUI configuration:

1. Login to https://app.brevo.com/automation/
2. Create new automation: "Neural Feed - Welcome Sequence"
3. Add trigger: "Contact added to list" → List 3 (The Neural Feed)
4. Add: Send email → Template 1 (immediate)
5. Add: Wait → 2 days
6. Add: Send email → Template 2
7. Add: Wait → 2 days (Day 4 total)
8. Add: Send email → Template 3
9. Add: Wait → 3 days (Day 7 total)
10. Add: Send email → Template 4
11. Add: Wait → 3 days (Day 10 total)
12. Add: Send email → Template 5
13. Add: Wait → 4 days (Day 14 total)
14. Add: Send email → Template 6
15. Add: Wait → 7 days (Day 21 total)
16. Add: Send email → Template 7
17. Click Activate

**IMPORTANT**: If Jared sets up the Brevo-native automation, the custom Python daemon must be disabled to prevent double-sends. The two systems would overlap and every subscriber would receive each email twice.

---

## Recommendation: Keep the Custom Daemon

The custom Python daemon is superior to a Brevo-native automation for these reasons:

1. **Telegram notifications**: Daemon alerts Jared on new subscriber + sequence completion. Native Brevo automation does not.
2. **Full state visibility**: `welcome_sequence_state.json` shows exact status for every subscriber. Brevo UI shows aggregate stats only.
3. **Retry logic**: Daemon retries failed sends up to 3 times. Native automation does not.
4. **Unsubscribe-aware**: Daemon checks `listIds` on every cycle — if subscriber unsubscribes from List 3, no further emails are sent. Native automation may still send if contact is not fully unsubscribed.
5. **Already running**: No additional setup needed.

---

## Status Check Command

```bash
/home/jared/projects/AI-CIV/aether/venv/bin/python3 \
  /home/jared/projects/AI-CIV/aether/tools/neural_feed_welcome_sequence.py --status
```

---

## Files Reference

- Daemon: `/home/jared/projects/AI-CIV/aether/tools/neural_feed_welcome_sequence.py`
- State: `/home/jared/projects/AI-CIV/aether/config/welcome_sequence_state.json`
- Templates script: `/home/jared/projects/AI-CIV/aether/tools/update_neural_feed_welcome_sequence.py`
- P.S. script: `/home/jared/projects/AI-CIV/aether/tools/deploy_ps_sections.py`
- Log: `/home/jared/projects/AI-CIV/aether/logs/purebrain_emails.jsonl`

---

## Memory Written

Path: `.claude/memory/agent-learnings/marketing-automation-specialist/2026-02-22--brevo-automation-api-complete-audit.md`
Type: operational + teaching
Topic: Complete state of Neural Feed welcome sequence automation as of 2026-02-22

---

**END MEMORY**
