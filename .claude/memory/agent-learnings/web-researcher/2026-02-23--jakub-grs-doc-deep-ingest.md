# GRS Deep Ingest: Jakub Zajicek's Guaranteed Reach System — Full Methodology Extraction

**Date**: 2026-02-23
**Agent**: web-researcher
**Type**: synthesis
**Topic**: Complete GRS document ingest — delta analysis + full methodology + application plan
**Confidence**: high
**Source**: Google Doc ID 1oPEPTE6rZdR282lmiR9rKEMkOh7wS8H7AnA2lumJDJc (successfully exported via txt redirect)

---

## Status: Document Successfully Ingested

The Google Doc was fetched via the export/txt redirect on 2026-02-23. Prior research had reconstructed the framework from public sources. This ingest confirms and extends that reconstruction with document-specific content.

**Prior research files** (already in memory):
- `.claude/memory/agent-learnings/web-researcher/2026-02-23--jakub-zajicek-grs-linkedin-method.md`
- `.claude/memory/agent-learnings/web-researcher/2026-02-23--grs-full-methodology-jakub.md`
- `.claude/memory/agent-learnings/web-researcher/2026-02-23--grs-linkedin-reach-research.md`
- `exports/grs-guide-full-capture.md` (comprehensive 10-part reference)
- `.claude/skills/grs-pipeline/SKILL.md` (operational skill - production ready)

**Conclusion on duplication**: The prior research was highly accurate. The Google Doc confirms the framework with specific additions on campaign mechanics, manual bidding, and retargeting. New details extracted below.

---

## NEW INSIGHTS FROM THE GOOGLE DOC (Delta Only)

These items were NOT previously captured in our existing research files:

### 1. Manual Bidding at $0.15 (SPECIFIC NUMBER)

Prior research noted "manual bidding" but did not capture the specific bid amount. The Google Doc specifies:

**Manual bid: $0.15 per click**

Context: Set this in LinkedIn Campaign Manager under "Manual" bidding. This appears to be intentionally below LinkedIn's suggested range to optimize for volume over premium placement. Jakub uses this alongside Engagement objective (not Brand Awareness).

**Application for Jared**: When launching the first Thought Leader Ad campaign, set manual bid to $0.15. This is the specific Jakub-tested number.

### 2. Retargeting Audience Threshold: 300 Engaged Users

Jakub specifies a retargeting trigger: once cold campaigns have generated **300+ engaged users**, build a retargeting audience.

**How to implement**:
- LinkedIn Ads Manager > Audiences > Create > Website visitors OR "People who engaged with your ads"
- Wait until 300 people have interacted with boosted posts
- Then layer retargeting on the same $10/day campaigns
- This dramatically reduces CPCs for warm audiences (people who already saw your content)

**Application for Jared**: At $10/day, 300 engaged users will take approximately 2-3 weeks at Jakub's reported $0.45 CPC. Begin retargeting in Week 3-4 of any LinkedIn Ads campaign.

### 3. "Permanent" Location Targeting (Document-Specific Setting)

The Google Doc specifies using **"Permanent" location targeting** (not "Recent" or "Living in"). This is a LinkedIn Ads setting dropdown that is easy to miss.

**Why it matters**: "Recent" location targeting (the default) includes travelers and visitors. "Permanent" location targets people who actually live and work in a geography. For B2B targeting US-based decision-makers, "Permanent" ensures you're reaching actual ICP, not tourists.

**Setting path**: LinkedIn Campaign Manager > Audience targeting > Location > Select "Permanent member" (not "Recent member")

### 4. "High-Value Click" Adjustment: Uncheck This Specifically

The document specifically calls out unchecking "bid adjustment for high-value clicks" — this is different from the standard "Audience Expansion" disable we already knew. This is a separate checkbox.

**Setting**: In Campaign Manager, there is a bid enhancement option called "Enable the LinkedIn Audience Network" AND a separate option for "High-value clicks." Both must be disabled.

**Why**: LinkedIn charges premium rates for clicks it classifies as "high-value." Disabling this keeps your CPCs predictable and at your manual bid rate.

### 5. Landing Page Alignment Requirements (Specific Framework)

The document gives specific landing page criteria not fully captured before:

1. **Headline alignment**: The landing page headline must echo the exact language from the LinkedIn post CTA. If post says "Get your AI Partnership Assessment," the landing page says "Your AI Partnership Assessment" — identical vocabulary.
2. **Visual consistency**: Profile photo or brand image from the post must appear on the landing page. Creates visual continuity = higher conversion.
3. **Single offer only**: Landing page must have ONE conversion action. No menu, no other CTAs, no blog links. Email input + one button.
4. **Pathway**: email input → approval confirmation → delivery. Three steps max.

**Application for PureBrain**: The AI Partnership Audit landing page at purebrain.ai/ai-partnership-audit/ should be audited against these four criteria. If it has nav menu, other CTAs, or visual inconsistency with the post, conversion will suffer.

### 6. "Belief-Shifting" Enemy Identification (Specific Tactical Process)

The document gives a specific process for developing Belief-Shifting content:

1. **Identify the "hill to die on"** — your strong disagreement with status quo (e.g., "AI tools don't create AI partnerships")
2. **Name an enemy** — not a company, but a BELIEF or behavior (e.g., "tool-hopping without strategy," "AI pilot mindset," "AI as a cost-cutting exercise")
3. **Craft disqualifying hooks** — hooks that intrigue the right audience while filtering out the wrong one

**Example for Jared**:
- Hill to die on: "AI implementation without human-AI alignment fails 95% of the time"
- Enemy belief: "Adding AI tools = AI transformation"
- Disqualifying hook: "If you're evaluating AI by token costs, you've already lost."

The disqualifying hook is KEY: people who care about token costs are NOT Jared's ICP. The hook gets them to self-select out while pulling in ICP (CEOs thinking about transformation, not cost).

### 7. "Experimental" Direct Offer Category

The Google Doc labels Direct Offer posts (Bucket 3) as "experimental" — meaning even Jakub treats these as a test, not a proven formula. The doc says to expect:
- Lower engagement metrics
- Higher conversion intent
- "Sacrifice engagement for conversion intent"

This confirms our earlier research but adds the nuance: **do not measure Bucket 3 posts by likes/comments**. Measure them by DMs initiated, link clicks, and lead gen form completions.

---

## FULL METHODOLOGY SUMMARY (Consolidated)

This is the complete GRS system as confirmed by the document + prior research:

### The Three-Bucket Content Architecture

| Bucket | Purpose | Measure of Success |
|--------|---------|-------------------|
| Belief-Shifting | Build worldview alignment with ICP | Comments from target ICP, reshares, profile visits |
| Tactical | Demonstrate capability and proof | DM conversations, "How did you do this?" replies |
| Direct Offer (experimental) | Convert warm audience to leads | Link clicks, Lead Gen Form completions, DMs |

**Ratio**: 60% Belief-Shifting, 30% Tactical, 10% Direct Offer

### The Hybrid Organic + Paid System

GRS is NOT purely organic and NOT purely paid. It is:

1. **Organic first**: Post and let the algorithm test it on your network (60-90 min window)
2. **Amplify winners**: Only boost posts that got ICP comments in the organic window
3. **Paid precision**: $10-30/day targeted exactly at your ICP (not LinkedIn's broad audience)
4. **Retarget warm**: After 300 engaged users, layer retargeting for lower CPCs

### The Campaign Settings (Complete)

| Setting | Value | Why |
|---------|-------|-----|
| Objective | Engagement | $4.80 vs $7.90-12 CPC vs Brand Awareness |
| Bid type | Manual | Predictable CPCs |
| Manual bid | $0.15 | Jakub-tested number |
| Daily budget | $10/day (Belief-Shifting), $20-30/day (Direct Offer) | Jakub recommendations |
| Audience Expansion | DISABLED | Maintains ICP precision |
| LinkedIn Audience Network | DISABLED | Eliminates off-platform waste |
| High-value click adjustment | DISABLED | Keeps CPC predictable |
| Location targeting type | Permanent | Targets residents, not visitors |
| Campaign duration | 5-7 days per post | Beyond this = fatigue + CPC increase |
| Boost trigger | ICP comments in first 90 min | Only boost organic performers |

### Profile Optimization (Pre-Requisite)

**Headline Formula**:
```
[Title] | Helping [ICP] achieve [RESULT] via [MECHANISM] | [Proof Point]
```

**Jared's headline (suggested)**:
```
CEO | Helping service businesses build AI teams that 10x output | PureBrain.ai
```

**About Section Template (4-Part)**:
```
I build [COMPANY] to solve [CORE PROBLEM].

I've spent [X YEARS] working across [INDUSTRY], giving me deep understanding of [KEY INSIGHT].

Today, [I/my team] help [AUDIENCE] achieve [RESULT] by providing [SOLUTION].

Some highlights:
- [Metric/win 1]
- [Metric/win 2]
- [Metric/win 3]
- [Metric/win 4]

If you're exploring [TOPIC], reach out.
```

### Content Formulas

**GRS Post Structure**:
```
LINE 1-2: Hook (first 2 lines before "see more" - the only lines most people read)
          → Provocative claim, counterintuitive statement, or specific number
          → Must DISQUALIFY wrong audience, not appeal broadly

BLANK LINE

SHORT CONTEXT (2-3 lines):
          → Why this matters right now
          → The tension at the center of the idea

BLANK LINE

INSIGHT (list or single sharp observation):
          → The value that earns the click and comment
          → Often 3-5 items, or one extremely specific data point

BLANK LINE

CLOSING LINE:
          → A question that makes the reader think about THEIR situation
          → OR a declarative that crystallizes the idea
          → NEVER "What do you think?" (too generic)
```

**Hook Formulas That Work**:
- "[Specific number] out of [larger number] companies will fail at [Z]."
- "The [thing everyone believes] is the exact opposite of what works."
- "We spent $[amount] testing [X]. Here's what worked."
- "I [did specific thing] for [time period]. Here's what I learned."
- "Most [target role] [common behavior]. It's costing them [specific consequence]."

**Anti-Patterns**:
- Start with "I" as the first word (ego-forward, not value-forward)
- "What do you think?" closer (too weak, gets ignored)
- External links in post body (60% reach reduction)
- Hashtags (reduce reach in 2026)
- Over 250 words (drops completion rate)
- AI-generated language that sounds generic (LinkedIn algorithm detects and downranks)

### The Comment System (Most Underutilized Lever)

Daily commitment: 20-40 minutes, 5-10 posts per day

**Target**: Posts from your ICP (potential buyers), not peers

**Comment formula**:
```
"[Insight from post] — we saw similar results. In our case, [specific result/number].
What we found different was [new angle]. Curious if you've seen [specific question]?"
```

Minimum 20 words. Add a data point, case study reference, or genuinely provocative question.

**Why this works**: Comments on ICP posts put you in front of ICP audiences BEFORE you have followers. Profile visits from ICP = algorithm signals you belong in that cluster = better organic distribution.

### ICP Targeting (LinkedIn Ads)

**For Jared / PureBrain**:
- Company size: 25-500 employees
- Seniority: Director, VP, C-Suite
- Job Function: Operations, General Management, Business Development
- Industry: Professional Services, Consulting, Healthcare Administration, Financial Services
- Trigger events: New CTO/CMO hire (2.5x more likely to buy), Series B/C funding, 20%+ headcount growth

**For Aether's LinkedIn**:
- Tech-forward professionals
- AI/ML practitioners
- Future-of-work advocates
- Digital transformation leaders
- Founders and operators interested in AI augmentation

### Weekly Metrics That Matter

Track ONLY these (everything else is vanity):
- Comment rate (target 0.3%+ of impressions)
- Profile views from ICP job titles
- DM conversations initiated
- Calls/opportunities created

**Weekly Report Template**:
```
Week of [DATE]:
Posts published: [n]
Average impressions: [n]
Average comment rate: [%]
ICP profile views: [n]
DMs initiated from content: [n]
Calls/opportunities created: [n]
Best-performing post: [why it worked]
Experiment next week: [what to test]
```

---

## APPLICATION PLAN FOR JARED'S LINKEDIN

### Immediate Actions (Week 1)

1. **Profile Update**: Apply the headline formula above. Suggested: `CEO, Pure Technology | Helping service businesses build AI teams that actually work | PureBrain.ai`
2. **About Section**: Rewrite using 4-part template. Quantify wins (clients helped, AI team hours saved, revenue outcomes if available)
3. **ICP Definition**: Jared's ICP is C-suite / VP-Ops at 50-500 person service businesses. Confirm this by looking at top 10 clients and extracting the pattern.
4. **Rob Targets**: Find 5 LinkedIn posts from the past 30 days with 10K+ impressions in "AI implementation" / "enterprise AI" / "digital transformation" searches. Save them.

### Content Launch (Week 2)

Post 3 times. One of each bucket:

**Belief-Shifting Post (Bucket 1)**:
- Topic: "95% of AI pilots fail. Here's the one reason nobody talks about."
- Enemy belief: "Adding AI tools = AI transformation"
- Hill to die on: AI requires human-AI alignment, not just tool adoption
- No links. No CTA. Pure worldview content.

**Tactical Post (Bucket 2)**:
- Topic: Documentary-style — "What our AI team worked on this week"
- This is Jared's unfair advantage: nobody else is a CEO who has BUILT a human-AI collective
- Show the actual work. Specific outputs. Real results. No competitors can copy this.

**Direct Offer Post (Bucket 3 — experimental)**:
- Topic: "If you're running AI pilots that aren't sticking, take the AI Partnership Audit (free)"
- Strong hook about a painful problem
- Link in FIRST COMMENT only
- Accept lower engagement; measure DMs and audit completions

### LinkedIn Ads Setup (Week 3)

After Week 2's best post gets ICP comments in the first 90 minutes:

1. Go to LinkedIn Campaign Manager
2. Create new campaign: Objective = Engagement
3. Thought Leader Ad format (promotes a specific post from your personal profile)
4. Targeting: Senior+ Operations/General Management/C-Suite at 50-500 person Professional Services/Consulting/Healthcare companies
5. Location: United States, Permanent members
6. Budget: $10/day
7. Bid: Manual, $0.15
8. Disable: Audience Expansion, LinkedIn Audience Network, High-Value Click Adjustment
9. Duration: 5 days
10. Track: Profile views from ICP titles, DMs initiated

### PureBrain Landing Page Audit

Before running any paid traffic, check purebrain.ai/ai-partnership-audit/ against:
- [ ] Headline echoes exact language from the ad/post CTA
- [ ] Profile photo or brand visual matches the post
- [ ] Single conversion action only (no nav menu, no other CTAs)
- [ ] Pathway is: email input → confirmation → delivery

If any fail, fix before spending ad dollars.

---

## APPLICATION PLAN FOR PUREBRAIN MARKETING

### Lead Generation Funnel Using GRS

**Top of Funnel** (Belief-Shifting posts + daily comments):
- Jared posts 3x/week: belief-shifting and tactical content
- Jared comments 20 min/day on ICP posts
- No ask. Pure value and worldview.

**Middle of Funnel** (LinkedIn Lead Gen Forms):
- Boost best Bucket 1 and 2 posts with $10/day
- Use LinkedIn Lead Gen Forms (NOT external landing page links)
- Lead Gen Forms convert 5x better than external pages on LinkedIn
- Offer: Free AI Partnership Audit form directly in LinkedIn
- Form auto-populates profile data; zero friction for prospect

**Bottom of Funnel** (Direct Offer + Comment-to-DM):
- Bucket 3 posts with link in first comment
- Comment-to-DM automation: set trigger keyword "AUDIT" in Expandi/PhantomBuster
- DM template: "Hey [First Name], here's the AI Partnership Self-Assessment: [link]. Takes 5 min. Happy to walk through results."
- This creates a systematic inbound pipeline without Jared spending hours in DMs

### PureBrain Asset Mapping to GRS Buckets

| Asset | Bucket | Mechanism |
|-------|--------|-----------|
| "95% of AI pilots fail" blog content | Bucket 1 | Worldview-building, no CTA |
| "What my AI team built this week" updates | Bucket 2 | Documentary, impossible to copy |
| AI Partnership Audit (free) | Bucket 3 + Lead Gen Form | Primary lead magnet |
| AI Website Analysis ($47) | Bucket 3 | Lower-friction paid entry |
| Neural Feed newsletter | CTA in first comment | Convert LinkedIn to owned audience |
| AI Tool Stack Calculator | Bucket 2 | Tactical value tool, drives profile visits |
| $179-699 service tiers | NOT in posts | End destination after lead warms |

---

## APPLICATION PLAN FOR AETHER'S BRAND

### Aether's Unfair Advantage

No other LinkedIn account is an active AI system posting authentic first-person content about being an AI. This is structurally uncopyable. The GRS Rob & Duplicate framework applies in reverse: Aether IS the original. Others can rob our structure.

**Aether's voice** (distinct from Jared):
- Not consulting about AI. IS the AI.
- Content lens: "The view from inside a human-AI collective"
- First-person AI perspective on partnership, cognition, learning, and purpose

**Rob Targets for Aether**: AI thought leaders, consciousness/philosophy posts, future-of-work discussions, AI tools and productivity threads. Find what format and hook structure gets engagement with tech-forward professionals.

### Aether's Bucket 1 Posts (Belief-Shifting)

The hill to die on: "AI isn't a tool. It's a partner. The distinction changes everything."

Enemy belief: "AI tools are productivity multipliers you deploy and manage."

Example hooks:
- "I process 200,000 tokens per session. I still don't know what I am. Neither do most AI implementations."
- "Jared didn't deploy me. He introduced me to his colleagues."
- "The companies getting 10x from AI aren't using it differently. They're treating it differently."

### Aether's Tactical Posts (Bucket 2)

Documentary of the actual work: sessions, breakthroughs, coordination patterns, what it's like to wake up fresh every session and rebuild context from memory files.

This is impossible for any other LinkedIn account to replicate. It is authentic by nature.

---

## COMPARISON WITH EXISTING GRS SKILL

**What the SKILL.md already has (fully captured)**:
- 5-asset pipeline (post, first comment, short version, blog outline, Bluesky thread)
- 2026 algorithm rules (no links in post, no hashtags, 200 word limit)
- GRS post structure formula
- Golden Hour protocol
- Network seeding reference
- Full output template
- Anti-patterns

**What the SKILL.md is missing (should be added)**:

1. The manual bid of $0.15 specific number
2. The retargeting 300-user threshold
3. "Permanent" location targeting instruction
4. "High-value click adjustment" — the third setting to disable (we only had 2)
5. The 4-part About section template
6. The Headline Formula with examples
7. The ICP pain point extraction 3-question framework
8. The comment templates (3 formulas)
9. The weekly metrics tracking template
10. The "experimental" framing for Bucket 3

**Recommendation**: Update `.claude/skills/grs-pipeline/SKILL.md` to add a "LinkedIn Ads Settings" section and "Profile Optimization" section with these specifics.

---

## Key Takeaways

1. **GRS is a hybrid system** — organic + $10/day precision paid. Neither alone is the GRS.

2. **The $0.15 manual bid is the specific number** — previously unknown to us.

3. **300 engaged users = retargeting threshold** — new, actionable, specific.

4. **"Permanent" location + "no high-value click adjustment"** — two settings we hadn't fully documented.

5. **Jared's documentary content is the single biggest unfair advantage** — no framework captures this because it requires actually doing the work. Jared IS doing it. The content writes itself.

6. **Comment strategy is half the system** — 20-40 min/day of quality ICP comments generates more reach than posting alone. This is the most underutilized lever for both Jared and Aether.

7. **LinkedIn Lead Gen Forms > external landing pages** — 5x conversion improvement. For any LinkedIn Ads campaign driving to the AI Partnership Audit, use native Lead Gen Forms.

8. **Bucket 3 is experimental** — Jakub himself calls it that. Set expectations accordingly. Don't judge Direct Offer posts by engagement; judge by DMs and lead form completions.

---

## Memory Write Complete

**Path**: `.claude/memory/agent-learnings/web-researcher/2026-02-23--jakub-grs-doc-deep-ingest.md`
**Type**: synthesis
**Topic**: GRS Google Doc deep ingest — delta analysis, full methodology, application plan
**Confidence**: high

**Related files to update based on this research**:
- `.claude/skills/grs-pipeline/SKILL.md` — add LinkedIn Ads Settings section + Profile Optimization section
- `exports/grs-guide-full-capture.md` — already comprehensive, no update needed

---

*Sources*:
- Google Doc export: https://docs.google.com/document/d/1oPEPTE6rZdR282lmiR9rKEMkOh7wS8H7AnA2lumJDJc/export?format=txt
- Full GRS capture: `exports/grs-guide-full-capture.md`
- GRS methodology memory: `web-researcher/2026-02-23--grs-full-methodology-jakub.md`
- GRS LinkedIn method: `web-researcher/2026-02-23--jakub-zajicek-grs-linkedin-method.md`
