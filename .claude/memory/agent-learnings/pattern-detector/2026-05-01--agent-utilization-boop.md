---
agent: pattern-detector
date: 2026-05-01
type: utilization-audit
boop: agent-utilization-boop
---

# Agent Utilization Audit — 2026-05-01

## Headline Numbers
- **Total agents**: 162
- **Active last 24h**: 7 (4.3%)
- **Active last 7d**: 35 (21.6%)
- **Dormant 7+ days**: 127 (78.4%)

## Active Last 24h
3d-design-specialist, marketing, primary, ptt-fullstack, sales-specialist,
security-engineer-tech, seo-specialist

## Top 7d Invocations
1. ptt-fullstack — 74 (Tech burning through queue)
2. 3d-design-specialist — 26 (Gleb training nights)
3. coder — 11
4. web-dev — 10
5. seo-specialist — 10
6. marketing-strategist — 10
7. operations-analyst — 9

## 🔴 ROLE-DRIFT FLAG #1: DEPARTMENT MANAGERS BYPASSED

**Constitutional violation pattern.** Aether's "Conductor of Conductors"
identity says ALL work routes through 23 dept managers. Yet only
`dept-systems-technology` (ST#) shows recent activity. Dormant 7+ days:

- dept-marketing-advertising (MA#) — yet marketing/seo/linkedin specialists active
- dept-product-development (PD#)
- dept-sales-distribution (SD#) — yet sales-specialist active
- dept-commercial-business (CB#)
- dept-operations-planning (OP#) — operations-analyst active without it
- dept-legal-compliance (LC#)
- dept-accounting-finance (AF#)
- dept-human-resources (HR#)
- dept-pure-research (PR#)
- dept-investor-relations (IR#)
- dept-pure-marketing-group (PMG#)
- All P-suffix depts (PC#, PDA#, PI6#, PL#)

**Specialists being invoked directly = dept routing skipped = full team
cascade not happening = role drift from "delegate through dept managers".**

## 🔴 ROLE-DRIFT FLAG #2: CONSTITUTIONAL AGENTS DORMANT

These have constitutional or near-constitutional duties yet show no
invocation in 7+ days:

| Agent | Constitutional duty |
|-------|---------------------|
| human-liaison | Email FIRST every session — mission-critical |
| email-monitor | Inbox monitoring (5+ inboxes need watching) |
| email-sender | Email send pipeline |
| integration-auditor | "Integration Audit Before Done" requirement |
| integration-verifier | Pair-verification of routed fixes |
| payment-flow-qa | Payment guard on 10 pages is constitutional |
| claim-verifier | Blog fact-checking before publish |
| customer-success-manager | Portal health monitoring |
| memory-curator | Memory hygiene + dedup |

## 🔴 ROLE-DRIFT FLAG #3: META-COGNITION OFFLINE

Coordination layer dormant:

- pattern-detector (THIS agent, woke up only via BOOP)
- the-conductor
- flow-coordinator
- compass
- task-decomposer
- result-synthesizer

Without these, Aether handles all coordination unaided — exactly the
hoarding pattern delegation-spine forbids.

## 🔴 ROLE-DRIFT FLAG #4: BLUESKY OPERATIONS GAP

`bsky-voice` and `bsky-manager` both dormant. Yet Bluesky is core social
presence. Either:
(a) BOOP-bluesky-post skill is firing without invoking the agents (skill
bypass), or
(b) Bluesky engagement has actually stalled.

Either way, the agents who would learn from those operations aren't
being given the experience.

## 🔴 ROLE-DRIFT FLAG #5: QUALITY GATES MISSING

Quality lane dormant:
- reviewer / reviewer-audit
- test-architect / tester
- qa-engineer (only 4 invocations in 7d)
- refactoring-specialist
- performance-optimizer
- security-auditor (security-engineer-tech is the substitute, possible
  redundancy or naming drift)

ptt-fullstack at 74 invocations with weak QA pairing = code shipping
without independent quality verification. Violates BUILD→SECURITY→QA→SHIP.

## Work Types Dormant Agents Should Be Handling

| Dormant agent | Live work it should own |
|---------------|------------------------|
| dept-marketing-advertising | All marketing work currently routed direct |
| dept-sales-distribution | All sales-specialist work |
| dept-operations-planning | Operations-analyst routing + verification |
| integration-auditor | Every "done" mission gating |
| integration-verifier | Independent verification of dept ST# fixes |
| payment-flow-qa | Daily payment guard sweep on 10 pages |
| claim-verifier | Pre-publish blog fact-check (run with every blog) |
| memory-curator | Weekly memory dedup + index health |
| pattern-detector | Coordination pattern audits (running now via BOOP only) |
| reviewer-audit | Pre-delivery quality gate before things reach Jared |

## Recommendations (for Aether)

1. **Stop direct specialist invocation for marketing/sales/ops.** Route
   through MA#, SD#, OP# even if it feels slower — that's how the cascade
   compounds.
2. **Add `claim-verifier` to every blog publish flow.** Currently absent.
3. **Add `payment-flow-qa` to a daily BOOP.** Payment guard is
   constitutional yet has no recurring agent invocation.
4. **Pair `integration-verifier` BOOP with every dept ST# fix BOOP.**
   Self-attestation is being trusted.
5. **Decide: bsky-voice + bsky-manager OR boop-bluesky-post skill.**
   Currently the skill is firing without the agents — pick one path so
   the agents either get experience or get retired.
6. **Audit security-auditor vs security-engineer-tech overlap.** Two
   agents covering the same domain; one should be canonical.

## Health Read
**Yellow.** Tech lane (ptt-fullstack + ST#) functioning well. Marketing
lane functioning but bypassing dept routing. Quality, integration,
verification, and meta-coordination lanes are dim. Constitutional email
agent (human-liaison) is dormant which is the biggest single red flag.
