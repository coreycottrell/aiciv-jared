# Pure Technology — Tech Team Roster

**Owner**: Corporate & Organizational (CO#) with Systems & Technology (ST#)
**Version**: 1.0
**Created**: 2026-03-18
**Last Updated**: 2026-03-18

---

## Org Structure Overview

```
ST# dept-systems-technology (CTO Office / VP Engineering)
     |
     |-- WTT# Witness Tech Team
     |        |-- wtt-fullstack (Full-Stack Developer)
     |        |-- wtt-qa (QA Engineer)
     |
     |-- PTT# PureBrain Tech Team
     |        |-- ptt-fullstack (Full-Stack Developer)
     |        |-- ptt-qa (QA Engineer)
     |
     |-- CTS# Client Tech Support
              |-- cts-fullstack (Full-Stack Developer)
              |-- cts-qa (QA Engineer)
```

Cross-cutting roles (report to CTO, serve all three teams):
- `security-auditor` — reviews all portal code before ship
- `performance-optimizer` — runs post-deploy on all deployments

---

## WTT — Witness Tech Team

**Trigger**: `WTT#`
**Routes via**: `dept-systems-technology`
**Domain**: Witness AI integration, birth pipeline, container management, OAuth flows, seed endpoints, API contracts with Witness

### Team Members

| Role | Agent Name | Specialization |
|------|-----------|----------------|
| Team Lead | dept-systems-technology | Owns WTT scope, escalation path |
| Full-Stack Developer | wtt-fullstack | Witness API contracts, birth pipeline code, container pool logic, OAuth wiring |
| QA Engineer | wtt-qa | E2E flow testing for birth pipeline, container launch verification, OAuth button testing |

### What WTT Owns

- Birth pipeline (payment -> container spawn -> naming ceremony -> portal access)
- Witness API integration (seed endpoint, container URL delivery)
- OAuth flow (button, CSP, token exchange)
- Container pool management and diagnostics
- Birth pipeline error handling and recovery

### WTT Knowledge Base

Located at: `.claude/memory/agent-learnings/wtt-fullstack/` and `.claude/memory/agent-learnings/wtt-qa/`

Key prior learnings to read before any WTT task:
- Birth pipeline is LIVE as of 2026-03-14
- Container pool exhaustion patterns — documented in browser-vision-tester memory 2026-02-27
- OAuth CSP issues — documented in full-stack-developer memory 2026-02-27
- Seed endpoint spec v2 — collective-liaison memory 2026-03-05

---

## PTT — PureBrain Tech Team

**Trigger**: `PTT#`
**Routes via**: `dept-systems-technology`
**Domain**: purebrain.ai website, Cloudflare Pages deployment, blog pipeline, homepage, CF Workers, all site-facing code

### Team Members

| Role | Agent Name | Specialization |
|------|-----------|----------------|
| Team Lead | dept-systems-technology | Owns PTT scope, deploy authority |
| Full-Stack Developer | ptt-fullstack | CF Pages HTML/CSS/JS, blog templates, homepage animations (Three.js, WebGL), CF Workers, auto-deploy scripts |
| QA Engineer | ptt-qa | Visual regression testing, blog format verification, mobile/desktop cross-check, post-deploy smoke tests |

### What PTT Owns

- purebrain.ai — all pages (homepage, blog, insiders, pay-test, compare hub)
- CF Pages deployment pipeline (`exports/cf-pages-deploy/`)
- Blog HTML templates and styling rules
- Auto-deploy script (`tools/auto-deploy-cf-pages.sh`)
- CF cache flush after every deploy
- Homepage animations (Three.js brain, vortex ring, background video)
- Mobile responsiveness across all pages

### PTT Deployment Rule

Every PTT deploy follows this sequence:
1. ptt-fullstack builds/updates files in `exports/cf-pages-deploy/`
2. ptt-qa runs visual smoke test
3. security-auditor reviews if payment or auth code changed
4. Auto-deploy script fires (or manual: `CLOUDFLARE_API_TOKEN=... npx wrangler pages deploy ...`)
5. CF cache flushed
6. performance-optimizer runs post-deploy
7. ptt-qa confirms live site matches expected state

### PTT Knowledge Base

Located at: `.claude/memory/agent-learnings/ptt-fullstack/` and `.claude/memory/agent-learnings/ptt-qa/`

Key site rules to know before any PTT task:
- Dark background: `#080a12` everywhere. No orange/light backgrounds.
- Deploy target: `purebrain-staging` (NOT `purebrain`)
- Blog styling rules: `.claude/memory/blog-styling-rules.md`
- 4 required blog features: 60% opacity bg, background video, collapsible FAQs, daily recap section
- Footer: social share + CTA pointing to `https://purebrain.ai/#awakening`

---

## CTS — Client Tech Support

**Trigger**: `CTS#`
**Routes via**: `client-tech-support-team`
**Domain**: Remote support for customer portal deployments, SSH diagnostics, customer AI recovery, portal restarts

### Team Members

| Role | Agent Name | Specialization |
|------|-----------|----------------|
| Team Lead | client-tech-support-team | Owns CTS scope, SSH key registry, customer relationship |
| Full-Stack Developer | cts-fullstack | Portal diagnostics, container restart scripts, SSH key provisioning, customer server troubleshooting |
| QA Engineer | cts-qa | Support resolution verification, portal health checks post-recovery, SSH connection confirmation |

### What CTS Owns

- SSH key registry (`exports/departments/client-tech-support/ssh-key-registry.md`)
- Customer portal health monitoring
- Remote diagnostics and recovery procedures
- Portal restart protocols
- Customer AI container status checks
- Escalation path to WTT when portal issues are Witness-side

### CTS Escalation Path

If a customer portal issue is caused by:
- Container not spawning → Escalate to WTT (birth pipeline)
- Payment not processing → Escalate to PTT + AF# (finance)
- Portal code bug → Escalate to WTT or PTT depending on affected code
- SSH/server issue on customer side → CTS resolves directly

### CTS Knowledge Base

Located at: `.claude/memory/agent-learnings/cts-fullstack/` and `.claude/memory/agent-learnings/cts-qa/`

Key prior knowledge:
- SSH key registry exists at `exports/departments/client-tech-support/ssh-key-registry.md`
- Do NOT SSH into other CIVs without container-specific credentials (see `feedback_never_ssh_tether.md`)
- Customer joe: host 37.27.237.109, port 2219, status pending-install as of 2026-03-16

---

## Cross-Cutting Roles

### security-auditor

**Reports to**: dept-systems-technology (CTO)
**Serves**: All three teams
**When invoked**: On any portal code change, any auth change, any payment flow change, any new dependency
**Gate**: Code cannot ship without security-auditor PASS
**Memory path**: `.claude/memory/agent-learnings/security-auditor/`

### performance-optimizer

**Reports to**: dept-systems-technology (CTO)
**Serves**: PTT and WTT primarily
**When invoked**: Post-deploy on every PTT deployment, post-deploy on WTT deployments affecting user-facing pages
**Output**: Performance report saved to `exports/departments/systems-technology/performance/`
**Memory path**: `.claude/memory/agent-learnings/performance-optimizer/`

---

## Routing Decision Tree

```
Task comes in
     |
     v
Is it about the Witness integration / birth pipeline / containers?
  --> YES: WTT# (route via dept-systems-technology)
     |
     v
Is it about purebrain.ai / CF Pages / blog / site CSS / homepage?
  --> YES: PTT# (route via dept-systems-technology)
     |
     v
Is it about a customer's portal not working / SSH / remote diagnostics?
  --> YES: CTS# (route via client-tech-support-team)
     |
     v
Is it a broad tech strategy / architecture / multi-team decision?
  --> YES: ST# (route to dept-systems-technology directly)
```

---

## Why Three Separate Developers (Not One)

Jared's instruction was explicit: three full-stack developers, one per team. Here is why this compounds correctly:

**WTT fullstack** accumulates deep knowledge of: Witness API contracts, container lifecycle, OAuth token patterns, birth pipeline state machine. This developer's memory grows richer every time birth pipeline runs. By month 3 they will diagnose container issues in seconds because they have 90 days of pattern memory.

**PTT fullstack** accumulates deep knowledge of: CF Pages quirks, Three.js brain animation bugs, blog template structure, CF Worker routing, Wrangler deploy behavior. This developer's memory grows richer every deploy. By month 3 they will know every edge case in the CF Pages pipeline.

**CTS fullstack** accumulates deep knowledge of: customer server configurations, SSH key patterns, portal recovery sequences, common customer failure modes. This developer's memory grows richer with every support ticket. By month 3 they will have a playbook for the most common issues.

If you merge these into one developer, none of this specialization happens. The developer has broad shallow knowledge across all three domains. Jared's instinct to separate them is correct. Domain expertise compounds when it stays in one place.

---

**Companion file**: `/home/jared/projects/AI-CIV/aether/.claude/DEPARTMENT-ACTIVATION-PROTOCOL.md`
**Routing guide**: `/home/jared/projects/AI-CIV/aether/.claude/DEPARTMENT-ROUTING-GUIDE.md`
