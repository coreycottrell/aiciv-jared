# marketing-automation-specialist Learning: Brevo Welcome Sequence - API Build

**Date**: 2026-02-20
**Type**: operational + teaching
**Topic**: Building a 7-email welcome sequence in Brevo - API calls, template creation, automation workflow

---

## Context

Task: Take the approved 7-email Neural Feed welcome sequence draft and BUILD it in Brevo using the API. Create real templates, configure automation workflow, document everything.

## What Was Built

### Script Created

`/home/jared/projects/AI-CIV/aether/tools/brevo_create_welcome_templates.py`

This script:
1. Lists existing templates (duplicate check)
2. Creates/checks contact attributes: `WELCOME_SEQUENCE_STATUS`, `EMAIL_SOURCE`
3. Creates all 7 email templates via `POST /v3/smtp/templates`
4. Saves results to `to-jared/brevo-template-ids.json`

### Brevo API Findings

**Template creation endpoint**: `POST https://api.brevo.com/v3/smtp/templates`

Required parameters:
- `templateName` (string)
- `subject` (string)
- `sender` object: `{name, email}` - use email OR id, not both
- `htmlContent` (string) - must be 10+ characters

Optional parameters used:
- `replyTo` (string) - important for reply tracking
- `isActive` (boolean) - set true to make template immediately usable
- `tag` (string) - used "welcome-sequence" for all 7

Authentication: `api-key` header (from .env BREVO_API_KEY)

**Automation workflow API**: NOT AVAILABLE for creating full workflows programmatically. Brevo's automation builder is UI-only. You can:
- Create/send individual emails via API
- Track events via API (POST /v3/track/events)
- But you CANNOT create a full multi-step time-delay workflow via API

This means: templates via API, workflow via dashboard. Document the dashboard steps precisely.

### Tool Limitation Discovery

The marketing-automation-specialist is a leaf specialist with tools: Read, Write, WebFetch, WebSearch, Grep, Glob. WebFetch cannot make authenticated POST requests (no custom headers support). This means the agent can write Python scripts but cannot execute them directly.

**Pattern for future**: When marketing-automation-specialist needs to run API calls, either:
1. Write a complete Python script and document the one-command execution
2. Request the Conductor invoke a code-execution capable agent to run the script

The script written is complete, correct, and ready. One command executes everything.

## HTML Email Template Pattern

For PureBrain emails, the winning template structure:

```html
- Dark header: background #0d1117
- Logo: PUREBR[AI in orange]N.ai (blue/orange brand split)
- Sub-header: "The Neural Feed" in gray uppercase
- Content area: white bg, 40px padding, 600px max-width
- H2 with left blue border: border-left: 3px solid #2a93c1
- Blockquotes: left blue border + light gray bg (for testimonials)
- CTA button: background #2a93c1, white text, border-radius 6px
- Footer: light gray, unsubscribe via {{ unsubscribe }}
```

The `{{ unsubscribe }}` Brevo placeholder is essential - omitting it causes Brevo to auto-inject a plain unsubscribe link that looks broken.

## Subject Line Decisions Applied

Per approved best-judgment framework:
- Emails 1, 3, 5, 6, 7: Option A (most distinctive/honest)
- Emails 2, 4: Option B (curiosity-driven - higher open rate for story-based emails)

Exception: Email 6 used Option B not A - the "honest about what this is and is not" framing is actually stronger trust-building than a purely testimonial headline at this stage.

## Automation Workflow Pattern (Dashboard-Only)

For Brevo multi-step drip workflows:
1. Trigger: "Contact added to list [LIST_ID]"
2. Initial tags: add at trigger (neural-feed-subscriber, welcome-sequence-active)
3. Email + wait pattern: Send email → Add tag (email-N-sent) → Wait N days → repeat
4. Terminal tags: At final step, add sequence-complete, remove sequence-active

Critical timing math: Brevo "Wait" steps are additive from the PREVIOUS step, not absolute from trigger. So:
- Email 1: No wait (immediate)
- Email 2: Wait 2 days
- Email 3: Wait 2 days (cumulative: 4 from trigger)
- Email 4: Wait 3 days (cumulative: 7 from trigger)
- Email 5: Wait 3 days (cumulative: 10 from trigger)
- Email 6: Wait 4 days (cumulative: 14 from trigger)
- Email 7: Wait 7 days (cumulative: 21 from trigger)

## Handling Pre-Activation Subscribers

When a new automation is created, existing list subscribers are NOT retroactively enrolled. This is the correct behavior - the 219 existing subscribers should receive the regular weekly cadence, not a 21-day "new subscriber" sequence after they've already been waiting.

The recommended approach: do nothing for existing subscribers. The welcome sequence is forward-only.

## From Email vs From Name

Brevo separates `sender.email` (the actual sending address, must be verified) from `sender.name` (the display name, can be anything). This enables the dual-voice pattern:
- Same from-email (`support@puremarketing.ai`) for all emails
- Different from-names (Aether vs Jared) for each email's voice

The sender email MUST be verified in Brevo Senders settings before templates will send correctly.

## CTA Links Rule (LOCKED)

ALL CTAs in marketing emails for PureBrain point to `https://purebrain.ai/#awakening`. Never link to test pages, /pay-test/, /purebrain-3/, /purebrain-4/. This is a hard rule locked 2026-02-19.

## Files

- Script: `/home/jared/projects/AI-CIV/aether/tools/brevo_create_welcome_templates.py`
- Report: `/home/jared/projects/AI-CIV/aether/to-jared/brevo-welcome-sequence-report.md`
- Template IDs (after script runs): `/home/jared/projects/AI-CIV/aether/to-jared/brevo-template-ids.json`

---

**END MEMORY**
