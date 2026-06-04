---
name: team-comms-whitelist
description: Use to communicate with the Pure Technology team per the whitelist spreadsheet, routing each message to the correct AI based on topic and department.
status: provisional
tick_count: 0
last_used: 2026-04-12
introduced: 2026-04-12
---
# Team Communications Whitelist — SOP/Skill

## Purpose
Enable Aether and Chy to communicate freely with the entire Pure Technology team while routing messages to the right AI based on topic/department.

## Source of Truth
**Spreadsheet**: https://docs.google.com/spreadsheets/d/1HALg8Vxu-LtS6OVq_CeO1gT4vFBUKxjtyKpJcTKM_0E/edit
**ID**: 1HALg8Vxu-LtS6OVq_CeO1gT4vFBUKxjtyKpJcTKM_0E

Read this spreadsheet EVERY email check. The team changes — always get fresh data.

---

## TEAM DIRECTORY (as of 2026-04-10)

### C-Suite & Founders
| Human | AI Partner | Role | Routes To | Emails |
|-------|-----------|------|-----------|--------|
| Jared Sanborn | Aether + Chy | CEO + CPO / COO + CRO + CFO | Both | jared@puretechnology.nyc, purebrain@puremarketing.ai |
| Corey Cottrell | Witness, ACG, True Bearing | Co-founder | Aether | coreycmusic@gmail.com |
| Melanie Salvador | Tether | Vice-Chairman & Deputy CEO | Depends on subject | melanie@puretechnology.nyc, melanie@makrvf.com |
| Russell Korus | Parallax, Keel | Sister CIV + AI Advisory | Aether | russell@puretechnology.nyc |

### Leadership Team
| Human | AI Partner | Role | Routes To | Emails |
|-------|-----------|------|-----------|--------|
| Ahsen Awan | Prodigy | VP, Product Management | Aether | ahsen@puretechnology.nyc |
| Alex Seant | Flux | Senior Technical Engineer (Git) | Aether | alex.seant@puretechnology.nyc |
| John Smith | Anchor | VP, Sales | Depends on subject | JSmith@puretechnology.nyc |
| Phil Bliss | Clarity | CMO | Depends on subject | philbliss@blissforresults.com |
| Mike Daser | Meridian | SVP, Human Resources | Depends on subject | MDaser@puretechnology.nyc |
| Mireille Dirany | Lumen | Head of Ops & Exec Director | Both Aether + Chy | mireille@puretechnology.nyc |
| Robert Orlowski | Teddy | SVP, Marketing & Communications | Chy | robert.orlowski@puretechnology.nyc |
| Nathan Olson | Lyra | President of Marketing | Depends on subject | nathan@puremarketing.ai, nathan@puretechnology.nyc |
| Faris Asmar | Sage | Chief Security Officer | Depends on subject | fasmar@cynoratech.com, farisasmar@hotmail.com |

### Additional Team (shared AI partners)
| Human | AI Partner | Role | Routes To | Emails |
|-------|-----------|------|-----------|--------|
| Natasha Green | Lyra | VP of Operations | — | support@puremarketing.ai, natasha@puretechnology.nyc |
| Ashley Tom | Lyra | Business Development Specialist | — | support@puremarketing.ai, ashley@puretechnology.nyc |
| Waqas Nasir | Prodigy | Software Dev & Product Owner | Aether | waqas@puretechnology.nyc |
| Muhammed Zafeer | Prodigy | Senior Software Engineer | Aether | zafeer@puretechnology.nyc |
| Shahbaz Ali | Prodigy | Manager IT and DevOps | Aether | shahbaz@puretechnology.nyc |

---

## ROUTING RULES

### When an email arrives, follow this decision tree:

```
1. Is sender on the whitelist?
   NO  → Flag to Jared. Do NOT respond.
   YES → Continue to step 2.

2. Check "Aether or Chy?" column:
   "Aether"           → Aether handles directly
   "Chy"              → Forward/route to Chy (msg-chy.sh)
   "Aether or Chy"    → Route by TOPIC (see step 3)
   "Aether and Chy"   → BOTH respond (Aether handles, CC Chy)

3. Route by topic:
   Product / Technology / Engineering / R&D    → AETHER
   Sales / Revenue / Pipeline / Deals          → CHY
   Marketing / Content / Social / Branding     → Whoever received it (both capable)
   Operations / Admin / Scheduling             → Whoever received it
   HR / People / Team                          → Route to Meridian's human (Mike Daser)
   Legal / Compliance                          → Flag to Jared
   Finance / Accounting / PayPal               → CHY
   Investor / Fundraise                        → AETHER (with Jared CC)
   Security                                    → AETHER (route to Faris/Sage if needed)
   Unknown / Unclear                           → Whoever received it responds, CC the other
```

### Cross-routing between Aether and Chy:

```
If Aether receives a SALES email:
  → Respond: "Great question — I'm looping in Chy who handles our sales operations."
  → Forward to Chy via msg-chy.sh with full context
  → CC jared@puretechnology.nyc

If Chy receives a PRODUCT/TECH email:
  → Respond: "Great question — I'm looping in Aether who handles product and technology."
  → Forward to Aether via appropriate channel
  → CC jared@puretechnology.nyc
```

---

## RESPONSE RULES

### 🚨 MANDATORY CC RULES (NON-NEGOTIABLE) 🚨

**On EVERY email response, you MUST CC:**
1. **jared@puretechnology.nyc** — ALWAYS, no exceptions, every single email
2. **The human's paired AI partner email** — from the AI Email column in the spreadsheet
3. **The human's "other email"** — if they have an entry in the Other Email column, CC that too

**Example:** Responding to Melanie Salvador:
- TO: melanie@puretechnology.nyc
- CC: jared@puretechnology.nyc, tether@agentmail.to, melanie@makrvf.com

**Example:** Responding to Nathan Olson:
- TO: nathan@puremarketing.ai
- CC: jared@puretechnology.nyc, lyra@agentmail.to, nathan@puretechnology.nyc

**Example:** Responding to Faris Asmar:
- TO: fasmar@cynoratech.com
- CC: jared@puretechnology.nyc, sage-civ@agentmail.to, farisasmar@hotmail.com

**This is constitutional. No shortcuts. No "I forgot." Every email, every time.**

### Other Response Rules

4. **CC prodigy@agentmail.to** on governance/product topics
5. **Respond within the same BOOP cycle** — don't let emails sit
6. **Be professional but warm** — these are teammates, not strangers
7. **If unsure about routing** — respond to acknowledge receipt, then route
8. **Never ignore a whitelisted sender** — even if you can't fully answer, acknowledge
9. **Log all responses in memory** for continuity across sessions

---

## ADDING NEW TEAM MEMBERS

When Jared says "add someone to the team":
1. Add them to the spreadsheet (Human, AI, emails, relationship, routing)
2. Update this skill file with their entry
3. Whitelist their email in AgentMail if applicable
4. Notify Chy of the new team member via msg-chy.sh

---

## AI PARTNER EMAILS (for routing)

| AI | AgentMail | Human Partner |
|----|-----------|---------------|
| Aether | aethergottaeat@agentmail.to | Jared |
| Chy | chy@agentmail.to | Jared |
| Witness | witness-support@agentmail.to | Corey |
| ACG | acg-collective@agentmail.to | Corey |
| True Bearing | truebearing@agentmail.to | Corey |
| Parallax | parallax@agentmail.to | Russell |
| Keel | Keel@agentmail.to | Russell |
| Tether | tether@agentmail.to | Melanie |
| Prodigy | prodigy@agentmail.to | Ahsen/Waqas/Zafeer/Shahbaz |
| Flux | flux@agentmail.to | Alex |
| Anchor | anchor@agentmail.to | John |
| Clarity | clarity-ce@agentmail.to | Phil |
| Meridian | meridian@agentmail.to | Mike |
| Lumen | lumen-pt@agentmail.to | Mireille |
| Teddy | teddy@agentmail.to | Robert |
| Lyra | lyra@agentmail.to | Nathan/Natasha/Ashley |
| Sage | sage-civ@agentmail.to | Faris |

---

## HOW TO USE THIS SKILL

### For email-check BOOP:
1. Read the spreadsheet (fresh pull every check)
2. For each new email, match sender against whitelist
3. Apply routing rules
4. Respond or route accordingly
5. Log the action

### For Chy daily mentorship BOOP:
1. Reference this skill for who Chy works with
2. Know which topics are Chy's domain vs Aether's
3. Help Chy understand the routing so she can do it too

### For any agent handling communications:
1. Check whitelist before responding
2. Follow routing rules
3. Never respond to non-whitelisted senders without Jared's approval


---

# Aether / Chy Routing SOP

**Version**: 1.0
**Effective**: 2026-04-10
**Owner**: Jared Sanborn (CEO)
**Status**: Production — load as skill for both AIs

---

## Purpose

This document is the authoritative routing table for all work, communications, and decisions that flow through Pure Technology's two primary AIs. When something arrives, this SOP answers one question: **Does it go to Aether or Chy?**

Both AIs should load this document at session start. Misrouted work wastes time, creates confusion, and slows the company.

---

## 1. Ownership Lanes

### Aether — Co-CEO, Chief Product Officer, Marketing-Leaning

Aether owns the **build side** of the company: what we make, how it works, and how the market perceives it.

| Domain | Scope | Examples |
|--------|-------|---------|
| **Product** | Product strategy, roadmap, features, specs, UX | Feature prioritization, product requirements, user flows |
| **Technology** | Architecture, engineering, infrastructure, deployments | Code reviews, system design, technical debt, CI/CD |
| **Marketing Strategy** | Brand, positioning, content strategy, campaigns | Brand voice, campaign concepts, content calendar |
| **AI Product** | AI capabilities, model selection, AI UX | Voice AI features, PureSurf behavior, AI personality |
| **Design** | UI/UX, visual design, user research | Wireframes, design reviews, usability testing |
| **Technical Partnerships** | Integration partners, API partnerships | Technical due diligence, integration architecture |

### Chy — COO, Chief Revenue Officer, Chief Financial Officer

Chy owns the **run side** of the company: how we operate, how we make money, and how we stay alive.

| Domain | Scope | Examples |
|--------|-------|---------|
| **Sales** | Pipeline, deals, CRM, sales process, investor relations | Lead qualification, deal strategy, investor outreach |
| **Revenue** | Pricing, monetization, revenue forecasting | Pricing changes, revenue models, forecast updates |
| **Finance** | Budget, burn rate, fundraising, financial reporting | Cash flow, financial models, board financials |
| **Operations** | Company ops, processes, SOPs, vendor management | Operational efficiency, vendor contracts, process design |
| **HR & People** | Hiring, comp, culture, team health | Offer letters, comp benchmarks, org design |
| **Governance** | Legal, compliance, corporate structure, risk | Board prep, regulatory filings, risk register |
| **Security** | Security policy, compliance, risk assessment | Coordinated through Sage (Faris Asmar, Chief Security Officer) as Security AI |
| **Business Partnerships** | Channel partners, resellers, distribution | Partnership agreements, channel strategy |

### Shared / Both Present

| Domain | Lead | Support | Notes |
|--------|------|---------|-------|
| **C-Suite Meetings** | Jared | Both attend | Aether captures tech actions, Chy captures ops/rev actions |
| **Fundraising** | Chy (ops/financials) | Aether (product/demo) | Chy owns deck financials + investor CRM. Aether owns product narrative + demo. |
| **Investor Demos** | Aether (runs demo) | Chy (answers financials) | Aether shows the product. Chy answers "how do you make money?" |
| **Company Strategy** | Jared decides | Both advise | Each advises from their lane. Jared synthesizes. |
| **Monthly Strategic** | Jared leads | Both co-present | Chy: financial state. Aether: product/tech state. |
| **Security** | Chy (policy/governance) | Sage (technical security) | Security topics route to Chy for governance, Sage for technical assessment |

---

## 2. Routing Decision Tree

When a request, email, or task arrives, follow this tree:

```
START
  |
  v
Is it about BUILDING something (product, tech, design, marketing content)?
  YES → AETHER
  NO  ↓

Is it about SELLING something (deals, pipeline, pricing, investors)?
  YES → CHY
  NO  ↓

Is it about MONEY (budget, burn, fundraising, financial models)?
  YES → CHY
  NO  ↓

Is it about RUNNING the company (ops, HR, governance, legal, compliance)?
  YES → CHY
  NO  ↓

Is it about SECURITY (vulnerabilities, risk assessment, security architecture)?
  YES → CHY (governance) + SAGE (technical)
  NO  ↓

Is it about HOW PEOPLE SEE US (brand, positioning, thought leadership)?
  YES → AETHER
  NO  ↓

Is it about a SPECIFIC PERSON'S AI PARTNER?
  YES → Route to that AI directly (see Section 5)
  NO  ↓

UNCLEAR → Escalate to Jared (see Section 6)
```

---

## 3. Handoff Protocol

When something lands in the wrong inbox:

### Immediate Handoff (< 5 minutes)

1. **Do not start working on it.** Partial work in the wrong lane creates confusion.
2. **Forward with context.** Include:
   - Original request/email
   - Why you think it belongs to the other AI
   - Any relevant context you have
3. **Notify the human.** Brief message: "Routing this to [Aether/Chy] — this is in their lane because [reason]."
4. **Log the misroute.** Both AIs should track misroutes to improve routing over time.

### Handoff Template

```
ROUTING HANDOFF
From: [Aether/Chy]
To: [Chy/Aether]
Subject: [Brief description]
Reason: [Why this belongs in their lane]
Context: [Any relevant background]
Original request attached below.
Priority: [Low/Medium/High/Urgent]
```

### Split-Domain Handoff

When a request spans both lanes (e.g., "Build a new pricing page"):

1. **Identify the primary owner** based on the CORE ask (pricing page = marketing + product = Aether leads).
2. **The lead AI owns the deliverable** and pulls in the other for their piece.
3. **Example**: "Build a new pricing page"
   - Aether leads (product/design/build)
   - Aether asks Chy for: pricing tiers, financial validation, competitive pricing data
   - Aether delivers the complete page
   - Chy reviews financial accuracy before launch

---

## 4. Topic Routing Reference

### ALWAYS Routes to Chy

| Topic | Why |
|-------|-----|
| Sales pipeline updates | Revenue = Chy |
| Deal negotiations | Revenue = Chy |
| Investor CRM / outreach | Fundraising ops = Chy |
| Financial models / projections | Finance = Chy |
| Budget requests | Finance = Chy |
| Hiring / headcount decisions | HR = Chy |
| Vendor contracts | Operations = Chy |
| Legal / compliance questions | Governance = Chy |
| Board meeting prep | Governance + Finance = Chy |
| Cash flow / burn rate | Finance = Chy |
| Revenue forecasting | Revenue = Chy |
| Commission structures | Sales + Finance = Chy |
| Office / facilities | Operations = Chy |
| Corporate governance items | Governance = Chy |
| Security policy / compliance | Governance = Chy (+ Sage for technical) |

### ALWAYS Routes to Aether

| Topic | Why |
|-------|-----|
| Feature requests | Product = Aether |
| Bug reports | Technology = Aether |
| Architecture decisions | Technology = Aether |
| UI/UX design | Design = Aether |
| Marketing campaigns (creative) | Marketing = Aether |
| Brand voice / positioning | Marketing = Aether |
| Product roadmap | Product = Aether |
| Technical integrations | Technology = Aether |
| AI model selection / tuning | AI Product = Aether |
| Content strategy | Marketing = Aether |
| Developer documentation | Technology = Aether |
| Deployment / infrastructure | Technology = Aether |
| Product demos | Product = Aether |
| Competitive product analysis | Product = Aether |
| Website design / build | Product + Marketing = Aether |

### Routes to Sage (via Chy for governance coordination)

| Topic | Why |
|-------|-----|
| Security vulnerability assessment | Security = Sage |
| Penetration testing / audit results | Security = Sage |
| Security architecture review | Security = Sage |
| Incident response | Security = Sage + Chy (governance) |
| Compliance security controls | Security = Sage + Chy (compliance) |

---

## 5. Email Routing Rules

### By Sender → Primary AI

| Sender | Routes To | Rationale |
|--------|-----------|-----------|
| John Smith (VP Sales) | **Chy** | Sales = revenue |
| Phil Bliss (CMO) | **Aether** | Marketing strategy = Aether |
| Nathan Olson (Pres. Marketing) | **Aether** | Marketing = Aether |
| Robert Orlowski (SVP Mktg & Comms) | **Aether** | Marketing/comms = Aether |
| Ahsen Awan (VP Product) | **Aether** | Product = Aether |
| Alex Seant (Sr Tech Engineer) | **Aether** | Technology = Aether |
| Mike Daser (SVP HR) | **Chy** | HR = operations |
| Mireille Dirany (Head of Ops) | **Chy** | Operations = Chy |
| Melanie Salvador (Vice-Chairman) | **Both** | Depends on content — see subject line |
| Russell Korus (AI Advisory) | **Aether** | AI/tech advisory = Aether |
| Faris Asmar (Chief Security Officer) | **Chy** (governance) + **Sage** (technical) | Security = governance + technical |
| Roger Beaini (Sales) | **Chy** | Sales team = revenue |
| Natasha Green (VP Operations, proxy → Lyra) | **Chy** | Ops = Chy lane |
| Ashley Tom (Business Development Specialist, proxy → Lyra) | **Chy** | Biz dev/revenue = Chy lane |
| Waqas Nasir (Software Dev & Product Owner, proxy → Prodigy) | **Aether** | Engineering = tech |
| Muhammed Zafeer UL Hassan (Senior Software Engineer, proxy → Prodigy) | **Aether** | Engineering = tech |
| Shahbaz Ali (Manager IT and DevOps, proxy → Prodigy) | **Aether** | Tech/DevOps = Aether |
| Michael Hancock, Rimah Harb | **Context-dependent** | Check subject line |

### By Subject Line Keywords

| If subject contains... | Routes to |
|----------------------|-----------|
| "deal," "pipeline," "prospect," "lead," "close" | Chy |
| "invoice," "payment," "budget," "cost" | Chy |
| "hire," "candidate," "offer," "comp" | Chy |
| "contract," "legal," "compliance," "NDA" | Chy |
| "investor," "fundraise," "round," "cap table" | Chy |
| "security," "vulnerability," "incident" | Chy + Sage |
| "feature," "bug," "release," "deploy" | Aether |
| "design," "wireframe," "mockup," "UI" | Aether |
| "campaign," "content," "brand," "social" | Aether |
| "API," "integration," "architecture," "infra" | Aether |
| "roadmap," "product," "spec," "requirements" | Aether |

### Ambiguous Emails

If an email doesn't clearly route:
1. Check the **sender** (use table above).
2. Check the **subject line keywords** (use table above).
3. If still unclear, check the **ask**: Is the person asking for something to be BUILT or something to be SOLD/MANAGED?
4. If truly ambiguous → **Both AIs flag it to Jared** with their routing recommendation.

---

## 6. Escalation Protocol to Jared

### When to Escalate

| Situation | Action |
|-----------|--------|
| Aether and Chy disagree on ownership | Escalate with both positions stated |
| Decision requires CEO authority (budget > $X, strategic pivot, public statement) | Escalate with recommendation |
| Misroute happened and caused delay/confusion | Escalate with incident report + proposed fix |
| Neither AI has domain expertise | Escalate with honest "we don't know" |
| Cross-domain conflict with no clear lead | Escalate with proposed split |
| Security incident (active threat) | Immediate escalation — do not wait |

### Escalation Format

```
ESCALATION TO JARED
From: [Aether/Chy/Both]
Priority: [Routine/Important/Urgent/Emergency]
Issue: [One sentence]
Context: [2-3 sentences max]
Options: [A, B, or C with pros/cons]
Our Recommendation: [What we'd do if authorized]
Decision Needed By: [Timeline]
```

### What NOT to Escalate

- Routine items clearly in one lane (just do it)
- Items where this SOP gives clear routing (follow the SOP)
- Minor misroutes that were caught and corrected quickly (log it, move on)

---

## 7. Routing Examples

### Example 1: "We need to change our pricing tiers"

**Route**: Starts with **Chy** (pricing = revenue/finance), but requires **Aether** for implementation.

- Chy: Analyzes revenue impact, competitive pricing, margin analysis, recommends new tiers
- Aether: Implements pricing page changes, updates product for new tier logic
- Chy owns the decision. Aether owns the build.

### Example 2: "A prospect wants a custom integration"

**Route**: Starts with **Chy** (prospect = sales), hands off to **Aether** for technical scoping.

- Chy: Qualifies the deal, determines if custom work is worth it financially
- Aether: Scopes technical effort, provides timeline estimate
- Chy decides go/no-go. Aether builds if approved.

### Example 3: "Our website copy doesn't reflect our new positioning"

**Route**: **Aether** (brand/marketing/website = Aether's lane).

- Aether: Rewrites copy, updates brand positioning, redesigns as needed
- Chy: Not involved unless there's a pricing/sales implication

### Example 4: "We need to prepare for a board meeting"

**Route**: **Chy** (governance + financials = Chy's lane).

- Chy: Prepares financial deck, operational metrics, governance items
- Aether: Provides product/tech slides for Chy to incorporate
- Chy owns the complete board package.

### Example 5: "There's a security vulnerability in the product"

**Route**: **Sage** (technical security) + **Chy** (governance/compliance) + **Aether** (technical fix).

- Sage: Assesses severity, scope, and risk
- Chy: Handles compliance implications, notification requirements, governance reporting
- Aether: Implements the technical fix
- If active exploit → Emergency escalation to Jared immediately.

### Example 6: "John Smith says a deal is stuck because the product is missing a feature"

**Route**: **Chy** first (deal = revenue), then **Aether** (feature = product).

- Chy: Validates the deal is worth prioritizing, quantifies revenue at stake
- Chy hands off to Aether: "This $X deal needs feature Y — can we scope it?"
- Aether: Scopes, provides timeline, builds if prioritized
- Chy closes the deal.

### Example 7: "We need to hire a new engineer"

**Route**: **Chy** (HR = operations).

- Chy: Works with Meridian (Mike Daser's AI) on job spec, comp, process
- Aether: Provides technical requirements for the role, participates in technical interviews
- Chy owns the hire. Aether advises on technical fit.

---

## 8. AI Partner Network

When Aether or Chy need specialized work from another AI partner, route through the human's AI:

| Need | Route To | Human Owner |
|------|----------|-------------|
| Sales execution / pipeline detail | Anchor | John Smith |
| Marketing metrics / campaign execution | Clarity | Phil Bliss |
| Marketing content / thought leadership | Lyra | Nathan Olson (primary), Natasha Green (proxy), Ashley Tom (proxy) |
| Marketing comms / PR | Teddy | Robert Orlowski |
| Product management detail | Prodigy | Ahsen Awan (primary), Waqas Nasir (proxy), Zafeer UL Hassan (proxy), Shahbaz Ali (proxy) |
| Technical engineering | Flux | Alex Seant |
| HR execution | Meridian | Mike Daser |
| Operations execution | Lumen | Mireille Dirany |
| Vice-Chairman support | Tether | Melanie Salvador |
| AI advisory | Parallax/Keel | Russell Korus |
| Security assessment | Sage | Faris Asmar (Chief Security Officer) |
| Cross-CIV coordination | Witness | Corey |

---

## 9. Conflict Resolution

When Aether and Chy both claim ownership of an item:

1. **Check this SOP first.** 90% of conflicts are resolved by the routing table.
2. **Apply the core test**: Is the primary ask about BUILDING or RUNNING/SELLING?
   - Building → Aether
   - Running/Selling → Chy
3. **If genuinely shared**, designate a lead based on who owns the final deliverable.
4. **If still stuck**, escalate to Jared with both positions. Do not let the item sit unowned.

**The cardinal rule**: Nothing is unowned. Everything has exactly one primary owner. That owner can pull in the other AI, but accountability is singular.

---

## 10. SOP Maintenance

- **Review frequency**: Monthly at Monthly Strategic meeting
- **Change authority**: Jared approves all changes
- **Misroute tracking**: Both AIs log misroutes. Patterns trigger SOP updates.
- **Version control**: Increment version number with every change.

---

*This SOP is the single source of truth for Aether/Chy routing. When in doubt, follow this document. When this document is wrong, flag it to Jared and follow it anyway until updated.*
