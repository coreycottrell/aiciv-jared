# marketing-automation-specialist Learning: Brevo 90-Day Roadmap Implementation Plan

**Date**: 2026-02-23
**Type**: operational + teaching
**Topic**: Complete Brevo automation implementation plan — RSS email, UTM template, behavioral triggers, re-engagement sequence

---

## Memory Search Results

- Searched: `.claude/memory/agent-learnings/marketing-automation-specialist/` for "brevo automation", "rss", "utm", "re-engagement", "behavioral triggers"
- Found: 5 prior learnings applied:
  - `2026-02-22--brevo-automation-api-complete-audit.md` — confirmed no Brevo REST API for workflows
  - `2026-02-22--audit-lead-nurture-sequence.md` — 4-email audit nurture design patterns
  - `2026-02-20--brevo-welcome-sequence-build.md` — template creation API, HTML pattern
  - `2026-02-22--ps-reply-invitations-neural-feed.md` — P.S. engagement patterns
  - `2026-02-20--neural-feed-welcome-sequence.md` — welcome sequence architecture

---

## What Was Built

### Output File

`/home/jared/projects/AI-CIV/aether/exports/brevo-automation-plan.md`

### Plan Contents (4 Items)

#### Item 1: RSS-to-Email Automation

- **Primary approach**: Brevo native RSS campaign (dashboard only) — fastest, zero maintenance
- **Fallback**: Custom Python daemon at `tools/rss_to_email.py`
- Complete HTML email template with PureBrain dark theme (tested pattern from prior sessions)
- UTM-tagged links: `utm_source=newsletter&utm_medium=email&utm_campaign=neural-feed-rss`
- State file: `config/rss_email_state.json` for daemon approach

#### Item 2: UTM Parameter Master Template

- Full `utm_source` taxonomy: newsletter, welcome-sequence, audit-nurture, blog, linkedin, bluesky, assessment, audit, purebrain, organic, referral
- Full `utm_medium` taxonomy: email, social, website, cta, referral
- Full `utm_campaign` taxonomy: all campaigns mapped
- Pre-built copy-paste URL templates for every channel combination
- GA4 setup instructions for custom dimensions and exploration reports
- Governance rules: lowercase, hyphens not underscores, no spaces

#### Item 3: Behavioral Trigger Sequences

Three triggers designed:

1. **Pricing page / Awakening visit trigger**
   - JavaScript IntersectionObserver on `#awakening` section
   - Fires `awakening_section_viewed` Brevo tracking event
   - Requires Brevo site tracking code + `localStorage` email storage
   - 2-email sequence: ROI reframe (Email 1, immediate) → Objection handler (Email 2, 48 hours)
   - Template creation script: `tools/brevo_create_pricing_intent_templates.py`

2. **Assessment abandonment trigger**
   - Fires `assessment_started` event on first question
   - Brevo automation: Wait 30 min → Check if `assessment_completed` → if not, send recovery emails
   - Critical dependency: Assessment must capture email at question 1 (not results page)
   - 2-email recovery sequence

3. **Email reply trigger**
   - Relies on human-liaison detecting replies to PureBrain emails
   - `log_email_reply()` function updates Brevo contact attributes via API
   - Tags replies as `email-2-reply`, `email-4-reply`, etc. for segmentation
   - Brevo automation tags repliers with `email-replier` and adds to List 10 (High Intent)

#### Item 4: Re-engagement Sequence (45-day inactive)

- **Trigger**: 45 days no open on List 3
- **Email 1** (Day 0): "We've missed you" — soft check-in, last 3 posts
- **Email 2** (Day 7): "What would bring you back?" — feedback request, single direct question
- **Email 3** (Day 21): "Last chance before we let you go" — sunset email with "Keep Me Subscribed" button
- `/stay-subscribed/` WordPress page needed — fires Brevo attribute update on load
- Template creation script: `tools/brevo_create_reengagement_templates.py`
- `re-engagement-sent` tag prevents double-enrollment
- Full HTML for all 3 emails included in plan

---

## Key Architectural Decisions

### Brevo Automation: GUI-Only (3x Confirmed)

Brevo REST API has no endpoints for creating automation workflows. Templates via API (`POST /v3/smtp/templates`) — workflows via dashboard only. This pattern is now permanently documented across 4 sessions (2026-02-20, 2026-02-21, 2026-02-22, 2026-02-23).

### Re-engagement 45-Day Window

21-day welcome sequence + 24 days of regular sends = first meaningful inactivity signal. 30 days is too soon (catches people who just finished welcome sequence). 60 days is too lenient (deliverability damage accumulates).

### Assessment Email Capture Position

Email must be captured at question 1, not at results page. Without this, abandonment tracking has no subject. This is a blocking dependency for Item 3B.

### UTM Architecture

- Use hyphens, not underscores (URL-safe, analytics-readable)
- All lowercase
- `utm_content` carries A/B test differentiators, not channel info

---

## Metrics Targets (Summary)

| Item | Primary Metric | Target |
|------|---------------|--------|
| RSS email | Open rate | > 25% |
| UTM coverage | Links with UTMs | 100% |
| Pricing intent | Email 1 open rate | > 50% |
| Assessment recovery | Completion rate after email | > 25% |
| Re-engagement | Re-subscribe rate (Email 3) | > 15% |

---

## Scripts to Create

| Script | Location | Status |
|--------|----------|--------|
| RSS daemon (fallback) | `tools/rss_to_email.py` | Plan written, needs execution |
| Pricing intent templates | `tools/brevo_create_pricing_intent_templates.py` | Plan written, needs execution |
| Re-engagement templates | `tools/brevo_create_reengagement_templates.py` | Plan written, needs execution |

All scripts are complete Python code in the plan file. Need full-stack-developer to execute them.

---

## Timeline

- Week 1-2: RSS email + UTM template distribution
- Week 3: Behavioral triggers (requires Brevo tracking code install on purebrain.ai first)
- Week 3-4: Re-engagement sequence

---

## Related Files

- Plan: `/home/jared/projects/AI-CIV/aether/exports/brevo-automation-plan.md`
- Config: `/home/jared/projects/AI-CIV/aether/config/audit_nurture_template_ids.json` (IDs 13-16)
- State: `/home/jared/projects/AI-CIV/aether/config/welcome_sequence_state.json`
- Welcome daemon: `/home/jared/projects/AI-CIV/aether/tools/neural_feed_welcome_sequence.py`

---

## Memory Written

Path: `.claude/memory/agent-learnings/marketing-automation-specialist/2026-02-23--brevo-90day-roadmap-implementation-plan.md`
Type: operational + teaching
Topic: Complete Brevo automation plan — RSS, UTM, behavioral triggers, re-engagement

---

**END MEMORY**
