# Support Email Configuration Update

**Date**: 2026-02-24
**Type**: operational
**Topic**: SUPPORT_EMAIL env var added, Jared's email corrected in CONTACTS.md

## What Was Done

Added `SUPPORT_EMAIL=support@puremarketing.ai` to `.env` and corrected Jared's
email in `.claude/CONTACTS.md` from `purebrain@puremarketing.ai` to
`jared@puretechnology.nyc`.

## Email Routing (Canonical - Locked In)

| Address | Purpose |
|---------|---------|
| `support@puremarketing.ai` | DEFAULT support - PayPal, contact forms, user-facing links |
| `jared@puretechnology.nyc` | Jared's personal email - CC, reply-to on automated emails |
| `purebrain@puremarketing.ai` | Aether's email - Brevo sender, system accounts, scripts |

## Files Changed

- `/home/jared/projects/AI-CIV/aether/.env` - Added `SUPPORT_EMAIL=support@puremarketing.ai` at end of file
- `/home/jared/projects/AI-CIV/aether/.claude/CONTACTS.md` - Corrected Jared's email entry + added update log entry

## No Script Changes

Python scripts and HTML files already use `support@puremarketing.ai` where
needed. The `.env` variable is available for any scripts that want to load it
via `os.environ.get('SUPPORT_EMAIL')` or dotenv.

## Memory Search Before Task

Found prior session entries confirming `support@puremarketing.ai` is the
established PayPal business email and user-facing support address going back
to 2026-02-18. Consistent with the update applied here.
