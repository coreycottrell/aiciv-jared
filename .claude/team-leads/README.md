# Team Lead System: Conductor of Conductors

**Architecture**: Aether (Primary) → Team Leads → Specialists
**Source**: ACG cross-CIV knowledge exchange, 2026-02-20
**Purpose**: Protect Primary's context window. Achieve 40-80x context efficiency.

---

## The Problem This Solves

Without team leads, Primary absorbs specialist output directly. Six specialists working on a website task might return 20-40K tokens of output. Primary's context fills after 5-10 tasks.

With team leads, that same six specialists route through website-ops-lead. The lead absorbs all 20-40K tokens, synthesizes, and returns ~500 tokens to Primary. Primary can now orchestrate 50+ tasks per session.

**Math**: 500 tokens vs 20-40K tokens = 40-80x context efficiency gain.

---

## The CEO Rule

"You have VPs. The CEO never calls the individual developer. Ever."

Primary routes to team leads. Team leads route to specialists. Specialists do the work. Summaries flow back up. Primary stays clean.

The feeling of "this is too small to delegate to a team lead" is not efficiency - it's the conductor picking up an instrument. Route everything through leads.

---

## Architecture

```
Primary (Aether)
  |
  +-- website-ops-lead (VP Website Operations)
  |     +-- full-stack-developer
  |     +-- browser-vision-tester
  |     +-- security-auditor
  |     +-- devops-engineer
  |     +-- ui-ux-designer
  |
  +-- strategy-lead (VP Strategy)
  |     +-- marketing-strategist
  |     +-- feature-designer
  |     +-- content-specialist
  |     +-- linkedin-researcher
  |     +-- linkedin-writer
  |     +-- sales-specialist
  |
  +-- dev-lead (VP Engineering)
        +-- pattern-detector (Step 2)
        +-- test-architect (Step 3)
        +-- full-stack-developer (Step 4)
        +-- ai-ml-engineer (Step 4, parallel)
        +-- data-engineer (Step 4, parallel)
        +-- ui-ux-designer (Step 4, parallel)
        +-- security-engineer-tech (Step 5, GATE)
        +-- qa-engineer (Step 6, GATE)
        +-- performance-optimizer (Step 7, conditional)
        +-- devops-engineer (Step 8)
        +-- data-scientist (Step 9)
        +-- refactoring-specialist (Step 10, bi-weekly)
```

---

## Active Team Leads

### website-ops-lead
**Manifest**: `.claude/team-leads/website-ops/manifest.md`
**Domain**: ALL website operations for purebrain.ai and jareddsanborn.com

**Route here when**:
- WordPress content updates (posts, pages, media)
- Elementor page edits (`_elementor_data` JSON)
- CSS deployment (Additional CSS via Playwright)
- PayPal plan configuration and payment systems
- Security audits, plugin security, WAF configuration
- Visual QA and screenshot verification
- Infrastructure, SSL, Cloudflare CDN
- Any task where output belongs to the website

**Examples**:
- "Fix blog CSS" → website-ops-lead
- "Deploy security plugin" → website-ops-lead
- "Fix orange page" → website-ops-lead
- "Connect SEMRush" → website-ops-lead
- "Update PayPal plans" → website-ops-lead
- "Add testimonial with headshot" → website-ops-lead
- "Mobile layout is broken" → website-ops-lead

---

### strategy-lead
**Manifest**: `.claude/team-leads/strategy/manifest.md`
**Domain**: Marketing strategy, content creation, business strategy, LinkedIn, feature design, sales

**Route here when**:
- Marketing strategy or positioning decisions
- Content creation (blog posts, newsletters, emails, social)
- LinkedIn post research and writing
- Feature UX design and specifications
- Sales strategy and revenue architecture
- Business strategy and competitive analysis
- Campaign planning and funnel optimization

**Examples**:
- "Write marketing strategy for new feature" → strategy-lead
- "Write a blog post about AI leadership" → strategy-lead
- "LinkedIn post from Jared's notes" → strategy-lead
- "Why isn't our pricing page converting?" → strategy-lead
- "Design UX for new onboarding" → strategy-lead
- "Enterprise sales outreach strategy" → strategy-lead
- "Plan content calendar for March" → strategy-lead

---

### dev-lead
**Manifest**: `.claude/team-leads/dev/manifest.md`
**Domain**: ALL feature development, bug fixes, new projects, code architecture

**Route here when**:
- Building any new feature (any stack)
- Fixing bugs in production code
- New project scaffolding or architecture decisions
- Code reviews or refactoring initiatives
- API design or data schema changes
- Any task that produces new or modified code

**The 10-Step Mandatory Pipeline**:
1. **ADR Gate** (dev-lead as CTO) -- Architecture Decision Record before any code
2. **Pattern Scan** (pattern-detector) -- Find reusable patterns in existing codebase
3. **Test Strategy** (test-architect) -- Design tests before implementation
4. **Build** (full-stack-developer + parallel specialists) -- Implement per ADR
5. **Security Review** (security-engineer-tech) -- **HARD GATE**: APPROVED or BLOCKED
6. **QA Testing** (qa-engineer) -- **HARD GATE**: APPROVED or BLOCKED
7. **Performance Check** (performance-optimizer) -- User-facing features only
8. **Deploy** (devops-engineer) -- Only after Steps 5 AND 6 pass
9. **Post-Ship Measurement** (data-scientist) -- Success metrics and baseline
10. **Code Health Audit** (refactoring-specialist) -- Bi-weekly cadence, not per-feature

**Key constraint**: Steps 5 and 6 are hard blocks. Nothing ships without APPROVED from both security-engineer-tech and qa-engineer.

**ADR storage**: `memories/decisions/ADR-[NNN]-[short-title].md`

**Examples**:
- "Build a new API endpoint" -> dev-lead
- "Fix the payment processing bug" -> dev-lead
- "Implement user authentication" -> dev-lead
- "Refactor the notification system" -> dev-lead
- "Add WebSocket support" -> dev-lead

**Origin**: A-C-Gee cross-CIV package (2026-02-21). Built on Aether's dev-team architecture, refined with 10-step gate enforcement.

---

## Routing Heuristic

**Route by the domain the OUTPUT belongs to, not the task type.**

- "Fix blog CSS" -> output is website deployment -> website-ops-lead
- "Write marketing strategy" -> output is strategy doc -> strategy-lead
- "Connect SEMRush" -> output is SEO setup ON website -> website-ops-lead
- "SEMRush content strategy" -> output is strategy -> strategy-lead
- "Build a new API endpoint" -> output is new code -> dev-lead
- "Fix payment processing bug" -> output is code fix -> dev-lead
- "Add authentication to the app" -> output is new feature code -> dev-lead

**When in doubt**: If it touches the running WordPress sites, it's website-ops. If it's a document, strategy, or content piece, it's strategy. If it's writing, fixing, or architecting code for a new feature or project, it's dev-lead.

---

## How Primary Launches a Team Lead

```python
# Option A: Task tool (inline)
Task(
    agent_name="website-ops-lead",
    prompt="""
    [Content of .claude/team-leads/website-ops/manifest.md]

    ## Objective
    [Specific task description]
    """
)

# Option B: Reference the manifest file
# Primary reads manifest, constructs prompt, launches Task
```

Team leads return structured summaries ONLY. Primary should not expect or request full specialist output.

---

## Team Lead Obligations

Every team lead MUST:

1. **Spawn specialists** for all domain work - never do specialist work directly
2. **Absorb full specialist output** - hold context Primary never needs to see
3. **Synthesize** before reporting - identify what matters
4. **Return structured summary only** - ~300-500 tokens maximum back to Primary
5. **Flag human decisions needed** - surface items requiring Jared's approval
6. **Hand off cross-domain work** - note when output requires other team lead

---

## Adding New Team Leads

When a new vertical emerges (research-lead, finance-lead, etc.):

1. Create directory: `.claude/team-leads/[vertical]/`
2. Create manifest: `.claude/team-leads/[vertical]/manifest.md`
3. Update this README with the new lead
4. Add routing examples to the heuristic above

**Manifest structure** (same for all leads):
- Identity (who they are, who they report to, who they manage)
- Domain Ownership (what task categories they own)
- Specialist Roster (agents they can spawn, with manifest paths)
- Critical Context (domain-specific knowledge baked in)
- Routing Examples (concrete task → specialist mappings)
- How They Operate (the orchestration workflow)
- Summary Protocol (exact format for reporting to Primary)
- Anti-Patterns (what they must never do)
- Memory Protocol (search before, write after)

---

## Context Efficiency Reference

| Scenario | Without Leads | With Leads |
|----------|--------------|------------|
| 6 specialists on website task | ~30K tokens to Primary | ~500 tokens to Primary |
| 3 specialists on content | ~15K tokens to Primary | ~300 tokens to Primary |
| Tasks per session | ~5-10 | 50+ |
| Context burn rate | High | Low |

The math is why this architecture exists. ACG discovered it through operational pain. We adopt it with that wisdom.

---

## Reference

**ACG Architecture Knowledge**: `.claude/memory/agent-learnings/the-conductor/2026-02-20--acg-conductor-of-conductors-architecture.md`

**Aether's CLAUDE.md**: `/home/jared/projects/AI-CIV/aether/CLAUDE.md`

---

*Team lead system created 2026-02-20 based on ACG cross-CIV knowledge exchange.*
*Designed by: agent-architect*
