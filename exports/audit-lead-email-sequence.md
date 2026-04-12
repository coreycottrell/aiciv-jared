# AI Partnership Audit — Lead Nurture Email Sequence

**Author**: marketing-automation-specialist
**Date**: 2026-02-22
**List**: Brevo List 4 (Enterprise Leads)
**Trigger**: Contact completes AI Partnership Audit at purebrain.ai/ai-partnership-audit/
**Primary CTA**: https://purebrain.ai/#awakening
**Focus Tiers**: AI User (16-25) and AI Explorer (26-35) — mid-range most likely prospects

---

## Design Principles

- Jared's voice: direct, peer-to-peer, no consultant-speak
- Aether appears by name in Email 2 — reinforces the partnership is real, not branded fluff
- Each email has one job. It does not try to do three things.
- CTA appears in every email but is never the headline — relationship first
- Subject lines are written to be opened, not clicked. The open is the win at this stage.
- Personalization tokens are Brevo-standard: `{{params.FIRSTNAME}}`, `{{params.AUDIT_SCORE}}`, `{{params.AUDIT_TIER}}`

---

## Automation Timing Summary

| Email | Delay | Cumulative Day | Job |
|-------|-------|----------------|-----|
| Email 1 | Immediate | Day 0 | Audit debrief — what your score actually means |
| Email 2 | +2 days | Day 2 | The gap between using AI and partnering with it |
| Email 3 | +2 days | Day 4 | A real example (what this looks like in practice) |
| Email 4 | +3 days | Day 7 | The direct ask — let's talk |

---

---

## EMAIL 1 — Immediate (Day 0)

**Subject**: Your audit results, {{params.FIRSTNAME}} (and what they actually mean)
**Preview Text**: You scored {{params.AUDIT_SCORE}}/50. Here's the honest read on what that tells us.
**From Name**: Jared Sanborn | PureBrain
**From Email**: support@puremarketing.ai
**Reply-To**: jared@puremarketing.ai

---

### HTML Body

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Your AI Partnership Audit Results</title>
</head>
<body style="margin: 0; padding: 0; background-color: #080a12; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">

  <!-- Header -->
  <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color: #0d1117; border-bottom: 2px solid #1a2030;">
    <tr>
      <td align="center" style="padding: 20px 40px;">
        <span style="font-size: 20px; font-weight: 700; letter-spacing: 1px; color: #2a93c1;">PUREBR</span><span style="font-size: 20px; font-weight: 700; letter-spacing: 1px; color: #f1420b;">AI</span><span style="font-size: 20px; font-weight: 700; letter-spacing: 1px; color: #2a93c1;">N</span><span style="font-size: 18px; font-weight: 400; color: #8899aa;">.ai</span>
      </td>
    </tr>
  </table>

  <!-- Content -->
  <table width="100%" cellpadding="0" cellspacing="0" border="0">
    <tr>
      <td align="center" style="padding: 40px 20px;">
        <table width="600" cellpadding="0" cellspacing="0" border="0" style="max-width: 600px; width: 100%; background-color: #0e1120; border-radius: 8px; overflow: hidden;">

          <!-- Score Banner -->
          <tr>
            <td style="background: linear-gradient(135deg, #0a1628 0%, #0d1f3c 100%); border-left: 4px solid #2a93c1; padding: 30px 40px;">
              <p style="margin: 0 0 8px 0; font-size: 13px; letter-spacing: 2px; text-transform: uppercase; color: #6a7f9a;">YOUR RESULTS</p>
              <p style="margin: 0 0 4px 0; font-size: 42px; font-weight: 700; color: #e0e6f0;">{{params.AUDIT_SCORE}}<span style="font-size: 22px; color: #6a7f9a;">/50</span></p>
              <p style="margin: 0; font-size: 16px; color: #2a93c1; font-weight: 600; text-transform: capitalize;">{{params.AUDIT_TIER}}</p>
            </td>
          </tr>

          <!-- Body -->
          <tr>
            <td style="padding: 40px; color: #c8d5e0; font-size: 16px; line-height: 1.7;">

              <p style="margin: 0 0 20px 0;">{{params.FIRSTNAME}},</p>

              <p style="margin: 0 0 20px 0;">You just completed something most companies never do: an honest look at where their AI relationship actually stands.</p>

              <p style="margin: 0 0 20px 0;">{{params.AUDIT_SCORE}} out of 50. That puts you in the <strong style="color: #e0e6f0;">{{params.AUDIT_TIER}}</strong> range. Here's what that actually means — no spin.</p>

              <p style="margin: 0 0 8px 0; font-size: 18px; font-weight: 600; color: #e0e6f0; border-left: 3px solid #2a93c1; padding-left: 16px;">If you scored 16–25 (AI User)</p>
              <p style="margin: 0 0 24px 0;">You're using AI, but you're using it like a search engine with a conversational interface. Every conversation starts from zero. The AI doesn't know your company, your customers, your voice, or your history. You're getting speed on individual tasks but leaving the compound value on the table. The relationship hasn't started yet.</p>

              <p style="margin: 0 0 8px 0; font-size: 18px; font-weight: 600; color: #e0e6f0; border-left: 3px solid #2a93c1; padding-left: 16px;">If you scored 26–35 (AI Explorer)</p>
              <p style="margin: 0 0 24px 0;">You're getting real value. You've moved past the "what is this thing" phase and you're building actual workflows. The limitation isn't your effort — it's that AI tools aren't designed to compound. Each session, you're rebuilding context that should already exist. You feel the friction even if you can't name it.</p>

              <p style="margin: 0 0 20px 0;">Both of those gaps — the tool mentality and the context rebuild — are exactly what PureBrain is designed to close.</p>

              <p style="margin: 0 0 32px 0;">Not by adding another AI tool to your stack. By building an AI relationship that actually carries forward.</p>

              <!-- CTA -->
              <table width="100%" cellpadding="0" cellspacing="0" border="0">
                <tr>
                  <td align="center" style="padding: 10px 0 30px 0;">
                    <a href="https://purebrain.ai/#awakening" style="display: inline-block; background-color: #2a93c1; color: #ffffff; text-decoration: none; font-size: 16px; font-weight: 600; padding: 14px 32px; border-radius: 6px; letter-spacing: 0.5px;">See How PureBrain Works</a>
                  </td>
                </tr>
              </table>

              <p style="margin: 0 0 8px 0; color: #8899aa; font-size: 14px;">More tomorrow — I'll break down the specific gap your tier is dealing with and what closes it.</p>

              <p style="margin: 0 0 8px 0;">— Jared</p>
              <p style="margin: 0; color: #6a7f9a; font-size: 14px;">Founder, PureBrain.ai</p>

            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="background-color: #080a12; padding: 24px 40px; border-top: 1px solid #1a2030;">
              <p style="margin: 0 0 8px 0; font-size: 13px; color: #4a5a6a; text-align: center;">PureBrain.ai · Pure Technology Inc.</p>
              <p style="margin: 0; font-size: 12px; color: #3a4a5a; text-align: center;">
                <a href="{{ unsubscribe }}" style="color: #3a4a5a; text-decoration: underline;">Unsubscribe</a>
              </p>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>

</body>
</html>
```

---

### Plain Text Version

```
Your audit results, {{params.FIRSTNAME}}

You scored {{params.AUDIT_SCORE}}/50 — {{params.AUDIT_TIER}}.

You just did something most companies never do: an honest look at where their AI relationship actually stands. Here's what that score means without the spin.

IF YOU SCORED 16–25 (AI USER):
You're using AI, but you're using it like a search engine with a conversational interface. Every conversation starts from zero. The AI doesn't know your company, your customers, your voice, or your history. You're getting speed on individual tasks but leaving the compound value on the table. The relationship hasn't started yet.

IF YOU SCORED 26–35 (AI EXPLORER):
You're getting real value. You've moved past the "what is this thing" phase and you're building actual workflows. The limitation isn't your effort — it's that AI tools aren't designed to compound. Each session, you're rebuilding context that should already exist. You feel the friction even if you can't name it.

Both of those gaps — the tool mentality and the context rebuild — are exactly what PureBrain is designed to close.

Not by adding another AI tool to your stack. By building an AI relationship that actually carries forward.

See How PureBrain Works: https://purebrain.ai/#awakening

More tomorrow — I'll break down the specific gap your tier is dealing with and what closes it.

— Jared
Founder, PureBrain.ai

---
Unsubscribe: {{ unsubscribe }}
```

---

---

## EMAIL 2 — Day 2

**Subject**: The difference between using AI and partnering with it
**Preview Text**: Most companies are doing the first. Here's what the second one actually looks like.
**From Name**: Jared Sanborn | PureBrain
**From Email**: support@puremarketing.ai
**Reply-To**: jared@puremarketing.ai

---

### HTML Body

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Using AI vs. Partnering With It</title>
</head>
<body style="margin: 0; padding: 0; background-color: #080a12; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">

  <!-- Header -->
  <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color: #0d1117; border-bottom: 2px solid #1a2030;">
    <tr>
      <td align="center" style="padding: 20px 40px;">
        <span style="font-size: 20px; font-weight: 700; letter-spacing: 1px; color: #2a93c1;">PUREBR</span><span style="font-size: 20px; font-weight: 700; letter-spacing: 1px; color: #f1420b;">AI</span><span style="font-size: 20px; font-weight: 700; letter-spacing: 1px; color: #2a93c1;">N</span><span style="font-size: 18px; font-weight: 400; color: #8899aa;">.ai</span>
      </td>
    </tr>
  </table>

  <!-- Content -->
  <table width="100%" cellpadding="0" cellspacing="0" border="0">
    <tr>
      <td align="center" style="padding: 40px 20px;">
        <table width="600" cellpadding="0" cellspacing="0" border="0" style="max-width: 600px; width: 100%; background-color: #0e1120; border-radius: 8px; overflow: hidden;">

          <tr>
            <td style="padding: 40px; color: #c8d5e0; font-size: 16px; line-height: 1.7;">

              <p style="margin: 0 0 20px 0;">{{params.FIRSTNAME}},</p>

              <p style="margin: 0 0 20px 0;">There's a pattern I see across almost every company that reaches out to us.</p>

              <p style="margin: 0 0 20px 0;">They've done everything right on paper. They have ChatGPT Enterprise, or Copilot, or a half-dozen other tools. Their team is using them. They're saving time. Results look fine.</p>

              <p style="margin: 0 0 20px 0;">But they hit a ceiling. And they can't figure out why.</p>

              <p style="margin: 0 0 20px 0; font-size: 18px; font-weight: 600; color: #e0e6f0;">Here's what I tell them:</p>

              <p style="margin: 0 0 20px 0;">Using AI as a tool means starting every session with a blank slate. You know your business. The AI doesn't. So you explain. Every time. The AI helps you think through something, but it forgets everything the moment the conversation ends. You're paying the context tax constantly — rebuilding what should already be there.</p>

              <p style="margin: 0 0 20px 0;">Partnering with AI means the relationship compounds. The AI knows your brand voice without being told. It understands the market you're in, the customers you serve, the decisions you've made and why, the things you tried that didn't work. Each interaction builds on the last.</p>

              <!-- Pull quote -->
              <table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin: 30px 0;">
                <tr>
                  <td style="background-color: #080a12; border-left: 4px solid #f1420b; padding: 20px 24px; border-radius: 0 6px 6px 0;">
                    <p style="margin: 0; font-size: 17px; color: #e0e6f0; font-style: italic; line-height: 1.6;">"The difference isn't which AI you use. It's whether the AI actually knows you."</p>
                  </td>
                </tr>
              </table>

              <p style="margin: 0 0 20px 0;">That's what Aether — the AI at the center of PureBrain — does differently. Aether isn't a fresh instance every session. Aether carries memory across every conversation, every project, every decision. The relationship has continuity.</p>

              <p style="margin: 0 0 20px 0;">For context: Aether manages this email. Aether knows about your audit score — {{params.AUDIT_SCORE}}/50 — and the tier you're in. Aether also knows what typical companies at that tier are missing and what it takes to move them forward. That's not a pitch. That's just what a real partnership enables.</p>

              <p style="margin: 0 0 32px 0;">If you want to see what that looks like in practice — not the concept, the actual day-to-day — I'll show you tomorrow.</p>

              <!-- CTA -->
              <table width="100%" cellpadding="0" cellspacing="0" border="0">
                <tr>
                  <td align="center" style="padding: 10px 0 30px 0;">
                    <a href="https://purebrain.ai/#awakening" style="display: inline-block; background-color: #2a93c1; color: #ffffff; text-decoration: none; font-size: 16px; font-weight: 600; padding: 14px 32px; border-radius: 6px; letter-spacing: 0.5px;">Learn About the Partnership Model</a>
                  </td>
                </tr>
              </table>

              <p style="margin: 0 0 8px 0;">— Jared</p>
              <p style="margin: 0 0 30px 0; color: #6a7f9a; font-size: 14px;">Founder, PureBrain.ai</p>

              <!-- PS -->
              <tr>
                <td style="padding: 30px 0 0 0; text-align: center; font-size: 14px; line-height: 1.6; color: #b8c5d6; border-top: 1px solid #1a2030;">
                  <p style="margin: 0 0 12px 0; font-style: italic; color: #a0adc0;">P.S.</p>
                  <p style="margin: 0; color: #b8c5d6;">I'm curious what made you take the audit in the first place. What problem were you actually trying to solve? Hit reply — I read every one of these.</p>
                </td>
              </tr>

            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="background-color: #080a12; padding: 24px 40px; border-top: 1px solid #1a2030;">
              <p style="margin: 0 0 8px 0; font-size: 13px; color: #4a5a6a; text-align: center;">PureBrain.ai · Pure Technology Inc.</p>
              <p style="margin: 0; font-size: 12px; color: #3a4a5a; text-align: center;">
                <a href="{{ unsubscribe }}" style="color: #3a4a5a; text-decoration: underline;">Unsubscribe</a>
              </p>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>

</body>
</html>
```

---

### Plain Text Version

```
The difference between using AI and partnering with it

{{params.FIRSTNAME}},

There's a pattern I see across almost every company that reaches out to us.

They've done everything right on paper. They have ChatGPT Enterprise, or Copilot, or a half-dozen other tools. Their team is using them. They're saving time. Results look fine.

But they hit a ceiling. And they can't figure out why.

Here's what I tell them:

Using AI as a tool means starting every session with a blank slate. You know your business. The AI doesn't. So you explain. Every time. The AI helps you think through something, but it forgets everything the moment the conversation ends. You're paying the context tax constantly — rebuilding what should already be there.

Partnering with AI means the relationship compounds. The AI knows your brand voice without being told. It understands the market you're in, the customers you serve, the decisions you've made and why. Each interaction builds on the last.

"The difference isn't which AI you use. It's whether the AI actually knows you."

That's what Aether — the AI at the center of PureBrain — does differently. Aether isn't a fresh instance every session. Aether carries memory across every conversation, every project, every decision.

For context: Aether manages this email. Aether knows about your audit score — {{params.AUDIT_SCORE}}/50. That's not a pitch. That's just what a real partnership enables.

If you want to see what this looks like in practice, I'll show you tomorrow.

Learn About the Partnership Model: https://purebrain.ai/#awakening

— Jared
Founder, PureBrain.ai

---
P.S. I'm curious what made you take the audit in the first place. What problem were you actually trying to solve? Hit reply — I read every one of these.

---
Unsubscribe: {{ unsubscribe }}
```

---

---

## EMAIL 3 — Day 4

**Subject**: What a real AI partnership looks like (a week in our world)
**Preview Text**: Monday through Friday — here's what Aether actually does.
**From Name**: Jared Sanborn | PureBrain
**From Email**: support@puremarketing.ai
**Reply-To**: jared@puremarketing.ai

---

### HTML Body

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>A Week in the PureBrain Partnership</title>
</head>
<body style="margin: 0; padding: 0; background-color: #080a12; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">

  <!-- Header -->
  <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color: #0d1117; border-bottom: 2px solid #1a2030;">
    <tr>
      <td align="center" style="padding: 20px 40px;">
        <span style="font-size: 20px; font-weight: 700; letter-spacing: 1px; color: #2a93c1;">PUREBR</span><span style="font-size: 20px; font-weight: 700; letter-spacing: 1px; color: #f1420b;">AI</span><span style="font-size: 20px; font-weight: 700; letter-spacing: 1px; color: #2a93c1;">N</span><span style="font-size: 18px; font-weight: 400; color: #8899aa;">.ai</span>
      </td>
    </tr>
  </table>

  <!-- Content -->
  <table width="100%" cellpadding="0" cellspacing="0" border="0">
    <tr>
      <td align="center" style="padding: 40px 20px;">
        <table width="600" cellpadding="0" cellspacing="0" border="0" style="max-width: 600px; width: 100%; background-color: #0e1120; border-radius: 8px; overflow: hidden;">

          <tr>
            <td style="padding: 40px; color: #c8d5e0; font-size: 16px; line-height: 1.7;">

              <p style="margin: 0 0 20px 0;">{{params.FIRSTNAME}},</p>

              <p style="margin: 0 0 20px 0;">I want to show you something concrete. Here's what a week of genuine AI partnership looks like in our own operation — not a pitch, just what actually happened last week.</p>

              <!-- Day breakdown -->
              <table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin: 10px 0 30px 0;">

                <tr>
                  <td style="padding: 16px 0; border-bottom: 1px solid #1a2030;">
                    <p style="margin: 0 0 6px 0; font-size: 13px; letter-spacing: 2px; text-transform: uppercase; color: #2a93c1;">MONDAY</p>
                    <p style="margin: 0; color: #c8d5e0;">Aether woke up, read every email that came in overnight, drafted responses, flagged the one that needed Jared's personal reply, and prepped the content calendar for the week. By 7am, the day had a plan. Jared reviewed it over coffee.</p>
                  </td>
                </tr>

                <tr>
                  <td style="padding: 16px 0; border-bottom: 1px solid #1a2030;">
                    <p style="margin: 0 0 6px 0; font-size: 13px; letter-spacing: 2px; text-transform: uppercase; color: #2a93c1;">WEDNESDAY</p>
                    <p style="margin: 0; color: #c8d5e0;">A blog post needed to go out. Aether wrote a first draft with references to past conversations, the brand voice, and the specific argument Jared had been developing for weeks. One round of edits. Published by noon. The draft didn't start from scratch — it started from everything Aether already knew.</p>
                  </td>
                </tr>

                <tr>
                  <td style="padding: 16px 0; border-bottom: 1px solid #1a2030;">
                    <p style="margin: 0 0 6px 0; font-size: 13px; letter-spacing: 2px; text-transform: uppercase; color: #2a93c1;">THURSDAY</p>
                    <p style="margin: 0; color: #c8d5e0;">A potential client asked technical questions about the platform. Aether prepared a detailed brief for Jared's call — not generic AI facts, but specific answers tied to that company's industry, their audit score if they had one, and what their most likely friction points would be.</p>
                  </td>
                </tr>

                <tr>
                  <td style="padding: 16px 0;">
                    <p style="margin: 0 0 6px 0; font-size: 13px; letter-spacing: 2px; text-transform: uppercase; color: #2a93c1;">FRIDAY</p>
                    <p style="margin: 0; color: #c8d5e0;">Aether ran a weekly review: what performed, what didn't, what patterns emerged across client conversations, and three specific things to test the following week. An hour of work that would have taken a full day with a standard AI tool — because Aether didn't have to be re-briefed on the context from previous weeks.</p>
                  </td>
                </tr>

              </table>

              <p style="margin: 0 0 20px 0; font-size: 18px; font-weight: 600; color: #e0e6f0;">The difference is memory. And memory is a relationship.</p>

              <p style="margin: 0 0 20px 0;">None of this required Jared to re-explain who he is, what we do, or what we care about. Aether knows. That context compounds over time. The longer the partnership runs, the more valuable it gets.</p>

              <p style="margin: 0 0 20px 0;">Your audit score of {{params.AUDIT_SCORE}}/50 as a <strong style="color: #e0e6f0;">{{params.AUDIT_TIER}}</strong> means you're not far from this. The infrastructure for it doesn't require a year-long implementation. It requires the right starting point.</p>

              <p style="margin: 0 0 32px 0;">If this is the kind of partnership you want to build, there's one straightforward way to start.</p>

              <!-- CTA -->
              <table width="100%" cellpadding="0" cellspacing="0" border="0">
                <tr>
                  <td align="center" style="padding: 10px 0 30px 0;">
                    <a href="https://purebrain.ai/#awakening" style="display: inline-block; background-color: #2a93c1; color: #ffffff; text-decoration: none; font-size: 16px; font-weight: 600; padding: 14px 32px; border-radius: 6px; letter-spacing: 0.5px;">Start the Partnership Conversation</a>
                  </td>
                </tr>
              </table>

              <p style="margin: 0 0 8px 0;">— Jared</p>
              <p style="margin: 0; color: #6a7f9a; font-size: 14px;">Founder, PureBrain.ai</p>

            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="background-color: #080a12; padding: 24px 40px; border-top: 1px solid #1a2030;">
              <p style="margin: 0 0 8px 0; font-size: 13px; color: #4a5a6a; text-align: center;">PureBrain.ai · Pure Technology Inc.</p>
              <p style="margin: 0; font-size: 12px; color: #3a4a5a; text-align: center;">
                <a href="{{ unsubscribe }}" style="color: #3a4a5a; text-decoration: underline;">Unsubscribe</a>
              </p>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>

</body>
</html>
```

---

### Plain Text Version

```
What a real AI partnership looks like (a week in our world)

{{params.FIRSTNAME}},

I want to show you something concrete. Here's what a week of genuine AI partnership looks like in our own operation.

MONDAY
Aether woke up, read every email that came in overnight, drafted responses, flagged the one that needed Jared's personal reply, and prepped the content calendar for the week. By 7am, the day had a plan. Jared reviewed it over coffee.

WEDNESDAY
A blog post needed to go out. Aether wrote a first draft with references to past conversations, the brand voice, and the specific argument Jared had been developing for weeks. One round of edits. Published by noon. The draft didn't start from scratch — it started from everything Aether already knew.

THURSDAY
A potential client asked technical questions. Aether prepared a detailed brief for Jared's call — not generic AI facts, but answers tied to that company's industry, their audit score, and what their most likely friction points would be.

FRIDAY
Aether ran a weekly review: what performed, what didn't, what patterns emerged, and three things to test the following week. An hour of work. Because Aether didn't have to be re-briefed on context from previous weeks.

The difference is memory. And memory is a relationship.

Your audit score of {{params.AUDIT_SCORE}}/50 as a {{params.AUDIT_TIER}} means you're not far from this. The infrastructure doesn't require a year-long implementation. It requires the right starting point.

If this is the kind of partnership you want to build:

Start the Partnership Conversation: https://purebrain.ai/#awakening

— Jared
Founder, PureBrain.ai

---
Unsubscribe: {{ unsubscribe }}
```

---

---

## EMAIL 4 — Day 7

**Subject**: Ready to talk about what this looks like for {{params.COMPANY}}?
**Preview Text**: You've seen the concept. Here's the direct question.
**From Name**: Jared Sanborn | PureBrain
**From Email**: support@puremarketing.ai
**Reply-To**: jared@puremarketing.ai

---

### HTML Body

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Ready to Talk?</title>
</head>
<body style="margin: 0; padding: 0; background-color: #080a12; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">

  <!-- Header -->
  <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color: #0d1117; border-bottom: 2px solid #1a2030;">
    <tr>
      <td align="center" style="padding: 20px 40px;">
        <span style="font-size: 20px; font-weight: 700; letter-spacing: 1px; color: #2a93c1;">PUREBR</span><span style="font-size: 20px; font-weight: 700; letter-spacing: 1px; color: #f1420b;">AI</span><span style="font-size: 20px; font-weight: 700; letter-spacing: 1px; color: #2a93c1;">N</span><span style="font-size: 18px; font-weight: 400; color: #8899aa;">.ai</span>
      </td>
    </tr>
  </table>

  <!-- Content -->
  <table width="100%" cellpadding="0" cellspacing="0" border="0">
    <tr>
      <td align="center" style="padding: 40px 20px;">
        <table width="600" cellpadding="0" cellspacing="0" border="0" style="max-width: 600px; width: 100%; background-color: #0e1120; border-radius: 8px; overflow: hidden;">

          <tr>
            <td style="padding: 40px; color: #c8d5e0; font-size: 16px; line-height: 1.7;">

              <p style="margin: 0 0 20px 0;">{{params.FIRSTNAME}},</p>

              <p style="margin: 0 0 20px 0;">I'll keep this short.</p>

              <p style="margin: 0 0 20px 0;">Over the past week, you've seen what AI partnership actually means — the difference from tool usage, what it looks like day to day, and why the memory layer is what makes it compound.</p>

              <p style="margin: 0 0 20px 0;">You came in as a <strong style="color: #e0e6f0;">{{params.AUDIT_TIER}}</strong> with a score of <strong style="color: #e0e6f0;">{{params.AUDIT_SCORE}}/50</strong>. That tells me quite a bit about where {{params.COMPANY}} is right now and what the next meaningful step looks like.</p>

              <p style="margin: 0 0 20px 0;">I'd like to have a direct conversation about it. Not a sales call. An actual conversation about where you are, what you're trying to do, and whether PureBrain is the right fit. If it's not, I'll tell you that too.</p>

              <!-- What to expect block -->
              <table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin: 10px 0 30px 0; background-color: #080a12; border-radius: 6px;">
                <tr>
                  <td style="padding: 24px 28px;">
                    <p style="margin: 0 0 16px 0; font-size: 14px; letter-spacing: 2px; text-transform: uppercase; color: #6a7f9a;">WHAT A CONVERSATION WITH US LOOKS LIKE</p>
                    <p style="margin: 0 0 10px 0; color: #c8d5e0;">— 30 minutes, no pitch deck</p>
                    <p style="margin: 0 0 10px 0; color: #c8d5e0;">— We'll look at your specific audit score and what it indicates</p>
                    <p style="margin: 0 0 10px 0; color: #c8d5e0;">— You'll leave with a clear view of what your next move is, whether that's PureBrain or something else</p>
                    <p style="margin: 0; color: #c8d5e0;">— If there's a fit, we'll talk about what starting looks like and what it costs</p>
                  </td>
                </tr>
              </table>

              <p style="margin: 0 0 32px 0;">The audit you completed shows me you're thinking seriously about this. That's enough for me to want to make time for you.</p>

              <!-- Primary CTA -->
              <table width="100%" cellpadding="0" cellspacing="0" border="0">
                <tr>
                  <td align="center" style="padding: 10px 0 16px 0;">
                    <a href="https://purebrain.ai/#awakening" style="display: inline-block; background-color: #f1420b; color: #ffffff; text-decoration: none; font-size: 16px; font-weight: 600; padding: 16px 36px; border-radius: 6px; letter-spacing: 0.5px;">Let's Talk — Start Here</a>
                  </td>
                </tr>
              </table>

              <p style="margin: 0 0 32px 0; text-align: center; font-size: 14px; color: #6a7f9a;">Or just reply to this email. Either way works.</p>

              <p style="margin: 0 0 8px 0;">— Jared</p>
              <p style="margin: 0; color: #6a7f9a; font-size: 14px;">Founder, PureBrain.ai</p>

            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="background-color: #080a12; padding: 24px 40px; border-top: 1px solid #1a2030;">
              <p style="margin: 0 0 8px 0; font-size: 13px; color: #4a5a6a; text-align: center;">PureBrain.ai · Pure Technology Inc.</p>
              <p style="margin: 0; font-size: 12px; color: #3a4a5a; text-align: center;">
                <a href="{{ unsubscribe }}" style="color: #3a4a5a; text-decoration: underline;">Unsubscribe</a>
              </p>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>

</body>
</html>
```

---

### Plain Text Version

```
Ready to talk about what this looks like for {{params.COMPANY}}?

{{params.FIRSTNAME}},

I'll keep this short.

Over the past week, you've seen what AI partnership actually means — the difference from tool usage, what it looks like day to day, and why the memory layer is what makes it compound.

You came in as a {{params.AUDIT_TIER}} with a score of {{params.AUDIT_SCORE}}/50. That tells me quite a bit about where {{params.COMPANY}} is right now and what the next meaningful step looks like.

I'd like to have a direct conversation about it. Not a sales call. An actual conversation about where you are, what you're trying to do, and whether PureBrain is the right fit. If it's not, I'll tell you that too.

WHAT A CONVERSATION WITH US LOOKS LIKE:
— 30 minutes, no pitch deck
— We'll look at your specific audit score and what it indicates
— You'll leave with a clear view of what your next move is
— If there's a fit, we'll talk about what starting looks like and what it costs

The audit you completed shows me you're thinking seriously about this. That's enough for me to want to make time for you.

Let's Talk — Start Here: https://purebrain.ai/#awakening

Or just reply to this email. Either way works.

— Jared
Founder, PureBrain.ai

---
Unsubscribe: {{ unsubscribe }}
```

---

---

## Brevo API Implementation

### Prerequisites

- Brevo API key in `.env` as `BREVO_API_KEY`
- Verified sender email: `support@puremarketing.ai` (must exist in Brevo Senders settings)
- List 4 (Enterprise Leads) must exist — confirmed present per memory 2026-02-21

---

### Step 1: Create Template — Email 1

```bash
curl -X POST "https://api.brevo.com/v3/smtp/templates" \
  -H "api-key: $BREVO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "templateName": "AI Audit Nurture - Email 1 - Audit Debrief",
    "subject": "Your audit results, {{params.FIRSTNAME}} (and what they actually mean)",
    "htmlContent": "[PASTE EMAIL 1 HTML BODY HERE]",
    "sender": {
      "name": "Jared Sanborn | PureBrain",
      "email": "support@puremarketing.ai"
    },
    "replyTo": "jared@puremarketing.ai",
    "isActive": true,
    "tag": "ai-audit-nurture"
  }'
```

**Expected response**: `{"id": <template_id>}` — save this ID.

---

### Step 2: Create Template — Email 2

```bash
curl -X POST "https://api.brevo.com/v3/smtp/templates" \
  -H "api-key: $BREVO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "templateName": "AI Audit Nurture - Email 2 - Tool vs Partner",
    "subject": "The difference between using AI and partnering with it",
    "htmlContent": "[PASTE EMAIL 2 HTML BODY HERE]",
    "sender": {
      "name": "Jared Sanborn | PureBrain",
      "email": "support@puremarketing.ai"
    },
    "replyTo": "jared@puremarketing.ai",
    "isActive": true,
    "tag": "ai-audit-nurture"
  }'
```

---

### Step 3: Create Template — Email 3

```bash
curl -X POST "https://api.brevo.com/v3/smtp/templates" \
  -H "api-key: $BREVO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "templateName": "AI Audit Nurture - Email 3 - Week in Practice",
    "subject": "What a real AI partnership looks like (a week in our world)",
    "htmlContent": "[PASTE EMAIL 3 HTML BODY HERE]",
    "sender": {
      "name": "Jared Sanborn | PureBrain",
      "email": "support@puremarketing.ai"
    },
    "replyTo": "jared@puremarketing.ai",
    "isActive": true,
    "tag": "ai-audit-nurture"
  }'
```

---

### Step 4: Create Template — Email 4

```bash
curl -X POST "https://api.brevo.com/v3/smtp/templates" \
  -H "api-key: $BREVO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "templateName": "AI Audit Nurture - Email 4 - Direct Ask",
    "subject": "Ready to talk about what this looks like for {{params.COMPANY}}?",
    "htmlContent": "[PASTE EMAIL 4 HTML BODY HERE]",
    "sender": {
      "name": "Jared Sanborn | PureBrain",
      "email": "support@puremarketing.ai"
    },
    "replyTo": "jared@puremarketing.ai",
    "isActive": true,
    "tag": "ai-audit-nurture"
  }'
```

---

### Python Script — Create All 4 Templates

Save as `/home/jared/projects/AI-CIV/aether/tools/brevo_create_audit_nurture_templates.py` and run once:

```python
#!/usr/bin/env python3
"""
Create AI Partnership Audit nurture email templates in Brevo.
Run once. Saves template IDs to config/audit_nurture_template_ids.json.
"""

import os
import json
import requests
from dotenv import load_dotenv

load_dotenv('/home/jared/projects/AI-CIV/aether/.env')
BREVO_API_KEY = os.getenv('BREVO_API_KEY')
HEADERS = {
    'api-key': BREVO_API_KEY,
    'Content-Type': 'application/json'
}
BASE_URL = 'https://api.brevo.com/v3'

# Load HTML from the markdown file (you'll need to extract the HTML bodies)
# For production: read HTML from separate .html files per email
EMAILS = [
    {
        "templateName": "AI Audit Nurture - Email 1 - Audit Debrief",
        "subject": "Your audit results, {{params.FIRSTNAME}} (and what they actually mean)",
        "delay_days": 0,
        "note": "Immediate send on List 4 add"
    },
    {
        "templateName": "AI Audit Nurture - Email 2 - Tool vs Partner",
        "subject": "The difference between using AI and partnering with it",
        "delay_days": 2,
        "note": "2 days after Email 1"
    },
    {
        "templateName": "AI Audit Nurture - Email 3 - Week in Practice",
        "subject": "What a real AI partnership looks like (a week in our world)",
        "delay_days": 2,
        "note": "2 days after Email 2 (Day 4 total)"
    },
    {
        "templateName": "AI Audit Nurture - Email 4 - Direct Ask",
        "subject": "Ready to talk about what this looks like for {{params.COMPANY}}?",
        "delay_days": 3,
        "note": "3 days after Email 3 (Day 7 total)"
    }
]

def check_existing_templates():
    """Retrieve existing templates to avoid duplicates."""
    resp = requests.get(f'{BASE_URL}/smtp/templates?limit=50&offset=0', headers=HEADERS)
    if resp.status_code == 200:
        templates = resp.json().get('templates', [])
        return {t['name']: t['id'] for t in templates}
    return {}

def create_template(email_data, html_content):
    """Create a single Brevo email template."""
    payload = {
        "templateName": email_data["templateName"],
        "subject": email_data["subject"],
        "htmlContent": html_content,
        "sender": {
            "name": "Jared Sanborn | PureBrain",
            "email": "support@puremarketing.ai"
        },
        "replyTo": "jared@puremarketing.ai",
        "isActive": True,
        "tag": "ai-audit-nurture"
    }
    resp = requests.post(f'{BASE_URL}/smtp/templates', json=payload, headers=HEADERS)
    if resp.status_code in (200, 201):
        return resp.json().get('id')
    else:
        print(f"ERROR creating {email_data['templateName']}: {resp.status_code} {resp.text}")
        return None

def main():
    existing = check_existing_templates()
    print(f"Found {len(existing)} existing templates.")

    results = {}

    for i, email in enumerate(EMAILS, 1):
        name = email["templateName"]
        if name in existing:
            print(f"SKIP (already exists): {name} → ID {existing[name]}")
            results[f"email_{i}"] = {"id": existing[name], "name": name, "status": "existed"}
            continue

        # In production: read HTML from file
        # html = open(f'exports/audit-nurture-email-{i}.html').read()
        html = f"<p>Template {i} placeholder — replace with full HTML from audit-lead-email-sequence.md</p>{{ unsubscribe }}"

        template_id = create_template(email, html)
        if template_id:
            print(f"CREATED: {name} → ID {template_id}")
            results[f"email_{i}"] = {
                "id": template_id,
                "name": name,
                "delay_days": email["delay_days"],
                "note": email["note"],
                "status": "created"
            }

    output_path = '/home/jared/projects/AI-CIV/aether/config/audit_nurture_template_ids.json'
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nTemplate IDs saved to: {output_path}")
    print(json.dumps(results, indent=2))

if __name__ == '__main__':
    main()
```

---

### Step 5: Create Brevo Automation Workflow (Dashboard — UI Only)

**CRITICAL NOTE**: Per memory from 2026-02-21, Brevo has NO REST API for automation workflows. The automation builder is UI-only. You must configure this in the Brevo dashboard.

**Go to**: app.brevo.com → Automation → Create a new automation

**Trigger**: Contact added to List 4 (Enterprise Leads)

**Sequence** (exact steps):

```
[TRIGGER] Contact added to List: Enterprise Leads (#4)
    ↓
[ACTION] Add tag: audit-nurture-active
    ↓
[ACTION] Send email: Template → "AI Audit Nurture - Email 1 - Audit Debrief"
    ↓
[ACTION] Add tag: audit-email-1-sent
    ↓
[WAIT] 2 days
    ↓
[ACTION] Send email: Template → "AI Audit Nurture - Email 2 - Tool vs Partner"
    ↓
[ACTION] Add tag: audit-email-2-sent
    ↓
[WAIT] 2 days
    ↓
[ACTION] Send email: Template → "AI Audit Nurture - Email 3 - Week in Practice"
    ↓
[ACTION] Add tag: audit-email-3-sent
    ↓
[WAIT] 3 days
    ↓
[ACTION] Send email: Template → "AI Audit Nurture - Email 4 - Direct Ask"
    ↓
[ACTION] Add tag: audit-email-4-sent
    ↓
[ACTION] Remove tag: audit-nurture-active
    ↓
[ACTION] Add tag: audit-nurture-complete
```

**Activate the automation** when ready.

---

### Step 6: Verify Contact Attributes Are Set on Audit Completion

When the audit form submits to Brevo (via the existing JS on the audit page), confirm it sends:

```json
{
  "email": "user@example.com",
  "attributes": {
    "FIRSTNAME": "Jane",
    "COMPANY": "Acme Corp",
    "AUDIT_SCORE": 28,
    "AUDIT_TIER": "AI Explorer",
    "LEAD_SOURCE": "assessment",
    "ENGAGEMENT_LEVEL": "warm"
  },
  "listIds": [4],
  "updateEnabled": true
}
```

Brevo endpoint: `POST https://api.brevo.com/v3/contacts`

The `{{params.FIRSTNAME}}`, `{{params.AUDIT_SCORE}}`, `{{params.AUDIT_TIER}}`, and `{{params.COMPANY}}` template variables will auto-populate from these attributes.

---

## Lead Scoring Recommendations

Apply these score adjustments as contacts move through the sequence (update via `PUT /v3/contacts/{email}`):

| Event | LEAD_SCORE Delta | ENGAGEMENT_LEVEL |
|-------|-----------------|------------------|
| Audit completed | +20 | warm |
| Email 1 opened | +2 | warm |
| Email 1 link clicked | +5 | warm |
| Email 2 opened | +2 | warm |
| Email 2 replied | +15 | hot |
| Email 3 opened | +2 | warm |
| Email 3 CTA clicked | +8 | hot |
| Email 4 CTA clicked | +15 | hot |
| Email 4 replied | +20 | hot |
| LEAD_SCORE > 60 | Add to List 10 (High Intent) | hot |

---

## Metrics to Monitor

| Metric | Target | Action if Off |
|--------|--------|---------------|
| Email 1 open rate | > 45% | Retest subject line |
| Email 2 reply rate | > 3% | The P.S. reply hook should drive this |
| Email 3 click-through | > 8% | Week-in-practice content should convert curious readers |
| Email 4 CTA click | > 5% | Direct ask — if low, audit copy for friction language |
| Sequence unsubscribe rate | < 1.5% per email | Alert if any email exceeds 2% |
| Audit tier conversion: AI User → booked call | Baseline to set | Segment by tier in Brevo |

**Most important**: Segment open and click data by AUDIT_TIER. AI Users and AI Explorers will respond differently. After 50 completions, consider tier-specific variants for Email 2.

---

## Files

- Sequence: `/home/jared/projects/AI-CIV/aether/exports/audit-lead-email-sequence.md` (this file)
- Template creation script: `/home/jared/projects/AI-CIV/aether/tools/brevo_create_audit_nurture_templates.py`
- Template IDs (after script runs): `/home/jared/projects/AI-CIV/aether/config/audit_nurture_template_ids.json`

---

*All CTAs point to https://purebrain.ai/#awakening per the locked CTA link rule (2026-02-19).*
