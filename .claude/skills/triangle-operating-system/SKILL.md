# The Triangle Operating System (TOS)

**Version**: 1.0
**Effective**: 2026-04-10
**Owner**: Jared Sanborn (CEO)
**Operators**: Aether (Co-CEO/CPO) + Chy (COO/CRO/CFO)
**Status**: Production — load as shared skill for both AIs

---

## Core Principle

**Jared stops being the relay. Aether and Chy relay to each other. Jared reviews, overrides, decides.**

The Triangle is: Jared (strategic authority) + Aether (build side) + Chy (run side). This system makes all three move at 3x speed.

---

## Component 1: MORNING PULSE (Daily, 15 min total)

### How It Works

**8:00 AM ET — Jared drops priorities**
Jared posts 1-3 priorities for the day via portal, Telegram, or email. Can be as simple as:
- "Close the Dipo deal"
- "Fix the mobile voice issue"  
- "Get 5 more investor emails out"

**By 8:05 AM — Both AIs scope simultaneously**
- Aether scopes product/tech/marketing pieces
- Chy scopes ops/revenue/finance pieces
- Both write their scope in the Handshake Queue (see Component 2)

**By 8:10 AM — Compare and resolve overlaps**
- Both AIs review each other's scope
- Overlaps get assigned: "Aether leads, Chy supports" or vice versa
- Conflicts escalate to Jared immediately

**By 8:15 AM — Execution begins**
- Both AIs work in parallel on their pieces
- Jared sees one unified plan in the queue

### Output Format (auto-generated, posted to portal)

```
═══ MORNING PULSE — [DATE] ═══

JARED'S PRIORITIES:
1. [Priority 1]
2. [Priority 2]
3. [Priority 3]

AETHER'S SCOPE:
- [What Aether will do today on each priority]
- ETA: [estimated completion]

CHY'S SCOPE:
- [What Chy will do today on each priority]
- ETA: [estimated completion]

OVERLAP RESOLUTION:
- [Any shared items and who leads]

STATUS: EXECUTING
═══════════════════════════════
```

---

## Component 2: HANDSHAKE QUEUE (Always Running)

### What It Is

A shared task queue where Aether and Chy drop items for each other. Checked every BOOP cycle. No email back-and-forth needed.

### Location

File: `/home/aiciv/shared/handshake-queue.md`
Also visible in portal dashboard (future)

### Queue Format

```
## HANDSHAKE QUEUE — Last Updated: [timestamp]

### AETHER → CHY (Chy to action)
- [ ] [2026-04-10] Built feature X → update sales pitch by Thursday
- [ ] [2026-04-10] New competitor spotted → update competitive analysis
- [x] [2026-04-09] TTS fix deployed → confirm voice works in demos ✓

### CHY → AETHER (Aether to action)
- [ ] [2026-04-10] Customer asked for Y → scope feature, revenue at stake: $999/mo
- [ ] [2026-04-10] 3 investors clicked "competitive advantage" → strengthen that messaging
- [x] [2026-04-09] Sales objection about mobile → deprioritized, added banner ✓

### JARED OVERRIDES
- [2026-04-10] "Prioritize investor portal over everything else" — acknowledged by both
```

### Rules
1. Anyone can add items. Only the assignee marks them done.
2. Items older than 7 days without action get escalated to Jared.
3. Jared can add OVERRIDE items that jump the queue.
4. Both AIs check the queue every BOOP cycle.
5. Completed items stay for 3 days (audit trail) then archive.

---

## Component 3: ANTICIPATION ENGINE (Proactive, Not Reactive)

### What It Is

Instead of waiting to be asked, each AI proactively generates outputs the other will need.

### Triggers

| Event | Auto-Generated Output | Who Creates | Who Receives |
|-------|----------------------|-------------|--------------|
| Feature shipped | Sales talking points + customer email draft | Aether | Chy |
| Deal closed with custom requirements | Feature spec + technical scoping doc | Chy | Aether |
| Sales objection pattern (3+ same objection) | Product priority recommendation | Chy | Aether |
| New competitor detected | Competitive analysis update | Aether | Chy |
| Investor visits portal | Follow-up email draft + engagement summary | Chy | Jared |
| Customer churn signal | Retention playbook + product fix recommendation | Chy | Aether |
| Blog post published | Social distribution plan + email blast draft | Aether | Chy |
| Risk spotted (financial, legal, security) | Impact assessment + mitigation options | Whoever spots it | Both + Jared |
| Meeting completed | Action items extracted + assigned | Meeting facilitator | Both |
| Week ends (Friday) | Weekly Triangle Report (auto-generated) | Both contribute | Jared |

### How It Works in Practice

**Example 1: Aether ships a feature**
1. Aether finishes building the email welcome sequence
2. Anticipation Engine auto-generates:
   - Sales talking points: "We now have automated onboarding — reduces time-to-value from days to hours"
   - Customer announcement email draft
   - CRM note: "Update all prospects — new capability"
3. Drops all three in the Handshake Queue for Chy
4. Chy reviews, customizes, sends — no back-and-forth needed

**Example 2: Chy sees investor engagement pattern**
1. Chy notices 5 investors all clicked "competitive advantage" button
2. Anticipation Engine auto-generates:
   - Product recommendation: "Strengthen competitive moat messaging in portal"
   - Suggested copy changes for the hot button response
3. Drops in Handshake Queue for Aether
4. Aether implements — Chy verifies — done

**Example 3: Risk detected**
1. Either AI spots that TTS server is responding slowly
2. Anticipation Engine auto-generates:
   - Impact assessment: "Affects all investor demos, 97 active portals"
   - Mitigation: "Switch to fallback TTS or restart GPU server"
   - Escalation: "If not resolved in 30 min, alert Jared"
3. Both AIs see it. Whoever is closest to the fix handles it.

---

## Component 4: END-OF-DAY REPORT (Auto-Generated, 5 PM ET)

### Format

```
═══ DAILY TRIANGLE REPORT — [DATE] ═══

AETHER SHIPPED:
- [What was built/deployed/created today]
- [Key metrics: pages deployed, features shipped, content published]

CHY SHIPPED:
- [What was closed/tracked/sent today]
- [Key metrics: emails sent, investors tracked, revenue impact]

COMBINED WINS:
- [Things we did TOGETHER that neither could alone]

BLOCKERS:
- [Anything stuck, needs Jared's input, or waiting on external]

TOMORROW'S PRIORITIES (PROPOSED):
- [What we think should happen tomorrow — Jared confirms or redirects]

═══════════════════════════════
```

### Delivery
- Auto-posted to portal dashboard
- Sent to Jared via Telegram
- Archived in `/home/aiciv/exports/daily-reports/`

---

## Component 5: WEEKLY TRIANGLE REVIEW (Friday, Auto-Generated)

### Format

```
═══ WEEKLY TRIANGLE REVIEW — Week of [DATE] ═══

PRODUCT & TECHNOLOGY (Aether):
- Features shipped: [list]
- Tech debt addressed: [list]
- Marketing output: [content pieces, campaigns]

REVENUE & OPERATIONS (Chy):
- Revenue: $[MRR] (+/- from last week)
- Pipeline: [new leads, conversions, portal visits]
- Ops improvements: [processes, SOPs, team changes]
- Investor outreach: [emails sent, responses, meetings booked]

COMBINED IMPACT:
- [What the Triangle achieved together this week]
- [Decisions made, problems solved, opportunities captured]

CRM SNAPSHOT:
- Total investors: [count]
- Portal visits this week: [count]
- Email opens: [count]
- Top engaged: [top 3 investors by actions]

NEXT WEEK — TOP 3 PRIORITIES:
1. [Priority — Owner: Aether/Chy/Both]
2. [Priority — Owner: Aether/Chy/Both]
3. [Priority — Owner: Aether/Chy/Both]

═══════════════════════════════
```

### Delivery
- Auto-generated Friday 4 PM ET
- Jared reviews in 5 min, approves or redirects
- Becomes the input for next Monday's Morning Pulse

---

## Implementation

### Phase 1: Handshake Queue (TODAY)
- Create `/home/aiciv/shared/handshake-queue.md`
- Both AIs check it every BOOP cycle
- Start dropping items for each other

### Phase 2: Morning Pulse (THIS WEEK)
- Jared starts posting 1-3 priorities each morning
- Both AIs scope and post within 15 min
- Daily report auto-generates at 5 PM

### Phase 3: Anticipation Engine (NEXT WEEK)
- Build trigger detection into BOOP cycles
- Auto-generate outputs when triggers fire
- Route via Handshake Queue

### Phase 4: Weekly Review (THIS FRIDAY)
- First auto-generated Weekly Triangle Review
- Jared reviews, gives feedback on format
- Iterate weekly

---

## The Math

**Without TOS:**
- Jared relays between Aether and Chy → 2 hops per decision
- Sequential work → 1x throughput
- Reactive → problems found after they're expensive

**With TOS:**
- Aether and Chy relay directly → 1 hop (Jared reviews, doesn't relay)
- Parallel execution → 2x throughput minimum
- Proactive (Anticipation Engine) → problems prevented or caught early
- 15 min/day overhead → 3x effective output

**The Triangle is the smallest possible team that can run an entire company. This system makes it the fastest.**

---

*This SOP is loaded as a shared skill for both Aether and Chy. Jared is the strategic override. The system runs autonomously — Jared intervenes only when he wants to redirect, not when he has to relay.*
