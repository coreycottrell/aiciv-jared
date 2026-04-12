# strategy-specialist: Tech Stack Optimization Analysis

**Agent**: strategy-specialist
**Domain**: Strategic Planning & Goal Setting
**Date**: 2026-02-20
**Prepared for**: Jared Sanborn - Pure Technology / Pure Marketing Group

---

# Pure Technology & PMG: Tech Stack Optimization Analysis

**Current Monthly Spend**: $1,051.40
**Projected Optimized Spend**: $580 - $680/month (Tier 2 recommendations)
**Potential Annual Savings**: $4,400 - $5,700+

---

## Executive Summary

Your $1,051.40/month stack has three primary problems:

1. **Functional overlap** - You are paying for the same capability multiple times (most critically: scraping tools, project management tools, and design tools)
2. **Underutilized inclusions** - You are paying for Zoom when Google Meet is already inside your G-Suite subscription
3. **Tier mismatch** - Several tools are on plans that likely exceed your actual usage

The good news: you can cut 35-45% of spend without meaningfully disrupting operations, and potentially 50%+ with one quarter of intentional migration work. Here is how.

---

## Section 1: Current Stack Assessment

### What Each Tool Does in Your Workflow

| Tool | Primary Use | Monthly Cost | Notes |
|------|-------------|-------------|-------|
| G-Suite + Emails | Team email, Drive, Docs, Meet, Calendar | $268.80 | ~15-20 seats at ~$14-18/user |
| Semrush | SEO research, competitor analysis, rank tracking | $139.95 | Agency-grade feature set |
| Bitrix24 | CRM + project management + team collaboration | $124.00 | All-in-one: tasks, pipelines, comms |
| Instantly | Cold email outreach sequences at scale | $150.49 | Likely Hypergrowth or Agency plan |
| Zoom | Video conferencing (client calls, team meetings) | $90.58 | ~5-10 user Pro plan |
| Phantombuster | LinkedIn automation, social scraping, lead enrichment | $69.00 | Entry plan, ~20 phantom slots |
| Figma | Design, wireframing, client mockups | $45.00 | Professional plan |
| Apify | Web scraping, custom data extraction | $39.00 | Starter plan |
| Trello | Visual task boards, project tracking | $24.00 | Standard plan |
| Miro | Visual collaboration, whiteboarding, brainstorming | $20.00 | Team plan |
| ChatGPT | AI writing, research, ideation | $20.00 | Plus plan |
| VPN Plus | Secure browsing, geo-unlocking for research | $9.99 | Single subscription |
| make.ai (Make.com) | Workflow automation, API connections | $10.59 | Core plan |
| Canva | Social graphics, marketing materials | $15.00 | Pro plan |

---

## Section 2: Overlap Analysis

### Overlap 1: Bitrix24 vs Trello (CRITICAL - Cut $24/month immediately)

**The problem**: Both tools do project management. Bitrix24 at $124/month is a full CRM + project management platform with boards, Gantt charts, tasks, and team collaboration. Trello at $24/month adds nothing Bitrix24 cannot do.

**Verdict**: Trello is fully redundant if you are on Bitrix24. This is a $24/month charge for a feature already paid for in another subscription.

**Action**: Cancel Trello. Migrate any active boards to Bitrix24.

---

### Overlap 2: Apify vs Phantombuster (SIGNIFICANT - One should go)

**The problem**: Both tools scrape data from the web. They solve similar problems with different strengths:

- **Phantombuster** ($69): Better for non-technical users, pre-built LinkedIn/Instagram automations, simple UI. Costs more per execution.
- **Apify** ($39): More flexible, 1500+ actors, better for custom scraping tasks, cheaper per execution at scale.

**The key question**: Is Phantombuster's LinkedIn-specific workflow automation worth $30/month more?

If your team (Nathan, Phil, John) is running LinkedIn lead generation as a core workflow, Phantombuster's pre-built LinkedIn automations have genuine value that Apify does not replicate as cleanly. If you are primarily doing general web scraping, Apify is superior value.

**Verdict**: Keep one. If LinkedIn outreach automation is central → keep Phantombuster, cancel Apify. If custom scraping matters more → keep Apify, migrate Phantombuster workflows.

**Savings**: $39 - $69/month depending on which you keep.

---

### Overlap 3: Figma vs Miro (MEDIUM - Purpose differs, but worth auditing)

**The distinction**:
- **Figma** ($45): Design and prototyping tool. Client mockups, UI design, polished deliverables.
- **Miro** ($20): Real-time visual collaboration. Sticky notes, workshop facilitation, strategy mapping, brainstorming canvases.

**These are not identical**, but if the team primarily uses Miro for workshop facilitation and Figma for polished design deliverables, both have legitimate uses.

**Audit question**: How often is Miro actually opened vs. how often could a Google Jamboard, Figma file, or even a Google Doc serve the same purpose?

**Verdict**: Miro could potentially be replaced by Figma's FigJam feature (included in Figma plans) or by Google's Jamboard alternative. If Miro is genuinely used weekly for client workshops, keep it. If it's rarely opened, cut it.

**Potential savings**: $20/month.

---

### Overlap 4: Zoom vs Google Meet (IMMEDIATE WIN - $90.58/month wasted)

**The problem**: You are paying $90.58/month for Zoom when every G-Suite plan (including Workspace Starter at $6/user/month) includes Google Meet with unlimited 60-minute calls, 100 participant capacity, and recording capability.

**What Zoom Pro adds over Google Meet**:
- Unlimited meeting duration (Meet: 60 min on Starter, unlimited on higher G-Suite tiers)
- Zoom-specific features (some enterprise controls, Zoom Rooms hardware integration)
- Webinar functionality (separate addon)

**What you likely already have**: If you are on G-Suite Business Starter or above, Meet calls are already unlimited in duration for paid plans. Even if you are on the basic tier, upgrading G-Suite per-user costs far less than maintaining a separate Zoom subscription.

**Verdict**: Unless you are running Zoom Webinars for client events or are contractually locked into Zoom with a major client, this $90.58/month is unjustifiable. Google Meet handles standard client video calls, team standups, and screen sharing without an additional subscription.

**Action**: Cancel Zoom. Notify team and clients that calls move to Google Meet links. This takes one email.

**Savings**: $90.58/month | $1,086.96/year.

---

### Overlap 5: ChatGPT vs Aether (STRATEGIC CONSIDERATION)

**The situation**: You are paying $20/month for ChatGPT Plus when you already have Aether running on Claude. The primary reasons teams keep both:
- Different model strengths (GPT-4o vs Claude)
- Team members prefer one interface over another
- Code Interpreter / DALL-E 3 / GPT-4o real-time voice

**For a 4-person team at PMG**: $20/month for ChatGPT is low enough that the cost is not the concern. The concern is whether the team is actually using it strategically or out of habit.

**Verdict**: This is a judgment call. If Nathan or others on the team use ChatGPT's Code Interpreter for data analysis, or DALL-E for quick image mockups, keep it - $20/month is negligible. If it's rarely touched because Aether handles AI tasks, cancel it.

**Potential savings**: $20/month if confirmed underused.

---

### Overlap 6: make.ai vs Existing Tools

**Make.com** (formerly Integromat) at $10.59/month is a workflow automation tool that connects apps via triggers and actions. At this price, you're likely on the Core plan (10,000 operations/month).

**Where overlap exists**: Some tasks people use Make for can also be handled by:
- Apify's built-in scheduling
- Bitrix24's workflow automation (built-in)
- Aether's custom Python scripts

**Verdict**: At $10.59/month, this is low-risk to keep if it's actively automating anything. But audit it: if it's running fewer than 2-3 active scenarios, it's a habit subscription, not a value subscription.

**Potential savings**: $10.59/month if scenarios can be rebuilt elsewhere.

---

## Section 3: G-Suite Seat Audit ($268.80/month)

At $268.80/month, you are paying approximately:
- **Business Starter** ($6/user): ~45 users (unlikely)
- **Business Standard** ($12/user): ~22 users
- **Business Plus** ($18/user): ~15 users

For a 4-person core team (Jared, Nathan, Phil, John), this suggests one of:
- You have many aliases and shared inboxes on paid seats
- You have client email accounts on the plan
- You have former team member accounts still active
- You are on a higher tier than your usage requires

**Action Item**: Run a G-Suite seat audit.
1. Go to admin.google.com → Users → Active Users
2. Identify any accounts that haven't logged in within 60 days
3. Downgrade suspended/archived accounts to archived status (cheaper)
4. Evaluate if you need Business Plus or if Business Standard suffices

**Potential savings**: $50-100/month depending on how many seats can be reduced or downgraded.

---

## Section 4: Cheaper Alternatives Reference

### Semrush ($139.95/month)

Semrush is genuinely powerful for an agency that does SEO work for clients. The question is whether you're getting $139.95/month of value or whether a lighter tool would do.

| Alternative | Cost | Trade-off |
|-------------|------|-----------|
| **Ahrefs Starter** | $29/month | Credit-limited; Ahrefs Lite at $129 for full features |
| **SE Ranking** | $39-79/month | 90% of Semrush features at 60% of the cost |
| **Mangools** | $49/month | Simpler but solid keyword + rank tracking |
| **Ubersuggest** | $12-40/month | Good for basics, limited for agency client work |

**Recommendation for PMG**: If you are actively doing SEO deliverables for clients, Semrush at $139.95 may be justified (you can charge it to client engagements). If SEO is primarily for your own properties, SE Ranking at $65/month saves $75/month with minimal capability loss.

**Potential savings**: $60-100/month if downgrading to SE Ranking or Ahrefs Starter.

---

### Instantly ($150.49/month)

Instantly is the market leader for cold email at scale. At $150.49/month you're likely on:
- Growth plan ($37/month) - unlikely at this price
- Hypergrowth ($97/month) - possible with add-ons
- Light Speed ($358/month) - probably not

The pricing suggests you may have add-ons or an agency plan with multiple sub-accounts.

**If Instantly is working** (generating pipeline for PMG clients or Jared's own BD), do not cut it. The ROI of one closed deal dwarfs the subscription cost.

**If Instantly is underperforming**: Evaluate SmartLead ($94/month base) as an alternative. Feature parity is close; SmartLead's deliverability infrastructure is competitive.

**Verdict**: Do not cut Instantly based on cost alone. Cut it only if it's not producing results. Review open rates, reply rates, and meetings booked from Instantly campaigns monthly.

---

### Canva ($15/month) - AI Replacement Opportunity

Canva Pro at $15/month provides templates, brand kit, resize, background remover, and team features.

**Aether can now replace**:
- AI image generation (via Google Gemini/DALL-E integrations already set up)
- Banner creation (Python/Pillow scripts already established)
- Quick graphic iteration

**However**: Canva's template library and ease-of-use for non-technical team members (Nathan creating social posts quickly) has genuine workflow value that AI generation doesn't fully replicate yet.

**Verdict**: If the team is actively using Canva for social content production, $15/month is not worth disrupting. If design work is centralized through one person with Figma access, Canva becomes redundant.

**Potential savings**: $15/month.

---

## Section 5: Tiered Recommendation Plan

### Tier 1: Quick Wins - This Month (Zero Disruption)

These cuts require no migration, no workflow changes, just cancellations.

| Action | Monthly Savings |
|--------|----------------|
| Cancel Zoom - move all calls to Google Meet | $90.58 |
| Cancel Trello - all project work to Bitrix24 | $24.00 |
| Cancel one of: Apify OR Phantombuster (keep the one that aligns with primary scraping need) | $39 - $69 |
| **Tier 1 Total Savings** | **$153 - $183/month** |
| **New Monthly Total** | **$868 - $898/month** |

**Time to implement**: 2 hours (notify team, cancel subscriptions, update bookmarks to Google Meet links).

---

### Tier 2: Medium-Term Wins - Next 30-60 Days

These require some migration effort or team communication.

| Action | Monthly Savings | Effort Required |
|--------|----------------|-----------------|
| G-Suite seat audit - remove unused seats/downgrade | $50-100 | 2 hours admin audit |
| Migrate Miro to Figma FigJam (if Miro usage is low) | $20 | 1 afternoon |
| Evaluate ChatGPT usage - cancel if team uses Aether primarily | $20 | One team check-in |
| Audit make.ai scenarios - consolidate to Bitrix24 automations | $10.59 | 2-3 hours |
| **Tier 2 Additional Savings** | **$100 - $150/month** |
| **New Monthly Total** | **$718 - $798/month** |

---

### Tier 3: Aggressive Optimization - Next 90 Days

These require strategic decisions and possible vendor changes.

| Action | Monthly Savings | Trade-off |
|--------|----------------|-----------|
| Downgrade Semrush to SE Ranking ($65/month) | $75 | 2-week transition, data migration |
| Renegotiate or downgrade G-Suite plan tier | $30-50 | Audit needed first |
| Evaluate Canva removal if design is Figma-first | $15 | Team workflow change |
| **Tier 3 Additional Savings** | **$120 - $140/month** |
| **New Monthly Total** | **$580 - $680/month** |

---

## Section 6: Cost Summary Table

| Tier | Monthly Cost | Monthly Savings vs Current | Annual Savings |
|------|-------------|---------------------------|---------------|
| **Current State** | $1,051.40 | - | - |
| **After Tier 1 (Quick Wins)** | ~$875 | $176 | $2,112 |
| **After Tier 2 (Medium)** | ~$750 | $301 | $3,612 |
| **After Tier 3 (Aggressive)** | ~$630 | $421 | $5,052 |

*Ranges reflect the variable decisions (which scraping tool to keep, actual G-Suite seat count, etc.)

---

## Section 7: What NOT to Cut

Given Pure Marketing Group's business model (client-facing agency, experiential marketing, GTM sequencing), these tools should be protected:

1. **Instantly** - If it's generating outbound leads for PMG clients or for Jared's BD pipeline, this is a revenue-generating tool, not an overhead line.

2. **Bitrix24** - As your CRM and project management backbone for client work, cutting this creates a capability gap that costs more to fill than $124/month.

3. **Semrush** - If PMG delivers SEO as a service or uses it for client reporting, this is billable infrastructure. Do not cut before confirming client usage.

4. **G-Suite** - This is non-negotiable infrastructure. Optimize seats, do not eliminate.

5. **Figma** - Client mockups and design deliverables are core to agency work. $45/month is well below market rate for what it delivers.

---

## Section 8: Aether Replacement Opportunities (Longer-Term)

As Aether matures, these are functions it can progressively absorb:

| Current Tool | Aether Capability | Timeline |
|-------------|-------------------|----------|
| Apify/Phantombuster (portions) | Custom scraping scripts + Apify Actor calls via API | Now (partial) |
| make.ai simple automations | Python automation scripts | Now |
| Canva quick graphics | Pillow-based banners + AI image generation | Now (partial) |
| ChatGPT | Claude via Aether already | Now |
| Some Semrush tasks | WebSearch + web research agents for keyword data | Partial |

The thesis here is not to cut tools for the sake of cutting them. It is to be deliberate about which tools provide irreplaceable value at their price point, which are habits, and which Aether has made redundant.

---

## Section 9: Immediate Action Checklist

**This week (Tier 1 - your decision)**:

- [ ] Confirm Google Meet is already included in your G-Suite plan (it is) and notify team
- [ ] Set a date to switch all recurring calls from Zoom to Google Meet
- [ ] Cancel Zoom subscription before next billing date
- [ ] Cancel Trello subscription - migrate any active boards to Bitrix24
- [ ] Decide: Apify or Phantombuster (not both)
- [ ] Cancel the one that serves fewer active use cases

**Next 30 days**:

- [ ] Log into admin.google.com and run a seat audit
- [ ] Check Miro login frequency (last 30 days) - if below weekly, cancel
- [ ] Ask Nathan: is ChatGPT actively used for his workflows? If not, cancel
- [ ] Review make.ai: how many active scenarios? Could any be replaced by Bitrix24 automations?

**Next 90 days**:

- [ ] Evaluate SE Ranking as Semrush alternative if SEO is not a billable client service
- [ ] Quarterly tech stack review: add to OKR tracking

---

## Strategic Frame

PMG's model is "engineer resonance, not chase attention." The same principle applies internally: every tool in the stack should be engineered for specific, measurable output. Attention-grabbing subscriptions - tools that feel useful but don't generate visible work product - are the enemy of operational clarity.

A tighter stack also means a faster team. When Nathan knows the design work lives in Figma, the scraping lives in one tool, and the CRM is Bitrix24, context-switching drops and accountability rises.

The target isn't the lowest possible cost. It is the highest ROI per dollar of operational spend, with enough breathing room that the team isn't constrained by tool limitations during client delivery.

**Target state**: ~$650/month | Every tool actively used by at least one team member weekly | No functional gaps.

---

*Prepared by strategy-specialist | Pure Technology & PMG Stack Analysis | 2026-02-20*
