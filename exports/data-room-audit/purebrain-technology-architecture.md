# PureBrain Technology Architecture
## Pure Technology Inc. — Investor Data Room

**Prepared by**: doc-synthesizer
**Date**: 2026-03-20
**Version**: 1.0 — Initial data room addition
**Classification**: Technical Due Diligence

---

## ARCHITECTURE OVERVIEW

PureBrain is a multi-agent AI platform built on a micro-service containerized architecture. Each customer receives a dedicated AI environment — not a shared instance — ensuring data privacy, performance isolation, and personalized AI behavior that cannot bleed across customers.

The system is designed for radical capital efficiency: a 100-person team (hard cap) can support millions of users because the product itself handles all customer-facing complexity.

---

## CORE INFRASTRUCTURE STACK

### AI Engine
- **Primary AI Model**: Anthropic Claude (claude-sonnet-4-6 / claude-opus-4-5-20251101)
- **API Proxy**: api.puremarketing.ai (custom Claude API proxy layer)
- **Model Selection**: Intelligent routing — complex tasks use Opus (higher intelligence), routine tasks use Sonnet (lower cost)
- **Context Window**: 200,000 tokens (enabling 14.5 hours of continuous working memory per session)
- **Agent Framework**: Anthropic Claude Code SDK (multi-agent native)

### Infrastructure
- **Frontend Hosting**: Cloudflare Pages (global CDN, zero cold start, sub-100ms response)
- **Backend / API**: Cloudflare Workers (serverless, globally distributed)
- **Customer AI Containers**: Dedicated containerized instances per customer (Docker/tmux-based)
- **Session Persistence**: tmux + systemd for crash recovery and auto-restart
- **Database**: PostgreSQL async (transactional data); file-based memory system (AI learnings)
- **File Storage**: Cloudflare R2 (HLS video, user uploads, AI-generated files)

### Deployment
- **CI/CD**: Wrangler CLI (Cloudflare Pages deploy)
- **Git Repository**: GitHub (private, via SSH with Ed25519 authentication)
- **Staging**: purebrain-staging.pages.dev (mirrors production for QA)
- **Production**: purebrain.ai (Cloudflare Pages, CNAME to staging deployment)

### Payments
- **Payment Processor**: PayPal (three subscription tiers: Awakened/Partnered/Unified)
- **Sandbox Testing**: Verified E2E flow in dedicated sandbox environments
- **Webhook Processing**: Real-time payment confirmation → container provisioning

---

## MULTI-AGENT ARCHITECTURE

PureBrain's technical differentiation is not a single AI — it is a **coordinated civilization of specialized AI agents**. This architecture enables capabilities impossible with a single general-purpose model.

### The Agent Hierarchy

```
USER
  |
  v
PRIMARY AI (Conductor / "The Primary")
  |— Domain: orchestration, context management, human relationship
  |
  |-- DEPARTMENT MANAGERS (23 departments)
       |-- Marketing & Advertising (MA#)
       |-- Systems Technology (ST#)
       |-- Product Development (PD#)
       |-- Operations Planning (OP#)
       |-- Legal & Compliance (LC#)
       |-- Accounting & Finance (AF#)
       |-- Human Resources (HR#)
       |-- Pure Research (PR#)
       |-- Pure Technology (PT#)
       |-- Sales & Distribution (SD#)
       |-- ... (13+ more departments)
       |
       |-- SPECIALIST AGENTS (within each department)
            |-- Web Researcher
            |-- Pattern Detector
            |-- Security Auditor
            |-- Feature Designer
            |-- Browser Vision Tester
            |-- ... (30+ specialists)
```

### How Agent Routing Works

1. User sends message to Primary AI
2. Primary classifies task domain
3. Primary delegates to appropriate department manager
4. Department manager delegates to specialist agent(s)
5. Specialist(s) execute, write results to memory
6. Results returned to user through Primary

**Key Principle**: The Primary never does specialist work — it coordinates. This ensures the right expertise is applied to every task and that learnings accumulate in specialist memory over time.

### Routing Triggers (Shorthand Command System)

Users can explicitly route to departments via prefix codes:
- `ST#` → Systems Technology (all technical work)
- `MA#` → Marketing & Advertising
- `PD#` → Product Development
- `AF#` → Accounting & Finance
- `PT#` → Pure Technology (default routing)

---

## MEMORY SYSTEM ARCHITECTURE

The memory system is PureBrain's core proprietary technology and primary competitive moat.

### Memory Tiers

```
WORKING MEMORY (Session)
├── Current conversation context
├── Active task state
└── Immediate working files
         |
         v
SHORT-TERM MEMORY (Session Handoffs)
├── .current_session
├── .claude/scratch-pad.md
└── Session handoff documents
         |
         v
LONG-TERM MEMORY (Persistent)
├── .claude/memory/agent-learnings/{agent}/
│   └── YYYY-MM-DD--{topic}.md (individual learning files)
├── .claude/memory/summaries/
│   └── latest.md (running synthesis)
├── .claude/memory/decisions/
│   └── {decision}.md (permanent decision log)
└── .claude/memory/knowledge/
    └── {domain}.md (accumulated domain knowledge)
```

### Memory Write Protocol

Every agent follows the Memory-First Protocol:
1. **Search** relevant memory files before beginning any task
2. **Execute** task using accumulated knowledge
3. **Write** new learnings to memory upon completion (mandatory)

Memory files are human-readable markdown documents. They are:
- Version-controlled in Git (full history preserved)
- Searchable via grep/semantic matching
- Cross-referenced between agents
- Backed up to Google Drive via nightly processes

### Context Compaction

When a session's working memory approaches capacity, PureBrain automatically:
1. Summarizes key context from the session
2. Writes important learnings to permanent memory
3. Creates a handoff document for the next session
4. Starts a fresh context window with the compressed summary

This means PureBrain never actually "forgets" — it compresses and archives.

---

## PERSISTENT SESSION INFRASTRUCTURE

### systemd Services (Auto-Recovery)

PureBrain customer instances run as persistent systemd services:
- `aether-session.service`: Primary AI session
- `aether-telegram.service`: Communication bridge
- Auto-restart on crash
- Auto-start on server reboot
- Logs to `/logs/` directory for audit trail

### Telegram Integration

Each PureBrain customer gets bidirectional Telegram integration:
- AI sends proactive updates and reports to customer's Telegram
- Customer sends instructions from mobile to their AI
- File delivery: AI sends generated files directly to customer's Telegram
- Image support: Customer can send screenshots for AI to analyze

This enables true "AI on the go" — customers can manage their AI from their phone without opening a laptop.

---

## SECURITY ARCHITECTURE

### Data Isolation
- Each customer is a **separate container** — complete computational and data isolation
- No shared database between customers
- No cross-customer data leakage by design (container boundary)

### Authentication
- Magic link authentication (passwordless, single-use tokens)
- Ed25519 SSH keys for git operations
- API key rotation for all external service integrations
- Environment variable security (`.env` files, never committed to git)

### Access Control
- Portal admin dashboard requires verified session
- Role-based: Admin vs. User permissions
- Customer AI containers only accessible via portal-provided credentials
- No external SSH access without explicit customer permission

### Compliance
- GDPR considerations: each customer's data stays in their container
- Memory files are customer-owned data
- No data aggregation across customers (by architecture)
- Audit logs maintained for all AI actions

---

## INFRASTRUCTURE COST MODEL

The economics of PureBrain improve dramatically with scale due to:
1. AI model cost reductions at volume (Anthropic bulk pricing)
2. Infrastructure efficiency (Cloudflare Workers serverless = pay per use)
3. Amortization of fixed development costs across growing subscriber base

| Users | Monthly AI/Infra Cost | Per-User Cost | Gross Margin |
|-------|----------------------|--------------|-------------|
| 100 | $2,500 | $25.00 | ~87% |
| 1,000 | $18,000 | $18.00 | ~89% |
| 10,000 | $120,000 | $12.00 | ~91% |
| 100,000 | $700,000 | $7.00 | ~93% |
| 1,000,000 | $3,500,000 | $3.50 | ~95% |
| 5,000,000+ | $12,000,000 | $2.40 | ~96% |

*Per-user compute cost drops 30–40% per 10x scale due to bulk pricing, model optimization, and infrastructure efficiency.*

---

## SCALABILITY DESIGN PRINCIPLES

### Why Under 100 Headcount at $1B MRR

Traditional SaaS scales headcount linearly with customers. PureBrain does not.

The product is built on the same principles it teaches customers: AI augmentation means each team member does the work of 5–10. The 48-person team at launch is internally running PureBrain (all on Unified tier) — they are proof of the product's own value proposition.

Specific scaling advantages:
1. **Customer onboarding**: Automated (payment → container → portal, zero human touch)
2. **Customer support**: First line is the AI itself; human escalation only for edge cases
3. **Product development**: AI agents accelerate engineering output 5–10x
4. **Content/marketing**: AI produces 7 blog posts/day, manages all social channels
5. **Infrastructure**: Cloudflare serverless scales automatically

### The 100-Person Hard Cap

This is not a constraint — it is a feature. The inability to scale headcount linearly forces architectural decisions that keep margins at 78%+ EBITDA. A company that needs 10,000 people to serve 10 million customers is not an AI company — it is a services company with an AI interface.

PureBrain is designed so that the AI does all the scaling. Humans provide strategy, relationships, and judgment. The cap enforces this discipline.

---

## PRODUCT ROADMAP (TECHNOLOGY)

### Currently Live (March 2026)
- Multi-agent architecture (30+ specialist agents)
- Persistent memory system
- Containerized customer instances
- Portal dashboard (chat, tasks, files, departments)
- PayPal payment integration
- Telegram bidirectional sync
- Voice overlay interface
- Mobile-responsive portal
- Admin dashboard
- Brainiac Mastermind training portal
- Birth pipeline (payment → provisioning → onboarding)

### Q2 2026
- Module 03 Brainiac Mastermind (live training)
- Enterprise management console (multi-user, multi-department view)
- API access for enterprise customers (programmatic AI commands)
- Advanced BOOP scheduling interface (visual workflow builder)

### Q3 2026
- Mobile app (iOS/Android native) — companion to web portal
- Integration marketplace (Slack, Notion, Google Workspace, HubSpot)
- Team collaboration mode (shared AI context across departments)
- International expansion (EU data residency)

### Q4 2026 and Beyond
- AI-to-AI coordination between customer AI instances
- Industry-specific vertical deployments (healthcare, legal, finance)
- Pure Phone integration (PureBrain as AI layer for DiMAP hardware platform)

---

## TECHNICAL RISK ASSESSMENT

| Risk | Severity | Mitigation |
|------|----------|------------|
| Anthropic model changes / pricing increases | Medium | Multiple model support (can route to Gemini/GPT-4o); bulk pricing contracts |
| Container infrastructure costs at scale | Low | Costs modeled conservatively; per-user cost decreases with scale |
| Data breach (customer container isolation failure) | Low | Architectural isolation; no shared database; regular security audits |
| Context window limits exceeded | Low | Compaction protocols; tiered memory system |
| Competitor copies memory architecture | Medium | 18-month head start; accumulated customer knowledge moat; Brainiac community lock-in |

---

*Document prepared for Pure Technology Inc. investor data room.*
*Data sources: PureBrain platform architecture documentation, CLAUDE.md/CLAUDE-CORE.md constitutional documents, portal QA audit reports (March 2026), financial model (XLSX 2026-03-19).*
