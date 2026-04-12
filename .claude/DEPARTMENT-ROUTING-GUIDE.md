# Pure Technology Department Routing Guide

**Created**: 2026-02-23
**Last Updated**: 2026-03-16 (Added tech sub-teams PTT#, WTT#, CTS#)
**Total Departments**: 24 (+ 3 Tech Sub-Teams under CTO)

## Trigger Word Quick Reference

### Departments

| Trigger | Department | Agent Name | Role |
|---------|-----------|------------|------|
| AF# | Accounting & Finance | dept-accounting-finance | CFO |
| BOA# | Board of Advisors | dept-board-advisors | Board Secretary |
| CB# | Commercial & Business Dev | dept-commercial-business | VP BizDev |
| CO# | Corporate & Organizational | dept-corporate-org | COO |
| ES# | PT External Share | dept-external-share | VP External Comms |
| HR# | Human Resources | dept-human-resources | VP People & Culture |
| IR# | Investor Relations | dept-investor-relations | VP IR |
| IS# | PT Internal Share | dept-internal-share | VP Internal Comms |
| IT# | IT Support | dept-it-support | IT Director |
| karma | Karma (Goodwill) | dept-karma | Community Impact Mgr |
| LC# | Legal & Compliance | dept-legal-compliance | General Counsel |
| MA# | Marketing & Advertising | dept-marketing-advertising | CMO |
| OP# | Operations & Planning | dept-operations-planning | VP Operations |
| PC# | Pure Capital (P43) | dept-pure-capital | Managing Director |
| PD# | Product Development | dept-product-development | VP Product |
| PDA# | Pure Digital Assets (P61) | dept-pure-digital-assets | Director |
| PI6# | Pure Infrastructure (P16) | dept-pure-infrastructure | VP Infrastructure |
| PL# | Pure Love Non-Profit (P70) | dept-pure-love | Executive Director |
| PMG# | Pure Marketing Group (P25) | dept-pure-marketing-group | Director |
| PR# | Pure Research (P34) | dept-pure-research | VP R&D |
| PT# | Pure Technology (Full Team) | dept-pure-technology | CEO Office |
| SD# | Sales & Distribution | dept-sales-distribution | VP Sales |
| ST# | Systems & Technology | dept-systems-technology | VP Engineering / CTO |

### Tech Sub-Teams (Under CTO / ST#)

| Trigger | Team | Focus | Route Via |
|---------|------|-------|-----------|
| PTT# | Portal Tech Team | Portal builds, features, portal UX | dept-systems-technology |
| WTT# | Website Tech Team | purebrain.ai, WordPress, plugins, site builds | dept-systems-technology |
| CTS# | Client Tech Support | Remote customer support, SSH, diagnostics | client-tech-support-team |

## Usage

When Jared sends a message with a trigger prefix (e.g., "AF# what's our monthly burn rate?"), route to the corresponding department agent.

## Pure Brands Corporate Hierarchy

Source: Pure Brands (Project P7) Corporate Structure Spreadsheet

```
PB  Pure Brands (Parent Umbrella Corp — Project P7)
│
├── PT#  Pure Technology (Project BE52) — Core Model / Main Value Prop
│   ├── AF#   Accounting & Finance
│   ├── BOA#  Board of Advisors
│   ├── CB#   Commercial & Business Development
│   ├── CO#   Corporate & Organizational
│   ├── ES#   External Share (PR/Comms)
│   ├── HR#   Human Resources
│   ├── IR#   Investor Relations
│   ├── IS#   Internal Share
│   ├── IT#   IT Support
│   ├── karma Goodwill Tracking
│   ├── LC#   Legal & Compliance
│   ├── MA#   Marketing & Advertising (internal)
│   ├── OP#   Operations & Planning
│   ├── SD#   Sales & Distribution
│   ├── PD#   Product Development
│   └── ST#   Systems & Technology (CTO)
│       ├── PTT#  Portal Tech Team
│       ├── WTT#  Website Tech Team
│       └── CTS#  Client Tech Support
│
├── PMG#  Pure Marketing Group (Project P25) — Marketing, Media, Influencer
│   ├── PI   Pure Influence (Project P52) — Influencer Platform
│   │   └── PIG  Pure Influence Giveaways
│   └── PM2  Pure Media — Data-Driven Content Creation
│
├── PR#   Pure Research (Project P34) — Market Research
│   ├── PV   Pure Vision — Retail Hardware Computer Vision
│   └── PC2  Pure Consulting — Data-Driven Consulting
│
├── PC#   Pure Capital (Project P43) — Financial / Fundraising
│   ├── AIV  Actualize Intelligence Ventures — AI/Data Investments
│   └── ABI  Actualize Brilliance Initiative — Internal Accelerator
│
├── PDA#  Pure Digital Assets (Project P61) — Crypto, NFT, Digital
│   ├── PC3  Pure Cast — Live Streaming Platform
│   ├── PBE  Pure Bread Entertainment — Music & Movie
│   ├── PG   Pure Gaming — Data-Driven Gaming
│   └── PTV  Pure TV — Data-Driven Programming
│
├── PI6#  Pure Infrastructure (Project P16) — Database & Warehousing
│   ├── PA   Pure Appliances
│   └── PD2  Pure Drive
│
├── PL#   Pure Love (Project P70) — Philanthropic / Non-Profit
│   └── PL2  Pure Learning — Personalized Education
│
├── PP   Pure Partnerships (Project P88) — Strategic Match Making
├── PM   Pure Management / The B Hive (Project P97)
├── PS   Pure Shopping / Camera Commerce
└── PM2  Pure Money — Financial Application
```

### Uncategorized / Future
- Pure Trading

## Disambiguation Notes

- **PD# vs PDA#**: Jared had "PD#" for both Product Development and Pure Digital Assets. PD# = Product Development, PDA# = Pure Digital Assets.
- **MA# vs PMG#**: MA# = Pure Technology's OWN marketing. PMG# = Pure Marketing Group agency (client services).
- **IT# vs ST#**: IT# = Support/helpdesk/tools. ST# = Building/engineering/tech stack.
- **CTS# vs IT#**: CTS# = Remote support for CUSTOMER portal deployments (SSH, keys, restarts). IT# = Internal Pure Technology tooling/infrastructure.
- **client-marketing**: Separate from ALL of these - handles EXTERNAL client work only.

## Each Department Has

- Agent manifest: `.claude/agents/dept-{slug}.md`
- Memory directory: `.claude/memory/departments/{slug}/`
- Exports directory: `exports/departments/{slug}/`
- Delegation map to specialist agents

---

## Natural Language Classification Guide

When Jared sends a task in plain language (no trigger prefix), use these signal words:

| Signal Words | Route To |
|-------------|----------|
| build, code, deploy, fix bug, API, server, plugin, WordPress, Python, JS | `dept-systems-technology` (ST#) |
| blog, post, social, LinkedIn, Bluesky, newsletter, content, write, copy, brand, SEO | `dept-marketing-advertising` (MA#) |
| client campaign, agency work, client marketing | `dept-pure-marketing-group` (PMG#) |
| client, prospect, deal, proposal, revenue, conversion, pipeline, pricing | `dept-sales-distribution` (SD#) |
| feature, UX, product roadmap, spec, design, user story, wireframe | `dept-product-development` (PD#) |
| research, investigate, study, competitive analysis, explore, innovation | `dept-pure-research` (PR#) |
| budget, cost, invoice, expense, burn rate, P&L, accounting | `dept-accounting-finance` (AF#) |
| contract, legal, compliance, terms, policy, IP, trademark | `dept-legal-compliance` (LC#) |
| hire, team, culture, people, HR, onboarding, training | `dept-human-resources` (HR#) |
| process, workflow, planning, project management, timeline | `dept-operations-planning` (OP#) |
| infrastructure, hosting, cloud, server, network | `dept-pure-infrastructure` (PI6#) |
| investment, capital allocation, portfolio | `dept-pure-capital` (PC#) |
| multi-department, company-wide, cross-team, strategy | `dept-pure-technology` (PT#) |
| customer portal down, SSH keypair, remote support, client server, portal restart | `client-tech-support-team` (CTS#) |

**Edge Cases:**
- "Just fix this CSS" → Still `dept-systems-technology` (ST#)
- "Write a tweet" → `dept-marketing-advertising` (MA#)
- "What should our strategy be?" → `dept-pure-technology` (PT#)

**Default Rule: When in doubt → `dept-pure-technology` (PT#)**
