# Neural Feed 7-Email Welcome Sequence

**Date**: 2026-02-21
**Type**: operational
**Agent**: full-stack-developer
**Topic**: Created/updated all 7 Neural Feed welcome sequence Brevo email templates with full content per brief

---

## What Was Done

Updated Brevo templates 1-7 (Neural Feed welcome sequence) with complete email content matching the brief:
- Dark PureBrain theme (#080a12 bg, #e0e6f0 text, #2a93c1 blue, #f1420b orange)
- PureBrain hexagon icon in header
- Full content for each email (200-400 words each)
- Correct subjects, CTAs, and sender display

Also updated the verified sender record (ID:1) to show "Jared Sanborn" as display name.

---

## Template IDs and Schedule

| ID | Subject | Day | CTA |
|----|---------|-----|-----|
| 1  | Welcome. You're about to meet Aether. | 0 (immediate) | Reply with question for Aether |
| 2  | The day I stopped using AI as a tool | 2 | Reply: have you named your AI? |
| 3  | Aether has something to say to you | 4 | Reply - Aether-written email |
| 4  | What AI partnership actually looks like (with numbers) | 7 | Share with someone in AI fatigue |
| 5  | The 5 things Aether does that generic AI can't | 10 | Free AI Partnership Audit |
| 6  | An honest comparison: PureBrain vs ChatGPT vs generic AI | 14 | 14-day trial |
| 7  | Your first month with a real AI partner — what to expect | 18 | Start + 30-day refund guarantee |

---

## Brevo Sender Configuration

- **Only active verified sender**: `purebrain@puremarketing.ai` (Sender ID: 1)
- Display name updated to: "Jared Sanborn"
- Reply-to: `purebrain@puremarketing.ai`
- `jared@purebrain.ai` is NOT a verified Brevo sender - cannot be used as FROM

---

## Key Technical Patterns

### Template Update API

```python
PUT https://api.brevo.com/v3/smtp/templates/{id}
# 204 = success (empty body)
# Payload: name, subject, htmlContent, sender{name,email}, replyTo, isActive, tag
```

### Sender Record Update

```python
PUT https://api.brevo.com/v3/senders/{id}
# Updates display name for the sender
# "duplicate_parameter" error = misleading, update still succeeded
```

### HTML Template Structure

- Dark bg: `#080a12` (wrapper + header), `#0d1117` (container)
- Brand colors: blue `#2a93c1`, orange `#f1420b`
- PureBrain icon: `https://purebrain.ai/wp-content/uploads/2026/02/purebrain-icon-email.png`
- Logo text: `PUREBR<orange>AI</orange>N<white>.ai</white>`
- CTA button: orange `#f1420b` (not blue)

---

## Automation NOT Set Up Yet

Templates are created and ready. Automation (Brevo workflow) to trigger sequence when contact
added to List 3 is NOT configured yet. That is a separate task.

---

## Files

- **Script**: `/home/jared/projects/AI-CIV/aether/tools/update_neural_feed_welcome_sequence.py`
- **Template IDs JSON**: `/home/jared/projects/AI-CIV/aether/to-jared/welcome-sequence-template-ids.json`

---

## DO NOT TOUCH

- Templates 11, 12 = post-purchase transactional emails (separate system)
- Templates 8, 9, 10 = legacy/unused templates
- List 3 = The Neural Feed (blog subscribers trigger)
- List 8 = PureBrain Customers (post-purchase trigger)
