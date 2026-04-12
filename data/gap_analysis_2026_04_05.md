# Capability Gap Analysis — April 5, 2026

## 1. Dormant Agent Problem: 62 agents (54%) never meaningfully invoked

High-priority dormant agents that SHOULD be active:
- payment-flow-qa: Payment pages CONSTITUTIONAL, but QA done ad-hoc
- customer-success-manager: Real customers need proactive monitoring
- seo-specialist: Daily blog posts ship without SEO review
- conversion-rate-optimizer: 6 payment pages, zero A/B testing
- operations-analyst: No operational metrics exist
- competitive-analyst: 4 major model drops this week, zero analysis

## 2. Recurring Blockers (4 patterns)
A. Email Welcome Sequence — Flagged 12+ times, never built. Route to marketing-automation-specialist.
B. LinkedIn/PureSurf 429s — recurring weekly. Need proactive rate-limit middleware.
C. CORS fixes — every sprint. security-engineer-tech should own policy.
D. CF Pages deploy conflicts — need deploy mutex from devops-engineer.

## 3. Recommendations
1. ACTIVATE dormant agents: customer-success-manager, seo-specialist, operations-analyst, payment-flow-qa
2. Build email welcome sequence via marketing-automation-specialist
3. Create cf-deploy-pipeline skill to prevent deploy conflicts
4. Activate competitive-analyst for model-release tracking
5. Add pre-publish SEO gate to post-blog chain
6. Customer lifecycle dashboard

## Stats: 115 agents | 53 with learnings | 62 dormant | 0 new agents proposed | 3 new skills proposed
