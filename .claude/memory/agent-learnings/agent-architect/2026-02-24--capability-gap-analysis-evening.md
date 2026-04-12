# Capability Gap Analysis - 2026-02-24 Evening

## Executive Summary
Building on pattern-detector's utilization audit from earlier today. This analysis focuses on **structural capability gaps** - recurring work patterns that lack dedicated ownership.

## Key Findings

### 1. WordPress Deployment Specialist Gap (CRITICAL)
- **Evidence**: 80 "fix" learnings, 34 "deploy" learnings, 15 "orange-fix", 6 "plugin-v" iterations in full-stack-developer
- **Pattern**: full-stack-developer handles ALL WordPress deployment (REST API, wp:html blocks, wpautop bypass, elementor canvas templates, CSS specificity battles)
- **Gap**: No dedicated WordPress/CMS specialist. full-stack-developer is overloaded with WP-specific tribal knowledge
- **Recommendation**: NOT a new agent. Instead, create a `wordpress-deployment` skill that codifies the hard-won patterns (wp:html wrapping, !important scoping, body class selectors, cache busting). The full-stack-developer learnings directory (229 files) IS the knowledge base - it needs extraction into reusable skill form.

### 2. SEO/Analytics Specialist Gap (MODERATE)
- **Evidence**: 5 seo learnings, 6 og-image learnings, 4 website-analysis learnings, Google indexing diagnostic today
- **Pattern**: SEO work (meta descriptions, og tags, schema markup, indexing) done ad-hoc by full-stack-developer
- **Gap**: data-scientist has analytics capability but hasn't been invoked since Feb 21. No agent owns SEO as a discipline.
- **Recommendation**: Activate data-scientist for analytics review (GA4, GSC, Clarity are connected). For SEO specifically, consider granting web-researcher a `seo-audit` skill rather than creating a new agent.

### 3. Brevo/Email Marketing Automation Gap (MODERATE)
- **Evidence**: 15 brevo-related learnings across full-stack-developer, 5 template iterations
- **Pattern**: Brevo template creation, automation workflows, list management all handled by full-stack-developer
- **Gap**: marketing-automation-specialist exists (6 learnings) but underutilized. Brevo-specific work routes to full-stack instead.
- **Recommendation**: Route ALL Brevo work to marketing-automation-specialist. No new agent needed - delegation routing fix.

### 4. Pipeline Enforcement Gap (ACKNOWLEDGED)
- **Evidence**: BUILD->SECURITY->QA->SHIP pipeline exists as a rule but enforcement is inconsistent
- **Pattern**: 13 qa-engineer learnings vs 229 full-stack learnings = QA sees ~6% of deployments
- **Gap**: engineering-flow-boop skill exists but isn't consistently triggered
- **Recommendation**: Already identified in pattern-detector's audit. Priority activation needed.

### 5. Dormant Agent Activation Priority
Agents with manifests but near-zero activity that SHOULD be active given current work:

| Priority | Agent | Why Now |
|----------|-------|---------|
| P0 | blogger | Daily posting cadence but blogger not writing posts |
| P0 | integration-auditor | Constitutional requirement, zero invocations ever |
| P1 | data-scientist | Analytics tools connected, nobody analyzing |
| P1 | capability-curator | 64+ skills with no lifecycle review |
| P2 | ai-psychologist | Collective health unmonitored during peak period |
| P2 | test-architect | Testing strategy absent |

## What Does NOT Need a New Agent
- WordPress work: Skill extraction, not agent creation
- SEO: Skill grant to existing agents
- Brevo: Routing fix to marketing-automation-specialist
- Orange-fix pattern: CSS specificity skill for full-stack-developer

## What MIGHT Need a New Agent (Future)
- **Site Reliability / Monitoring Agent**: As purebrain.ai grows, proactive monitoring (uptime, performance, broken links, SSL) could justify a dedicated agent. Not yet - volume doesn't warrant it.

## Conclusion
The collective has MORE than enough agents (78 manifests). The gap is **utilization and routing**, not capability. Top actions:
1. Extract WordPress deployment patterns into a codified skill
2. Route Brevo work to marketing-automation-specialist
3. Activate blogger, integration-auditor, data-scientist
4. Enforce BUILD->SECURITY->QA->SHIP consistently
