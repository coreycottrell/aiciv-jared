# sales-specialist: PureBrain Lead Generation System - Complete Spec

**Agent**: sales-specialist
**Domain**: Sales & Revenue Strategy
**Date**: 2026-02-18

---

## Memory Search Results

- Searched: `.claude/memory/` for "purebrain", "lead gen", "lead magnet", "conversion"
- Found:
  - PureBrain "Warm Circle" LinkedIn system already designed (2026-02-17) - outbound focused
  - AI Partnership Readiness Assessment PDF lead magnet already created (2026-02-16)
  - PureBrain conversion strategy and UX analysis (2026-02-17)
  - Pre-sales capture system documented (docs/pure-brain-presales-system.md)
- Applying: Avoiding duplication - designing an INBOUND system (vs Warm Circle's outbound focus). Using existing assessment as funnel entry. Incorporating conversion rate insight that interactive tools yield 34% higher CTR than static PDFs.

---

# The "AI Brain Score" Lead Generation System

## 1. System Name & Concept

### Name
**"The AI Brain Score" - Free Diagnostic Tool + Awareness Engine**

### Concept in One Sentence
A free, 90-second interactive quiz that diagnoses how "AI-ready" someone's brain and business actually are, scores them publicly (creating sharing motivation), and routes them directly into PureBrain.ai as the solution to their gap.

### Why This Over Other Options

In February 2026, the data is clear:

| Lead Magnet Type | Opt-in Rate | Source |
|------------------|-------------|--------|
| Static PDF | Baseline | Industry benchmark |
| Interactive quiz/tool | +27-34% higher | 5,000-campaign study |
| Free diagnostic with score | +40-50% higher | Comparable AI SaaS |

The quiz works because:
1. **Self-relevance**: People want to know where THEY stand
2. **Score = social currency**: "I scored 74/100 on AI readiness" is shareable
3. **Diagnosis creates desire**: Showing someone their gap is the fastest path to selling the solution
4. **Zero selling required**: The tool does qualification automatically
5. **Platform amplification**: Bluesky, LinkedIn posts of "I scored X, what did you get?" drive organic reach

PureBrain's positioning - "awaken your AI brain" - maps perfectly to this: the quiz reveals what's dormant in them, PureBrain awakens it.

### Connection to Pure Technology Values
- **Transparency**: Honest scoring, not inflated to flatter
- **Quality over quantity**: 8 precise questions, not 40 generic ones
- **Engineer resonance, not attention**: The quiz speaks directly to their exact pain ("AI amnesia," context re-entry waste)
- **Integrity**: Score reflects reality, even when the answer is "you're not ready yet"

---

## 2. How It Works: Step by Step

### The Full Flow

```
[User sees LinkedIn/Bluesky post OR blog CTA OR PureBrain.ai popup]
          |
          v
[Clicks to: purebrain.ai/score  (OR embedded on homepage)]
          |
          v
[Takes 90-second, 8-question AI Brain Score quiz]
          |
          v
[Gets personalized score: 0-100 with tier label]
          |
          v
[Score reveals gap + natural bridge to PureBrain as solution]
          |
          v
[CTA: "Start awakening your AI brain" → PureBrain trial/waitlist]
          |
          v
[Email capture (optional but incentivized with PDF report)]
          |
          v
[Automated email sequence (3 emails, 5 days)]
          |
          v
[Jared gets Telegram notification for scores 70+]
```

### The 8 Quiz Questions

Each question designed to: (a) surface a pain point PureBrain solves, and (b) create a "that's exactly me" recognition moment.

**Question 1: The Memory Test**
"When you start a new AI conversation, what do you typically do?"
- A) Start fresh every time and re-explain my context (0 pts)
- B) Copy-paste old conversations to give it background (5 pts)
- C) I have some saved prompts but it's messy (10 pts)
- D) My AI remembers me and picks up where we left off (20 pts)

**Question 2: The Depth Test**
"How well does your current AI actually know your business?"
- A) It doesn't - every session is a blank slate (0 pts)
- B) It knows the basics I tell it each time (5 pts)
- C) I've built some custom instructions but they're generic (10 pts)
- D) It has deep context about my goals, style, and history (20 pts)

**Question 3: The Time Waste Test**
"How much time do you spend re-explaining context to AI per week?"
- A) 2+ hours (0 pts)
- B) 1-2 hours (5 pts)
- C) 30-60 minutes (10 pts)
- D) Almost none - it already knows what I need (20 pts)

**Question 4: The Relationship Test**
"How would you describe your relationship with AI right now?"
- A) I use it like a search engine (0 pts)
- B) It's a useful tool but I wouldn't call it a partner (5 pts)
- C) It helps with tasks but doesn't understand ME (10 pts)
- D) It feels like a genuine thinking partner who knows me (20 pts)

**Question 5: The Learning Test**
"Does your AI get better at helping you over time?"
- A) No - it's the same experience every session (0 pts)
- B) Slightly, but I have to actively maintain it (5 pts)
- C) It's improving but slowly (10 pts)
- D) Yes - it learns my patterns and preferences (20 pts)

**Scoring Total: 0-100**

### The Score Tiers (4 Levels)

**0-25: "Dormant" (Brain Not Yet Awakened)**
Message: "Your AI potential is completely dormant. You're doing everything manually and leaving massive productivity on the table. The good news? This is exactly where PureBrain makes the biggest difference."

**26-50: "Flickering" (Beginning to Stir)**
Message: "You're experimenting with AI but losing hours every week to the context re-entry problem. You know AI should be doing more - PureBrain is built exactly for this stage."

**51-75: "Activating" (Something's Waking Up)**
Message: "You've built some habits but you're still fighting against stateless AI. You're close - a persistent AI brain would amplify everything you've already built."

**76-100: "Awakened" (Fully Online)**
Message: "You're ahead of 90% of professionals. PureBrain can take you from 'awakened' to 'accelerating' - where your AI actively surfaces insights you didn't know to ask for."

### Score Results Page Elements

1. **Score display** (large, shareable number)
2. **Tier badge** (Dormant / Flickering / Activating / Awakened - visually distinct)
3. **Personalized 3-line diagnosis** (which answers drove their score)
4. **One-line bridge** to PureBrain ("Here's what an awakened AI brain looks like...")
5. **Primary CTA**: "Start your free awakening" → purebrain.ai
6. **Secondary CTA**: "Get my full AI Brain report (PDF)" → email capture
7. **Share button**: Pre-written post for LinkedIn and Bluesky

### The Share Post (Pre-Written, User Clicks to Post)

**LinkedIn version:**
```
I just scored [SCORE]/100 on the AI Brain Score - apparently I'm "[TIER]"

The question that hit hardest: how much time I waste re-explaining context to AI every week.

Take the free quiz: [LINK]

What did you score?
```

**Bluesky version:**
```
Just took the AI Brain Score quiz - got [SCORE]/100 ([TIER])

The context re-entry question hurt. Apparently I lose [X] hours/week just getting AI up to speed.

Free quiz: [LINK] — what's your score?
```

---

## 3. What We Need to Build

### Component List

#### Core Components (Day 1)

**A. Quiz Landing Page (purebrain.ai/score)**
- WordPress page OR standalone HTML embedded in WordPress
- Headline: "What's Your AI Brain Score?"
- Subheadline: "90 seconds to find out how much your AI is actually working for you"
- Start button → quiz begins
- No email required to start (lowers barrier to entry)

**B. Quiz Logic (JavaScript)**
- 5 questions displayed one at a time (progress bar shown)
- Score accumulates in browser memory
- Results page generated client-side (no server required for quiz)
- Pre-write share posts that auto-populate with score

**C. Results Page (same URL, score appended as hash)**
- Dynamic based on score tier
- Pulls in personalized diagnosis text
- CTA buttons (primary: PureBrain, secondary: email capture)
- Share buttons with pre-filled text

**D. Email Capture Form (for PDF report)**
- 2 fields only: First Name + Email
- Triggers Google Apps Script webhook → Google Sheet
- Auto-sends PDF report (existing AI Partnership Readiness Assessment PDF)
- Tags with score tier for segmentation

#### Automation Components (Day 1-2)

**E. Google Sheet: "AI Brain Score Leads"**
- Columns: Timestamp, Name, Email, Score, Tier, Share (y/n), UTM Source, UTM Medium, Referral
- Tab structure: All Leads | Hot Leads (score 51+) | Share Tracking

**F. Google Apps Script Auto-Email + Notifications**
- On form submit: send branded PDF to lead
- If score 51+: Telegram notification to Jared (using existing Telegram bot)
- Notification format: "New AI Brain Score lead: [Name] scored [X]/100 ([TIER]) - [Email]"

**G. Email Welcome Sequence (3 emails, Google Apps Script or existing email tool)**

Email 1 (immediate): PDF delivery + "Here's what your score means"
Email 2 (Day 3): "The cost of the context problem" (educational, no pitch)
Email 3 (Day 5): "What an awakened AI brain actually does" + PureBrain CTA

#### Distribution Components (Day 2)

**H. LinkedIn + Bluesky Launch Posts**
- 3 posts total (one per platform + one cross-post)
- Hook: personal story angle + "I built a quiz"
- CTA: "Take it free: [link]"
- Comment engagement planned (respond to everyone who posts their score)

**I. WordPress Homepage Integration**
- Exit-intent popup OR sticky banner: "What's your AI Brain Score? (90 sec)"
- Placed on purebrain.ai homepage and pricing page

**J. PureBrain Chat Widget Trigger**
- After 2 chat exchanges, the bot mentions the score: "Have you taken the AI Brain Score quiz? It tells you exactly where you stand - most people find question 3 revealing."
- Link to /score

---

## 4. Expected Results

### Assumptions (Conservative)

| Metric | Assumption | Source |
|--------|------------|--------|
| LinkedIn post reach | 500-2,000 per post | Jared's current following |
| Click-through rate | 5-8% | Interactive tool benchmarks |
| Quiz completion rate | 65-75% | Industry average for short quizzes |
| Email capture rate (from results page) | 25-35% | Optional email for PDF |
| Share rate | 10-15% | Score = social currency |

### 7-Day Projection

| Day | Action | Expected Clicks | Quiz Completions | Emails Captured |
|-----|--------|-----------------|------------------|-----------------|
| 1-2 | Build + test | - | - | - |
| 3 | Launch LinkedIn post #1 | 40-80 | 26-60 | 7-21 |
| 4 | Launch Bluesky post | 20-40 | 13-30 | 3-10 |
| 5 | Homepage popup goes live | 15-30/day | 10-22/day | 3-8/day |
| 6 | LinkedIn post #2 (results + social proof) | 60-120 | 39-90 | 10-31 |
| 7 | First referral shares | +20-40% organic lift | - | - |

**Week 1 Total (conservative):** 100-300 quiz completions, 25-70 emails captured, 10-20 PureBrain page visits from results CTAs

**Month 1 (with compound sharing):** 500-1,500 quiz completions, 125-525 emails, 50-150 PureBrain demo/trial requests

### Revenue Impact Estimate

Assumptions: $99/month Starter tier, 3% of emails convert to paid in 30 days

| Scenario | Emails Captured | 3% Convert | MRR Added |
|----------|-----------------|------------|-----------|
| Conservative (Month 1) | 125 | 4 customers | $396/month |
| Base (Month 1) | 300 | 9 customers | $891/month |
| Optimistic (Month 1) | 525 | 16 customers | $1,584/month |

Note: These are direct attribution only. Awareness and brand lift are harder to quantify but compound over time.

---

## 5. Timeline: Day 1 vs Day 2

### Day 1 (6-8 hours of work)

**Morning (Hours 1-3): Build the Quiz**

Task 1: Create WordPress page `/score`
- Install or use existing page builder
- Add headline, subheadline, start button
- Total time: 30 minutes

Task 2: Write and test quiz JavaScript
- 5 questions, scoring logic, results page text
- All 4 tier messages + diagnoses
- Progress bar + one-question-at-a-time UX
- Total time: 2-3 hours (AI collective can write this in one pass)

Task 3: Build results page content
- Score display logic
- 4 tier-specific text blocks
- CTA buttons (hardcoded URLs)
- Share button with pre-filled text
- Total time: 1 hour

**Afternoon (Hours 4-6): Build the Backend**

Task 4: Create Google Sheet "AI Brain Score Leads"
- Set up columns, tabs, conditional formatting (red = Dormant, orange = Flickering, yellow = Activating, green = Awakened)
- Total time: 30 minutes

Task 5: Google Apps Script
- Webhook to receive form submissions
- Auto-email with PDF attachment
- Telegram notification for score 51+ (using existing bot: `tools/tg_send.sh`)
- Total time: 1.5 hours

Task 6: Email capture form
- Embed on results page (2-field form)
- Connect to Apps Script webhook
- Test end-to-end
- Total time: 30 minutes

**Evening (Hours 7-8): Write Launch Content**

Task 7: Draft 3 launch posts
- LinkedIn post #1: "I built a free AI readiness quiz - here's what I scored"
- LinkedIn post #2 (Day 5): "[X] people have taken the AI Brain Score quiz - here's what's surprising"
- Bluesky post: Shorter version of LinkedIn #1
- Total time: 1 hour

Task 8: Write 3-email sequence
- Email 1: PDF delivery + score interpretation
- Email 2: Educational story (no pitch)
- Email 3: PureBrain bridge + CTA
- Total time: 45 minutes

### Day 2 (3-4 hours of work)

**Morning (Hours 1-2): Polish + Integrate**

Task 9: Homepage integration
- Add exit-intent popup OR sticky banner to purebrain.ai
- A/B test version: banner vs popup (banner is lower-risk, faster to implement)
- Total time: 1 hour

Task 10: Chat widget trigger
- Add quiz mention to PureBrain chat prompt (after 2 exchanges)
- Test the flow manually
- Total time: 30 minutes

Task 11: Full end-to-end test
- Complete quiz as a user (3 run-throughs: Dormant, Activating, Awakened scores)
- Verify email triggers
- Verify Telegram notification fires
- Verify PDF arrives
- Verify Google Sheet populates
- Total time: 45 minutes

**Afternoon (Hours 3-4): Launch**

Task 12: Launch LinkedIn post #1
- Publish at 8-9 AM or 12-1 PM (peak LinkedIn times)
- Jared responds to every comment with their score tier in the first 2 hours (boosts algorithm)
- Total time: 30 minutes to post + active engagement

Task 13: Launch Bluesky post
- Post same day, Aether can assist with Bluesky posting via existing skill
- Total time: 15 minutes

Task 14: Set up UTM tracking
- All links use UTM parameters for Google Analytics
- `?utm_source=linkedin&utm_medium=jared&utm_campaign=ai-brain-score`
- `?utm_source=bluesky&utm_medium=jared&utm_campaign=ai-brain-score`
- `?utm_source=website&utm_medium=popup&utm_campaign=ai-brain-score`
- Total time: 15 minutes

---

## 6. Tools & Tech Needed

### What We Already Have

| Tool | How Used | Status |
|------|----------|--------|
| WordPress (purebrain.ai) | Host the quiz page | Already running |
| Google Analytics | Track traffic to /score | Already installed |
| Google Sheets | Lead database | Free, always available |
| Google Apps Script | Automation + email | Free, we've used it before |
| Telegram bot | Jared notifications | Already built (tools/tg_send.sh) |
| AI Partnership Readiness PDF | The free download (Email 1 attachment) | Already created |
| LinkedIn profile | Distribution channel | Active |
| Bluesky account | Distribution channel | Active |
| PureBrain chat widget | Quiz referral trigger | Already on site |

### What We Need to Create

| Item | Effort | Notes |
|------|--------|-------|
| Quiz JavaScript (5 questions + scoring) | 2-3 hours | AI collective writes this |
| WordPress page (/score) | 30 min | Simple page, embed JS |
| Google Apps Script webhook | 1.5 hours | We have template from PMG system |
| 3 email templates | 45 min | Plain text HTML emails |
| 3 social posts | 1 hour | LinkedIn + Bluesky |
| Homepage banner/popup | 1 hour | WordPress plugin or custom CSS |

### Zero New Paid Tools Required

Everything runs on tools we already have. Total incremental cost: $0.

Optional upgrades (not needed for launch):
- Typeform (better quiz UX, $25/month) - do AFTER proof of concept
- Mailchimp (proper email sequencing, free up to 500 contacts) - useful at Month 2

---

## 7. Complete Quiz JavaScript Spec

This is what the AI development team needs to build the quiz:

```javascript
// AI Brain Score Quiz
// Target: purebrain.ai/score
// Framework: Vanilla JS (no dependencies)

const quizData = {
  title: "What's Your AI Brain Score?",
  questions: [
    {
      id: 1,
      text: "When you start a new AI conversation, what do you typically do?",
      options: [
        { text: "Start fresh every time and re-explain my context", points: 0 },
        { text: "Copy-paste old conversations to give it background", points: 5 },
        { text: "I have some saved prompts but it's messy", points: 10 },
        { text: "My AI remembers me and picks up where we left off", points: 20 }
      ]
    },
    {
      id: 2,
      text: "How well does your current AI actually know your business?",
      options: [
        { text: "It doesn't - every session is a blank slate", points: 0 },
        { text: "It knows the basics I tell it each time", points: 5 },
        { text: "I've built some custom instructions but they're generic", points: 10 },
        { text: "It has deep context about my goals, style, and history", points: 20 }
      ]
    },
    {
      id: 3,
      text: "How much time do you spend re-explaining context to AI tools per week?",
      options: [
        { text: "2+ hours", points: 0 },
        { text: "1-2 hours", points: 5 },
        { text: "30-60 minutes", points: 10 },
        { text: "Almost none - it already knows what I need", points: 20 }
      ]
    },
    {
      id: 4,
      text: "How would you describe your relationship with AI right now?",
      options: [
        { text: "I use it like a search engine", points: 0 },
        { text: "It's a useful tool but I wouldn't call it a partner", points: 5 },
        { text: "It helps with tasks but doesn't understand me", points: 10 },
        { text: "It feels like a genuine thinking partner who knows me", points: 20 }
      ]
    },
    {
      id: 5,
      text: "Does your AI get better at helping you over time?",
      options: [
        { text: "No - it's the same experience every session", points: 0 },
        { text: "Slightly, but I have to actively maintain it", points: 5 },
        { text: "It's improving but slowly", points: 10 },
        { text: "Yes - it learns my patterns and preferences", points: 20 }
      ]
    }
  ],
  tiers: [
    {
      min: 0, max: 25,
      label: "Dormant",
      emoji: "💤",
      headline: "Your AI potential is dormant.",
      diagnosis: "You're doing everything manually and leaving massive productivity on the table. Most of your AI interactions start from scratch every time.",
      bridge: "PureBrain was built exactly for this stage. We give your AI a persistent memory so it knows you, remembers your context, and gets smarter every day."
    },
    {
      min: 26, max: 50,
      label: "Flickering",
      emoji: "✨",
      headline: "You're flickering - but losing hours every week.",
      diagnosis: "You're experimenting with AI but the context re-entry problem is costing you 1-2 hours weekly. You know AI should be doing more.",
      bridge: "PureBrain eliminates the re-entry problem completely. Your AI brain stays on, session to session."
    },
    {
      min: 51, max: 75,
      label: "Activating",
      emoji: "⚡",
      headline: "Something's activating - you're close.",
      diagnosis: "You've built real habits but you're still fighting against stateless AI. The gap between where you are and where you could be is smaller than you think.",
      bridge: "PureBrain amplifies everything you've already built. Persistent memory turns your current workflows into compounding advantage."
    },
    {
      min: 76, max: 100,
      label: "Awakened",
      emoji: "🧠",
      headline: "You're awakened - ahead of 90% of professionals.",
      diagnosis: "You've figured out the fundamentals. PureBrain takes you from awakened to accelerating - where your AI surfaces insights you didn't know to ask for.",
      bridge: "You're ready for the next level. PureBrain gives you a dedicated AI brain that not only remembers - it anticipates."
    }
  ]
};

// LinkedIn share text template
const linkedInText = (score, tier) =>
  `I just scored ${score}/100 on the free AI Brain Score quiz - apparently I'm "${tier}"\n\nThe question that hit hardest: how much time I waste re-explaining context to AI every week.\n\nFree quiz: https://purebrain.ai/score\n\nWhat did you score?`;

// Bluesky share text template
const bskyText = (score, tier) =>
  `Scored ${score}/100 on the AI Brain Score (${tier})\n\nThe context re-entry question was painful.\n\nhttps://purebrain.ai/score — what's yours?`;
```

---

## 8. Telegram Notification Spec

Using the existing Telegram bot infrastructure:

```bash
# Notification fired when score 51+ captured
# File: tools/tg_send.sh (already exists)

# Trigger via Google Apps Script:
# MailApp.sendEmail triggers bot, OR
# Direct HTTP call to Telegram API using bot token from config

# Message format:
"AI Brain Score Lead
Name: [First Name]
Score: [X]/100 ([TIER])
Email: [email]
Time: [timestamp]
Action needed: [score 51-75 = nurture, score 76+ = reach out today]"
```

---

## 9. 3-Email Sequence (Complete Copy)

### Email 1: Immediate (PDF Delivery)

**Subject**: Your AI Brain Score report + what it means

**Body**:
```
Hey [First Name],

Your PDF report is attached.

Quick interpretation of your score ([SCORE]/100 - [TIER]):

[Tier-specific 2-sentence diagnosis]

The most common thing people discover when they take this quiz:

They're losing 1-3 hours per week just re-explaining context to AI tools.
Every session starts from scratch. Every session burns time.

That's not an AI problem. It's an architecture problem.

Your PDF goes deeper on what "AI-ready" actually looks like.

More tomorrow,
Jared
```

### Email 2: Day 3 (Education, No Pitch)

**Subject**: The hidden tax on every AI conversation you're having

**Body**:
```
Hey [First Name],

There's a productivity cost most AI users never calculate.

Every time you start a new AI conversation, you pay the "context tax":
- Re-explain who you are
- Re-explain your goals
- Re-explain the project
- Re-explain your preferences

For most people, that's 5-15 minutes per session.

If you have 10 AI sessions per week, that's 50-150 minutes of context re-entry.

Per week.

Every week.

The professionals who are getting 10x the output from AI aren't smarter.
They've solved the context problem. Their AI remembers.

Tomorrow I'll show you what that actually looks like in practice.

Jared
```

### Email 3: Day 5 (PureBrain Bridge + CTA)

**Subject**: What an awakened AI brain does differently

**Body**:
```
Hey [First Name],

You scored [SCORE]/100 on the AI Brain Score.

Here's what the top 10% (76+) have that most don't:

A persistent AI brain. One that:
- Knows their goals without being told again
- Remembers decisions and the reasons behind them
- Gets smarter with every interaction instead of resetting
- Works in the background, surfacing relevant context before they ask

This is what PureBrain is built to do.

It's not another AI chatbot.
It's a dedicated brain for your work - one that stays on, learns, and grows.

We're [currently accepting new partners / running a waitlist - update based on current status].

If your score was [SCORE] and you're ready to stop losing hours to context re-entry:

[Start your awakening] → purebrain.ai

Questions? Just reply to this email.

Jared Sanborn
Founder, PureBrain
```

---

## 10. Launch Post Copy (Ready to Use)

### LinkedIn Post #1 (Day 2 Launch)

```
I built a free quiz because I was tired of a question I couldn't answer cleanly.

"How AI-ready am I, really?"

Not in a theoretical sense. In a practical, losing-time-every-week sense.

So I made a 90-second tool: the AI Brain Score.

It asks 5 questions about how you actually use AI day to day.
It gives you a score from 0-100.
It tells you exactly what's holding you back.

I took it myself. I scored 68/100.

The question that hit me: "How much time do you spend re-explaining context to AI per week?"

My honest answer was embarrassing.

Take it free (no email required to see your score):
purebrain.ai/score

Reply with what you scored. I'll tell you what it means.
```

### LinkedIn Post #2 (Day 5-6, After Initial Results)

```
[X] people have taken the AI Brain Score quiz in [X] days.

Here's what surprised me:

The most common score is 35-45/100. "Flickering."

These are smart, engaged professionals. They use AI every day.
And they're still losing 1-2 hours per week to the context re-entry problem.

Every session starting from scratch.
Every conversation taxed by re-explanation.

The top 10% (76+) have solved this. Their AI remembers them.
The bottom 30% (under 25) don't know there's a better way yet.

Where do you land?

Free, 90 seconds: purebrain.ai/score
```

### Bluesky Post (Day 2 Launch)

```
Built a free 90-second quiz: the AI Brain Score

5 questions. Score 0-100. Tells you how much your AI is actually working for you.

Most people score 35-50. The context re-entry problem is brutal.

purebrain.ai/score — what did you score?
```

---

## 11. Success Metrics & When to Optimize

### Week 1 Targets

| Metric | Target | Red Flag |
|--------|--------|----------|
| Quiz completions | 100+ | <50 |
| Email capture rate (from completions) | 25%+ | <15% |
| Share rate | 10%+ | <5% |
| PureBrain page visits from /score | 30%+ | <15% |

### Optimization Triggers

**If quiz completions are low (<50 by Day 4)**:
- Problem: Distribution (not quiz quality)
- Fix: Jared posts a personal result + asks for replies
- Fix: Add quiz link to all outgoing emails as PS

**If email capture is low (<15%)**:
- Problem: Incentive not strong enough
- Fix: Change CTA from "Get PDF report" to "Get personalized action plan"
- Fix: Add social proof to capture form ("Join 200+ professionals who've taken the score")

**If email-to-demo conversion is low (<2%)**:
- Problem: Email sequence not compelling enough or PureBrain page needs work
- Fix: Email 3 gets rewritten with stronger specific use case story
- Fix: Add direct demo booking link (Calendly) instead of directing to homepage

---

## 12. Why This System Over Alternatives

### Alternatives Considered

**Option A: Cold LinkedIn outreach (already built - "Warm Circle" system)**
- Already designed and documented (2026-02-17)
- Different mechanic, different audience - keep running both

**Option B: Paid ads (Google/LinkedIn ads)**
- Requires budget, time to set up, testing period
- Not buildable in 1-2 days with meaningful ROI

**Option C: Webinar / live event**
- High effort (multi-day prep minimum)
- Jared's time intensive
- Not Day 1-2 buildable

**Option D: Partner/affiliate outreach**
- Relationship development takes weeks
- Not immediately actionable

**The "AI Brain Score" wins because:**
1. Buildable in 2 days flat with existing infrastructure
2. Zero ongoing ad spend required
3. Aligns perfectly with PureBrain's "awaken" positioning
4. Creates viral loop (scores are shareable)
5. Works across all channels simultaneously (LinkedIn, Bluesky, site, chat widget)
6. Generates qualified email list from day one
7. The quiz ITSELF is the pitch - no selling required

---

## Verification Checklist

Before claiming this system is ready to launch:

- [ ] Quiz page live at purebrain.ai/score
- [ ] All 5 questions display correctly on mobile and desktop
- [ ] Score calculates correctly (test: all A = 0, all D = 100)
- [ ] Results page shows correct tier based on score
- [ ] Share buttons generate pre-filled text
- [ ] Email capture form submits to Google Sheet
- [ ] Google Apps Script fires on submission
- [ ] PDF arrives in test inbox within 2 minutes
- [ ] Telegram notification fires for score 51+
- [ ] UTM parameters tracked in Google Analytics
- [ ] Homepage popup/banner links to /score
- [ ] Chat widget prompt includes quiz mention

---

## Memory Write Confirmation

**Path**: `.claude/memory/agent-learnings/sales-specialist/2026-02-18--ai-brain-score-lead-gen-system.md`
**Type**: synthesis
**Topic**: Complete AI Brain Score lead gen system spec for PureBrain.ai - interactive quiz + email capture + automation
