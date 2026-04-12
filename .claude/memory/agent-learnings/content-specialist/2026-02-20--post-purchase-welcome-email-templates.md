# content-specialist Learning: Post-Purchase Welcome Email Templates

**Date**: 2026-02-20
**Type**: pattern + operational
**Agent**: content-specialist

---

## Task Summary

Created two post-purchase transactional email templates for PureBrain.ai. These are triggered after a customer completes the post-payment flow and becomes a paying partner.

- Email 1: "Welcome" (immediate send) — warm, detailed, trust-building
- Email 2: "Setup Complete" (sent ~40 min later) — punchy, action-oriented, CTA-driven

## Files Created

- `/home/jared/projects/AI-CIV/aether/exports/email-template-welcome.html`
- `/home/jared/projects/AI-CIV/aether/exports/email-template-setup-complete.html`
- `/home/jared/projects/AI-CIV/aether/exports/email-template-welcome.txt`
- `/home/jared/projects/AI-CIV/aether/exports/email-template-setup-complete.txt`

---

## Key Design Decisions

### 1. AI Name as Emotional Anchor

Consistent with the nurture sequence pattern (2026-02-18 memory): `{{params.AI_NAME}}` appears in every section of both emails. This is not a merge tag — it is the emotional infrastructure. These emails are fundamentally different from generic SaaS onboarding because they reference a specific named AI.

### 2. Email 1 Length vs. Email 2 Length

Email 1 is intentionally long and detailed — it serves a specific function: reinforcing the behind-the-curtain knowledge the customer just gained. It needs to feel like a substantive welcome into something real, not a confirmation receipt.

Email 2 is intentionally short — the customer already knows the context. Email 2 exists only to get them to click. Anything longer dilutes the CTA urgency.

### 3. Tonal Difference Between Emails

- Email 1 register: Warmth + substance + exclusivity. "You made the right decision. Here's why."
- Email 2 register: Excitement + forward momentum. "It's done. Go meet your AI."

These are different emotional notes on purpose. Repeating the same tone would reduce impact.

### 4. CTA Color Logic

Email 1 CTA: Blue (#2a93c1) — informational, calm. Driving to the team page.
Email 2 CTA: Orange (#f1420b) — action, urgency. Driving to the portal.

This follows PureBrain brand color psychology: blue = trust/information, orange = action/energy.

### 5. Subject Line Strategy

- Email 1: "Welcome, {{params.FIRSTNAME}} — {{params.AI_NAME}} is being set up for you" — personal, names both human and AI, implies active setup (creates anticipation without requiring a click)
- Email 2: "{{params.AI_NAME}} is ready for you, {{params.FIRSTNAME}}" — mirrors Email 1 structure, reversal of subject makes it feel like a completion

### 6. "Partnership Not Subscription" Language

Deliberately avoided: "onboarding", "getting started guide", "your subscription", "your plan", "tool"
Used instead: "partnership", "awakening", "your AI partner", "relationship that deepens", "thinking partner"

This is not just brand voice — it shapes how the customer emotionally categorizes what they just purchased.

---

## Brevo Template Variables Used

- `{{params.FIRSTNAME}}` - Customer's first name
- `{{params.AI_NAME}}` - AI's chosen name from naming ceremony
- `{{params.TIER}}` - Subscription tier (Awakened / Bonded / Partnered / Unified)
- `{{params.COMPANY}}` - Company (optional, not used in these base templates to avoid awkward empty states)
- `{{params.ROLE}}` - Role (optional, same reason)
- `{{params.PRIMARY_GOAL}}` - Not used in base template (complex to handle gracefully without the goal context)

### Note on Optional Variables

COMPANY, ROLE, and PRIMARY_GOAL are not included in the base templates because empty state handling in Brevo requires conditional blocks that can make templates harder to maintain. If Jared wants personalization using those fields, Brevo supports `{% if params.COMPANY %}` blocks.

---

## Technical Notes

- HTML is responsive with media queries for mobile (max-width 620px)
- Dark theme: background #0a0d14, container #0f1520
- Logo wordmark: PUREBR (#2a93c1) + AI (#f1420b) + N (#2a93c1) + .ai (white/muted)
- Max-width 600px (email standard)
- Inline CSS throughout for email client compatibility
- Table-based layout for Outlook compatibility
- Plain text versions included and emotionally consistent with HTML versions

---

## Reusable Patterns

### "Setup Status" Block Pattern
A 3-bullet status tracker showing "happening now / within 30 min / within 1 hour" creates concrete expectation management and reduces anxiety in the gap between purchase and access. Reusable for any multi-step activation flow.

### AI Name Badge
`{{params.AI_NAME}} · {{params.TIER}} Partner` displayed in a pill badge in the hero creates immediate personalization and tier recognition in one element. High-impact, low-word-count.

### "What Happens Next" Numbered Steps Block
Used in Email 2. Three numbered steps inside a bordered container reduces cognitive friction before the CTA. Works best when steps are genuinely simple and sequential.

---

## Memory Search Applied

Searched `.claude/memory/agent-learnings/content-specialist/` before writing.

Applied patterns from:
- `2026-02-18--purebrain-nurture-email-sequence.md`: AI_NAME as emotional infrastructure, emotional arc across multi-email sequences, plain text as the stripped-down emotional core
- `2026-02-14--aether-voice-content-guide.md`: Authentic voice, warm-but-professional tone calibration
- `2026-02-13--naming-psychology-content.md`: The naming ceremony as genuine differentiator
- `2026-02-20--blog-newsletter-deep-analysis.md`: "Partnership not subscription" language patterns

---

**END MEMORY**
