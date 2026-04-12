# Office Hours Email Sequences

**Platform**: Brevo
**Segment**: Create "office-hours-registrants" segment in Brevo
**From Name**: Jared Sanborn (or "Jared + Aether" for Aether-authored emails)
**From Email**: jared@puretechnology.nyc
**Reply-To**: jared@puretechnology.nyc
**Automation trigger**: Tally/Typeform registration form submission → Brevo webhook

---

## HOW TO USE THESE SEQUENCES

Each webinar session requires four email touches:

1. **Registration Confirmation** (immediate, automated)
2. **24-Hour Reminder** (automated, day before)
3. **1-Hour Reminder** (automated, day of)
4. **Post-Session Follow-Up** (semi-automated, day of + day 3 + day 7)

Set up as Brevo automation flows. Trigger on registration. Date-based delays handle the timing.

Additionally: **Replay Notification** for non-registrants who missed it (sent 24 hours after session).

---

## EMAIL 1: REGISTRATION CONFIRMATION

**Trigger**: Immediately on form submission
**To**: All registrants
**Subject**: You're registered. Here's what happens next.

---

**Subject A/B test options**:
- Option A: You're registered. Here's what happens next.
- Option B: [First name], you're in for [DATE]

---

**Body**:

```
[First name],

You're registered for AI Strategy Office Hours on [DATE] at 11 AM PST / 2 PM EST.

Your calendar invite is attached. Drop it in your calendar now so it doesn't disappear.

---

Here's what the 45 minutes looks like:

The first 30 minutes are content — a focused breakdown of one specific AI strategy topic. Not theory. The actual framework I use.

Then 5 minutes of live demo where Aether handles a real business problem on screen.

Then 15 minutes of Q&A where you can ask anything. And at the very end, Aether synthesizes what happened in the room and adds one observation of its own. That part always surprises people.

---

One thing you can do right now:

If you have a specific question you want answered live, submit it here:

[Submit Your Question →]

Questions submitted in advance get prioritized in the Q&A. You don't have to attend live to submit one — questions from people who can't make it live often end up being the most interesting ones.

---

Can't make it live? Register anyway. Recording lands in your inbox within 2 hours of the session ending.

See you [DATE],

Jared

P.S. If you know someone who's been struggling with the AI thing — tools that don't quite work, results that don't quite hit — forward this to them. The session is free. The more real questions in the room, the better it gets.
```

**Attachment**: .ics calendar file for the session date/time

---

## EMAIL 2: 24-HOUR REMINDER

**Trigger**: 24 hours before session start time
**To**: All registrants
**Subject**: Tomorrow: AI Strategy Office Hours (+ your reminder to submit a question)

---

**Subject A/B test options**:
- Option A: Tomorrow: AI Strategy Office Hours
- Option B: [First name], office hours is tomorrow. One thing to do tonight.

---

**Body**:

```
[First name],

Quick reminder: AI Strategy Office Hours is tomorrow at 11 AM PST / 2 PM EST.

[Join Link]

---

Tomorrow's topic: [SESSION TOPIC]

Here's the specific thing I'm covering:

[2-3 sentence preview of the session content — be specific, not vague. Pull from the session outline.]

---

If you haven't submitted a question yet, now's a good time:

[Submit Your Question →]

I read every question before the session. Aether prioritizes them during Q&A. Questions with real stakes — not hypotheticals, but actual problems you're sitting with — get the most useful answers.

---

Can't make it live? Recording arrives within 2 hours of the session ending. You're still good.

See you tomorrow,

Jared
```

---

## EMAIL 3: 1-HOUR REMINDER

**Trigger**: 60 minutes before session start time
**To**: All registrants
**Subject**: Starting in 1 hour — here's your link

---

**Body**:

```
[First name],

We're live in 1 hour.

[JOIN SESSION →]  ← Large, prominent button

[DATE] at 11 AM PST / 2 PM EST
Topic: [SESSION TOPIC]

---

What to expect:
- 30 min: The framework — [one sentence on what you'll learn]
- 5 min: Live Aether demo
- 15 min: Q&A — bring your questions, or type them in chat

---

Questions go in the chat or the Q&A tool. Either works.

See you in an hour,

Jared

P.S. If you're watching from your phone, the link works in mobile browser. No app needed.
```

---

## EMAIL 4A: POST-SESSION FOLLOW-UP (ATTENDEES)

**Trigger**: 2 hours after session end time
**To**: Registrants marked as "attended" in Brevo
**Subject**: Recording inside + [one insight from today's session]

---

**Body**:

```
[First name],

Thank you for showing up today. Genuinely.

The sessions are better when the questions are real, and yours were.

Here's the recording:
[WATCH RECORDING →]

---

The thing I'm still thinking about from today:

[1-2 paragraphs in Jared's genuine voice about one specific moment, question, or insight from the session. Not a recap. One real thing. This is the email people forward.]

---

One thing you can do with this right now:

[Tie to the action step from the session. If the offer was a free trial: "If today's demo made you want to try Aether on your own business, the 7-day free trial is here." If the offer was a lead magnet: "The [lead magnet name] from today is attached."]

[SESSION CTA BUTTON]

---

Next office hours is [NEXT DATE]. Same format, different topic.

See you then,

Jared

P.S. If today sparked something for a colleague — a question, a challenge, a "we have the same problem" moment — forward them the recording. The link is accessible, no registration required.
```

---

## EMAIL 4B: POST-SESSION FOLLOW-UP (NO-SHOWS)

**Trigger**: 2 hours after session end time
**To**: Registrants marked as "did not attend"
**Subject**: You missed it — here's the recording + what happened

```
[First name],

You were registered but couldn't make it. No problem.

Here's the recording:
[WATCH RECORDING →]

45 minutes. Worth the time.

---

Quick summary of what happened:

[3 bullet points — top insight, most interesting Q&A moment, the Aether synthesis observation]

---

The one thing most people took away:

[One specific, concrete insight from the session. Make it the kind of thing someone would screenshot and send to a colleague.]

---

If you watch it and want to talk about what it could mean for your business:

[SESSION CTA BUTTON]

---

Next session is [NEXT DATE]. Register here if you want the early reminder.

[REGISTER FOR NEXT SESSION →]

Jared
```

---

## EMAIL 5: DAY 3 FOLLOW-UP (NON-CONVERTERS)

**Trigger**: 3 days after session, to attendees + no-shows who have NOT started trial or clicked CTA
**Subject**: [First name], the one question from office hours that stayed with me

---

**Body**:

```
[First name],

Three days after office hours, I'm still thinking about [specific question from the Q&A — pick the most interesting one].

The person asked [brief description of question]. And my honest answer was [what I said]. But what I've been sitting with since is this:

[1 short paragraph of genuine reflection — Jared's actual thinking on the question. Not polished. Not sales copy. Real thought.]

This is what we built PureBrain to solve, and I keep running into it.

Most people trying to get AI to do useful work are missing one layer: the context layer. The part where the AI actually knows your business — your clients, your language, your history, your goals — before you ask it anything.

Without that layer, every AI interaction starts at zero. With it, you're starting every conversation 60% further than everyone else.

That's the difference between using AI and working with AI.

If you've been thinking about trying PureBrain — even tentatively — this week is a good time to start.

7-day free trial. No card required. No commitment.

[TRY PUREBRAIN FREE →]

Jared

P.S. If the session raised questions you didn't get to ask, hit reply. I read these.
```

---

## EMAIL 6: DAY 7 FOLLOW-UP (NON-CONVERTERS)

**Trigger**: 7 days after session, to non-converters who have not started trial
**Subject**: Quick question before I close the loop

---

**Body**:

```
[First name],

Short one.

You attended office hours [DATE] but haven't started a trial. I'm not going to send you a third pitch email.

Instead: did the session help?

I'm genuinely curious which part was most useful — or what didn't land the way you needed it to.

Hit reply. One sentence is enough.

Jared
```

**Design note**: No CTA button in this email. No links except the standard footer unsubscribe. This is a reply-harvesting email. Every reply is a sales conversation worth 10x any click.

**Response protocol**: Jared (or Aether on Jared's behalf with his review) responds personally to every reply within 24 hours.

---

## EMAIL 7: REPLAY NOTIFICATION (NON-REGISTRANTS)

**Trigger**: 24 hours after session, to Neural Feed list subscribers who did NOT register for this session
**Subject**: In case you missed it: AI Strategy Office Hours ([TOPIC])

---

**Body**:

```
[First name],

Last week I hosted office hours on [TOPIC].

[Number] people joined live. The recording is available for the next [30 days / indefinitely — your choice].

[WATCH THE RECORDING →]

45 minutes. Here's what happened:

[One paragraph — genuine summary of the session. Include one specific insight and the Aether synthesis moment.]

---

If you want to be there for the next one live — [NEXT SESSION DATE] — registration is here:

[REGISTER FOR NEXT SESSION →]

Jared
```

---

## BREVO AUTOMATION SETUP GUIDE

**Automation flow name**: "Office Hours - [Session Date]"

**Trigger**: Contact added to segment "office-hours-[session-date]-registrants"

**Steps**:
1. Immediately → Send Email 1 (Registration Confirmation) + tag "registered"
2. [Session Date - 24 hours] → Send Email 2 (24-Hour Reminder)
3. [Session Date - 1 hour] → Send Email 3 (1-Hour Reminder)
4. [Session Date + 2 hours] → Branch: IF tag "attended" → Send Email 4A; ELSE → Send Email 4B
5. [Session Date + 3 days] → Condition: IF NOT tag "trial-started" → Send Email 5
6. [Session Date + 7 days] → Condition: IF NOT tag "trial-started" → Send Email 6

**Tags to create**:
- `oh-registered-[date]`
- `oh-attended-[date]`
- `oh-no-show-[date]`
- `trial-started` (shared across all flows, marks conversion)

**Attended tagging**: Manually export attendee list from StreamYard/Zoom after session, import to Brevo, add `oh-attended-[date]` tag. Takes ~15 minutes post-session.

---

*Email sequences by: content-specialist | 2026-02-24*
*Brevo setup required by: full-stack-developer*
