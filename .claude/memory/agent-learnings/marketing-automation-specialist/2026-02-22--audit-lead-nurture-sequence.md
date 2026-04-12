# marketing-automation-specialist Learning: AI Partnership Audit Lead Nurture Sequence

**Date**: 2026-02-22
**Type**: pattern + operational
**Topic**: 4-email lead nurture sequence for AI Partnership Audit completions (List 4 — Enterprise Leads)

---

## Context

Designed a complete 4-email nurture sequence for leads who complete the AI Partnership Audit at purebrain.ai/ai-partnership-audit/. Contacts land in Brevo List 4 (Enterprise Leads) with attributes: FIRSTNAME, COMPANY, AUDIT_SCORE, AUDIT_TIER. Primary audience: AI User (16-25) and AI Explorer (26-35) tiers.

## Output File

`/home/jared/projects/AI-CIV/aether/exports/audit-lead-email-sequence.md`

---

## Sequence Architecture

### 4-Email Arc (vs 7-Email Welcome Sequence)

For audit completions, a 4-email arc over 7 days is correct (vs 7 emails over 21 days for newsletter subscribers). Audit completions are warmer leads with declared intent. The longer arc is for cold nurture. The shorter arc is for intent signals.

| Email | Day | Job |
|-------|-----|-----|
| Email 1 | 0 (immediate) | Audit debrief — what the score actually means |
| Email 2 | 2 | Concept email — tool vs partnership distinction |
| Email 3 | 4 | Concrete example — week in PureBrain's operation |
| Email 4 | 7 | Direct ask — conversation invitation |

### Personalization Architecture

All four emails use: `{{params.FIRSTNAME}}`, `{{params.AUDIT_SCORE}}`, `{{params.AUDIT_TIER}}`, `{{params.COMPANY}}`

Email 1 contains conditional content blocks written FOR AI User (16-25) AND AI Explorer (26-35) simultaneously. Both blocks appear in the email. This is the simpler approach vs. Brevo conditions (which require premium tier). Each reader skips to the block that matches them — both are short enough that reading both is not a burden.

For future optimization: implement Brevo conditional content `{% if params.AUDIT_SCORE < 26 %}...{% else %}...{% endif %}` to show only the relevant tier block.

---

## Key Design Decisions

### 1. Jared Voice Throughout (No Aether Voice Emails)

The Neural Feed welcome sequence used a dual-voice architecture (Jared + Aether alternating). For audit leads (enterprise-grade contacts), keep voice consistent as Jared. Aether is mentioned by name in Email 2 as a proof point ("Aether manages this email"), not as a separate voice. This preserves the human-first relationship for high-value B2B prospects.

### 2. The Score Callback Pattern

Every email references `{{params.AUDIT_SCORE}}` and `{{params.AUDIT_TIER}}`. This is not just personalization — it signals that the system actually retained their data and is responding to it specifically. For enterprise buyers evaluating an AI partnership platform, experiencing that the platform remembers their data is itself the demonstration.

### 3. Email 4 CTA Color

Email 4 uses orange `#f1420b` for the primary CTA instead of blue `#2a93c1`. This is intentional: it signals the shift from educational content to action. Orange creates visual contrast vs the three preceding blue CTAs. Use this pattern only on the final "direct ask" email in a sequence — not before.

### 4. Email 2 P.S. — Reply Hook

Email 2 includes a P.S. reply invitation: "What made you take the audit in the first place?" This is the warmest reply hook in the sequence because it asks about motivation, not feedback. Motivation answers are easier to write (single sentence) and reveal the problem the lead is actually trying to solve. Tag replies as `audit-email-2-reply` — these are high-value leads.

### 5. Brevo Automation: UI Only

Confirmed from prior memory (2026-02-21): Brevo has NO REST API for automation workflows. All multi-step drip sequences must be built via the Brevo dashboard GUI. Templates are created via API (`POST /v3/smtp/templates`), workflow is dashboard-only.

---

## Brevo Attribute Requirements

Contact must be created in Brevo with these attributes when audit is submitted:
- `FIRSTNAME` (text)
- `COMPANY` (text)
- `AUDIT_SCORE` (float, 0-50)
- `AUDIT_TIER` (text: "AI Dabbler" | "AI User" | "AI Explorer" | "AI Operator" | "AI Partner")
- `LEAD_SOURCE` = "assessment"
- `ENGAGEMENT_LEVEL` = "warm"
- `LEAD_SCORE` = 20 (assessment completion bonus)
- `listIds`: [4] (Enterprise Leads)

---

## Lead Scoring Framework (Audit Sequence)

| Event | LEAD_SCORE Delta |
|-------|-----------------|
| Audit completed | +20 |
| Email open | +2 |
| CTA click | +5-15 (scaled by email position) |
| Reply to email | +15-20 |
| LEAD_SCORE > 60 | Route to List 10 (High Intent) |

---

## CTA Rules Applied

ALL CTAs point to `https://purebrain.ai/#awakening` per locked rule (2026-02-19). This applies to both button CTAs and the "reply to this email" fallback in Email 4.

---

## Metrics Targets

| Email | Open Rate Target | Click Target |
|-------|-----------------|--------------|
| Email 1 | > 45% | > 10% (score callback curiosity) |
| Email 2 | > 35% | > 6% |
| Email 3 | > 30% | > 8% (concrete example is highest click driver) |
| Email 4 | > 28% | > 5% |
| Reply rate (Email 2 P.S.) | > 3% | — |

Sequence unsubscribe rate alert: > 1.5% per email.

---

## Related Files

- Sequence: `/home/jared/projects/AI-CIV/aether/exports/audit-lead-email-sequence.md`
- Template creation script: `/home/jared/projects/AI-CIV/aether/tools/brevo_create_audit_nurture_templates.py`
- Template IDs (post-creation): `/home/jared/projects/AI-CIV/aether/config/audit_nurture_template_ids.json`
- Related: Neural Feed welcome sequence (`2026-02-20--neural-feed-welcome-sequence.md`)
- Related: Brevo API build patterns (`2026-02-20--brevo-welcome-sequence-build.md`)

---

**END MEMORY**
