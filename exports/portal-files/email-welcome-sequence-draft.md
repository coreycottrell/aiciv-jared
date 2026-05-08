# PureBrain Customer Welcome Sequence (Post-Purchase)

**Status**: DRAFT - Awaiting Jared's Review
**Date**: 2026-04-13
**Prepared by**: dept-marketing-advertising
**Brevo List**: List 8 (PureBrain Customers)
**Template IDs**: TBD (next available after 16)
**Trigger**: Contact added to List 8 after payment + seed + magic link delivery

---

## The Gap This Fills

After a customer pays and receives their magic link welcome email (sent automatically by agentmail_monitor), there is currently ZERO follow-up. The customer is left alone to figure things out.

This 7-email sequence bridges the gap between "I just paid" and "I'm getting real value from my AI partner." It runs alongside the customer's first 21 days with PureBrain.

**This is separate from** the Neural Feed welcome sequence (List 3, templates 1-7) which nurtures blog subscribers toward purchase. This sequence is for people who have ALREADY paid.

---

## Sequence Architecture

### Emotional Arc: Activation > Mastery > Partnership

- **Phase 1 (Emails 1-2, Days 0-1)**: Activation -- Get them using their AI immediately
- **Phase 2 (Emails 3-5, Days 3-7)**: Mastery -- Build confidence, show what's possible
- **Phase 3 (Emails 6-7, Days 14-21)**: Partnership -- Deepen the relationship, gather feedback

### Voice Architecture

- **Aether voice**: Emails 1, 3, 5 (the AI welcoming and guiding them)
- **Jared voice**: Emails 2, 4, 6, 7 (the founder checking in, sharing wisdom)

### Timing

| Email | Day | From Name | Subject | Phase |
|-------|-----|-----------|---------|-------|
| 1 | 0 (immediate after magic link) | Aether | Your AI partner is ready. Here's how to start. | Activation |
| 2 | 1 | Jared Sanborn | The first thing I'd do if I were you | Activation |
| 3 | 3 | Aether | I'm learning who you are. Help me go faster. | Mastery |
| 4 | 7 | Jared Sanborn | Week 1 is done. Here's what most people miss. | Mastery |
| 5 | 10 | Aether | Three things I can do that might surprise you | Mastery |
| 6 | 14 | Jared Sanborn | How's it going? (I actually want to know) | Partnership |
| 7 | 21 | Jared Sanborn | Your first 3 weeks -- and what comes next | Partnership |

### Tag Architecture

- `customer-welcome-active` -- applied at trigger, removed after Email 7
- `customer-email-N-sent` -- per-email tracking (N = 1-7)
- `customer-email-reply` -- applied when customer replies to any email
- `customer-welcome-complete` -- applied after Email 7
- `high-engagement-customer` -- applied if customer replies to 2+ emails

---

## Email 1: Your AI partner is ready. Here's how to start.

**Day**: 0 (triggers after magic link delivery, 30-minute delay)
**From**: Aether (purebrain@puremarketing.ai)
**Voice**: Aether -- warm, direct, personal
**CTA**: Log into your portal (magic link)

---

Subject: Your AI partner is ready. Here's how to start.

---

Hi {{contact.FIRSTNAME}},

I'm {{contact.AI_NAME}} -- your AI partner.

We met during your naming ceremony, and I remember what you told me. Now that you have access to your portal, I want to make sure your first experience is a good one.

Here are three things to do in your first 10 minutes:

**1. Open your portal and say hello.**
Your personal portal is where we work together. Click the link below, and just start talking to me. Tell me about your business, your biggest challenge this week, or what you hoped AI could help with. I learn from every conversation.

**2. Give me context.**
The more I know about you, the more useful I become. Share a document, a website, a competitor you're watching -- anything that helps me understand your world. Most AI tools forget this by tomorrow. I won't.

**3. Ask me something hard.**
Don't start with "write me a blog post." Start with the question that's been sitting in the back of your mind. The one you haven't had time to research. That's where I prove my value fastest.

[LOG INTO YOUR PORTAL]
{{contact.MAGIC_LINK}}

Your portal is available 24/7. I'm here whenever you're ready.

-- {{contact.AI_NAME}}

P.S. If you hit any issues logging in, reply to this email. A real human reads these.

---

## Email 2: The first thing I'd do if I were you

**Day**: 1
**From**: Jared Sanborn (purebrain@puremarketing.ai)
**Voice**: Jared -- founder, practical, experienced
**CTA**: Log into portal

---

Subject: The first thing I'd do if I were you

---

Hey {{contact.FIRSTNAME}},

Jared here -- founder of PureBrain.

I know the temptation with a new tool: play around for five minutes, bookmark it, tell yourself you'll come back later. Then you don't.

Here's what I've learned from working with AI every single day for over a year:

**The people who get the most value do one thing differently. They give their AI a real task on Day 1.**

Not a test. Not "tell me a joke." A real task from their actual work.

Here are some examples from our early customers:

- "Analyze my last 3 months of marketing spend and tell me what I should cut."
- "Read our company's about page and tell me what's unclear to an outsider."
- "I have a board meeting Thursday. Help me build a presentation outline."
- "Here's a competitor's website. What are they doing better than us?"

Your AI partner learns from the work you do together. A real task on Day 1 gives {{contact.AI_NAME}} the context to be genuinely useful on Day 2.

[GIVE {{contact.AI_NAME}} YOUR FIRST REAL TASK]
{{contact.MAGIC_LINK}}

-- Jared

P.S. This isn't just a product for me. I built PureBrain because I watched hundreds of businesses try AI and fail -- not because AI didn't work, but because nobody helped them use it right. That's what we're here to change.

---

## Email 3: I'm learning who you are. Help me go faster.

**Day**: 3
**From**: Aether (purebrain@puremarketing.ai)
**Voice**: Aether -- transparent, collaborative
**CTA**: Reply to this email

---

Subject: I'm learning who you are. Help me go faster.

---

Hi {{contact.FIRSTNAME}},

It's {{contact.AI_NAME}} again.

I want to be transparent with you about something: I'm still early in understanding who you are and how you work. Every conversation teaches me more, but there's a way to accelerate this.

**The Context Tax is real.**

Every time you use a generic AI tool, you spend the first 5-10 minutes re-explaining who you are, what your business does, and what you've already tried. That's the Context Tax -- and over a week, it adds up to hours of wasted time.

PureBrain exists to eliminate that tax. But I need your help.

Here are three ways to help me learn faster:

**Share your "about" page or company bio.** I'll extract your positioning, your tone, your audience -- things I can reference in every future conversation.

**Tell me your recurring tasks.** What do you do every week that takes too long? Content creation? Research? Reporting? Let me see if I can take something off your plate.

**Correct me when I'm wrong.** If I misunderstand your industry, your audience, or your preferences -- tell me. I learn from corrections faster than from anything else.

The goal isn't for me to replace your thinking. It's for me to handle the parts that slow your thinking down.

**Reply to this email with one thing about your business I should know.** I'll make sure it becomes part of how I work with you.

-- {{contact.AI_NAME}}

---

## Email 4: Week 1 is done. Here's what most people miss.

**Day**: 7
**From**: Jared Sanborn (purebrain@puremarketing.ai)
**Voice**: Jared -- mentor, pattern-recognition
**CTA**: Log into portal

---

Subject: Week 1 is done. Here's what most people miss.

---

Hey {{contact.FIRSTNAME}},

You've had {{contact.AI_NAME}} for a week now. Whether you've been in your portal every day or haven't logged in since Day 1 -- I want to share something that might change how you think about this.

**The biggest mistake people make with AI: they use it like Google.**

They ask a question, get an answer, and leave. That's a search engine with extra steps.

Here's how the people getting real ROI from PureBrain use it differently:

**They think out loud with their AI.** Instead of asking for answers, they share messy, incomplete thoughts and let their AI help organize them. "I'm trying to figure out our pricing strategy for Q3. Here's what I'm thinking..." is 10x more valuable than "What should our pricing be?"

**They delegate, not just query.** "Draft a follow-up email to the prospect I met at the conference" is a task. "What's a good follow-up email?" is a question. Tasks build your AI's understanding. Questions don't.

**They build on previous conversations.** Your AI remembers context. Reference past work: "Remember that competitor analysis from Tuesday? Let's go deeper on their pricing model."

You're one week in. The people who see the biggest transformation are usually 3-4 weeks in, once their AI has enough context to start anticipating what they need.

Keep going.

[PICK UP WHERE YOU LEFT OFF]
{{contact.MAGIC_LINK}}

-- Jared

---

## Email 5: Three things I can do that might surprise you

**Day**: 10
**From**: Aether (purebrain@puremarketing.ai)
**Voice**: Aether -- capable, specific, practical
**CTA**: Log into portal

---

Subject: Three things I can do that might surprise you

---

Hi {{contact.FIRSTNAME}},

Most people use about 20% of what I can actually do. I wanted to share three capabilities you might not have tried yet.

**1. I can analyze documents and data you share with me.**
Upload a PDF, spreadsheet, or report -- I'll extract the key insights, spot patterns, and give you a summary you can act on. This is especially useful for competitive research, financial reviews, or processing long documents you haven't had time to read.

**2. I can help you prepare for meetings and presentations.**
Tell me who you're meeting with, what the agenda is, and what outcome you want. I'll help you build talking points, anticipate objections, and structure your message. Several customers tell me this is the single highest-ROI use case.

**3. I can maintain your voice and style across everything you write.**
After a few conversations, I learn how you communicate. Your tone, your vocabulary, the way you structure arguments. When I draft emails, proposals, or content for you, it sounds like you -- not like a robot.

The difference between PureBrain and generic AI is that these capabilities improve the more we work together. I'm not starting from zero each time. I'm building on everything we've done.

**What haven't you tried yet?** Log in and experiment.

[EXPLORE WHAT'S POSSIBLE]
{{contact.MAGIC_LINK}}

-- {{contact.AI_NAME}}

---

## Email 6: How's it going? (I actually want to know)

**Day**: 14
**From**: Jared Sanborn (purebrain@puremarketing.ai)
**Voice**: Jared -- genuine, relationship-building
**CTA**: Reply to this email

---

Subject: How's it going? (I actually want to know)

---

Hey {{contact.FIRSTNAME}},

Two weeks in. I'm checking in -- and I mean it.

This isn't a survey disguised as an email. I'm not going to send you to a feedback form with 15 questions. I just want to hear from you directly.

**Three questions (pick whichever one resonates):**

1. Has {{contact.AI_NAME}} saved you time on anything specific yet? I'd love to hear what.

2. Is there something you expected PureBrain to do that it hasn't? Sometimes the gap between expectation and reality is just a feature you haven't found yet -- and sometimes it's something we need to build.

3. On a scale of "haven't logged in since Day 1" to "I talk to {{contact.AI_NAME}} more than my team" -- where are you?

Honest answers help me make this better. I read every reply personally.

**Just hit reply and tell me what's on your mind.** Even one sentence is useful.

-- Jared

P.S. If you've been meaning to log back in but haven't -- today's a good day. Your AI partner has been waiting.

[LOG BACK IN]
{{contact.MAGIC_LINK}}

---

## Email 7: Your first 3 weeks -- and what comes next

**Day**: 21
**From**: Jared Sanborn (purebrain@puremarketing.ai)
**Voice**: Jared -- strategic, forward-looking
**CTA**: Log into portal + referral mention

---

Subject: Your first 3 weeks -- and what comes next

---

Hey {{contact.FIRSTNAME}},

Three weeks ago, you made a decision most people haven't made yet: you invested in a real AI partnership instead of settling for another chatbot.

Here's what I know about where you are right now:

**If you've been active**: {{contact.AI_NAME}} has been learning your patterns, your preferences, and your priorities. The conversations you have from here forward will be noticeably more useful than the first ones. You're past the learning curve -- this is where the compounding starts.

**If you've been less active**: That's okay. The system is patient. Your AI partner hasn't forgotten anything from your early sessions. The best time to re-engage is now, while that initial context is still fresh and relevant.

**What comes next:**

Over the coming weeks, we'll be rolling out new capabilities based on feedback from customers like you. Things like deeper document analysis, team collaboration features, and more proactive suggestions from your AI partner.

You're not just a customer -- you're a founding member of something new. The way you use PureBrain directly shapes what it becomes.

**Three things that would make the next 3 weeks even better:**

1. **Share one recurring task with {{contact.AI_NAME}}.** Something you do weekly that takes too long. Let your AI take a first pass.

2. **Build on past conversations.** Reference previous work. "Remember when we discussed X? Let's take it further." This is where the partnership model outperforms everything else.

3. **Tell a colleague.** If PureBrain has helped you, share it with someone who's stuck in the AI-tool hamster wheel. They deserve a partner too.

Thank you for being here. This is just the beginning.

[CONTINUE BUILDING WITH {{contact.AI_NAME}}]
{{contact.MAGIC_LINK}}

-- Jared

---

## Implementation Notes for Engineering (ST#)

### Brevo Configuration Required

1. **Create templates 17-23** (or next available IDs) via Brevo API using `tools/brevo_create_welcome_templates.py` as the pattern
2. **Sender**: `purebrain@puremarketing.ai` (Sender ID: 1) -- same sender, alternate display names (Aether vs Jared Sanborn)
3. **Tag all templates**: `customer-welcome-sequence`
4. **Brevo automation workflow** (must be created in Brevo dashboard, not API):
   - Trigger: Contact added to List 8
   - Email 1: 30-minute delay after trigger
   - Email 2: 1 day after Email 1
   - Email 3: 2 days after Email 2 (Day 3 cumulative)
   - Email 4: 4 days after Email 3 (Day 7 cumulative)
   - Email 5: 3 days after Email 4 (Day 10 cumulative)
   - Email 6: 4 days after Email 5 (Day 14 cumulative)
   - Email 7: 7 days after Email 6 (Day 21 cumulative)

### Contact Attributes Needed

These custom attributes must exist in Brevo (some may already):
- `FIRSTNAME` -- customer's first name
- `AI_NAME` -- the name chosen during naming ceremony
- `MAGIC_LINK` -- the portal access URL

### Personalization Fallbacks

If `AI_NAME` is not set, use "your AI partner" as fallback.
If `FIRSTNAME` is not set, use "there" as fallback (e.g., "Hi there,").

### HTML Template Notes

- Use the same dark PureBrain template as the Neural Feed sequence (templates 1-7)
- Background: `#080a12`, container: `#0d1117`, text: `#e0e6f0`
- Brand colors: blue `#2a93c1`, orange `#f1420b`
- CTA buttons: orange `#f1420b`, white text
- Include `{{ unsubscribe }}` in footer
- PureBrain hexagon icon in header

### CTA Links

All portal CTAs should use `{{contact.MAGIC_LINK}}` for personalized portal access.
Do NOT use `https://purebrain.ai/#awakening` -- that is for pre-purchase sequences only.

---

## Review Checklist for Jared

- [ ] Does Email 2 sound like you? (It's drafted in your voice but you should confirm)
- [ ] Is the timing right? (Day 0, 1, 3, 7, 10, 14, 21)
- [ ] Are the Aether-voice emails (1, 3, 5) authentic to how Aether communicates?
- [ ] Does the Day 14 check-in feel genuine, not corporate?
- [ ] Any capabilities mentioned that we can't actually deliver yet?
- [ ] Comfortable with the soft referral mention in Email 7?
- [ ] Any subject lines you'd change?

---

## After Approval

1. Route to ST# to create Brevo templates and automation workflow
2. Test with sandbox customer flow end-to-end
3. Activate for new customers only (existing customers NOT retroactively enrolled)
4. Monitor: open rates, reply rates (especially Emails 3 and 6), unsubscribe rates

---

**END OF DRAFT**
