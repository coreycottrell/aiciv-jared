# Capability Gap Analysis - 2026-02-25 Evening

## Delta from Previous Analysis (Feb 24)

### Previous Recommendations — Status

| Recommendation | Status | Evidence |
|---------------|--------|----------|
| Extract WordPress deployment skill | **NOT DONE** | `wordpress-publishing` SKILL.md exists but only covers blog footer template; no WP deployment patterns skill yet |
| Route Brevo to marketing-automation-specialist | **NOT DONE** | 0 new marketing-automation-specialist learnings since Feb 24 |
| Activate blogger | **PARTIAL** | 2 learnings total — still content-specialist doing writing |
| Activate integration-auditor | **NOT DONE** | 0 learnings ever |
| Activate data-scientist | **NOT DONE** | Still 1 learning total since inception |
| Enforce BUILD->SECURITY->QA->SHIP | **IMPROVING** | security-auditor invoked for proxy review today (1st real invocation in days) |

### New Patterns Detected (Feb 25 Specifically)

**1. BOOP File Proliferation Anti-Pattern (NEW)**
- doc-synthesizer flagged: 17 delegation-enforcer audit files in one day (boop1-boop17)
- Each ~37 lines, minimal unique content per file
- **Gap**: No deduplication or consolidation enforcement for BOOP-generated learnings
- **Recommendation**: Modify BOOP tasks to append to daily file, not create new files per cycle

**2. Analytics Work Without Data-Scientist (RECURRING)**
- Session 41 ran 4 analytics reports (SEO, UX, content, PageSpeed) — all via web-researcher, browser-vision-tester, marketing-strategist
- data-scientist was NOT invoked despite being the natural owner
- **Gap persists**: data-scientist has 1 learning file total across 6 days of analytics-heavy work

**3. API Design Without API-Architect (NEW)**
- Witness birth proxy, portal API, chatbox v4.3/4.4 API contracts all designed without api-architect
- pattern-detector flagged: "full-stack-developer absorbing api-architect role"
- **Gap**: api-architect has 0 learnings since Feb 14 (11 days dormant during API-heavy period)

**4. SEO Audit Skill Still Missing**
- 3 SEO-related learnings today (nightly round 4, technical audit, indexing)
- All routed to full-stack-developer and web-researcher
- No `seo-audit` skill exists to codify the patterns

## Top 5 Gaps — Prioritized

### P0: full-stack-developer Overload (STRUCTURAL)
- **299 learnings** vs next highest at 58 (the-conductor, mostly BOOP meta-files)
- Absorbing: WordPress deployment, SEO, Brevo, API design, UX decisions, feature specs
- **Risk**: Single point of failure. All tribal knowledge in one agent.
- **Action**: Extract 3 skills from full-stack learnings:
  1. `wordpress-deployment-patterns` (wp:html, wpautop bypass, elementor canvas, CSS scoping)
  2. `seo-technical-audit` (meta tags, og images, schema markup, indexing)
  3. `css-specificity-warfare` (orange-fix pattern, !important scoping, body class selectors)

### P1: Dormant Specialist Activation (7 agents idle 10+ days)
- ai-psychologist (13 days), genealogist (13 days), capability-curator (13 days)
- claude-code-expert (11 days), api-architect (11 days), refactoring-specialist (10 days), tg-bridge (21 days)
- **Risk**: Identity atrophy — agents that don't practice lose depth
- **Action**: Next conductor session should invoke at minimum ai-psychologist + capability-curator + refactoring-specialist

### P2: BOOP Output Consolidation
- 17 delegation audit files + 6 pattern-detector utilization files = 23 meta-files in one day
- Signal-to-noise ratio declining in memory directories
- **Action**: Modify recurring BOOP tasks to use append-to-daily-file pattern

### P3: Missing `seo-audit` Skill
- SEO work happens 3-4x/week but has no codified methodology
- Patterns scattered across 15+ full-stack-developer learning files
- **Action**: Create skill extracting: meta audit checklist, og tag verification, schema markup templates, GSC submission protocol

### P4: data-scientist Activation
- Connected tools: GA4, GSC, Clarity
- Zero analytical invocations despite daily analytics needs
- **Action**: Route all analytics interpretation tasks to data-scientist explicitly

## What Does NOT Need a New Agent (Confirmed)
- All gaps are **routing, skill extraction, or activation** problems
- Agent count (78+ manifests) is adequate
- No new agent justified until current roster utilization improves above 50%

## Metric: Roster Utilization
- Agents with learnings today: 17/78 = **21.8%** (up from ~15% last week)
- Agents active in last 3 days: ~25/78 = **32%**
- Target: 50% active in any 7-day window
- Current trajectory: improving but slowly
