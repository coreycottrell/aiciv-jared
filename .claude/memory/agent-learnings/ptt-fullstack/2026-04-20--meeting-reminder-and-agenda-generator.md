# Meeting Reminder Cron + Agenda Generator

**Date**: 2026-04-20
**Type**: operational
**Agent**: full-stack-developer

## What Was Built

### Feature 1: Day-Before Meeting Email Reminders
- Script: `tools/meeting_reminder_cron.py`
- Runs daily at 6pm ET (BOOP added)
- For each meeting happening TOMORROW, emails all assigned participants
- Gets participant list from `social.purebrain.ai/api/meetings/assignments` API
- Maps person IDs to emails via Google Sheets whitelist (spreadsheet `1HALg8Vxu-LtS6OVq_CeO1gT4vFBUKxjtyKpJcTKM_0E`) with hardcoded fallback
- Email via Gmail SMTP from purebrain@puremarketing.ai (BCC all, Jared in TO)
- Handles: regular weekly, daily Mon-Thu, first Monday of month, bi-weekly cadence
- Filters out AI-only emails (agentmail.to addresses) from BCC
- Flags: `--dry-run`, `--date YYYY-MM-DD` for testing

### Feature 2: Auto-Generate Agenda from Form Responses  
- Script: `tools/meeting_agenda_generator.py`
- Runs ~1hr before each meeting (BOOP added)
- Fetches responses from `social.purebrain.ai/api/meetings/responses/{meeting_id}`
- Generates agenda page matching existing purebrain-site style (dark theme, password gate)
- Deploys to `/meetings/{slug}/MMYYYY/index.html` via git commit + push
- Auto-extracts action items from blocker/risk fields
- Handles both present and absent responses gracefully
- Flags: `--dry-run`, `--meeting {id}`, `--date YYYY-MM-DD`

## Key Patterns
- Responses API currently returns 404 (endpoint not yet built in social-api worker)
- CF Worker already has a meeting cron using MS Graph (`sendDailyMeetingForms`)
- The Python scripts use Gmail SMTP instead (as specified), independent of the Worker cron
- TEAM_EMAIL_MAP in worker and Python script must stay in sync
- bi-weekly check uses ISO week parity (even weeks = on)
- Monthly-first check: day <= 7

## Files
- `/home/jared/projects/AI-CIV/aether/tools/meeting_reminder_cron.py`
- `/home/jared/projects/AI-CIV/aether/tools/meeting_agenda_generator.py`
- BOOP entries added to `.claude/scheduled-tasks-state.json`
