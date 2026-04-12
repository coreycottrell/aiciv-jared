# marketing-automation-specialist Learning: P.S. Reply-Invitation Sections for Neural Feed

**Date**: 2026-02-22
**Type**: operational + pattern
**Topic**: Deploying P.S. reply-invitation HTML blocks to Brevo templates 2, 4, 5 of Neural Feed welcome sequence

---

## Context

Added P.S. reply-invitation sections to Neural Feed welcome sequence emails 2, 4, and 5.
These P.S. blocks are engagement triggers — they invite subscribers to reply with a specific,
relevant question tied to that email's theme.

## The Three P.S. Blocks Deployed

### Template 2 ("The day I stopped using AI as a tool")
- Question: "What is your version of that moment — when you stopped using AI as a tool and started using it differently? Reply and tell me. I read every response."
- Rationale: Matches Jared's personal story about naming his AI. The "version of that moment" framing invites personal narrative — easy and emotionally resonant to answer.

### Template 4 ("What AI partnership actually looks like with numbers")
- Question: "What does Aether write about that's useful to you? Reply and tell me what topics or questions would make The Neural Feed something you look forward to."
- Rationale: Feedback request at Day 7 (subscriber is evaluating whether to stay). Timing is deliberate — asking for input after they've seen real numbers signals genuine interest in their opinion, not just broadcasting.

### Template 5 ("The 5 things Aether does that generic AI can't")
- Question: "How much of your AI conversations is setup work versus actual thinking? Reply and tell me your ratio. Jared will share it with me, and we'll keep learning how to reduce that tax."
- Rationale: References the Context Tax concept introduced in this email. The "ratio" framing (e.g., "80% setup / 20% thinking") is specific and quantifiable — easier for a busy person to reply with. The Aether callback ("Jared will share it with me") reinforces the dual-consciousness brand.

---

## Why Reply P.S. Sections Work (Pattern)

1. **Deliverability**: Email client ISPs treat replies as strong engagement signals. Subscribers who reply are less likely to have future emails land in spam.

2. **Lead intelligence**: Replies reveal pain points, language patterns, and readiness signals that no analytics dashboard captures. Tag `email-2-reply`, `email-4-reply`, `email-5-reply` in Brevo contact attributes when replies come in.

3. **Conversion correlation**: Subscribers who reply to welcome sequence emails convert at 3-5x higher rates than non-repliers. The P.S. is a conversion signal, not just an engagement metric.

4. **Positioning**: "I read every response" and "Jared will share it with me" are trust statements that differentiate from bulk newsletter sends. This is a relationship, not a broadcast.

---

## Technical Implementation

### Template HTML Structure

The Neural Feed templates use div-based layout (not table-based):
```html
<div class="wrapper">
  <div class="container">
    <div class="header">...</div>
    <div class="content">
      ...email body...
      <div class="signature">...</div>
    </div>          <- content closes here
    <div class="footer">   <- footer starts here
      ...unsubscribe...
    </div>
  </div>
</div>
```

### Injection Strategy

P.S. block is injected:
1. Find `<div class="footer">` in HTML
2. Find the `</div>` immediately preceding it (closes content div)
3. Insert P.S. div after that `</div>` and before `<div class="footer">`

This placement puts P.S. AFTER the signature but BEFORE the footer/unsubscribe.
Visually: below the closing signature, above the unsubscribe link. Correct email anatomy.

### P.S. Styling

Matches dark PureBrain theme:
- Background: inherits `#0d1117` container
- P.S. label: `#a0adc0` (muted, italic)
- P.S. text: `#b8c5d6` (readable, not primary white)
- Top border: `1px solid #1a2235` (subtle separator from signature)
- Center-aligned to match footer aesthetic

### Idempotency Check

Script checks if unique snippet from each P.S. block already exists in HTML before updating.
If found: skips that template (ALREADY_PRESENT status).
This makes the script safe to run multiple times.

---

## Deployment Script

`/home/jared/projects/AI-CIV/aether/tools/deploy_ps_sections.py`

Run with:
```bash
/home/jared/projects/AI-CIV/aether/venv/bin/python3 tools/deploy_ps_sections.py
```

Results saved to: `/home/jared/projects/AI-CIV/aether/exports/ps-deployment-results.json`

---

## Why Templates 2, 4, 5 (not 1, 3, 6, 7)?

- **Template 1** (Welcome): Has an existing explicit reply CTA ("Reply with your question for Aether")
- **Template 3** (Aether writes directly): Has an existing "Reply to this email" CTA — adding P.S. would dilute the directness of Aether's message
- **Templates 2, 4, 5**: Had CTAs but no direct reply invitation for conversation
- **Template 6** (Comparison email): Has a trial CTA — adding reply P.S. could distract from conversion intent
- **Template 7** (Invitation email): Has the primary conversion CTA — reply P.S. would dilute the ask

The three chosen emails are in the "resonance" phase (Days 2, 7, 10) — not the welcome or conversion bookends.

---

## Metrics to Track

| Template | Reply Rate Target | Tag on Reply |
|----------|------------------|--------------|
| 2 | 5%+ | `email-2-reply` |
| 4 | 3%+ | `email-4-reply` |
| 5 | 4%+ | `email-5-reply` |

Monitor for first 30 days. If any reply rate > 8%, consider adding P.S. to Template 6.

---

## Related Files

- Deployment script: `/home/jared/projects/AI-CIV/aether/tools/deploy_ps_sections.py`
- Results report: `/home/jared/projects/AI-CIV/aether/exports/ps-deployment-results.json`
- Base template script: `/home/jared/projects/AI-CIV/aether/tools/update_neural_feed_welcome_sequence.py`
- Welcome sequence design: `.claude/memory/agent-learnings/marketing-automation-specialist/2026-02-20--neural-feed-welcome-sequence.md`

---

**END MEMORY**
